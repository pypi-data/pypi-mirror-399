import pytest
from unittest.mock import Mock, patch, MagicMock
import datetime
import json
from requests.exceptions import RequestException
from uwl_client import UWLClient, UWLClientError


class TestWLClientInitialization:
    """Tests para la inicialización de UWLClient"""
    
    def test_init_success(self):
        client = UWLClient(api_key="test-key", api_secret="test-secret")
        assert client.base_url == "https://api.weatherlink.com/v2"
        assert client.get_config("api_key") == "test-key"
        assert client.get_config("api_secret") == "test-secret"
        assert client.timeout == 600
    
    def test_init_custom_timeout(self):
        client = UWLClient(api_key="key", api_secret="secret", timeout=300)
        assert client.timeout == 300
    
    def test_init_missing_api_key(self):
        with pytest.raises(ValueError, match="api_key y api_secret son requeridos"):
            UWLClient(api_key="", api_secret="secret")
    
    def test_init_missing_api_secret(self):
        with pytest.raises(ValueError, match="api_key y api_secret son requeridos"):
            UWLClient(api_key="key", api_secret="")
    
    def test_base_query_params(self):
        client = UWLClient(api_key="test-key", api_secret="test-secret")
        params = client.base_query_params
        assert params["api-key"] == "test-key"


class TestDateUtilities:
    """Tests para utilidades de fecha y timestamp"""
    
    def test_date_to_timestamp(self):
        client = UWLClient(api_key="key", api_secret="secret")
        date = datetime.datetime(2024, 1, 1, 12, 0, 0)
        timestamp = client._date_to_timestamp(date)
        assert isinstance(timestamp, int)
        assert timestamp > 0
    
    def test_date_to_timestamp_invalid_type(self):
        client = UWLClient(api_key="key", api_secret="secret")
        with pytest.raises(TypeError, match="debe ser un objeto datetime"):
            client._date_to_timestamp("2024-01-01")
    
    def test_timestamp_to_date(self):
        client = UWLClient(api_key="key", api_secret="secret")
        timestamp = 1704110400  # 2024-01-01 12:00:00 UTC
        date = client.timestamp_to_date(timestamp)
        assert isinstance(date, datetime.datetime)
    
    def test_get_timestamp(self):
        client = UWLClient(api_key="key", api_secret="secret")
        timestamp = client.get_timestamp()
        assert isinstance(timestamp, int)
        assert timestamp > 0
    
    def test_date_roundtrip(self):
        client = UWLClient(api_key="key", api_secret="secret")
        original_date = datetime.datetime(2024, 1, 1, 12, 0, 0)
        timestamp = client._date_to_timestamp(original_date)
        converted_date = client.timestamp_to_date(timestamp)
        assert original_date == converted_date


class TestValidationMethods:
    """Tests para métodos de validación"""
    
    def test_validate_date_range_valid(self):
        client = UWLClient(api_key="key", api_secret="secret")
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        # No debe lanzar excepción
        client._validate_date_range(start, end)
    
    def test_validate_date_range_invalid_order(self):
        client = UWLClient(api_key="key", api_secret="secret")
        start = datetime.datetime(2024, 1, 2)
        end = datetime.datetime(2024, 1, 1)
        with pytest.raises(ValueError, match="start debe ser anterior a end"):
            client._validate_date_range(start, end)
    
    def test_validate_date_range_equal_dates(self):
        client = UWLClient(api_key="key", api_secret="secret")
        date = datetime.datetime(2024, 1, 1)
        with pytest.raises(ValueError, match="start debe ser anterior a end"):
            client._validate_date_range(date, date)
    
    def test_validate_date_range_invalid_type(self):
        client = UWLClient(api_key="key", api_secret="secret")
        with pytest.raises(TypeError, match="debe ser un objeto datetime"):
            client._validate_date_range("2024-01-01", datetime.datetime.now())
    
    def test_normalize_sensor_ids_single_int(self):
        client = UWLClient(api_key="key", api_secret="secret")
        result = client._normalize_sensor_ids(123)
        assert result == [123]
    
    def test_normalize_sensor_ids_single_string(self):
        client = UWLClient(api_key="key", api_secret="secret")
        result = client._normalize_sensor_ids("456")
        assert result == [456]
    
    def test_normalize_sensor_ids_list(self):
        client = UWLClient(api_key="key", api_secret="secret")
        result = client._normalize_sensor_ids([1, "2", 3])
        assert result == [1, 2, 3]


class TestResponseHandling:
    """Tests para manejo de respuestas"""
    
    def test_handle_response_raw_content(self):
        client = UWLClient(api_key="key", api_secret="secret")
        mock_response = Mock(status_code=200)
        result = client._handle_response(mock_response, raw_content=True)
        assert result is mock_response
    
    def test_handle_response_success_with_key(self):
        client = UWLClient(api_key="key", api_secret="secret")
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"stations": [{"id": 1}, {"id": 2}]}
        
        result = client._handle_response(mock_response, data_key="stations")
        assert result == [{"id": 1}, {"id": 2}]
    
    def test_handle_response_success_without_key(self):
        client = UWLClient(api_key="key", api_secret="secret")
        mock_response = Mock(status_code=200)
        data = {"status": "ok", "data": [1, 2, 3]}
        mock_response.json.return_value = data
        
        result = client._handle_response(mock_response)
        assert result == data
    
    def test_handle_response_error_status(self):
        client = UWLClient(api_key="key", api_secret="secret")
        mock_response = Mock(status_code=404)
        mock_response.json.return_value = {"message": "Not found"}
        mock_response.text = "Not found"
        
        with pytest.raises(UWLClientError, match="404"):
            client._handle_response(mock_response)
    
    def test_handle_response_error_no_json(self):
        client = UWLClient(api_key="key", api_secret="secret")
        mock_response = Mock(status_code=500)
        mock_response.json.side_effect = ValueError()
        mock_response.text = "Internal Server Error"
        
        with pytest.raises(UWLClientError, match="500"):
            client._handle_response(mock_response)


class TestGetStations:
    """Tests para get_stations"""
    
    @patch('requests.get')
    def test_get_stations_success(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "stations": [
                {"station_id": 1, "name": "Station 1"},
                {"station_id": 2, "name": "Station 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        stations = client.get_stations()
        
        assert len(stations) == 2
        assert stations[0]["station_id"] == 1
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_stations_raw_content(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        result = client.get_stations(raw_content=True)
        
        assert result is mock_response
    
    @patch('requests.get')
    def test_get_stations_error(self, mock_get):
        mock_response = Mock(status_code=401)
        mock_response.json.return_value = {"message": "Unauthorized"}
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        with pytest.raises(UWLClientError):
            client.get_stations()


class TestGetSensors:
    """Tests para get_sensors"""
    
    @patch('requests.get')
    def test_get_sensors_success(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "sensors": [
                {"lsid": 123, "type": "temperature"},
                {"lsid": 456, "type": "humidity"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        sensors = client.get_sensors()
        
        assert len(sensors) == 2
        assert sensors[0]["lsid"] == 123


class TestGetSensorCatalog:
    """Tests para get_sensor_catalog"""
    
    @patch('requests.get')
    def test_get_sensor_catalog_all(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "sensor_types": [
                {"sensor_type": 1, "name": "Type 1"},
                {"sensor_type": 2, "name": "Type 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        catalog = client.get_sensor_catalog()
        
        assert len(catalog) == 2
    
    @patch('requests.get')
    def test_get_sensor_catalog_specific_type(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "sensor_types": [
                {"sensor_type": 1, "name": "Type 1"},
                {"sensor_type": 2, "name": "Type 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        sensor = client.get_sensor_catalog(sensor_type=1)
        
        assert sensor is not None
        assert sensor["sensor_type"] == 1
    
    @patch('requests.get')
    def test_get_sensor_catalog_type_not_found(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "sensor_types": [
                {"sensor_type": 1, "name": "Type 1"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        sensor = client.get_sensor_catalog(sensor_type=999)
        
        assert sensor is None


class TestGetHistoric:
    """Tests para get_historic"""
    
    @patch('requests.get')
    def test_get_historic_all_sensors(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "sensors": [
                {
                    "lsid": 123,
                    "data": [
                        {"ts": 1704110400, "temp": 20.5, "hum": 60},
                        {"ts": 1704114000, "temp": 21.0, "hum": 58}
                    ]
                },
                {
                    "lsid": 456,
                    "data": [
                        {"ts": 1704110400, "pressure": 1013},
                        {"ts": 1704114000, "pressure": 1014}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        start = datetime.datetime(2024, 1, 1, 0, 0, 0)
        end = datetime.datetime(2024, 1, 2, 0, 0, 0)
        
        data = client.get_historic(station_id=1, start=start, end=end, sensors="all")
        
        assert len(data) == 2
        # Verificar que los datos están consolidados
        assert "temp" in data[0]
        assert "pressure" in data[0]
    
    @patch('requests.get')
    def test_get_historic_specific_sensor(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "sensors": [
                {
                    "lsid": 123,
                    "data": [{"ts": 1704110400, "temp": 20.5}]
                },
                {
                    "lsid": 456,
                    "data": [{"ts": 1704110400, "pressure": 1013}]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        
        data = client.get_historic(station_id=1, start=start, end=end, sensors=123)
        
        assert len(data) == 1
        assert "temp" in data[0]
        assert "pressure" not in data[0]
    
    @patch('requests.get')
    def test_get_historic_multiple_sensors(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "sensors": [
                {"lsid": 123, "data": [{"ts": 1704110400, "temp": 20}]},
                {"lsid": 456, "data": [{"ts": 1704110400, "pressure": 1013}]},
                {"lsid": 789, "data": [{"ts": 1704110400, "wind": 10}]}
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        
        data = client.get_historic(
            station_id=1, 
            start=start, 
            end=end, 
            sensors=[123, 456]
        )
        
        assert len(data) == 1
        assert "temp" in data[0]
        assert "pressure" in data[0]
        assert "wind" not in data[0]
    
    def test_get_historic_invalid_date_range(self):
        client = UWLClient(api_key="key", api_secret="secret")
        start = datetime.datetime(2024, 1, 2)
        end = datetime.datetime(2024, 1, 1)
        
        with pytest.raises(ValueError, match="start debe ser anterior"):
            client.get_historic(station_id=1, start=start, end=end)
    
    @patch('requests.get')
    def test_get_historic_raw_content(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        
        result = client.get_historic(
            station_id=1, 
            start=start, 
            end=end, 
            raw_content=True
        )
        
        assert result is mock_response
    
    @patch('requests.get')
    def test_get_historic_consolidates_timestamps(self, mock_get):
        """Verifica que registros del mismo timestamp se consolidan"""
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "sensors": [
                {
                    "lsid": 123,
                    "data": [
                        {"ts": 1704110400, "temp": 20.5, "sensor_id": 123}
                    ]
                },
                {
                    "lsid": 456,
                    "data": [
                        {"ts": 1704110400, "hum": 60, "sensor_id": 456}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        client = UWLClient(api_key="key", api_secret="secret")
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        
        data = client.get_historic(station_id=1, start=start, end=end)
        
        # Debe haber un solo registro con ambos valores
        assert len(data) == 1
        assert data[0]["ts"] == 1704110400
        assert data[0]["temp"] == 20.5
        assert data[0]["hum"] == 60


class TestIntegrationScenarios:
    """Tests de escenarios de integración"""
    
    @patch('requests.get')
    def test_full_workflow(self, mock_get):
        """Simula un flujo completo de uso del cliente"""
        client = UWLClient(api_key="key", api_secret="secret")
        
        # 1. Obtener estaciones
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {"stations": [{"station_id": 1, "name": "My Station"}]}
        )
        stations = client.get_stations()
        assert len(stations) == 1
        
        # 2. Obtener sensores
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {"sensors": [{"lsid": 123, "station_id": 1}]}
        )
        sensors = client.get_sensors()
        assert len(sensors) == 1
        
        # 3. Obtener datos históricos
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "sensors": [{
                    "lsid": 123,
                    "data": [{"ts": 1704110400, "temp": 20}]
                }]
            }
        )
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        data = client.get_historic(station_id=1, start=start, end=end)
        assert len(data) == 1


# Fixtures
@pytest.fixture
def wl_client():
    """Cliente WL para tests"""
    return UWLClient(api_key="test-key", api_secret="test-secret")


@pytest.fixture
def mock_historic_response():
    """Response mock para datos históricos"""
    return {
        "sensors": [
            {
                "lsid": 123,
                "data": [
                    {"ts": 1704110400, "temp": 20.5, "hum": 60},
                    {"ts": 1704114000, "temp": 21.0, "hum": 58}
                ]
            }
        ]
    }


# Tests usando fixtures
class TestWithFixtures:
    
    def test_client_fixture(self, wl_client):
        assert wl_client.get_config("api_key") == "test-key"
        assert wl_client.timeout == 600
    
    @patch('requests.get')
    def test_historic_with_fixture(self, mock_get, wl_client, mock_historic_response):
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: mock_historic_response
        )
        
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        data = wl_client.get_historic(station_id=1, start=start, end=end)
        
        assert len(data) == 2
        assert data[0]["temp"] == 20.5
