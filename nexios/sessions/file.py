import os,uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from nexios.config.settings import BaseConfig
from .base import BaseSessionInterface
from nexios.utils import timezone

class FileSessionManager(BaseSessionInterface):
    def __init__(self, session_key: str, config: BaseConfig = BaseConfig):
        session_key = session_key or uuid.uuid4()
        super().__init__(session_key, config)
        self.session_file_path = os.path.join(self.config.SESSION_FILE_STORAGE_PATH or "sessions", f"{session_key}.json")
        
        # Ensure the session storage directory exists
        os.makedirs(self.config.SESSION_FILE_STORAGE_PATH or "sessions_dir", exist_ok=True)

    def _load_session_data(self) -> Optional[Dict[str, Any]]:
        """Load session data from the file."""
        if os.path.exists(self.session_file_path):
            with open(self.session_file_path, 'r') as file:
                try:
                    session_data = json.load(file)
                    return session_data
                except json.JSONDecodeError:
                    return None
        return None

    def _save_session_data(self):
        """Save the session data to a file."""
        with open(self.session_file_path, 'w') as file:
            json.dump(self._session_cache, file)

    def set_session(self, key: str, value: str):
        """Set a session value."""
        self.modified = True
        self._session_cache[key] = value
        self._save_session_data()

    def get_session(self, key: str) -> Optional[str]:
        """Get a session value."""
        return self._session_cache.get(key, None)

    def get_all(self) -> dict:
        """Get all session data."""
        return self._session_cache.items()

    def keys(self):
        """Get all session keys."""
        return self._session_cache.keys()

    def values(self):
        """Get all session values."""
        return self._session_cache.items()

    def is_empty(self) -> bool:
        """Check if the session is empty."""
        return len(self._session_cache.items()) == 0

    async def save(self):
        """Save the session data to the file."""
        self._save_session_data()

    

    @property
    def should_set_cookie(self) -> bool:
        """Determines if the cookie should be set."""
        return self.modified or (
            self.config.SESSION_PERMANENT and self.config.SESSION_REFRESH_EACH_REQUEST
        )

    def has_expired(self) -> bool:
        """Returns True if the session has expired."""
        expiration_time = self.get_expiration_time()
        if expiration_time and timezone.now() > expiration_time:
            return True
        return False

    async def load(self):
        """Load the session data from the file."""
        session_data = self._load_session_data()

        if session_data:
            self._session_cache.update(session_data)
        else:
            self._session_cache = {}

    def clear(self):
        """Clear the session data."""
        self._session_cache.clear()
        if os.path.exists(self.session_file_path):
            os.remove(self.session_file_path)

    def get_session_key(self) -> str:
        """Returns the session key."""
        return self.session_key
