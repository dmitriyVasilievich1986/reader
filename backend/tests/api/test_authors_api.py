"""Integration tests for ``/api/v1/author`` endpoints.

Drives the FastAPI app via ``httpx.AsyncClient`` (ASGI transport) against a
migrated SQLite database, exercising the CRUD surface plus pagination and
error paths (404 missing). The ``admin_client`` fixture supplies a Bearer token
for the seeded admin user so ``admin_required`` mutations succeed.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.integration
class TestAuthorsApi:
    """End-to-end behaviour of the author router."""

    async def test_create_author_returns_201_with_payload(self, admin_client: AsyncClient) -> None:
        """POST creates an author and echoes the persisted fields.

        Args:
            admin_client (AsyncClient): Admin-authenticated client bound to the
                in-process FastAPI app.

        Returns:
            None

        """
        response = await admin_client.post(
            "/api/v1/author",
            json={"first_name": "Frank", "last_name": "Herbert", "cover": "frank.png"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["firstName"] == "Frank"
        assert body["lastName"] == "Herbert"
        assert body["cover"] == "frank.png"
        assert isinstance(body["id"], int)

    async def test_create_author_without_last_name_succeeds(self, admin_client: AsyncClient) -> None:
        """``last_name`` is optional and is stored as ``None`` when omitted.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.post("/api/v1/author", json={"first_name": "Homer"})

        assert response.status_code == 201
        body = response.json()
        assert body["firstName"] == "Homer"
        assert body["lastName"] is None

    async def test_get_single_author_returns_persisted_row(self, admin_client: AsyncClient) -> None:
        """GET by id returns the row previously created via POST.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        created = (
            await admin_client.post("/api/v1/author", json={"first_name": "Isaac", "last_name": "Asimov"})
        ).json()

        response = await admin_client.get(f"/api/v1/author/{created['id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["firstName"] == "Isaac"
        assert body["lastName"] == "Asimov"

    async def test_get_single_author_missing_returns_404(self, admin_client: AsyncClient) -> None:
        """Unknown ids surface as 404 Not Found.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.get("/api/v1/author/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Author not found"

    async def test_get_all_authors_paginates_and_reports_total(self, admin_client: AsyncClient) -> None:
        """GET list returns rows plus matching pagination metadata.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        for name in ("A", "B", "C"):
            await admin_client.post("/api/v1/author", json={"first_name": name})

        response = await admin_client.get("/api/v1/author", params={"limit": 2, "offset": 1})

        assert response.status_code == 200
        body = response.json()
        assert body["metadata"]["total"] == 3
        assert body["metadata"]["limit"] == 2
        assert body["metadata"]["offset"] == 1
        assert len(body["data"]) == 2

    async def test_patch_author_updates_subset_of_fields(self, admin_client: AsyncClient) -> None:
        """PATCH applies only provided fields and returns the updated row.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        created = (
            await admin_client.post("/api/v1/author", json={"first_name": "John", "last_name": "Doe"})
        ).json()

        response = await admin_client.patch(
            f"/api/v1/author/{created['id']}",
            json={"last_name": "Smith"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["firstName"] == "John"
        assert body["lastName"] == "Smith"

    async def test_patch_missing_author_returns_404(self, admin_client: AsyncClient) -> None:
        """PATCH against unknown id surfaces 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.patch("/api/v1/author/9999", json={"first_name": "ghost"})

        assert response.status_code == 404

    async def test_delete_author_returns_204_then_404(self, admin_client: AsyncClient) -> None:
        """DELETE removes the row; subsequent GET returns 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        created = (await admin_client.post("/api/v1/author", json={"first_name": "Temp"})).json()

        delete_response = await admin_client.delete(f"/api/v1/author/{created['id']}")

        assert delete_response.status_code == 204
        assert delete_response.content == b""

        follow_up = await admin_client.get(f"/api/v1/author/{created['id']}")
        assert follow_up.status_code == 404

    async def test_delete_missing_author_returns_404(self, admin_client: AsyncClient) -> None:
        """DELETE against unknown id surfaces 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.delete("/api/v1/author/9999")

        assert response.status_code == 404
