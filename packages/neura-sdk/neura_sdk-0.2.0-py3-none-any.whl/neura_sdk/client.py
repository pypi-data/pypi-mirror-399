import os
import requests
from typing import Optional, Dict, Any

class NeuraClient:
    def __init__(self, api_key: Optional[str] = None, endpoint: str = "https://control.neura-os.com"):
        self.api_key = api_key or os.environ.get("NEURA_API_KEY")
        if not self.api_key:
             # Warning or allow for registration only?
             # For strictness we keep it required for general usage, but registration might fail.
             # Let's keep it required for now as per previous logic, user can pass dummy key for bootstrap if needed?
             # Or better, just don't raise error here, check in methods.
             pass
        self.endpoint = endpoint.rstrip('/')
        self.auth = self.AuthClient(self)

    class AuthClient:
        def __init__(self, client):
            self.client = client

        def register(self, org_id: str, name: str, permissions: list = None) -> Dict[str, Any]:
            """
            Register a new SDK client.
            """
            url = f"{self.client.endpoint}/v1/auth/register"
            payload = {
                "org_id": org_id,
                "name": name,
                "permissions": permissions
            }
            # Use a separate request for auth as it might need different headers/auth
            # For now, assuming open registration or bootstrap token handled by caller in headers if needed
            # but usually register is public or uses a specific token.
            # Using the main client's post but we might need to bypass api_key check if it's not set?
            # The constructor requires api_key. If registration is the first step, we might need to allow
            # initialization without api_key.
            
            # TODO: Allow NeuraClient init without API Key for registration flow.
            return self.client._post(url, payload)

    class MemoryClient:
        def __init__(self, client):
            self.client = client

        def store(self, content: str, type: str = "semantic", metadata: Dict[str, Any] = None, identity_id: str = None) -> Dict[str, Any]:
            """
            Store a memory in the Neura Memory System.
            """
            url = f"{self.client.endpoint}/v1/memory"
            payload = {
                "content": content,
                "type": type,
                "metadata": metadata,
                "identity_id": identity_id
            }
            return self.client._post(url, payload)

        def search(self, query: str, limit: int = 5, identity_id: str = None) -> list:
            """
            Search memories using semantic search.
            """
            url = f"{self.client.endpoint}/v1/memory/search"
            payload = {
                "query": query,
                "limit": limit,
                "identity_id": identity_id
            }
            return self.client._post(url, payload)

    def decide(self, intent: str, actor: Dict[str, Any], resource: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Request a decision from the Neura Control Plane.
        """
        url = f"{self.endpoint}/v1/decide"
        payload = {
            "intent": intent,
            "actor": actor,
            "resource": resource,
            "context": context or {}
        }
        return self._post(url, payload)

    def validate(self, intent: str, actor: Dict[str, Any], resource: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate an intent without executing it (Dry Run).
        """
        url = f"{self.endpoint}/v1/validate"
        payload = {
            "intent": intent,
            "actor": actor,
            "resource": resource,
            "context": context or {}
        }
        return self._post(url, payload)

    def get_decision(self, decision_id: str) -> Dict[str, Any]:
        """
        Get a past decision by ID.
        """
        url = f"{self.endpoint}/v1/decision/{decision_id}"
        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers)
            self._handle_error(response)
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response:
                 self._handle_error(e.response)
            raise Exception(f"Failed to get decision: {str(e)}") from e

    def wait_for_decision(self, decision_id: str, timeout: int = 30, interval: int = 1) -> Dict[str, Any]:
        """
        Wait for a decision to transition from OBSERVE/ESCALATE to ACT/DENY.
        """
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            decision = self.get_decision(decision_id)
            outcome = decision.get("outcome")
            if outcome in ["ACT", "DENY"]:
                return decision
            time.sleep(interval)
        
        raise TimeoutError(f"Timeout waiting for decision {decision_id} to finalize.")

    def _post(self, url: str, payload: Dict[str, Any]) -> Any:
        headers = self._get_headers()
        try:
            response = requests.post(url, json=payload, headers=headers)
            self._handle_error(response)
            return response.json()
        except requests.exceptions.RequestException as e:
             if hasattr(e, 'response') and e.response is not None:
                 self._handle_error(e.response)
             raise Exception(f"Failed to request Neura: {str(e)}") from e

    def _handle_error(self, response):
        if not response.ok:
            try:
                data = response.json()
                error_msg = data.get("error", response.reason)
                code = data.get("code", "unknown_error")
                raise Exception(f"Neura API Error ({response.status_code}): {code} - {error_msg}")
            except ValueError:
                response.raise_for_status()

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "neura-sdk-python/0.2.0"
        }

