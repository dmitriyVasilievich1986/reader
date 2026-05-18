"""Integration tests for ``/api/v1/page`` endpoints.

Drives the FastAPI app via ``httpx.AsyncClient`` (ASGI transport) against a
migrated SQLite database, exercising the CRUD surface plus pagination and
error paths (404 missing, 400 invalid ``book_id``). The ``admin_client``
fixture supplies a Bearer token for the seeded admin user so ``admin_required``
mutations succeed.
"""

import pytest
from httpx import AsyncClient


async def _create_book(client: AsyncClient, name: str = "Container") -> int:
    """POST a minimal author+book pair through the supplied client.

    Args:
        client (AsyncClient): HTTP client carrying any auth required for the
            author / book POSTs (typically the admin client).
        name (str, optional): Value for ``Book.name``. Defaults to "Container".

    Returns:
        int: Newly created book id.

    """
    author_id = (await client.post("/api/v1/author", json={"first_name": "Author"})).json()["id"]
    return (await client.post("/api/v1/book", json={"name": name, "author_id": author_id})).json()["id"]


@pytest.mark.api
@pytest.mark.integration
class TestPagesApi:
    """End-to-end behaviour of the page router."""

    async def test_create_page_returns_201_with_payload(self, admin_client: AsyncClient) -> None:
        """POST creates a page linked to an existing book.

        Args:
            admin_client (AsyncClient): Admin-authenticated client bound to the
                in-process FastAPI app.

        Returns:
            None

        """
        book_id = await _create_book(admin_client)

        response = await admin_client.post(
            "/api/v1/page",
            json={"position": 1, "cover": "page1.png", "book_id": book_id},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["position"] == 1
        assert body["cover"] == "page1.png"
        assert body["bookId"] == book_id

    async def test_create_page_with_invalid_book_id_returns_400(self, admin_client: AsyncClient) -> None:
        """Foreign-key violation on ``book_id`` maps to 400.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.post(
            "/api/v1/page",
            json={"position": 1, "book_id": 9999},
        )

        assert response.status_code == 400

    async def test_get_single_page_returns_persisted_row(self, admin_client: AsyncClient) -> None:
        """GET by id returns the row previously created via POST.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        book_id = await _create_book(admin_client)
        created = (await admin_client.post("/api/v1/page", json={"position": 7, "book_id": book_id})).json()

        response = await admin_client.get(f"/api/v1/page/{created['id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["position"] == 7
        assert body["bookId"] == book_id

    async def test_get_single_page_missing_returns_404(self, admin_client: AsyncClient) -> None:
        """Unknown ids surface as 404 Not Found.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.get("/api/v1/page/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Page not found"

    async def test_get_all_pages_paginates_and_reports_total(self, admin_client: AsyncClient) -> None:
        """GET list returns rows plus matching pagination metadata.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        book_id = await _create_book(admin_client)
        for position in (1, 2, 3):
            await admin_client.post("/api/v1/page", json={"position": position, "book_id": book_id})

        response = await admin_client.get("/api/v1/page", params={"limit": 2, "offset": 0})

        assert response.status_code == 200
        body = response.json()
        assert body["metadata"]["total"] == 3
        assert body["metadata"]["limit"] == 2
        assert len(body["data"]) == 2

    async def test_patch_page_updates_subset_of_fields(self, admin_client: AsyncClient) -> None:
        """PATCH applies only provided fields and returns the updated row.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        book_id = await _create_book(admin_client)
        created = (
            await admin_client.post(
                "/api/v1/page",
                json={"position": 5, "cover": "old.png", "book_id": book_id},
            )
        ).json()

        response = await admin_client.patch(
            f"/api/v1/page/{created['id']}",
            json={"cover": "new.png"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["position"] == 5
        assert body["cover"] == "new.png"

    async def test_patch_missing_page_returns_404(self, admin_client: AsyncClient) -> None:
        """PATCH against unknown id surfaces 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.patch("/api/v1/page/9999", json={"position": 1})

        assert response.status_code == 404

    async def test_delete_page_returns_204_then_404(self, admin_client: AsyncClient) -> None:
        """DELETE removes the row; subsequent GET returns 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        book_id = await _create_book(admin_client)
        created = (await admin_client.post("/api/v1/page", json={"position": 9, "book_id": book_id})).json()

        delete_response = await admin_client.delete(f"/api/v1/page/{created['id']}")

        assert delete_response.status_code == 204
        assert delete_response.content == b""

        follow_up = await admin_client.get(f"/api/v1/page/{created['id']}")
        assert follow_up.status_code == 404

    async def test_delete_missing_page_returns_404(self, admin_client: AsyncClient) -> None:
        """DELETE against unknown id surfaces 404.

        Args:
            admin_client (AsyncClient): Admin-authenticated HTTP client.

        Returns:
            None

        """
        response = await admin_client.delete("/api/v1/page/9999")

        assert response.status_code == 404
