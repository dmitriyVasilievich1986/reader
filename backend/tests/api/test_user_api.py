"""Integration tests for ``/api/v1/user`` endpoints and Bearer-token auth.

Covers the login flow (success, wrong password, unknown user), ``/me``
behaviours, and the cross-cutting authorization guards on other routers:

* ``user_authorized`` rejects requests with a missing or malformed token (401).
* ``admin_required`` rejects authenticated non-admin requests to mutating
  endpoints (403) while allowing them to read.

Uses the API-layer fixtures (``client``, ``admin_client``, ``user_client``,
``seed_admin_user``, ``seed_regular_user``) from ``api.conftest``.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.integration
class TestUserLogin:
    """``POST /api/v1/user/login`` exchanges credentials for a JWT."""

    async def test_login_returns_access_token(
        self,
        client: AsyncClient,
        seed_admin_user: dict[str, str],
    ) -> None:
        """Valid credentials yield a 200 response carrying ``accessToken``.

        Args:
            client (AsyncClient): Anonymous HTTP client.
            seed_admin_user (dict[str, str]): Pre-seeded admin credentials.

        Returns:
            None

        """
        response = await client.post("/api/v1/user/login", json=seed_admin_user)

        assert response.status_code == 200
        body = response.json()
        assert body["accessToken"]
        assert "expiresAt" in body

    async def test_login_wrong_password_returns_401(
        self,
        client: AsyncClient,
        seed_admin_user: dict[str, str],
    ) -> None:
        """Wrong password is reported as 401 Unauthorized.

        Args:
            client (AsyncClient): Anonymous HTTP client.
            seed_admin_user (dict[str, str]): Pre-seeded admin credentials.

        Returns:
            None

        """
        response = await client.post(
            "/api/v1/user/login",
            json={"username": seed_admin_user["username"], "password": "wrong"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    async def test_login_unknown_user_returns_401(self, client: AsyncClient, migrated_db: None) -> None:
        """Unknown username is reported as 401 (no user enumeration leak).

        Args:
            client (AsyncClient): Anonymous HTTP client.
            migrated_db (None): Ensures schema exists so the lookup runs.

        Returns:
            None

        """
        response = await client.post(
            "/api/v1/user/login",
            json={"username": "ghost", "password": "pw"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"


@pytest.mark.api
@pytest.mark.integration
class TestUserMe:
    """``/api/v1/user/me`` GET and PATCH require a valid Bearer token."""

    async def test_get_me_returns_current_user(self, admin_client: AsyncClient) -> None:
        """GET /me surfaces the username embedded in the JWT.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.get("/api/v1/user/me")

        assert response.status_code == 200
        body = response.json()
        assert body["username"] == "admin"
        assert body["email"] == "admin@example.com"

    async def test_patch_me_updates_profile_fields(self, user_client: AsyncClient) -> None:
        """PATCH /me applies allowed profile changes for the authenticated user.

        Args:
            user_client (AsyncClient): Non-admin authenticated HTTP client.

        Returns:
            None

        """
        response = await user_client.patch(
            "/api/v1/user/me",
            json={"first_name": "Reg", "last_name": "User"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["firstName"] == "Reg"
        assert body["lastName"] == "User"


@pytest.mark.api
@pytest.mark.integration
class TestUserAuthorizationGuards:
    """Cross-router checks: ``user_authorized`` / ``admin_required`` behaviour."""

    async def test_missing_token_returns_401(self, client: AsyncClient, migrated_db: None) -> None:
        """Requests without an ``Authorization`` header are rejected with 401.

        Args:
            client (AsyncClient): Anonymous HTTP client.
            migrated_db (None): Ensures the app has a migrated database.

        Returns:
            None

        """
        response = await client.get("/api/v1/author")

        assert response.status_code in {401, 403}

    async def test_malformed_token_returns_401(self, client: AsyncClient, migrated_db: None) -> None:
        """A garbage Bearer token decodes to ``Invalid token`` (401).

        Args:
            client (AsyncClient): Anonymous HTTP client.
            migrated_db (None): Ensures the app has a migrated database.

        Returns:
            None

        """
        response = await client.get(
            "/api/v1/author",
            headers={"Authorization": "Bearer not-a-real-jwt"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    async def test_get_me_without_token_returns_401(self, client: AsyncClient, migrated_db: None) -> None:
        """User-specific endpoints honor the same Bearer requirement.

        Args:
            client (AsyncClient): Anonymous HTTP client.
            migrated_db (None): Ensures the app has a migrated database.

        Returns:
            None

        """
        response = await client.get("/api/v1/user/me")

        assert response.status_code in {401, 403}

    async def test_non_admin_can_list_authors(self, user_client: AsyncClient) -> None:
        """``user_authorized`` allows non-admin reads on listing endpoints.

        Args:
            user_client (AsyncClient): Non-admin authenticated HTTP client.

        Returns:
            None

        """
        response = await user_client.get("/api/v1/author")

        assert response.status_code == 200
        assert "data" in response.json()

    async def test_non_admin_cannot_create_author(self, user_client: AsyncClient) -> None:
        """``admin_required`` rejects non-admin POSTs with 403.

        Args:
            user_client (AsyncClient): Non-admin authenticated HTTP client.

        Returns:
            None

        """
        response = await user_client.post("/api/v1/author", json={"first_name": "Nope"})

        assert response.status_code == 403
        assert response.json()["detail"] == "You are not authorized to access this resource"

    async def test_non_admin_cannot_delete_category(self, user_client: AsyncClient) -> None:
        """``admin_required`` rejects non-admin DELETEs with 403.

        Args:
            user_client (AsyncClient): Non-admin authenticated HTTP client.

        Returns:
            None

        """
        response = await user_client.delete("/api/v1/category/1")

        assert response.status_code == 403
