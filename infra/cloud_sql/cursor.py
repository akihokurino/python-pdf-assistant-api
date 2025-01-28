import base64
from datetime import datetime
from typing import Optional, Callable, Sequence

from adapter.adapter import Pager


def encode_cursor(sk: datetime, pk: str) -> str:
    timestamp = sk.isoformat()
    cursor_data = f"{timestamp} {pk}"
    return base64.urlsafe_b64encode(cursor_data.encode()).decode()


def decode_cursor(cursor: Optional[str]) -> Optional[tuple[datetime, str]]:
    if not cursor:
        return None

    decoded_bytes = base64.urlsafe_b64decode(cursor.encode())
    decoded_str = decoded_bytes.decode()
    timestamp, pk = decoded_str.split(" ", 1)
    sk = datetime.fromisoformat(timestamp)
    return sk, pk


def paging_result[
    T, U
](
    pager: Pager,
    entities: Sequence[T],
    conv: Callable[[T], U],
    cursor: Callable[[T], str],
) -> tuple[list[U], str]:
    items = entities[: pager.limit]
    has_next = len(entities) > pager.limit
    next_cursor = ""
    if has_next:
        last_item = entities[pager.limit - 1]
        next_cursor = cursor(last_item)

    return [conv(e) for e in items], next_cursor
