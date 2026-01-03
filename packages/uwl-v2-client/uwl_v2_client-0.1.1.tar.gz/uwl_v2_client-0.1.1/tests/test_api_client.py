import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import ConnectionError, Timeout, RequestException
import requests


from uwl_client.client import ApiClient


class TestApiClientInitialization:
    """Tests para la inicialización del cliente"""
    
    def test_init_default_values(self):
        client = ApiClient()
        assert client.base_url == ''
        assert client.timeout == 10
        assert client.config == {}
    
    def test_init_with_base_url(self):
        client = ApiClient(base_url="https://api.example.com")
        assert client.base_url == "https://api.example.com"
    
    def test_init_removes_trailing_slash(self):
        client = ApiClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"
    
    def test_init_with_config(self):
        config = {"api_secret": "test-secret", "custom_key": "value"}
        client = ApiClient(config=config)
        assert client.config == config
        assert client.get_config("api_secret") == "test-secret"
    
    def test_init_with_custom_timeout(self):
        client = ApiClient(timeout=30)
        assert client.timeout == 30


class TestUrlConstruction:
    """Tests para la construcción de URLs"""
    
    def test_url_for_simple_endpoint(self):
        client = ApiClient(base_url="https://api.example.com")
        url = client.url_for("/users")
        assert url == "https://api.example.com/users"
    
    def test_url_for_without_leading_slash(self):
        client = ApiClient(base_url="https://api.example.com")
        url = client.url_for("users")
        assert url == "https://api.example.com/users"
    
    def test_url_for_with_trailing_slash(self):
        client = ApiClient(base_url="https://api.example.com")
        url = client.url_for("/users/")
        assert url == "https://api.example.com/users"
    
    def test_url_for_nested_endpoint(self):
        client = ApiClient(base_url="https://api.example.com")
        url = client.url_for("/users/123/posts")
        assert url == "https://api.example.com/users/123/posts"
    
    def test_url_for_without_base_url_raises_error(self):
        client = ApiClient()
        with pytest.raises(ValueError, match="base_url no está configurado"):
            client.url_for("/users")


class TestConfigManagement:
    """Tests para el manejo de configuración"""
    
    def test_get_config_existing_key(self):
        client = ApiClient(config={"api_secret": "secret123"})
        assert client.get_config("api_secret") == "secret123"
    
    def test_get_config_missing_key_returns_default(self):
        client = ApiClient(config={})
        assert client.get_config("missing_key", "default") == "default"
    
    def test_get_config_missing_key_returns_none(self):
        client = ApiClient(config={})
        assert client.get_config("missing_key") is None


class TestHeadersPreparation:
    """Tests para la preparación de headers"""
    
    def test_get_default_headers_with_api_secret(self):
        client = ApiClient(config={"api_secret": "my-secret"})
        headers = client._get_default_headers()
        assert headers["X-Api-Secret"] == "my-secret"
        assert headers["Content-Type"] == "application/json"
    
    def test_get_default_headers_without_api_secret(self):
        client = ApiClient()
        headers = client._get_default_headers()
        assert headers["X-Api-Secret"] == ""
        assert headers["Content-Type"] == "application/json"
    
    def test_merge_headers_with_custom(self):
        client = ApiClient(config={"api_secret": "secret"})
        custom = {"Authorization": "Bearer token"}
        merged = client._merge_headers(custom)
        assert merged["X-Api-Secret"] == "secret"
        assert merged["Authorization"] == "Bearer token"
        assert merged["Content-Type"] == "application/json"
    
    def test_merge_headers_overrides_default(self):
        client = ApiClient(config={"api_secret": "secret"})
        custom = {"Content-Type": "text/plain"}
        merged = client._merge_headers(custom)
        assert merged["Content-Type"] == "text/plain"


class TestDataPreparation:
    """Tests para la preparación de datos"""
    
    def test_prepare_data_with_dict(self):
        client = ApiClient()
        data = {"name": "John", "age": 30}
        prepared = client._prepare_data(data)
        assert prepared == json.dumps(data)
    
    def test_prepare_data_with_string(self):
        client = ApiClient()
        data = '{"name": "John"}'
        prepared = client._prepare_data(data)
        assert prepared == data
    
    def test_prepare_data_with_none(self):
        client = ApiClient()
        prepared = client._prepare_data(None)
        assert prepared is None
    
    def test_prepare_data_with_list(self):
        client = ApiClient()
        data = [1, 2, 3]
        prepared = client._prepare_data(data)
        assert prepared == json.dumps(data)


class TestGetRequest:
    """Tests para peticiones GET"""
    
    @patch('requests.get')
    def test_get_request_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "John"}
        mock_get.return_value = mock_response
        
        client = ApiClient(
            base_url="https://api.example.com",
            config={"api_secret": "secret"}
        )
        response = client.get_request("/users/1")
        
        assert response.status_code == 200
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://api.example.com/users/1"
        assert call_args[1]["headers"]["X-Api-Secret"] == "secret"
    
    @patch('requests.get')
    def test_get_request_with_params(self, mock_get):
        mock_response = Mock()
        mock_get.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com")
        params = {"page": 1, "limit": 10}
        client.get_request("/users", params=params)
        
        call_args = mock_get.call_args
        assert call_args[1]["params"] == params
    
    @patch('requests.get')
    def test_get_request_with_custom_headers(self, mock_get):
        mock_response = Mock()
        mock_get.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com")
        custom_headers = {"Authorization": "Bearer token"}
        client.get_request("/users", headers=custom_headers)
        
        call_args = mock_get.call_args
        assert "Authorization" in call_args[1]["headers"]
    
    @patch('requests.get')
    def test_get_request_timeout(self, mock_get):
        mock_get.side_effect = Timeout()
        
        client = ApiClient(base_url="https://api.example.com")
        with pytest.raises(Exception, match="Error en GET request"):
            client.get_request("/users")
    
    @patch('requests.get')
    def test_get_request_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError()
        
        client = ApiClient(base_url="https://api.example.com")
        with pytest.raises(Exception, match="Error en GET request"):
            client.get_request("/users")


class TestPostRequest:
    """Tests para peticiones POST"""
    
    @patch('requests.post')
    def test_post_request_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com")
        data = {"name": "John", "email": "john@example.com"}
        response = client.post_request("/users", data=data)
        
        assert response.status_code == 201
        call_args = mock_post.call_args
        assert call_args[1]["data"] == json.dumps(data)
    
    @patch('requests.post')
    def test_post_request_with_string_data(self, mock_post):
        mock_response = Mock()
        mock_post.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com")
        data = '{"name": "John"}'
        client.post_request("/users", data=data)
        
        call_args = mock_post.call_args
        assert call_args[1]["data"] == data
    
    @patch('requests.post')
    def test_post_request_with_params(self, mock_post):
        mock_response = Mock()
        mock_post.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com")
        params = {"notify": "true"}
        client.post_request("/users", params=params, data={"name": "John"})
        
        call_args = mock_post.call_args
        assert call_args[1]["params"] == params
    
    @patch('requests.post')
    def test_post_request_error(self, mock_post):
        mock_post.side_effect = RequestException("Network error")
        
        client = ApiClient(base_url="https://api.example.com")
        with pytest.raises(Exception, match="Error en POST request"):
            client.post_request("/users", data={"name": "John"})


class TestPutRequest:
    """Tests para peticiones PUT"""
    
    @patch('requests.put')
    def test_put_request_success(self, mock_put):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com")
        data = {"name": "John Updated"}
        response = client.put_request("/users/1", data=data)
        
        assert response.status_code == 200
        call_args = mock_put.call_args
        assert call_args[0][0] == "https://api.example.com/users/1"
        assert call_args[1]["data"] == json.dumps(data)
    
    @patch('requests.put')
    def test_put_request_error(self, mock_put):
        mock_put.side_effect = Timeout()
        
        client = ApiClient(base_url="https://api.example.com")
        with pytest.raises(Exception, match="Error en PUT request"):
            client.put_request("/users/1", data={"name": "John"})


class TestDeleteRequest:
    """Tests para peticiones DELETE"""
    
    @patch('requests.delete')
    def test_delete_request_success(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com")
        response = client.delete_request("/users/1")
        
        assert response.status_code == 204
        call_args = mock_delete.call_args
        assert call_args[0][0] == "https://api.example.com/users/1"
    
    @patch('requests.delete')
    def test_delete_request_with_data(self, mock_delete):
        mock_response = Mock()
        mock_delete.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com")
        data = {"reason": "spam"}
        client.delete_request("/users/1", data=data)
        
        call_args = mock_delete.call_args
        assert call_args[1]["data"] == json.dumps(data)
    
    @patch('requests.delete')
    def test_delete_request_error(self, mock_delete):
        mock_delete.side_effect = ConnectionError()
        
        client = ApiClient(base_url="https://api.example.com")
        with pytest.raises(Exception, match="Error en DELETE request"):
            client.delete_request("/users/1")


class TestIntegration:
    """Tests de integración más complejos"""
    
    @patch('requests.get')
    @patch('requests.post')
    def test_multiple_requests_same_client(self, mock_post, mock_get):
        get_response = Mock(status_code=200)
        post_response = Mock(status_code=201)
        mock_get.return_value = get_response
        mock_post.return_value = post_response
        
        client = ApiClient(
            base_url="https://api.example.com",
            config={"api_secret": "secret"}
        )
        
        # Primera petición GET
        response1 = client.get_request("/users")
        assert response1.status_code == 200
        
        # Segunda petición POST
        response2 = client.post_request("/users", data={"name": "John"})
        assert response2.status_code == 201
        
        # Verificar que ambas usaron el mismo API secret
        get_headers = mock_get.call_args[1]["headers"]
        post_headers = mock_post.call_args[1]["headers"]
        assert get_headers["X-Api-Secret"] == "secret"
        assert post_headers["X-Api-Secret"] == "secret"
    
    @patch('requests.get')
    def test_timeout_configuration(self, mock_get):
        mock_response = Mock()
        mock_get.return_value = mock_response
        
        client = ApiClient(base_url="https://api.example.com", timeout=5)
        client.get_request("/users")
        
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 5


# Fixtures para reutilizar en tests
@pytest.fixture
def client():
    """Cliente básico para tests"""
    return ApiClient(
        base_url="https://api.example.com",
        config={"api_secret": "test-secret"}
    )


@pytest.fixture
def mock_response():
    """Response mock genérico"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    return response


# Tests usando fixtures
class TestWithFixtures:
    
    def test_client_fixture(self, client):
        assert client.base_url == "https://api.example.com"
        assert client.get_config("api_secret") == "test-secret"
    
    @patch('requests.get')
    def test_mock_response_fixture(self, mock_get, client, mock_response):
        mock_get.return_value = mock_response
        response = client.get_request("/test")
        assert response.json()["success"] is True