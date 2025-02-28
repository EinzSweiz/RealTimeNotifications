import pytest
from datetime import datetime
from uuid import uuid4
from app.domain.entities.notifications import Notification, NotificationType

@pytest.mark.parametrize("user_id, message, notification_type, expected_valid", [
    (1, "Your proposal was accepted!", NotificationType.PROPOSAL_ACCEPTED, True),
    (2, "", NotificationType.PROPOSAL_REJECTED, False),
])
def test_notification_is_valid(user_id, message, notification_type, expected_valid):
    """Test that notifications validate correctly based on business rules."""
    notification = Notification(user_id=user_id, message=message, type=notification_type)
    assert notification.is_valid() == expected_valid

def test_notification_to_dict():
    """Test conversion of Notification to dictionary."""
    notification = Notification(user_id=1, message="Your proposal was accepted!", type=NotificationType.PROPOSAL_ACCEPTED)
    notification_dict = notification.to_dict()

    assert isinstance(notification_dict, dict)
    assert notification_dict["user_id"] == 1
    assert notification_dict["message"] == "Your proposal was accepted!"
    assert notification_dict["type"] == NotificationType.PROPOSAL_ACCEPTED.value
    assert isinstance(notification_dict["created_at"], str)  # Should be ISO string
    assert isinstance(notification_dict["notification_id"], str)

def test_notification_mark_as_read():
    """Test marking a notification as read."""
    notification = Notification(user_id=1, message="Your proposal was accepted!", type=NotificationType.PROPOSAL_ACCEPTED)
    assert not notification.read  # Initially False

    notification.mark_as_read()
    assert notification.read  # Now it should be True

def test_notification_from_dict():
    """Test creating a Notification from a dictionary."""
    notification_data = {
        "user_id": 1,
        "message": "Your proposal was rejected.",
        "type": "proposal_rejected",
        "created_at": datetime.now().isoformat(),
        "read": False
    }
    notification = Notification.from_dict(notification_data)

    assert notification.user_id == notification_data["user_id"]
    assert notification.message == notification_data["message"]
    assert notification.type == NotificationType.PROPOSAL_REJECTED
    assert isinstance(notification.created_at, datetime)
    assert not notification.read

def test_notification_from_dict_missing_field():
    """Test creating a Notification from a dictionary with missing fields."""
    notification_data = {
        "user_id": 1,
        "message": "Your proposal was rejected."
    }
    with pytest.raises(ValueError, match="Missing required field: 'type'"):
        Notification.from_dict(notification_data)

def test_notification_from_dict_invalid_type():
    """Test creating a Notification with an invalid type."""
    notification_data = {
        "user_id": 1,
        "message": "Your proposal was rejected.",
        "type": "invalid_type",
        "created_at": datetime.now().isoformat(),
        "read": False
    }
    with pytest.raises(ValueError, match="Invalid field value"):
        Notification.from_dict(notification_data)
