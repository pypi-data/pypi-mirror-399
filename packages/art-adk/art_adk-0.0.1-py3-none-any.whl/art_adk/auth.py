import logging
import aiohttp
import json
import base64
import time
import threading
from typing import Dict, Any
from .constant import Constant
from .exceptions import AuthenticationError
logger = logging.getLogger(__name__)

class Auth:
    """
    Instance-based Auth class.
    Each AsyncAdk instance creates its own Auth instance with isolated credentials.
    """

    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize Auth instance with credentials.

        Args:
            credentials: Dictionary containing authentication credentials
                        (ClientID, ClientSecret, OrgTitle, Environment, ProjectKey, etc.)
        """
        logger.debug("Initializing Auth instance")
        self.credentials = credentials
        self.auth_data = {
            "AccessToken": "",
            "RefreshToken": "",
        }
        self._lock = threading.Lock()  # Thread-safe access to auth_data

    async def authenticate(self, force_auth: bool = False) -> Dict[str, str]:
        """
        Authenticate and get access token with thread-safe caching.

        Args:
            force_auth: Force re-authentication even if cached token is valid

        Returns:
            Dictionary containing AccessToken and RefreshToken
        """
        # Quick check - return cached token if valid
        with self._lock:
            if not force_auth and self.auth_data.get("AccessToken"):
                if not self._is_token_expired(self.auth_data["AccessToken"]):
                    return self.auth_data.copy()

        get_credentials = self.credentials.get("config", {}).get("getCredentials")
        if callable(get_credentials):
            fresh_creds = get_credentials()
            if fresh_creds:
                if fresh_creds.get("AccessToken"):
                    self.credentials["AccessToken"] = fresh_creds["AccessToken"]
                if fresh_creds.get("ClientID"):
                    self.credentials["ClientID"] = fresh_creds["ClientID"]
                if fresh_creds.get("ClientSecret"):
                    self.credentials["ClientSecret"] = fresh_creds["ClientSecret"]
                if fresh_creds.get("OrgTitle"):
                    self.credentials["OrgTitle"] = fresh_creds["OrgTitle"]
                if fresh_creds.get("Environment"):
                    self.credentials["Environment"] = fresh_creds["Environment"]
                if fresh_creds.get("ProjectKey"):
                    self.credentials["ProjectKey"] = fresh_creds["ProjectKey"]
                if fresh_creds.get("AuthToken"):
                    if "config" not in self.credentials:
                        self.credentials["config"] = {}
                    self.credentials["config"]["AuthToken"] = fresh_creds["AuthToken"]
                logger.debug("Credentials refreshed via getCredentials callback")

        org_title = self.credentials.get("OrgTitle")
        environment = self.credentials.get("Environment")
        project_key = self.credentials.get("ProjectKey")

        if not org_title or not environment or not project_key:
            raise AuthenticationError("OrgTitle, Environment, and ProjectKey required")

        refresh_token_info = self._get_refresh_token_expiry_info(
            self.auth_data.get("RefreshToken", "")
        )
        if not refresh_token_info["expired"]:
            return await self._refresh_auth_token()

        return await self._generate_auth_token()

    async def _generate_auth_token(self) -> Dict[str, str]:
        """
        Generate new auth token from credentials.
        """
        access_token = self.credentials.get("AccessToken")
        client_id = self.credentials.get("ClientID")
        client_secret = self.credentials.get("ClientSecret")

        if not access_token:
            if not client_id or not client_secret:
                raise AuthenticationError(
                    "ClientID and ClientSecret required when AccessToken is not present"
                )

        header_payload = {
            'Client-Id': str(client_id) if client_id else '',
            'Client-Secret': str(client_secret) if client_secret else '',
            'X-Org': self.credentials.get("OrgTitle"),
            'Environment': self.credentials.get("Environment"),
            'ProjectKey': self.credentials.get("ProjectKey"),
        }

        if access_token:
            header_payload['T-pass'] = str(access_token)

        if self.credentials.get("config", {}).get("AuthToken"):
            header_payload['X-pass'] = str(self.credentials["config"]["AuthToken"])

        url = f"{Constant.BASE_URL}/auth/token"
        logger.debug("Generating auth token for org: %s", self.credentials.get('OrgTitle'))
        try:
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.post(url, headers=header_payload, timeout=timeout) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise AuthenticationError(f"Authentication failed: {response.status}, {text}")

                    resp_json = await response.json()
                    data = resp_json.get("data", {})
                    with self._lock:
                        self.auth_data = {
                            "AccessToken": data.get("access_token", ""),
                            "RefreshToken": data.get("refresh_token", ""),
                        }
                    logger.info("Authentication token generated successfully")
                    return self.get_auth_data()
        except Exception as e:
            logger.error("Token generation error: %s", e, exc_info=True)
            raise

    async def _refresh_auth_token(self) -> Dict[str, str]:
        """
        Refresh existing auth token using refresh token.
        """
        access_token = self.credentials.get("AccessToken")
        client_id = self.credentials.get("ClientID")

        if not access_token:
            if not client_id:
                raise AuthenticationError("ClientID required when AccessToken is not present")

        header_payload = {
            'Client-Id': str(client_id) if client_id else '',
            'X-Org': self.credentials.get("OrgTitle"),
            'Environment': self.credentials.get("Environment"),
            'ProjectKey': self.credentials.get("ProjectKey"),
        }

        refresh_token = self.auth_data.get("RefreshToken", "")
        if not refresh_token:
            logger.warning("No refresh token available, generating new token")
            return await self._generate_auth_token()

        url = f"{Constant.BASE_URL}/auth/token/refresh"
        logger.debug("Refreshing auth token for org: %s", self.credentials.get('OrgTitle'))

        try:
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=10)
                payload = {"refresh_token": refresh_token}
                async with session.post(
                    url,
                    headers=header_payload,
                    json=payload,
                    timeout=timeout
                ) as response:
                    if response.status != 200:
                        body = None
                        try:
                            body = await response.json()
                        except:
                            body = None

                        if response.status == 500 and body and body.get("error") == "Failed to get WebSocket backend":
                            raise AuthenticationError(body.get("error", "Internal server error"))

                        self._clear_auth_data()
                        error_msg = body.get("message") if body else f"HTTP {response.status}"
                        logger.warning("Token refresh failed: %s, will generate new token", error_msg)
                        raise AuthenticationError(f"Token refresh failed: {response.status}, {error_msg}")

                    resp_json = await response.json()
                    data = resp_json.get("data", {})
                    with self._lock:
                        self.auth_data = {
                            "AccessToken": data.get("access_token", ""),
                            "RefreshToken": data.get("refresh_token", ""),
                        }
                    logger.info("Authentication token refreshed successfully")
                    return self.get_auth_data()
        except Exception as e:
            logger.error("Token refresh error: %s, will try generating new token", e)
            self._clear_auth_data()
            raise

    def _clear_auth_data(self) -> None:
        """Clear authentication data"""
        with self._lock:
            self.auth_data = {
                "AccessToken": "",
                "RefreshToken": "",
            }

    def _decode_jwt_payload(self, token: str) -> Dict[str, Any]:
        """Decode JWT payload from token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")
            
            payload_b64 = parts[1]
            b64 = payload_b64.replace('-', '+').replace('_', '/')
            padding = (4 - len(b64) % 4) % 4
            b64 += '=' * padding
            
            json_str = base64.b64decode(b64).decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to decode JWT: {e}")

    def _is_token_expired(self, token: str) -> bool:
        """
        Check if JWT token is expired with 100-second safety buffer.

        The buffer prevents edge cases where token expires during request processing.
        """
        try:
            payload = self._decode_jwt_payload(token)
            exp = payload.get('exp')
            # Consider token expired 100 seconds before actual expiry
            return exp < (time.time() - 100) if isinstance(exp, (int, float)) else True
        except:
            return True

    def _get_refresh_token_expiry_info(self, token: str) -> Dict[str, Any]:
        """
        Get refresh token expiry information.

        Args:
            token: Refresh token string (format: part1.expiry_timestamp)

        Returns:
            Dictionary with expired (bool), exp (int), and remaining (int) seconds
        """
        if not token:
            return {"expired": True, "exp": None, "remaining": 0}

        parts = token.split(".")
        if len(parts) < 2:
            return {"expired": True, "exp": None, "remaining": 0}

        exp_str = parts[1]
        try:
            exp = int(exp_str)
        except (ValueError, TypeError):
            return {"expired": True, "exp": None, "remaining": 0}

        now = int(time.time())
        return {
            "expired": now >= exp,
            "exp": exp,
            "remaining": exp - now,
        }

    def get_auth_data(self) -> Dict[str, str]:
        """
        Get current authentication data (thread-safe).
        """
        with self._lock:
            return self.auth_data.copy()

    def get_credentials(self) -> Dict[str, Any]:
        """Get credentials (returns copy)"""
        return self.credentials.copy()

    async def update_profile(self, connection_id: str, data: Dict[str, Any]) -> None:
        """Update user profile on server"""
        try:
            auth_data = self.get_auth_data()
            
            url = f"{Constant.BASE_URL}/v1/update-profile"
            headers = {
                'Content-Type': 'application/json',
                "Authorization": f"Bearer {auth_data['AccessToken']}",
                "X-Org": self.credentials.get("OrgTitle", ""),
                "Environment": self.credentials.get("Environment", ""),
                "ProjectKey": self.credentials.get("ProjectKey", ""),
            }
            
            payload = {
                "first_name": data.get("FirstName"),
                "last_name": data.get("LastName"),
                "username": data.get("Username"),
                "attributes": data.get("Attributes")
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if not response.ok:
                        raise AuthenticationError("Failed to update profile")
                    logger.info("Profile updated successfully")
                    
        except Exception as e:
            logger.error("Profile update error: %s", e, exc_info=True)
            raise

    def cleanup(self) -> None:
        """Cleanup resources"""
        self._clear_auth_data()