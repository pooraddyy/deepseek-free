from dataclasses import dataclass
from typing import Optional
from typing import Literal

ModelType = Literal["default", "expert"]


@dataclass
class ChatResponse:
    session_id: str
    message_id: int
    response: str
    model_type: str
    thinking_enabled: bool
    search_enabled: bool
    status: str
    thinking_content: Optional[str] = None
