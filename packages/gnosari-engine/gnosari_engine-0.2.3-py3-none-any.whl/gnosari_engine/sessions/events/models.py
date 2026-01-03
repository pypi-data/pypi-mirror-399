"""
Session event data models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from ...schemas.domain.execution import AgentRunMetadata


class SessionEventBase(BaseModel):
    """Base model for all session events."""
    
    event_type: str = Field(..., description="Type of the event")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    account_id: Optional[int] = Field(None, description="Account identifier")
    team_id: Optional[int] = Field(None, description="Team identifier")
    agent_id: Optional[int] = Field(None, description="Agent identifier")
    team_identifier: Optional[str] = Field(None, description="Team string identifier")
    agent_identifier: Optional[str] = Field(None, description="Agent string identifier")
    
    @classmethod
    def from_metadata(
        cls, 
        event_type: str, 
        session_id: str, 
        metadata: Optional[AgentRunMetadata] = None,
        **kwargs
    ) -> "SessionEventBase":
        """Create event from agent run metadata."""
        data = {
            "event_type": event_type,
            "session_id": session_id,
            **kwargs
        }
        
        if metadata:
            data.update({
                "account_id": metadata.account_id,
                "team_id": metadata.team_id,
                "agent_id": metadata.agent_id,
                "team_identifier": metadata.team_identifier,
                "agent_identifier": metadata.agent_identifier,
            })
        
        return cls(**data)


class MessagesAddedEvent(SessionEventBase):
    """Event fired when messages are added to a session."""
    
    event_type: str = Field(default="session.messages_added", description="Event type")
    message_count: int = Field(..., ge=1, description="Number of messages added")
    messages_data: List[str] = Field(..., description="Serialized message data")
    
    @classmethod
    def create(
        cls, 
        session_id: str, 
        message_count: int,
        messages_data: List[str],
        metadata: Optional[AgentRunMetadata] = None
    ) -> "MessagesAddedEvent":
        """Create messages added event."""
        return cls(
            session_id=session_id,
            message_count=message_count,
            messages_data=messages_data,
            account_id=metadata.account_id if metadata else None,
            team_id=metadata.team_id if metadata else None,
            agent_id=metadata.agent_id if metadata else None,
            team_identifier=metadata.team_identifier if metadata else None,
            agent_identifier=metadata.agent_identifier if metadata else None,
        )


class SessionCreatedEvent(SessionEventBase):
    """Event fired when a new session is created."""
    
    event_type: str = Field(default="session.created", description="Event type")
    
    @classmethod
    def create(
        cls, 
        session_id: str,
        metadata: Optional[AgentRunMetadata] = None
    ) -> "SessionCreatedEvent":
        """Create session created event."""
        return cls(
            session_id=session_id,
            account_id=metadata.account_id if metadata else None,
            team_id=metadata.team_id if metadata else None,
            agent_id=metadata.agent_id if metadata else None,
            team_identifier=metadata.team_identifier if metadata else None,
            agent_identifier=metadata.agent_identifier if metadata else None,
        )


class SessionClearedEvent(SessionEventBase):
    """Event fired when a session is cleared."""
    
    event_type: str = Field(default="session.cleared", description="Event type")
    
    @classmethod
    def create(
        cls, 
        session_id: str,
        metadata: Optional[AgentRunMetadata] = None
    ) -> "SessionClearedEvent":
        """Create session cleared event."""
        return cls(
            session_id=session_id,
            account_id=metadata.account_id if metadata else None,
            team_id=metadata.team_id if metadata else None,
            agent_id=metadata.agent_id if metadata else None,
            team_identifier=metadata.team_identifier if metadata else None,
            agent_identifier=metadata.agent_identifier if metadata else None,
        )