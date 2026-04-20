from locust import HttpUser, between, task


class WeatherApiUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_weather(self) -> None:
        self.client.get("/api/weather?city=Curitiba", name="/api/weather")

    @task(1)
    def get_history(self) -> None:
        self.client.get("/api/history")

    @task(1)
    def get_status(self) -> None:
        self.client.get("/api/status")
