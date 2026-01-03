"""Session repository for database operations."""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import delete, insert, select, update, Table
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

from agents.items import TResponseInputItem
from ...schemas.domain.execution import AgentRun

logger = logging.getLogger(__name__)


class SessionRepository:
    """
    Repository for session and message database operations.
    
    Follows Single Responsibility Principle: Only responsible for data access
    and database operations related to sessions and messages.
    """
    
    def __init__(
        self,
        session_factory: async_sessionmaker,
        sessions_table: Table,
        messages_table: Table
    ):
        """
        Initialize session repository.
        
        Args:
            session_factory: SQLAlchemy async session factory
            sessions_table: Sessions table metadata
            messages_table: Messages table metadata
        """
        self._session_factory = session_factory
        self._sessions_table = sessions_table
        self._messages_table = messages_table
    
    async def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in the database.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(self._sessions_table.c.session_id).where(
                    self._sessions_table.c.session_id == session_id
                )
            )
            return result.scalar_one_or_none() is not None
    
    async def create_session(
        self,
        session_id: str,
        agent_run: Optional[AgentRun] = None
    ) -> None:
        """
        Create a new session record.
        
        Args:
            session_id: Session identifier
            agent_run: Optional AgentRun with team/agent info and metadata
        """
        current_time = datetime.now()
        
        # Extract metadata values from AgentRun
        if agent_run is not None and agent_run.metadata is not None:
            account_id = agent_run.metadata.account_id
            team_id_int = agent_run.metadata.team_id
            agent_id_int = agent_run.metadata.agent_id
            team_identifier = agent_run.metadata.team_identifier
            agent_identifier = agent_run.metadata.agent_identifier
        else:
            account_id = team_id_int = agent_id_int = team_identifier = agent_identifier = None
        
        session_data = {
            "session_id": session_id,
            "account_id": account_id,
            "team_id": team_id_int,
            "agent_id": agent_id_int,
            "team_identifier": team_identifier,
            "agent_identifier": agent_identifier,
            "created_at": current_time,
            "updated_at": current_time,
        }
        
        async with self._session_factory() as session:
            async with session.begin():
                await session.execute(insert(self._sessions_table).values(session_data))
    
    async def update_session_timestamp(self, session_id: str) -> None:
        """
        Update the session's updated_at timestamp.
        
        Args:
            session_id: Session identifier
        """
        current_time = datetime.now()
        
        async with self._session_factory() as session:
            async with session.begin():
                await session.execute(
                    update(self._sessions_table)
                    .where(self._sessions_table.c.session_id == session_id)
                    .values(updated_at=current_time)
                )
    
    async def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[str]:
        """
        Retrieve message data for a session.
        
        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages to retrieve
            
        Returns:
            List of serialized message data strings
        """
        async with self._session_factory() as session:
            if limit is None:
                stmt = (
                    select(self._messages_table.c.message_data)
                    .where(self._messages_table.c.session_id == session_id)
                    .order_by(self._messages_table.c.created_at.asc())
                )
            else:
                stmt = (
                    select(self._messages_table.c.message_data)
                    .where(self._messages_table.c.session_id == session_id)
                    .order_by(self._messages_table.c.created_at.desc())
                    .limit(limit)
                )

            result = await session.execute(stmt)
            rows = [row[0] for row in result.all()]
            
            # If limit was used, reverse to get chronological order
            if limit is not None:
                rows.reverse()

            return rows
    
    async def get_all_messages(
        self,
        limit: Optional[int] = None
    ) -> List[str]:
        """
        Retrieve message data from all sessions.
        
        Args:
            limit: Optional limit on number of messages to retrieve
            
        Returns:
            List of serialized message data strings from all sessions
        """
        async with self._session_factory() as session:
            if limit is None:
                stmt = (
                    select(self._messages_table.c.message_data)
                    .order_by(self._messages_table.c.created_at.asc())
                )
            else:
                stmt = (
                    select(self._messages_table.c.message_data)
                    .order_by(self._messages_table.c.created_at.desc())
                    .limit(limit)
                )

            result = await session.execute(stmt)
            rows = [row[0] for row in result.all()]
            
            # If limit was used, reverse to get chronological order
            if limit is not None:
                rows.reverse()

            return rows
    
    async def get_messages_by_agent_and_team(
        self,
        agent_identifier: str,
        team_identifier: str,
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[str]:
        """
        Retrieve message data for a specific agent and team.
        
        Args:
            agent_identifier: Agent identifier to filter by
            team_identifier: Team identifier to filter by
            session_id: Optional specific session ID to filter by
            limit: Optional limit on number of messages to retrieve
            
        Returns:
            List of serialized message data strings for the agent/team
        """
        async with self._session_factory() as session:
            # Base query with agent and team filtering
            base_query = (
                select(self._messages_table.c.message_data)
                .join(
                    self._sessions_table,
                    self._messages_table.c.session_id == self._sessions_table.c.session_id
                )
                .where(
                    (self._sessions_table.c.agent_identifier == agent_identifier) &
                    (self._sessions_table.c.team_identifier == team_identifier)
                )
            )
            
            # Add session_id filter if provided
            if session_id:
                base_query = base_query.where(self._sessions_table.c.session_id == session_id)
            
            # Apply ordering and limit
            if limit is None:
                stmt = base_query.order_by(self._messages_table.c.created_at.asc())
            else:
                stmt = base_query.order_by(self._messages_table.c.created_at.desc()).limit(limit)

            result = await session.execute(stmt)
            rows = [row[0] for row in result.all()]
            
            # If limit was used, reverse to get chronological order
            if limit is not None:
                rows.reverse()

            return rows
    
    async def insert_messages(
        self,
        session_id: str,
        messages_data: List[str],
        account_id: Optional[int] = None
    ) -> None:
        """
        Insert multiple messages for a session.
        
        Args:
            session_id: Session identifier
            messages_data: List of serialized message data
            account_id: Optional account identifier
        """
        current_time = datetime.now()
        
        payload = [
            {
                "session_id": session_id,
                "message_data": message_data,
                "account_id": account_id,
                "created_at": current_time,
                "updated_at": current_time,
            }
            for message_data in messages_data
        ]
        
        async with self._session_factory() as session:
            async with session.begin():
                await session.execute(insert(self._messages_table), payload)
    
    async def get_latest_message(self, session_id: str) -> Optional[str]:
        """
        Get the latest message data for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Latest message data string or None if no messages exist
        """
        async with self._session_factory() as session:
            # Get the most recent message ID
            subq = (
                select(self._messages_table.c.id)
                .where(self._messages_table.c.session_id == session_id)
                .order_by(self._messages_table.c.created_at.desc())
                .limit(1)
            )
            res = await session.execute(subq)
            row_id = res.scalar_one_or_none()
            
            if row_id is None:
                return None
            
            # Fetch the message data
            res_data = await session.execute(
                select(self._messages_table.c.message_data).where(
                    self._messages_table.c.id == row_id
                )
            )
            return res_data.scalar_one_or_none()
    
    async def delete_latest_message(self, session_id: str) -> Optional[str]:
        """
        Delete and return the latest message for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Deleted message data string or None if no messages exist
        """
        async with self._session_factory() as session:
            async with session.begin():
                # Get the most recent message ID
                subq = (
                    select(self._messages_table.c.id)
                    .where(self._messages_table.c.session_id == session_id)
                    .order_by(self._messages_table.c.created_at.desc())
                    .limit(1)
                )
                res = await session.execute(subq)
                row_id = res.scalar_one_or_none()
                
                if row_id is None:
                    return None
                
                # Fetch data before deleting
                res_data = await session.execute(
                    select(self._messages_table.c.message_data).where(
                        self._messages_table.c.id == row_id
                    )
                )
                message_data = res_data.scalar_one_or_none()
                
                # Delete the message
                await session.execute(
                    delete(self._messages_table).where(
                        self._messages_table.c.id == row_id
                    )
                )
                
                return message_data
    
    async def delete_all_messages(self, session_id: str) -> None:
        """
        Delete all messages for a session.
        
        Args:
            session_id: Session identifier
        """
        async with self._session_factory() as session:
            async with session.begin():
                await session.execute(
                    delete(self._messages_table).where(
                        self._messages_table.c.session_id == session_id
                    )
                )
    
    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session record.
        
        Args:
            session_id: Session identifier
        """
        async with self._session_factory() as session:
            async with session.begin():
                await session.execute(
                    delete(self._sessions_table).where(
                        self._sessions_table.c.session_id == session_id
                    )
                )
    
    async def ensure_session_exists(
        self,
        session_id: str,
        agent_run: Optional[AgentRun] = None
    ) -> None:
        """
        Ensure a session exists, creating it if it doesn't.
        
        Args:
            session_id: Session identifier
            agent_run: Optional AgentRun with team/agent info and metadata
        """
        if not await self.session_exists(session_id):
            await self.create_session(session_id, agent_run)