from fastapi import APIRouter, Depends
from typing import List

from auth.dependencies import get_current_user
from chat.history_store import ChatHistoryStore

router = APIRouter(prefix="/chat", tags=["Chat History"])

history_store = ChatHistoryStore()


@router.get("/history")
def get_chat_history(
    current_user: dict = Depends(get_current_user),
):
    """
    Fetch chat history for the authenticated user.
    """
    user_id = current_user["user_id"]

    messages = history_store.get_user_history(user_id)

    return {
        "user_id": user_id,
        "messages": messages,
    }


@router.delete("/history")
def clear_chat_history(
    current_user: dict = Depends(get_current_user),
):
    """
    Clear chat history for the authenticated user.
    """
    user_id = current_user["user_id"]

    history_store.clear_user_history(user_id)

    return {
        "status": "success",
        "message": "Chat history cleared",
    }
