import os
import uuid
import datetime
import json

# Optionally import from a config or define expected key names

def get_chat_path(chats_dir, chat_id):
    return os.path.join(chats_dir, f"{chat_id}.json")

def load_chat(chats_dir, chat_id):
    """Load a chat from disk."""
    chat_path = get_chat_path(chats_dir, chat_id)
    if os.path.exists(chat_path):
        with open(chat_path, 'r') as f:
            return json.load(f)
    return None

def save_chat(chats_dir, chat):
    """Save a chat to disk."""
    chat_path = get_chat_path(chats_dir, chat['id'])
    with open(chat_path, 'w') as f:
        json.dump(chat, f, indent=2)

def create_new_chat(model):
    """Create a new chat."""
    now = datetime.datetime.now().isoformat()
    return {
        "id": str(uuid.uuid4()),
        "title": "New Chat",
        "model": model,
        "created_at": now,
        "updated_at": now,
        "favorite": False,
        "messages": []
    }

def get_all_chats(chats_dir):
    """Get all chats."""
    chats = []
    if not os.path.exists(chats_dir):
        return []
    for filename in os.listdir(chats_dir):
        if filename.endswith(".json"):
            with open(os.path.join(chats_dir, filename), 'r') as f:
                chat = json.load(f)
                chats.append(chat)
    return sorted(chats, key=lambda x: x.get("updated_at", ""), reverse=True)