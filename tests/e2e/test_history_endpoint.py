from fastapi.testclient import TestClient


class TestGetHistory:
    def test_empty_history_returns_empty_list(self, test_client: TestClient) -> None:
        response = test_client.get("/api/history")

        assert response.status_code == 200
        assert response.json() == []

    def test_history_returns_most_recent_first(self, test_client: TestClient) -> None:
        for city in ("Recife", "Fortaleza", "Natal"):
            test_client.get("/api/weather", params={"city": city})

        response = test_client.get("/api/history")
        data = response.json()

        assert response.status_code == 200
        assert [row["city_name"] for row in data] == ["Natal", "Fortaleza", "Recife"]

    def test_history_row_contains_required_fields(self, test_client: TestClient) -> None:
        test_client.get("/api/weather", params={"city": "Manaus"})

        row = test_client.get("/api/history").json()[0]

        assert set(row.keys()) == {"city_name", "latitude", "longitude", "created_at"}
