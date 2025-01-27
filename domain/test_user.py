from datetime import datetime, timedelta, timezone

from domain.user import User, UserId


def test_user_initialization() -> None:
    now = datetime.now(timezone.utc)
    user = User(id=UserId("123"), name="Alice", created_at=now, updated_at=now)

    assert user.id == "123"
    assert user.name == "Alice"
    assert user.created_at == now
    assert user.updated_at == now


def test_user_new() -> None:
    now = datetime.now(timezone.utc)
    user = User.new(_id=UserId("456"), name="Bob", now=now)

    assert user.id == "456"
    assert user.name == "Bob"
    assert user.created_at == now
    assert user.updated_at == now


def test_user_update() -> None:
    now = datetime.now(timezone.utc)
    user = User.new(_id=UserId("789"), name="Charlie", now=now)

    assert user.name == "Charlie"
    assert user.updated_at == now

    updated_time = now + timedelta(days=1)
    user.update(name="Charlie_updated", now=updated_time)

    assert user.name == "Charlie_updated"
    assert user.created_at == now
    assert user.updated_at == updated_time
