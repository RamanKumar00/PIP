import os
import httpx
import streamlit as st
from dotenv import load_dotenv

# Load env file
load_dotenv(dotenv_path="frontend/.env")

# Restore session from query parameters (Remember me functionality)
def load_session():
    if "access_token" not in st.session_state or not st.session_state.access_token:
        if "access_token" in st.query_params:
            st.session_state.access_token = st.query_params["access_token"]
    if "refresh_token" not in st.session_state or not st.session_state.refresh_token:
        if "refresh_token" in st.query_params:
            st.session_state.refresh_token = st.query_params["refresh_token"]
    if "user_email" not in st.session_state or not st.session_state.user_email:
        if "user_email" in st.query_params:
            st.session_state.user_email = st.query_params["user_email"]

load_session()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")


class APIClient:
    def __init__(self):
        # Force base_url to end with a trailing slash to preserve /api/v1 prefix during merges
        self.base_url = BACKEND_URL if BACKEND_URL.endswith("/") else f"{BACKEND_URL}/"
        self.timeout_default = httpx.Timeout(5.0, connect=3.0)
        self.timeout_upload = httpx.Timeout(120.0, connect=5.0)
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout_default,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )

    def _get_headers(self) -> dict:
        """Helper to assemble HTTP headers including Bearer token if authed.
        """
        headers = {"Content-Type": "application/json"}
        if "access_token" in st.session_state and st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        return headers

    def _refresh_tokens(self) -> bool:
        """Call token refresh endpoint to get a new access token.

        Returns:
            bool: True if refresh succeeded and saved, False otherwise.
        """
        if "refresh_token" not in st.session_state or not st.session_state.refresh_token:
            return False

        try:
            # We bypass the standard _get_headers and call directly to avoid recursion
            # Strip leading slash to preserve /api/v1 path prefix in base_url
            response = self.client.post(
                "auth/refresh",
                params={"refresh_token": st.session_state.refresh_token},
                timeout=self.timeout_default,
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.access_token = data["access_token"]
                st.session_state.refresh_token = data["refresh_token"]
                
                # Sync query parameters if they are being used (Remember me)
                if "access_token" in st.query_params:
                    st.query_params["access_token"] = data["access_token"]
                if "refresh_token" in st.query_params:
                    st.query_params["refresh_token"] = data["refresh_token"]
                return True
        except Exception:
            pass
        
        # Clear credentials on failure
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        for k in ["access_token", "refresh_token", "user_email"]:
            if k in st.query_params:
                del st.query_params[k]
        return False

    def request(
        self, method: str, path: str, data: dict = None, json: dict = None, params: dict = None, files: dict = None
    ) -> httpx.Response:
        """Execute HTTP request with automatic token injection and refresh retry logic.
        """
        headers = self._get_headers()
        
        # Content-Type must not be application/json when uploading files
        if files:
            headers.pop("Content-Type", None)
            timeout = self.timeout_upload
        else:
            timeout = self.timeout_default

        json_body = json if json is not None else data
        
        # Strip leading slash to preserve /api/v1 path prefix in base_url
        clean_path = path.lstrip("/")

        try:
            response = self.client.request(
                method, clean_path, headers=headers, params=params, json=json_body, files=files, timeout=timeout
            )
        except Exception as e:
            # Reraise as a custom exception or response
            raise RuntimeException(f"Network error connecting to Backend: {e}")

        # Check for 401 Unauthorized (token expired)
        if response.status_code == 401 and "access_token" in st.session_state:
            # Attempt to refresh token
            if self._refresh_tokens():
                # Re-fetch headers and retry request once
                headers = self._get_headers()
                if files:
                    headers.pop("Content-Type", None)
                    return self.client.request(
                        method, clean_path, headers=headers, params=params, files=files, timeout=self.timeout_upload
                    )
                else:
                    return self.client.request(
                        method, clean_path, headers=headers, params=params, json=json_body, timeout=self.timeout_default
                    )
            else:
                # Trigger a streamlit rerun to kick user back to login
                st.session_state.access_token = None
                st.session_state.refresh_token = None
                for k in ["access_token", "refresh_token", "user_email"]:
                    if k in st.query_params:
                        del st.query_params[k]
                st.rerun()

        return response

    def get(self, path: str, params: dict = None) -> httpx.Response:
        return self.request("GET", path, params=params)

    def post(self, path: str, data: dict = None, json: dict = None, params: dict = None, files: dict = None) -> httpx.Response:
        return self.request("POST", path, data=data, json=json, params=params, files=files)

    def put(self, path: str, data: dict = None, json: dict = None, params: dict = None) -> httpx.Response:
        return self.request("PUT", path, data=data, json=json, params=params)

    def delete(self, path: str, params: dict = None) -> httpx.Response:
        return self.request("DELETE", path, params=params)


class RuntimeException(Exception):
    pass


# Global API instance
api_client = APIClient()
