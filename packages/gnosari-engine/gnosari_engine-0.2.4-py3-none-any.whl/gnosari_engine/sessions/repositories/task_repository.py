"""
Task repository for database operations.

Provides reusable data access layer for task management operations.
Follows Repository Pattern for clean separation of data access logic.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy import (
    Column, ForeignKey, Integer, String, Text, DateTime, JSON,
    select, insert, update, delete, and_
)
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# Create declarative base for ORM models
Base = declarative_base()


class TaskModel(Base):
    """SQLAlchemy model for task table."""
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    input_message = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    tags = Column(JSON, nullable=False)
    account_id = Column(Integer, nullable=False)
    assigned_team_id = Column(Integer, nullable=False)
    assigned_agent_id = Column(Integer, nullable=True)
    assigned_team_identifier = Column(String(255), nullable=True)
    assigned_agent_identifier = Column(String(255), nullable=True)
    reporter_team_id = Column(Integer, nullable=True)
    reporter_agent_id = Column(Integer, nullable=True)
    reporter_team_identifier = Column(String(255), nullable=True)
    reporter_agent_identifier = Column(String(255), nullable=True)
    parent_id = Column(Integer, ForeignKey('task.id'), nullable=True)
    result = Column(Text, nullable=True)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentModel(Base):
    """SQLAlchemy model for agent table."""
    __tablename__ = 'agent'

    id = Column(Integer, primary_key=True, autoincrement=True)
    identifier = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    account_id = Column(Integer, nullable=False)


class TeamModel(Base):
    """SQLAlchemy model for teams table."""
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    identifier = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    account_id = Column(Integer, nullable=False)


class TaskDependencyModel(Base):
    """SQLAlchemy model for task_dependency table."""
    __tablename__ = 'task_dependency'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    dependency_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TaskRepository:
    """
    Repository for task database operations.

    Provides reusable data access layer following Repository Pattern.
    All database operations are encapsulated here for maximum reusability.

    Follows Single Responsibility Principle: Only responsible for task data access.
    """

    def __init__(self, session_factory: async_sessionmaker):
        """
        Initialize task repository.

        Args:
            session_factory: SQLAlchemy async session factory
        """
        self._session_factory = session_factory

    async def resolve_team_id(self, team_identifier: str, account_id: int) -> Optional[int]:
        """
        Resolve team identifier to team_id.

        Args:
            team_identifier: Team identifier string
            account_id: Account ID for multi-tenancy

        Returns:
            Team ID if found, None otherwise
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(TeamModel.id).where(
                    and_(
                        TeamModel.identifier == team_identifier,
                        TeamModel.account_id == account_id
                    )
                )
            )
            row = result.first()
            return row[0] if row else None

    async def resolve_agent_id(self, agent_identifier: str, account_id: int) -> Optional[int]:
        """
        Resolve agent identifier to agent_id.

        Args:
            agent_identifier: Agent identifier string
            account_id: Account ID for multi-tenancy

        Returns:
            Agent ID if found, None otherwise
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(AgentModel.id).where(
                    and_(
                        AgentModel.identifier == agent_identifier,
                        AgentModel.account_id == account_id
                    )
                )
            )
            row = result.first()
            return row[0] if row else None

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a single task.

        Args:
            task_data: Dictionary with task fields

        Returns:
            Created task as dictionary
        """
        async with self._session_factory() as session:
            async with session.begin():
                # Insert and get ID
                result = await session.execute(
                    insert(TaskModel).values(**task_data).returning(TaskModel.id)
                )
                task_row = result.fetchone()
                task_id = task_row[0]

                # Fetch complete task
                task_fetch = await session.execute(
                    select(TaskModel).where(TaskModel.id == task_id)
                )
                task = task_fetch.fetchone()
                return self._task_to_dict(task)

    async def create_task_tree(
        self,
        task_data: Dict[str, Any],
        subtasks: Optional[List[Dict[str, Any]]] = None,
        account_id: int = None
    ) -> Dict[str, Any]:
        """
        Create a task with optional subtasks in a single transaction.

        Follows atomicity: all tasks are created or none are.

        Args:
            task_data: Parent task data
            subtasks: Optional list of subtask data
            account_id: Account ID for multi-tenancy

        Returns:
            Created parent task with subtasks as dictionary
        """
        async with self._session_factory() as session:
            async with session.begin():
                # Create parent task
                parent_result = await session.execute(
                    insert(TaskModel).values(**task_data).returning(TaskModel.id)
                )
                parent_row = parent_result.fetchone()
                parent_id = parent_row[0]  # Get the ID integer

                created_subtasks = []
                if subtasks:
                    for subtask_data in subtasks:
                        # Set parent_id and inherit account_id
                        subtask_data['parent_id'] = parent_id
                        if 'account_id' not in subtask_data:
                            subtask_data['account_id'] = account_id

                        # Set defaults if not provided
                        if 'type' not in subtask_data:
                            subtask_data['type'] = 'task'
                        if 'status' not in subtask_data:
                            subtask_data['status'] = 'pending'
                        if 'tags' not in subtask_data:
                            subtask_data['tags'] = []

                        # Inherit session_id from parent task if not explicitly set
                        if 'session_id' not in subtask_data and 'session_id' in task_data:
                            subtask_data['session_id'] = task_data['session_id']

                        # Inherit reporter information from parent task if not explicitly set
                        if 'reporter_team_id' not in subtask_data and 'reporter_team_id' in task_data:
                            subtask_data['reporter_team_id'] = task_data['reporter_team_id']
                        if 'reporter_team_identifier' not in subtask_data and 'reporter_team_identifier' in task_data:
                            subtask_data['reporter_team_identifier'] = task_data['reporter_team_identifier']
                        if 'reporter_agent_id' not in subtask_data and 'reporter_agent_id' in task_data:
                            subtask_data['reporter_agent_id'] = task_data['reporter_agent_id']
                        if 'reporter_agent_identifier' not in subtask_data and 'reporter_agent_identifier' in task_data:
                            subtask_data['reporter_agent_identifier'] = task_data['reporter_agent_identifier']

                        # Resolve team/agent identifiers for subtask if needed
                        if 'assigned_team_identifier' in subtask_data and not subtask_data.get('assigned_team_id'):
                            team_id = await self._resolve_team_id_in_session(
                                session,
                                subtask_data['assigned_team_identifier'],
                                subtask_data['account_id']
                            )
                            if team_id:
                                subtask_data['assigned_team_id'] = team_id

                        if 'assigned_agent_identifier' in subtask_data and not subtask_data.get('assigned_agent_id'):
                            agent_id = await self._resolve_agent_id_in_session(
                                session,
                                subtask_data['assigned_agent_identifier'],
                                subtask_data['account_id']
                            )
                            if agent_id:
                                subtask_data['assigned_agent_id'] = agent_id

                        # Create subtask - return only ID, then fetch complete record
                        subtask_result = await session.execute(
                            insert(TaskModel).values(**subtask_data).returning(TaskModel.id)
                        )
                        subtask_row = subtask_result.fetchone()
                        subtask_id = subtask_row[0]

                        # Fetch complete subtask
                        subtask_fetch = await session.execute(
                            select(TaskModel).where(TaskModel.id == subtask_id)
                        )
                        subtask = subtask_fetch.fetchone()
                        created_subtasks.append(self._task_to_dict(subtask))

                # Fetch the complete parent task with all fields
                parent_fetch_result = await session.execute(
                    select(TaskModel).where(TaskModel.id == parent_id)
                )
                parent_task = parent_fetch_result.fetchone()

                # Return parent with subtasks
                parent_dict = self._task_to_dict(parent_task)
                parent_dict['subtasks'] = created_subtasks
                return parent_dict

    async def get_task(self, task_id: int, account_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a task by ID.

        Args:
            task_id: Task ID
            account_id: Account ID for multi-tenancy

        Returns:
            Task as dictionary if found, None otherwise
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(TaskModel).where(
                    and_(
                        TaskModel.id == task_id,
                        TaskModel.account_id == account_id
                    )
                )
            )
            task = result.fetchone()
            return self._task_to_dict(task) if task else None

    async def get_task_with_subtasks(self, task_id: int, account_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a task with its subtasks.

        Args:
            task_id: Task ID
            account_id: Account ID for multi-tenancy

        Returns:
            Task with subtasks as dictionary if found, None otherwise
        """
        async with self._session_factory() as session:
            # Get parent task
            result = await session.execute(
                select(TaskModel).where(
                    and_(
                        TaskModel.id == task_id,
                        TaskModel.account_id == account_id
                    )
                )
            )
            task = result.fetchone()
            if not task:
                return None

            # Get subtasks
            subtasks_result = await session.execute(
                select(TaskModel).where(
                    and_(
                        TaskModel.parent_id == task_id,
                        TaskModel.account_id == account_id
                    )
                )
            )
            subtasks = subtasks_result.fetchall()

            task_dict = self._task_to_dict(task)
            task_dict['subtasks'] = [self._task_to_dict(st) for st in subtasks]
            return task_dict

    async def list_tasks(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        assigned_team_id: Optional[int] = None,
        assigned_agent_id: Optional[int] = None,
        parent_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List tasks with optional filtering.

        Args:
            account_id: Account ID for multi-tenancy
            skip: Number of records to skip
            limit: Maximum records to return
            status: Filter by status
            task_type: Filter by task type
            assigned_team_id: Filter by assigned team
            assigned_agent_id: Filter by assigned agent
            parent_id: Filter by parent task

        Returns:
            List of tasks as dictionaries
        """
        async with self._session_factory() as session:
            query = select(TaskModel).where(TaskModel.account_id == account_id)

            if status:
                query = query.where(TaskModel.status == status)
            if task_type:
                query = query.where(TaskModel.type == task_type)
            if assigned_team_id:
                query = query.where(TaskModel.assigned_team_id == assigned_team_id)
            if assigned_agent_id:
                query = query.where(TaskModel.assigned_agent_id == assigned_agent_id)
            if parent_id is not None:
                query = query.where(TaskModel.parent_id == parent_id)

            query = query.offset(skip).limit(limit).order_by(TaskModel.created_at.desc())

            result = await session.execute(query)
            tasks = result.fetchall()
            return [self._task_to_dict(task) for task in tasks]

    async def update_task(
        self,
        task_id: int,
        account_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a task.

        Args:
            task_id: Task ID
            account_id: Account ID for multi-tenancy
            update_data: Fields to update

        Returns:
            Updated task as dictionary if found, None otherwise
        """
        async with self._session_factory() as session:
            async with session.begin():
                # Add updated_at
                update_data['updated_at'] = datetime.utcnow()

                result = await session.execute(
                    update(TaskModel)
                    .where(
                        and_(
                            TaskModel.id == task_id,
                            TaskModel.account_id == account_id
                        )
                    )
                    .values(**update_data)
                    .returning(TaskModel.id)
                )
                row = result.fetchone()
                if not row:
                    return None

                # Fetch complete task
                task_fetch = await session.execute(
                    select(TaskModel).where(TaskModel.id == task_id)
                )
                task = task_fetch.fetchone()
                return self._task_to_dict(task) if task else None

    async def delete_task(self, task_id: int, account_id: int) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID
            account_id: Account ID for multi-tenancy

        Returns:
            True if task was deleted, False if not found
        """
        async with self._session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    delete(TaskModel).where(
                        and_(
                            TaskModel.id == task_id,
                            TaskModel.account_id == account_id
                        )
                    )
                )
                return result.rowcount > 0

    async def add_dependency(self, task_id: int, dependency_id: int, account_id: int) -> bool:
        """
        Add a dependency between tasks.

        Args:
            task_id: Task ID
            dependency_id: Dependency task ID
            account_id: Account ID for multi-tenancy

        Returns:
            True if dependency was added, False if tasks not found
        """
        async with self._session_factory() as session:
            async with session.begin():
                # Verify both tasks belong to the same account
                result = await session.execute(
                    select(TaskModel.id).where(
                        and_(
                            TaskModel.id.in_([task_id, dependency_id]),
                            TaskModel.account_id == account_id
                        )
                    )
                )
                if len(result.fetchall()) != 2:
                    return False

                # Create dependency
                await session.execute(
                    insert(TaskDependencyModel).values(
                        task_id=task_id,
                        dependency_id=dependency_id
                    )
                )
                return True

    async def remove_dependency(self, task_id: int, dependency_id: int, account_id: int) -> bool:
        """
        Remove a dependency between tasks.

        Args:
            task_id: Task ID
            dependency_id: Dependency task ID
            account_id: Account ID for multi-tenancy

        Returns:
            True if dependency was removed, False if not found
        """
        async with self._session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    delete(TaskDependencyModel).where(
                        and_(
                            TaskDependencyModel.task_id == task_id,
                            TaskDependencyModel.dependency_id == dependency_id
                        )
                    )
                )
                return result.rowcount > 0

    async def get_task_dependencies(self, task_id: int, account_id: int) -> List[Dict[str, Any]]:
        """
        Get all dependencies for a task.

        Args:
            task_id: Task ID
            account_id: Account ID for multi-tenancy

        Returns:
            List of dependency tasks as dictionaries
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(TaskModel)
                .join(TaskDependencyModel, TaskDependencyModel.dependency_id == TaskModel.id)
                .where(
                    and_(
                        TaskDependencyModel.task_id == task_id,
                        TaskModel.account_id == account_id
                    )
                )
            )
            tasks = result.fetchall()
            return [self._task_to_dict(task) for task in tasks]

    async def _resolve_team_id_in_session(self, session, team_identifier: str, account_id: int) -> Optional[int]:
        """
        Resolve team identifier within existing session.

        Args:
            session: Active SQLAlchemy session
            team_identifier: Team identifier string
            account_id: Account ID for multi-tenancy

        Returns:
            Team ID if found, None otherwise
        """
        result = await session.execute(
            select(TeamModel.id).where(
                and_(
                    TeamModel.identifier == team_identifier,
                    TeamModel.account_id == account_id
                )
            )
        )
        row = result.first()
        return row[0] if row else None

    async def _resolve_agent_id_in_session(self, session, agent_identifier: str, account_id: int) -> Optional[int]:
        """
        Resolve agent identifier within existing session.

        Args:
            session: Active SQLAlchemy session
            agent_identifier: Agent identifier string
            account_id: Account ID for multi-tenancy

        Returns:
            Agent ID if found, None otherwise
        """
        result = await session.execute(
            select(AgentModel.id).where(
                and_(
                    AgentModel.identifier == agent_identifier,
                    AgentModel.account_id == account_id
                )
            )
        )
        row = result.first()
        return row[0] if row else None

    def _task_to_dict(self, task) -> Dict[str, Any]:
        """
        Convert SQLAlchemy row to dictionary.

        Args:
            task: SQLAlchemy row (from SELECT query)

        Returns:
            Task as dictionary
        """
        if task is None:
            return None

        # When selecting TaskModel, fetchone() returns a Row where the first element is the ORM object
        # We need to extract the ORM model object from the Row
        if hasattr(task, '__getitem__') and not isinstance(task, dict):
            # This is a Row object, get the first element (the ORM model)
            try:
                task_model = task[0] if isinstance(task[0], TaskModel) else task
            except (IndexError, TypeError):
                task_model = task
        else:
            task_model = task

        # Now extract data from the ORM model object
        return {
            'id': task_model.id,
            'title': task_model.title,
            'description': task_model.description,
            'input_message': task_model.input_message,
            'type': task_model.type,
            'status': task_model.status,
            'tags': task_model.tags,
            'account_id': task_model.account_id,
            'assigned_team_id': task_model.assigned_team_id,
            'assigned_agent_id': task_model.assigned_agent_id,
            'assigned_team_identifier': task_model.assigned_team_identifier,
            'assigned_agent_identifier': task_model.assigned_agent_identifier,
            'reporter_team_id': task_model.reporter_team_id,
            'reporter_agent_id': task_model.reporter_agent_id,
            'reporter_team_identifier': task_model.reporter_team_identifier,
            'reporter_agent_identifier': task_model.reporter_agent_identifier,
            'parent_id': task_model.parent_id,
            'result': task_model.result,
            'session_id': task_model.session_id,
            'created_at': task_model.created_at.isoformat() if task_model.created_at else None,
            'updated_at': task_model.updated_at.isoformat() if task_model.updated_at else None
        }


__all__ = ["TaskRepository", "TaskModel", "AgentModel", "TeamModel", "TaskDependencyModel"]
