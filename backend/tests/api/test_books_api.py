"""Integration tests for ``/api/v1/book`` endpoints.

Drives the FastAPI app via ``httpx.AsyncClient`` (ASGI transport) against a
migrated SQLite database, exercising the CRUD surface plus pagination and
error paths (404 missing, 400 invalid ``author_id``, 400 duplicate name).
"""

import pytest
from httpx import AsyncClient


async def _create_author(client: AsyncClient, first_name: str = "Frank") -> int:
    """POST a minimal author and return its id.

    Args:
        client (AsyncClient): HTTP client.
        first_name (str, optional): Value for ``first_name``. Defaults to "Frank".

    Returns:
        int: Newly created author id.

    """
    response = await client.post("/api/v1/author", json={"first_name": first_name})
    return response.json()["id"]


@pytest.mark.api
@pytest.mark.integration
class TestBooksApi:
    """End-to-end behaviour of the book router."""

    async def test_create_book_returns_201_with_payload(self, client: AsyncClient) -> None:
        """POST creates a book linked to an existing author.

        Args:
            client (AsyncClient): HTTP client bound to the in-process FastAPI app.

        Returns:
            None

        """
        author_id = await _create_author(client)

        response = await client.post(
            "/api/v1/book",
            json={"name": "Dune", "description": "Sand", "cover": "dune.png", "author_id": author_id},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Dune"
        assert body["authorId"] == author_id
        assert isinstance(body["id"], int)

    async def test_create_book_with_invalid_author_id_returns_400(self, client: AsyncClient) -> None:
        """Foreign-key violation on ``author_id`` maps to 400.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        response = await client.post(
            "/api/v1/book",
            json={"name": "Orphan", "author_id": 9999},
        )

        assert response.status_code == 400

    async def test_get_single_book_returns_persisted_row(self, client: AsyncClient) -> None:
        """GET by id returns the row previously created via POST.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        author_id = await _create_author(client, first_name="Isaac")
        created = (await client.post("/api/v1/book", json={"name": "Foundation", "author_id": author_id})).json()

        response = await client.get(f"/api/v1/book/{created['id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Foundation"
        assert body["authorId"] == author_id

    async def test_get_single_book_missing_returns_404(self, client: AsyncClient) -> None:
        """Unknown ids surface as 404 Not Found.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        response = await client.get("/api/v1/book/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Book not found"

    async def test_get_all_books_paginates_and_reports_total(self, client: AsyncClient) -> None:
        """GET list returns rows plus matching pagination metadata.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        author_id = await _create_author(client)
        for name in ("Book A", "Book B", "Book C"):
            await client.post("/api/v1/book", json={"name": name, "author_id": author_id})

        response = await client.get("/api/v1/book", params={"limit": 2, "offset": 0})

        assert response.status_code == 200
        body = response.json()
        assert body["metadata"]["total"] == 3
        assert body["metadata"]["limit"] == 2
        assert len(body["data"]) == 2

    async def test_patch_book_updates_subset_of_fields(self, client: AsyncClient) -> None:
        """PATCH applies only provided fields and returns the updated row.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        author_id = await _create_author(client)
        created = (
            await client.post(
                "/api/v1/book",
                json={"name": "OldName", "description": "Old", "author_id": author_id},
            )
        ).json()

        response = await client.patch(
            f"/api/v1/book/{created['id']}",
            json={"description": "New"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "OldName"
        assert body["description"] == "New"

    async def test_patch_missing_book_returns_404(self, client: AsyncClient) -> None:
        """PATCH against unknown id surfaces 404.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        response = await client.patch("/api/v1/book/9999", json={"name": "ghost"})

        assert response.status_code == 404

    async def test_delete_book_returns_204_then_404(self, client: AsyncClient) -> None:
        """DELETE removes the row; subsequent GET returns 404.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        author_id = await _create_author(client)
        created = (await client.post("/api/v1/book", json={"name": "ToDelete", "author_id": author_id})).json()

        delete_response = await client.delete(f"/api/v1/book/{created['id']}")

        assert delete_response.status_code == 204
        assert delete_response.content == b""

        follow_up = await client.get(f"/api/v1/book/{created['id']}")
        assert follow_up.status_code == 404

    async def test_delete_missing_book_returns_404(self, client: AsyncClient) -> None:
        """DELETE against unknown id surfaces 404.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        response = await client.delete("/api/v1/book/9999")

        assert response.status_code == 404

    async def test_create_duplicate_book_name_returns_400(self, client: AsyncClient) -> None:
        """Unique-name violation on ``book.name`` maps to 400.

        Args:
            client (AsyncClient): HTTP client.

        Returns:
            None

        """
        author_id = await _create_author(client)
        await client.post("/api/v1/book", json={"name": "Unique", "author_id": author_id})

        response = await client.post(
            "/api/v1/book",
            json={"name": "Unique", "author_id": author_id},
        )

        assert response.status_code == 400
