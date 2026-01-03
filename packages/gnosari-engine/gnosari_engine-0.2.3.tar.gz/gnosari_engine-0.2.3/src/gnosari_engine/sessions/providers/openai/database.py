"""OpenAI database session provider implementation."""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from agents.memory.session import SessionABC
from agents.items import TResponseInputItem

from ...interfaces import ISessionProvider
from ....schemas.domain.execution import AgentRun
from ...repositories.session_repository import SessionRepository
from ...events import ISessionEventPublisher, NullSessionEventPublisher

# SQLAlchemy imports for database implementation
from sqlalchemy import (
    DateTime, Column, ForeignKey, Index, Integer, MetaData, String, Table, Text,
    delete, insert, select, text as sql_text, update
)
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)


class OpenAIDatabaseSession(SessionABC):
    """
    SessionABC implementation using database storage.
    
    This is the concrete session that gets passed to OpenAI agents.
    Follows existing DatabaseSession logic but with better separation.
    
    Follows Single Responsibility Principle: Only responsible for
    implementing SessionABC interface with database persistence.
    """
    
    def __init__(
        self, 
        session_id: str,
        database_url: str,
        agent_run: Optional[AgentRun] = None,
        event_publisher: Optional[ISessionEventPublisher] = None,
        **db_config
    ):
        """
        Initialize OpenAI database session.
        
        Args:
            session_id: Unique session identifier
            database_url: Database connection URL
            agent_run: AgentRun context with agent/team info and metadata
            event_publisher: Optional event publisher for session events
            **db_config: Additional database configuration
        """
        self.session_id = session_id
        self._database_url = database_url
        self._agent_run = agent_run
        self._db_config = db_config
        self._event_publisher = event_publisher or NullSessionEventPublisher()
        self._lock = asyncio.Lock()
        
        # Initialize database components
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._metadata: Optional[MetaData] = None
        self._sessions: Optional[Table] = None
        self._messages: Optional[Table] = None
        self._repository: Optional[SessionRepository] = None
        self._database_available = True
        self._create_tables = True
        
        self._setup_database()
    
    def _setup_database(self) -> None:
        """Set up database engine and schema."""
        try:
            # Initialize database engine with robust connection handling
            self._engine = create_async_engine(
                self._database_url,
                pool_size=20,
                max_overflow=30,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,
                connect_args=self._get_connect_args()
            )
            
            self._setup_database_schema()
            
            # Async session factory
            self._session_factory = async_sessionmaker(
                self._engine, 
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
            
            # Initialize repository
            if self._sessions is not None and self._messages is not None:
                self._repository = SessionRepository(
                    self._session_factory,
                    self._sessions,
                    self._messages
                )
            
            logger.info(f"Database engine initialized successfully: {self._database_url}")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            self._database_available = False
            self._engine = None
    
    def _get_connect_args(self) -> Dict[str, Any]:
        """
        Get database-specific connection arguments.

        Note: statement_timeout is disabled by default because many managed
        PostgreSQL services don't support it. Set GNOSARI_DB_ENABLE_STATEMENT_TIMEOUT=true
        to enable it for self-hosted PostgreSQL.
        """
        connect_args = {}

        if "sqlite" in self._database_url:
            connect_args["timeout"] = 30
        elif "mysql" in self._database_url:
            connect_args["command_timeout"] = 30
        elif "postgresql" in self._database_url:
            # statement_timeout is disabled by default because managed PostgreSQL
            # services (Neon, Supabase, CockroachDB, etc.) don't support it
            enable_statement_timeout = os.getenv(
                "GNOSARI_DB_ENABLE_STATEMENT_TIMEOUT", "false"
            ).lower() in ("true", "1", "yes")

            if enable_statement_timeout:
                connect_args["server_settings"] = {"statement_timeout": "30s"}

        return connect_args
    
    def _setup_database_schema(self) -> None:
        """Set up database schema using existing structure."""
        self._metadata = MetaData()
        
        # Sessions table - compatible with existing schema
        self._sessions = Table(
            "sessions",
            self._metadata,
            Column("session_id", String, primary_key=True),
            Column("account_id", Integer, nullable=True),
            Column("team_id", Integer, nullable=True),
            Column("agent_id", Integer, nullable=True),
            Column("team_identifier", String, nullable=True),
            Column("agent_identifier", String, nullable=True),
            Column("created_at", DateTime, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")),
            Column("updated_at", DateTime, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP"), onupdate=sql_text("CURRENT_TIMESTAMP")),
        )

        # Messages table
        self._messages = Table(
            "session_messages",
            self._metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("session_id", String, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False),
            Column("message_data", Text, nullable=False),
            Column("account_id", Integer, nullable=True),
            Column("created_at", DateTime, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")),
            Column("updated_at", DateTime, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP"), onupdate=sql_text("CURRENT_TIMESTAMP")),
            Index("idx_session_messages_session_time", "session_id", "created_at"),
            sqlite_autoincrement=True,
        )
    
    async def _ensure_tables(self) -> None:
        """Ensure tables are created before any database operations."""
        if not self._database_available or self._engine is None:
            raise RuntimeError("Database is not available")
            
        if self._create_tables and self._metadata is not None:
            try:
                async with self._engine.begin() as conn:
                    await conn.run_sync(self._metadata.create_all)
                self._create_tables = False  # Only create once
                logger.info(f"Database tables created successfully for session {self.session_id}")
            except Exception as e:
                logger.error(f"Failed to create database tables: {e}")
                self._database_available = False
                raise
    
    async def _serialize_item(self, item: TResponseInputItem) -> str:
        """Serialize an item to JSON string."""
        try:
            if hasattr(item, 'model_dump'):
                return json.dumps(item.model_dump(), separators=(",", ":"))
            elif hasattr(item, 'dict'):
                return json.dumps(item.dict(), separators=(",", ":"))
            else:
                return json.dumps(item, separators=(",", ":"))
        except (TypeError, AttributeError) as e:
            logger.warning(f"Failed to serialize item properly: {e}, using string representation")
            return json.dumps(str(item), separators=(",", ":"))
    
    async def get_items(self, limit: int | None = None) -> List[TResponseInputItem]:
        """Retrieve conversation history for this session."""
        logger.debug(f"Getting items for session {self.session_id} (limit: {limit})")
        
        if not self._database_available or self._repository is None:
            logger.warning(f"Database unavailable for session {self.session_id}, returning empty conversation history")
            return []
        
        try:
            await asyncio.wait_for(self._ensure_tables(), timeout=10.0)
            
            async with asyncio.timeout(30.0):
                rows = await self._repository.get_messages(self.session_id, limit)
                
                items: List[TResponseInputItem] = []
                for raw in rows:
                    try:
                        items.append(json.loads(raw))
                    except json.JSONDecodeError:
                        continue
                
                logger.debug(f"Retrieved {len(items)} items for session {self.session_id}")
                return items
                    
        except asyncio.TimeoutError:
            logger.error(f"Database operation timed out while retrieving items for session {self.session_id}")
            self._database_available = False
            return []
        except Exception as e:
            logger.error(f"Database error while retrieving items for session {self.session_id}: {e}")
            self._database_available = False
            return []

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        """Store new items for this session."""
        logger.debug(f"Adding {len(items)} items to session {self.session_id}")
        
        if not self._database_available or self._repository is None:
            logger.warning(f"Database unavailable for session {self.session_id}, conversation will not be persisted")
            return
        
        if not items:
            logger.debug(f"No items to add for session {self.session_id}")
            return

        try:
            await asyncio.wait_for(self._ensure_tables(), timeout=10.0)
            
            # Get account_id from AgentRun metadata
            account_id = self._agent_run.metadata.account_id if self._agent_run and self._agent_run.metadata else None
            
            logger.debug(f"AgentRun context for {self.session_id}: account_id={account_id}")
            
            # Serialize items
            messages_data = []
            for item in items:
                serialized = await self._serialize_item(item)
                messages_data.append(serialized)

            async with asyncio.timeout(30.0):
                # Ensure the session exists with AgentRun context
                await self._repository.ensure_session_exists(self.session_id, self._agent_run)
                
                # Insert messages in bulk
                await self._repository.insert_messages(self.session_id, messages_data, account_id)
                
                # Update session timestamp
                await self._repository.update_session_timestamp(self.session_id)
                
                # Publish messages added event
                try:
                    await self._event_publisher.publish_messages_added(
                        session_id=self.session_id,
                        message_count=len(items),
                        messages_data=messages_data,
                        metadata=self._agent_run.metadata if self._agent_run else None
                    )
                except Exception as e:
                    logger.warning(f"Failed to publish messages added event for session {self.session_id}: {e}")
                
                logger.debug(f"Successfully added {len(items)} items to session {self.session_id}")
                        
        except asyncio.TimeoutError:
            logger.error(f"Database operation timed out while adding items for session {self.session_id}")
            self._database_available = False
            raise
        except Exception as e:
            logger.error(f"Database error while adding items for session {self.session_id}: {e}")
            self._database_available = False
            raise

    async def pop_item(self) -> TResponseInputItem | None:
        """Remove and return the most recent item from this session."""
        if not self._database_available or self._repository is None:
            logger.warning("Database unavailable, cannot pop item")
            return None
        
        try:
            await asyncio.wait_for(self._ensure_tables(), timeout=10.0)
            
            async with asyncio.timeout(30.0):
                message_data = await self._repository.delete_latest_message(self.session_id)
                
                if message_data is None:
                    return None
                
                try:
                    return json.loads(message_data)
                except json.JSONDecodeError:
                    return None
                            
        except asyncio.TimeoutError:
            logger.error(f"Database operation timed out while popping item for session {self.session_id}")
            self._database_available = False
            return None
        except Exception as e:
            logger.error(f"Database error while popping item for session {self.session_id}: {e}")
            self._database_available = False
            return None

    async def clear_session(self) -> None:
        """Clear all items for this session."""
        if not self._database_available or self._repository is None:
            logger.warning("Database unavailable, cannot clear session")
            return
        
        try:
            await asyncio.wait_for(self._ensure_tables(), timeout=10.0)
            
            async with asyncio.timeout(30.0):
                await self._repository.delete_all_messages(self.session_id)
                await self._repository.delete_session(self.session_id)
                
                # Publish session cleared event
                try:
                    await self._event_publisher.publish_session_cleared(
                        session_id=self.session_id,
                        metadata=self._agent_run.metadata if self._agent_run else None
                    )
                except Exception as e:
                    logger.warning(f"Failed to publish session cleared event for session {self.session_id}: {e}")
                        
        except asyncio.TimeoutError:
            logger.error(f"Database operation timed out while clearing session {self.session_id}")
            self._database_available = False
            raise
        except Exception as e:
            logger.error(f"Database error while clearing session {self.session_id}: {e}")
            self._database_available = False
            raise
    
    async def cleanup(self) -> None:
        """Clean up database connections and resources."""
        # Clean up event publisher
        try:
            await self._event_publisher.cleanup()
        except Exception as e:
            logger.warning(f"Error cleaning up event publisher: {e}")
        
        # Clean up database engine
        if self._engine is not None:
            try:
                await self._engine.dispose()
                logger.debug(f"Disposed database engine for session {self.session_id}")
            except Exception as e:
                logger.warning(f"Error disposing database engine: {e}")


class OpenAIDatabaseSessionProvider(ISessionProvider):
    """
    Provider strategy that creates OpenAI database sessions.
    
    This is what GnosariSession uses internally to manage the lifecycle
    of OpenAIDatabaseSession instances.
    
    Follows Single Responsibility Principle: Only responsible for creating
    and managing OpenAI database session instances.
    """
    
    def __init__(
        self, 
        session_id: str, 
        agent_run: Optional[AgentRun] = None,
        event_publisher: Optional[ISessionEventPublisher] = None
    ):
        """
        Initialize OpenAI database session provider.
        
        Args:
            session_id: Unique session identifier
            agent_run: Optional AgentRun with team/agent context and metadata
            event_publisher: Optional event publisher for session events
        """
        self._session_id = session_id
        self._agent_run = agent_run
        self._event_publisher = event_publisher
        self._database_url: Optional[str] = None
        self._session_instance: Optional[OpenAIDatabaseSession] = None
        self._is_initialized = False
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai_database"
    
    @property
    def session_type(self) -> str:
        """Get the session type this provider creates."""
        return "SessionABC"
    
    @property
    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        return self._is_initialized
    
    async def initialize(self, database_url: Optional[str] = None, **config) -> None:
        """
        Initialize the database session provider.
        
        Args:
            database_url: Optional database URL (uses environment or default if not provided)
            **config: Additional database configuration
        """
        self._database_url = (
            database_url or 
            os.getenv("GNOSARI_DATABASE_URL") or 
            "sqlite+aiosqlite:///sessions.db"
        )
        
        self._session_instance = OpenAIDatabaseSession(
            session_id=self._session_id,
            database_url=self._database_url,
            agent_run=self._agent_run,
            event_publisher=self._event_publisher,
            **config
        )
        
        self._is_initialized = True
    
    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        if self._session_instance is not None:
            await self._session_instance.cleanup()
        
        self._session_instance = None
        self._is_initialized = False
    
    def get_session_implementation(self) -> SessionABC:
        """Return the SessionABC implementation for OpenAI agents."""
        if not self._is_initialized or not self._session_instance:
            raise RuntimeError("Provider not initialized")
        
        return self._session_instance


__all__ = ["OpenAIDatabaseSession", "OpenAIDatabaseSessionProvider"]