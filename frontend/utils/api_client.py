import os
import httpx
import streamlit as st
from dotenv import load_dotenv

# Load env file
load_dotenv(dotenv_path="frontend/.env")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")


class APIClient:
    def __init__(self):
        self.base_url = BACKEND_URL

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
            response = httpx.post(
                f"{self.base_url}/auth/refresh",
                params={"refresh_token": st.session_state.refresh_token},
                timeout=10.0,
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.access_token = data["access_token"]
                st.session_state.refresh_token = data["refresh_token"]
                return True
        except Exception:
            pass
        
        # Clear credentials on failure
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        return False

    def request(
        self, method: str, path: str, data: dict = None, params: dict = None, files: dict = None
    ) -> httpx.Response:
        """Execute HTTP request with automatic token injection and refresh retry logic.
        """
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        
        # Content-Type must not be application/json when uploading files
        if files:
            headers.pop("Content-Type", None)

        try:
            if files:
                response = httpx.request(
                    method, url, headers=headers, params=params, files=files, timeout=30.0
                )
            else:
                json_data = data if data is not None else None
                response = httpx.request(
                    method, url, headers=headers, params=params, json=json_data, timeout=10.0
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
                    return httpx.request(
                        method, url, headers=headers, params=params, files=files, timeout=30.0
                    )
                else:
                    return httpx.request(
                        method, url, headers=headers, params=params, json=data, timeout=10.0
                    )
            else:
                # Trigger a streamlit rerun to kick user back to login
                st.session_state.access_token = None
                st.session_state.refresh_token = None
                st.rerun()

        return response

    def get(self, path: str, params: dict = None) -> httpx.Response:
        return self.request("GET", path, params=params)

    def post(self, path: str, data: dict = None, params: dict = None, files: dict = None) -> httpx.Response:
        return self.request("POST", path, data=data, params=params, files=files)

    def put(self, path: str, data: dict = None, params: dict = None) -> httpx.Response:
        return self.request("PUT", path, data=data, params=params)

    def delete(self, path: str, params: dict = None) -> httpx.Response:
        return self.request("DELETE", path, params=params)


class RuntimeException(Exception):
    pass


# Global API instance
api_client = APIClient()
