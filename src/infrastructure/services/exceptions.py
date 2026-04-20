from fastapi import HTTPException, status


class CityNotFoundError(HTTPException):
    def __init__(self, city: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cidade '{city}' não encontrada.",
        )


class WeatherApiAuthError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha de autenticação na API OpenWeatherMap. Verifique a chave configurada.",
        )


class WeatherApiError(HTTPException):
    def __init__(self, status_code_upstream: int) -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Resposta inesperada da API OpenWeatherMap (status {status_code_upstream}).",
        )


class WeatherApiUnavailableError(HTTPException):
    def __init__(self, reason: str) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível conectar à API OpenWeatherMap: {reason}",
        )
