from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from enum import Enum

class NotificationType(str, Enum):
    PROPOSAL_ACCEPTED = "proposal_accepted"
    PROPOSAL_REJECTED = "proposal_rejected"

@dataclass
class Notification:
    user_id: int
    message: str
    type: NotificationType
    created_at: datetime = field(default_factory=lambda: datetime.now())
    notification_id: str = field(default_factory=lambda: str(uuid4()))
    read: bool = False



    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)

    def is_valid(self):
        """Business rule: No empty messages"""
        return bool(self.message)
    
    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'message': self.message,
            'type': self.type.value,
            'created_at': self.created_at.isoformat(),
            'read': self.read,
        }
    
    def mark_as_read(self):
        self.read = True
        return self

    @classmethod
    def from_dict(cls, data: dict):
        try:
            notification_type = data.get('type', data.get('notification_type'))
            if not notification_type:
                raise ValueError("Missing required field: 'type'")
            return cls(
                notification_id=data.get('notification_id', str(uuid4())),
                user_id=data['user_id'],
                message=data['message'],
                type=NotificationType(notification_type),
                created_at=data.get('created_at', datetime.now()),
                read=data.get('read', False)
            )
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid field value: {e}")
