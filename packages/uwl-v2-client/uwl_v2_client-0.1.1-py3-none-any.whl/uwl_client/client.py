from typing import Any, Optional
import requests
import json


class ApiClient(object):
    def __init__(
            self,
            base_url: str = '',
            timeout: int = 10,
            config: Optional[dict] = None, 
            **kwargs
    ):
        self.__base_url = base_url.rstrip('/') if base_url else ''
        self.timeout = timeout
        self.config = config or {}

    @property
    def base_url(self) -> str:
        return self.__base_url

    def url_for(self, endpoint: str) -> str:
        if not self.__base_url:
            raise ValueError("base_url no está configurado")
        endpoint = endpoint.strip('/')
        return f"{self.__base_url}/{endpoint}"

    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def _get_default_headers(self) -> dict[str, str]:
        """Genera headers por defecto con el API secret"""
        api_secret = self.get_config("api_secret", "")
        return {
            "X-Api-Secret": api_secret,
            "Content-Type": "application/json",
        }

    def _prepare_data(self, data: Any) -> Optional[str]:
        """Serializa datos a JSON si es necesario"""
        if data is None:
            return None
        if isinstance(data, str):
            return data
        return json.dumps(data)
    
    def _merge_headers(
            self,
            custom_headers: Optional[dict] = None
        ) -> dict[str, str]:
        """Combina headers por defecto con headers personalizados"""
        headers = self._get_default_headers()
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def get_request(
        self, 
        endpoint: str, 
        params: Optional[dict] = None, 
        headers: Optional[dict] = None
    ) -> requests.Response:
        """Realiza una petición GET"""
        try:
            return requests.get(
                self.url_for(endpoint),
                params=params,
                headers=self._merge_headers(headers),
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise Exception(f"Error en GET request a {endpoint}: {str(e)}")

    def post_request(
        self, endpoint: str, 
        params: Optional[dict] = None,
        data: Any = None, 
        headers: Optional[dict] = None
    ) -> requests.Response:
        """Realiza una petición POST"""
        try:
            return requests.post(
                self.url_for(endpoint),
                params=params,
                data=self._prepare_data(data),
                headers=self._merge_headers(headers),
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise Exception(f"Error en POST request a {endpoint}: {str(e)}")
    
    def put_request(
        self, 
        endpoint: str, 
        params: Optional[dict] = None,
        data: Any = None, 
        headers: Optional[dict] = None
    ) -> requests.Response:
        """Realiza una petición PUT"""
        try:
            return requests.put(
                self.url_for(endpoint),
                params=params,
                data=self._prepare_data(data),
                headers=self._merge_headers(headers),
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise Exception(f"Error en PUT request a {endpoint}: {str(e)}")
    
    def delete_request(
        self, endpoint: str, 
        params: Optional[dict] = None,
        data: Any = None, 
        headers: Optional[dict] = None
    ) -> requests.Response:
        """Realiza una petición DELETE"""
        try:
            return requests.delete(
                self.url_for(endpoint),
                params=params,
                data=self._prepare_data(data),
                headers=self._merge_headers(headers),
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise Exception(f"Error en DELETE request a {endpoint}: {str(e)}")
