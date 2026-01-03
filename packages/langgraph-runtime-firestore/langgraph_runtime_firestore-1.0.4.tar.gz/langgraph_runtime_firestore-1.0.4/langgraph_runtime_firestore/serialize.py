from datetime import datetime
from typing import Any
from uuid import UUID


def normalize_message_content(content: Any) -> Any:
    """Normalize AI message content that was incorrectly accumulated.
    
    When streaming AIMessageChunks, if the first chunk has content as a list
    (e.g., [{"type": "text", "text": "..."}]) and subsequent chunks have content
    as strings, the accumulation incorrectly appends strings to the list instead
    of merging them into the text block.
    
    This function fixes:
    [{"type": "text", "text": "first"}, "second", "third"]
    Into:
    [{"type": "text", "text": "firstsecondthird"}]
    """
    if not isinstance(content, list):
        return content
    
    # Check if we have the malformed pattern: content block followed by strings
    if len(content) < 2:
        return content
    
    # Check if there are any string items in the list (which indicates malformed content)
    has_string_items = any(isinstance(item, str) for item in content)
    if not has_string_items:
        return content
    
    # Log that we found malformed content
    content_types = [type(item).__name__ for item in content]
    print(f"NORMALIZE_CONTENT: Found malformed content with types: {content_types}")
    
    # Find all text blocks and collect all string fragments
    text_blocks = []
    string_fragments = []
    other_items = []
    
    for item in content:
        if isinstance(item, str):
            string_fragments.append(item)
        elif isinstance(item, dict) and item.get("type") == "text":
            text_blocks.append(dict(item))  # Make a copy
        else:
            other_items.append(item)
    
    # If we have text blocks and string fragments, merge them
    if text_blocks and string_fragments:
        # Append all string fragments to the last text block's text
        combined_strings = "".join(string_fragments)
        text_blocks[-1]["text"] = text_blocks[-1].get("text", "") + combined_strings
        print(f"NORMALIZE_CONTENT: Merged {len(string_fragments)} string fragments into text block")
    
    # Return text blocks first, then other items
    return text_blocks + other_items


def normalize_ai_message(message: dict) -> dict:
    """Normalize an AI message dictionary, fixing malformed content from chunk accumulation."""
    if not isinstance(message, dict):
        return message
    
    # Only process AI messages
    if message.get("type") not in ("ai", "AIMessage", "AIMessageChunk"):
        return message
    
    # Make a copy to avoid modifying the original
    result = dict(message)
    modified = False
    
    # Normalize content if it has malformed chunk accumulation
    content = result.get("content")
    if content is not None:
        normalized_content = normalize_message_content(content)
        if normalized_content != content:
            result["content"] = normalized_content
            modified = True
    
    # Fix response_metadata.finish_reason if it's concatenated
    response_metadata = result.get("response_metadata")
    if isinstance(response_metadata, dict):
        finish_reason = response_metadata.get("finish_reason")
        if isinstance(finish_reason, str) and len(finish_reason) > 10 and "STOP" in finish_reason:
            # Extract just the final finish reason (usually "STOP")
            new_response_metadata = dict(response_metadata)
            if finish_reason.endswith("STOP"):
                new_response_metadata["finish_reason"] = "STOP"
            elif "STOP" in finish_reason:
                # Find the last occurrence of a valid finish reason
                new_response_metadata["finish_reason"] = "STOP"
            result["response_metadata"] = new_response_metadata
            modified = True
    
    return result if modified else message


def normalize_messages_in_values(values: Any) -> Any:
    """Normalize all AI messages in a values dict (state snapshot)."""
    # Accept both dicts and message objects (with model_dump)
    if hasattr(values, "model_dump") and callable(values.model_dump):
        # Convert message object to dict
        values = values.model_dump()
    if not isinstance(values, dict):
        return values

    result = dict(values)

    # Check for 'messages' key which is common in MessagesState
    if "messages" in result and isinstance(result["messages"], list):
        normalized_messages = []
        for msg in result["messages"]:
            # Handle message objects (LangChain BaseMessage)
            if hasattr(msg, "model_dump") and callable(msg.model_dump):
                msg_dict = msg.model_dump()
                normalized_messages.append(normalize_ai_message(msg_dict))
            elif isinstance(msg, dict):
                normalized_messages.append(normalize_ai_message(msg))
            else:
                normalized_messages.append(msg)
        result["messages"] = normalized_messages

    return result


def serialize_for_firestore(obj: Any) -> Any:
    """Convert UUID and datetime objects to Firestore-compatible types (strings).
    
    Also filters out reserved field names (starting with __ or __) to comply with Firestore
    field naming restrictions.
    
    Additionally normalizes AI messages to fix malformed content from chunk accumulation.
    """
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, "model_dump") and callable(obj.model_dump):
        # Handle LangChain BaseMessage and Pydantic models
        serialized = serialize_for_firestore(obj.model_dump())
        # Apply normalization for AI messages after serialization
        if isinstance(serialized, dict) and serialized.get("type") in ("ai", "AIMessage", "AIMessageChunk"):
            serialized = normalize_ai_message(serialized)
        return serialized
    elif isinstance(obj, dict):
        result = {
            k: serialize_for_firestore(v)
            for k, v in obj.items()
            if not k.startswith("__")  # Filter out reserved field names
        }
        # Apply normalization for AI messages in dicts
        if result.get("type") in ("ai", "AIMessage", "AIMessageChunk"):
            result = normalize_ai_message(result)
        return result
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_firestore(item) for item in obj]
    return obj


def deserialize_from_firestore(obj: Any) -> Any:
    """Convert strings back to datetime objects, and reconstruct Pydantic models.
    
    NOTE: We do NOT convert UUID-formatted strings back to UUID objects because:
    1. LangChain message objects require 'id' fields to be strings
    2. Most UUID values are better kept as strings for consistency
    3. If UUIDs are needed elsewhere, they can be converted explicitly using UUID(string)
    """
    if isinstance(obj, str):
        # Try to parse as datetime (but not UUID strings)
        try:
            return datetime.fromisoformat(obj)
        except (ValueError, TypeError):
            pass
    elif isinstance(obj, dict):
        # Recursively deserialize dict values
        deserialized = {k: deserialize_from_firestore(v) for k, v in obj.items()}

        # Try to reconstruct LangChain message objects from dict
        # Check if this looks like a message (has type field with specific values)
        if "type" in deserialized:
            try:
                from langchain_core.messages import (
                    AIMessage,
                    FunctionMessage,
                    HumanMessage,
                    SystemMessage,
                    ToolMessage,
                )

                msg_type = deserialized.get("type")
                if msg_type == "human":
                    return HumanMessage(**deserialized)
                elif msg_type == "ai":
                    return AIMessage(**deserialized)
                elif msg_type == "system":
                    return SystemMessage(**deserialized)
                elif msg_type == "tool":
                    return ToolMessage(**deserialized)
                elif msg_type == "function":
                    return FunctionMessage(**deserialized)
            except (ImportError, TypeError, ValueError):
                # If message reconstruction fails, return dict as-is
                pass

        return deserialized
    elif isinstance(obj, list):
        return [deserialize_from_firestore(item) for item in obj]
    return obj
