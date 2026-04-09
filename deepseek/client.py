from typing import Optional
from .models import ChatResponse, ModelType
from ._http import create_session, create_pow_challenge, send_message
from .pow import solve_pow


class DeepSeekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def chat(
        self,
        prompt: str,
        model: ModelType = "default",
        thinking: bool = False,
        search: bool = False,
        session_id: Optional[str] = None,
        parent_message_id: Optional[int] = None,
    ) -> ChatResponse:
        if not session_id:
            session_data = create_session(self.api_key)
            session_id = session_data["session_id"]

        pow_data = create_pow_challenge(self.api_key)
        challenge = pow_data["challenge"]
        session_cookie = pow_data.get("session_cookie", "")

        solved = solve_pow(
            challenge=challenge["challenge"],
            salt=challenge["salt"],
            difficulty=challenge["difficulty"],
            signature=challenge["signature"],
            target_path=challenge["target_path"],
            expire_at=challenge["expire_at"],
        )

        result = send_message(
            authorization=self.api_key,
            chat_session_id=session_id,
            prompt=prompt,
            pow_response=solved["pow_response"],
            session_cookie=session_cookie,
            model_type=model,
            thinking_enabled=thinking,
            search_enabled=search,
            parent_message_id=parent_message_id,
        )

        raw_answer = result["response"]
        thinking_content = result.get("thinking_content")

        if thinking and thinking_content:
            combined_response = f"{thinking_content}\n\n{raw_answer}"
        else:
            combined_response = raw_answer

        return ChatResponse(
            session_id=session_id,
            message_id=result["message_id"],
            response=combined_response,
            model_type=model,
            thinking_enabled=thinking,
            search_enabled=search,
            status=result["status"],
            thinking_content=thinking_content,
            answer=raw_answer,
        )
