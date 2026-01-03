from typing import Dict, Any, List
from .auth import get_auth_manager
class AgentAPIClient:
    def __init__(self):
        a = get_auth_manager()
        self.token = a.get_stored_token()
        self.base_url = a.api_base_url
    def reset_cancel_flag(self):
        pass