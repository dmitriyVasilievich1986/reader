"""Integration tests for ``/api/v1/category`` endpoints.

Drives the FastAPI app via ``httpx.AsyncClient`` (ASGI transport) against a
migrated SQLite database, exercising the CRUD surface plus pagination and
error paths (404 missing, 400 duplicate-name). The ``admin_client`` fixture
supplies a Bearer token for the seeded admin user so ``admin_required``
mutations succeed.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.integration
class TestCategoriesApi:
    """End-to-end behaviour of the category router."""

    async def test_create_category_returns_201_with_payload(self, admin_client: AsyncClient) -> None:
        """POST creates a category and echoes the persisted fields.

        Args:
            admin_client (AsyncClient): Admin-authenticated client bound to the
                in-process FastAPI app.

        Returns:
            None

        """
        response = await admin_client.post(
            "/api/v1/category",
            json={"name": "Mystery", "description": "Whodunits", "cover": "mystery.png"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Mystery"
        assert body["description"] == "Whodunits"
        assert body["cover"] == "mystery.png"
        assert isinstance(body["id"], int)

    async def test_get_single_category_returns_persisted_row(self, admin_client: AsyncClient) -> None:
        """GET by id returns the row previously created via POST.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        created = (await admin_client.post("/api/v1/category", json={"name": "Drama"})).json()

        response = await admin_client.get(f"/api/v1/category/{created['id']}")

        assert response.status_code == 200
        assert response.json()["name"] == "Drama"

    async def test_get_single_category_missing_returns_404(self, admin_client: AsyncClient) -> None:
        """Unknown ids surface as 404 Not Found.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.get("/api/v1/category/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    async def test_get_all_categories_paginates_and_reports_total(self, admin_client: AsyncClient) -> None:
        """GET list returns rows plus matching pagination metadata.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        for name in ("A", "B", "C"):
            await admin_client.post("/api/v1/category", json={"name": name})

        response = await admin_client.get("/api/v1/category", params={"limit": 2, "offset": 0})

        assert response.status_code == 200
        body = response.json()
        assert body["metadata"]["total"] == 3
        assert body["metadata"]["limit"] == 2
        assert body["metadata"]["offset"] == 0
        assert len(body["data"]) == 2

    async def test_patch_category_updates_subset_of_fields(self, admin_client: AsyncClient) -> None:
        """PATCH applies only provided fields and returns the updated row.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        created = (
            await admin_client.post(
                "/api/v1/category",
                json={"name": "SciFi", "description": "Space"},
            )
        ).json()

        response = await admin_client.patch(
            f"/api/v1/category/{created['id']}",
            json={"description": "Aliens"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "SciFi"
        assert body["description"] == "Aliens"

    async def test_patch_missing_category_returns_404(self, admin_client: AsyncClient) -> None:
        """PATCH against unknown id surfaces 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.patch("/api/v1/category/9999", json={"name": "ghost"})

        assert response.status_code == 404

    async def test_delete_category_returns_204_then_404(self, admin_client: AsyncClient) -> None:
        """DELETE removes the row; subsequent GET returns 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        created = (await admin_client.post("/api/v1/category", json={"name": "Temp"})).json()

        delete_response = await admin_client.delete(f"/api/v1/category/{created['id']}")

        assert delete_response.status_code == 204
        assert delete_response.content == b""

        follow_up = await admin_client.get(f"/api/v1/category/{created['id']}")
        assert follow_up.status_code == 404

    async def test_delete_missing_category_returns_404(self, admin_client: AsyncClient) -> None:
        """DELETE against unknown id surfaces 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.delete("/api/v1/category/9999")

        assert response.status_code == 404

    async def test_create_duplicate_name_returns_400(self, admin_client: AsyncClient) -> None:
        """Unique-name violation maps to 400 Bad Request via IntegrityError.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        await admin_client.post("/api/v1/category", json={"name": "Unique"})

        response = await admin_client.post("/api/v1/category", json={"name": "Unique"})

        assert response.status_code == 400
