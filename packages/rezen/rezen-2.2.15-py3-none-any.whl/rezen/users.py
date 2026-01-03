"""Users client for ReZEN API."""

from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class UsersClient(BaseClient):
    """Client for users API endpoints.

    This client provides access to user-related functionality including
    getting current user info with team details. Note: This uses the yenta
    service with a different base URL.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        *,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_backoff_seconds: Optional[float] = None,
    ) -> None:
        """Initialize the users client.

        Args:
            api_key: API key for authentication. If None, will look for REZEN_API_KEY env var
            base_url: Base URL for the users API. Defaults to yenta production URL
            timeout_seconds: Default request timeout (seconds).
            max_retries: Maximum number of retries for transient failures.
            retry_backoff_seconds: Base backoff (seconds) between retries.
        """
        # Use the yenta base URL for users API
        users_base_url = base_url or "https://yenta.therealbrokerage.com/api/v1"
        super().__init__(
            api_key=api_key,
            base_url=users_base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )

    def get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user information from Yenta.

        This returns more detailed user information than the keymaker endpoint,
        including team and office details.

        Returns:
            Dictionary containing current user's agent information including:
            - Basic user info (id, name, email, etc.)
            - Team information (teamId, teamName, etc.)
            - Office information (officeId, officeName, etc.)
            - License details
            - And more agent-specific fields

        Raises:
            AuthenticationError: If not authenticated
            RezenError: If the API request fails

        Example:
            ```python
            # Get current user with full agent details
            user = client.users.get_current_user()
            print(f"User ID: {user.get('id')}")
            print(f"Name: {user.get('firstName')} {user.get('lastName')}")
            print(f"Team ID: {user.get('teamId')}")
            print(f"Office ID: {user.get('officeId')}")
            ```
        """
        return self.get("users/me")

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get user information by ID.

        Args:
            user_id: UUID of the user to retrieve

        Returns:
            Dictionary containing user's agent information

        Raises:
            NotFoundError: If user not found
            RezenError: If the API request fails

        Example:
            ```python
            # Get user by ID
            user = client.users.get_user_by_id("550e8400-e29b-41d4-a716-446655440000")
            print(f"Name: {user.get('firstName')} {user.get('lastName')}")
            ```
        """
        return self.get(f"users/{user_id}")

    def get_generic_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get generic user information by ID.

        This endpoint returns user information in a generic format,
        suitable for non-agent users.

        Args:
            user_id: UUID of the user to retrieve

        Returns:
            Dictionary containing generic user information

        Raises:
            NotFoundError: If user not found
            RezenError: If the API request fails

        Example:
            ```python
            # Get generic user by ID
            user = client.users.get_generic_user_by_id("550e8400-e29b-41d4-a716-446655440000")
            print(f"Username: {user.get('username')}")
            ```
        """
        return self.get(f"users/generic/{user_id}")

    def get_current_generic_user(self) -> Dict[str, Any]:
        """Get current authenticated user in generic format.

        This returns user information in a generic format,
        suitable for non-agent users.

        Returns:
            Dictionary containing current user's generic information

        Raises:
            AuthenticationError: If not authenticated
            RezenError: If the API request fails

        Example:
            ```python
            # Get current user in generic format
            user = client.users.get_current_generic_user()
            print(f"Username: {user.get('username')}")
            print(f"Email: {user.get('email')}")
            ```
        """
        return self.get("users/generic/me")

    def get_keymaker_ids(self, yenta_ids: Union[str, List[str]]) -> List[str]:
        """Get keymaker IDs for the given Yenta IDs.

        Note: For owner agent setup in transactions, you typically don't need this method.
        The user ID from get_current_user() can be used directly as the agent ID.

        Args:
            yenta_ids: A single Yenta user ID (UUID) or a list of Yenta user IDs.

        Returns:
            List of Keymaker user IDs corresponding to the provided Yenta IDs.

        Raises:
            ValidationError: If yenta_ids is empty or invalid
            RezenError: If the API request fails
            ValueError: If the API response payload is not recognized.

        Example:
            ```python
            # Get keymaker IDs for Yenta users
            yenta_ids = ["id1", "id2", "id3"]
            keymaker_ids = client.users.get_keymaker_ids(yenta_ids)
            ```
        """
        yenta_ids_list = [yenta_ids] if isinstance(yenta_ids, str) else yenta_ids
        params = {"yentaIds": yenta_ids_list}
        response: Any = self.get("users/keymaker-ids", params=params)
        if isinstance(response, list):
            return [str(item) for item in response]

        # Defensive fallback if the API ever wraps the array.
        if isinstance(response, dict):
            for key in ("ids", "keymakerIds", "keymaker_ids"):
                value = response.get(key)
                if isinstance(value, list):
                    return [str(item) for item in value]

        raise ValueError("Expected keymaker IDs list payload from get_keymaker_ids().")

    def get_agent_id_for_current_user(self) -> str:
        """Get the agent ID for the current user.

        ✅ WORKING METHOD - Key Discovery: User ID = Agent ID in ReZEN.

        This is a convenience method that returns the user ID, which serves as the agent ID
        in the ReZEN system. This discovery eliminates the need to call the keymaker endpoint
        for owner agent setup in transactions.

        🎯 KEY INSIGHT:
        In ReZEN's system architecture, the user ID from get_current_user() can be used
        directly as the agent ID in owner agent configurations. This simplifies the
        transaction setup process significantly.

        Returns:
            String containing the agent ID (same as user ID)

        Raises:
            AuthenticationError: If not authenticated
            RezenError: If the API request fails

        Example:
            ```python
            # Get agent ID for current user (for owner agent setup)
            agent_id = client.users.get_agent_id_for_current_user()
            print(f"Agent ID: {agent_id}")

            # Use directly in owner agent setup - NO KEYMAKER LOOKUP NEEDED
            user = client.users.get_current_user()
            owner_info = {
                "ownerAgent": {
                    "agentId": user["id"],  # Same as get_agent_id_for_current_user()
                    "role": "BUYERS_AGENT"
                },
                "officeId": user["offices"][0]["id"],  # From user profile
                "teamId": "your-team-uuid"              # From team selection
            }

            # This approach works and eliminates API complexity
            client.transaction_builder.update_owner_agent_info(transaction_id, owner_info)
            ```

        Alternative Usage:
            ```python
            # Direct approach without this method
            user = client.users.get_current_user()
            agent_id = user["id"]  # User ID IS the agent ID
            ```
        """
        user = self.get_current_user()
        return str(user["id"])

    def get_principal_user(self) -> Dict[str, Any]:
        """Get principal user information.

        Returns the principal user associated with the current authentication context.

        Returns:
            Dictionary containing principal user information

        Raises:
            AuthenticationError: If not authenticated
            RezenError: If the API request fails

        Example:
            ```python
            # Get principal user
            principal = client.users.get_principal_user()
            print(f"Principal ID: {principal.get('id')}")
            ```
        """
        return self.get("users/myprincipal")

    def get_user_count(self, terminated_only: bool = False) -> Dict[str, Any]:
        """Get total count of users.

        Args:
            terminated_only: If True, only count terminated users

        Returns:
            Dictionary containing user count or the count as integer

        Raises:
            RezenError: If the API request fails

        Example:
            ```python
            # Get total user count
            total_users = client.users.get_user_count()
            count = total_users if isinstance(total_users, int) else total_users.get("count", 0)
            print(f"Total users: {count}")

            # Get terminated user count
            terminated = client.users.get_user_count(terminated_only=True)
            count = terminated if isinstance(terminated, int) else terminated.get("count", 0)
            print(f"Terminated users: {count}")
            ```
        """
        params = {}
        if terminated_only:
            params["terminatedOnly"] = terminated_only

        return self.get("users/count", params=params)
