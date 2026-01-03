from .client import ApiClient
import datetime
import math
from typing import Optional, Union, List, Dict, Any
import requests

API_URL = "https://api.weatherlink.com/v2"


class UWLClientError(Exception):
    """Excepción personalizada para errores del cliente WeatherLink"""
    pass


class UWLClient(ApiClient):
    def __init__(self, api_key: str, api_secret: str, timeout: int = 600):
        super().__init__(base_url=API_URL, timeout=timeout)
        
        if not api_key or not api_secret:
            raise ValueError("api_key y api_secret son requeridos")
        
        self.config = {
            "base_url": API_URL,
            "api_key": api_key,
            "api_secret": api_secret,
        }

    def _date_to_timestamp(self, date_: datetime.datetime) -> int:
        """Convierte un objeto datetime a timestamp Unix"""
        if not isinstance(date_, datetime.datetime):
            raise TypeError("date_ debe ser un objeto datetime")
        return math.trunc(date_.timestamp())
    
    def timestamp_to_date(self, ts: int) -> datetime.datetime:
        """Convierte un timestamp Unix a objeto datetime"""
        return datetime.datetime.fromtimestamp(ts)
    
    def get_timestamp(self) -> int:
        """Obtiene el timestamp actual"""
        return self._date_to_timestamp(datetime.datetime.now())

    @property
    def base_query_params(self) -> Dict[str, str]:
        """Parámetros base requeridos para todas las peticiones"""
        return {
            "api-key": self.get_config("api_key"),
        }

    def _handle_response(
        self, 
        response: requests.Response, 
        data_key: Optional[str] = None,
        raw_content: bool = False
    ) -> Union[requests.Response, Dict, List]:
        """
        Maneja la respuesta de la API de forma centralizada
        
        Args:
            response: Objeto Response de requests
            data_key: Clave para extraer datos específicos del JSON
            raw_content: Si True, retorna el objeto Response completo
            
        Returns:
            Response completo, datos extraídos o mensaje de error
        """
        if raw_content:
            return response
        
        if response.status_code == 200:
            json_data = response.json()
            if data_key and data_key in json_data:
                return json_data[data_key]
            return json_data
        else:
            # Intentar extraer mensaje de error del JSON
            try:
                error_data = response.json()
                error_msg = error_data.get('message', error_data)
            except:
                error_msg = response.text or f"HTTP {response.status_code}"
            
            raise UWLClientError(
                f"Error en petición: {response.status_code} - {error_msg}"
            )
    
    def _validate_date_range(
        self, 
        start: datetime.datetime, 
        end: datetime.datetime
    ) -> None:
        """Valida que el rango de fechas sea correcto"""
        if not isinstance(start, datetime.datetime):
            raise TypeError("start debe ser un objeto datetime")
        if not isinstance(end, datetime.datetime):
            raise TypeError("end debe ser un objeto datetime")
        if start >= end:
            raise ValueError("start debe ser anterior a end")
    
    def _normalize_sensor_ids(
        self, 
        sensors: Union[str, int, List[Union[str, int]]]
    ) -> List[int]:
        """Normaliza los IDs de sensores a una lista de enteros"""
        if isinstance(sensors, (list, tuple)):
            return [int(sid) for sid in sensors]
        return [int(sensors)]

    def get_stations(self, raw_content: bool = False) -> Union[requests.Response, List[Dict]]:
        """
        Obtiene la lista de estaciones meteorológicas
        
        Args:
            raw_content: Si True, retorna el objeto Response completo
            
        Returns:
            Lista de estaciones o Response completo
            
        Raises:
            UWLClientError: Si hay un error en la petición
        """
        try:
            response = self.get_request("/stations", params=self.base_query_params)
            return self._handle_response(
                response, 
                data_key="stations", 
                raw_content=raw_content
            )
        except Exception as e:
            if isinstance(e, UWLClientError):
                raise
            raise UWLClientError(f"Error obteniendo estaciones: {str(e)}")
    
    def get_sensors(self, raw_content: bool = False) -> Union[requests.Response, List[Dict]]:
        """
        Obtiene la lista de sensores disponibles
        
        Args:
            raw_content: Si True, retorna el objeto Response completo
            
        Returns:
            Lista de sensores o Response completo
            
        Raises:
            UWLClientError: Si hay un error en la petición
        """
        try:
            response = self.get_request("/sensors", params=self.base_query_params)
            return self._handle_response(response, data_key="sensors", raw_content=raw_content)
        except Exception as e:
            if isinstance(e, UWLClientError):
                raise
            raise UWLClientError(f"Error obteniendo sensores: {str(e)}")
    
    def get_sensor_activity(self, raw_content: bool = False) -> Union[requests.Response, List[Dict]]:
        """
        Obtiene la actividad de los sensores
        
        Args:
            raw_content: Si True, retorna el objeto Response completo
            
        Returns:
            Actividad de sensores o Response completo
            
        Raises:
            UWLClientError: Si hay un error en la petición
        """
        try:
            response = self.get_request("/sensor-activity", params=self.base_query_params)
            return self._handle_response(
                response,
                data_key="sensor_activity",
                raw_content=raw_content
            )
        except Exception as e:
            if isinstance(e, UWLClientError):
                raise
            raise UWLClientError(f"Error obteniendo actividad de sensores: {str(e)}")
    
    def get_sensor_catalog(
        self, 
        sensor_type: Optional[int] = None, 
        raw_content: bool = False
    ) -> Union[requests.Response, List[Dict], Dict, None]:
        """
        Obtiene el catálogo de tipos de sensores
        
        Args:
            sensor_type: ID del tipo de sensor específico (opcional)
            raw_content: Si True, retorna el objeto Response completo
            
        Returns:
            Catálogo completo, sensor específico, o Response completo
            
        Raises:
            UWLClientError: Si hay un error en la petición
        """
        try:
            response = self.get_request("/sensor-catalog", params=self.base_query_params)
            
            if raw_content:
                return response
            
            if response.status_code == 200:
                data = response.json().get("sensor_types", [])
                
                if sensor_type is not None:
                    # Buscar tipo de sensor específico
                    for sensor in data:
                        if sensor.get("sensor_type") == sensor_type:
                            return sensor
                    return None  # No encontrado
                
                return data
            else:
                raise UWLClientError(
                    f"Error {response.status_code}: {response.text}"
                )
        except Exception as e:
            if isinstance(e, UWLClientError):
                raise
            raise UWLClientError(f"Error obteniendo catálogo de sensores: {str(e)}")
    
    def get_historic(
        self,
        station_id: Union[str, int],
        start: datetime.datetime,
        end: datetime.datetime,
        sensors: Union[str, int, List[Union[str, int]]] = "all",
        raw_content: bool = False
    ) -> Union[requests.Response, List[Dict]]:
        """
        Obtiene datos históricos de una estación
        
        Args:
            station_id: ID de la estación
            start: Fecha de inicio
            end: Fecha de fin
            sensors: "all" o lista/int de IDs de sensores específicos
            raw_content: Si True, retorna el objeto Response completo
            
        Returns:
            Lista de registros históricos consolidados o Response completo
            
        Raises:
            UWLClientError: Si hay un error en la petición
            ValueError: Si los parámetros son inválidos
        """
        # Validaciones
        self._validate_date_range(start, end)
        
        try:
            # Preparar parámetros
            start_ts = self._date_to_timestamp(start)
            end_ts = self._date_to_timestamp(end)
            
            query_params = {
                "api-key": self.get_config("api_key"),
                "start-timestamp": start_ts,
                "end-timestamp": end_ts,
            }
            
            # Realizar petición
            response = self.get_request(
                f"/historic/{station_id}", 
                params=query_params
            )
            
            if raw_content:
                return response
            
            if response.status_code != 200:
                raise UWLClientError(
                    f"Error {response.status_code}: {response.text}"
                )
            
            # Procesar datos
            json_data = response.json()
            sensor_list = json_data.get("sensors", [])
            
            # Determinar qué sensores incluir
            if sensors == "all":
                sensor_ids = None  # Incluir todos
            else:
                sensor_ids = self._normalize_sensor_ids(sensors)
            
            # Consolidar datos por timestamp
            sensor_data: Dict[int, Dict] = {}
            
            for sensor in sensor_list:
                lsid = sensor.get("lsid")
                
                # Filtrar por sensor si es necesario
                if sensor_ids is not None and lsid not in sensor_ids:
                    continue
                
                # Agregar datos del sensor
                for record in sensor.get("data", []):
                    ts = record.get("ts")
                    if ts is None:
                        continue
                    
                    if ts in sensor_data:
                        # Actualizar registro existente con nuevos datos
                        sensor_data[ts].update(record)
                    else:
                        # Crear nuevo registro
                        sensor_data[ts] = record.copy()
            
            # Convertir a lista ordenada por timestamp
            result = sorted(sensor_data.values(), key=lambda x: x.get("ts", 0))
            
            return result
            
        except Exception as e:
            if isinstance(e, UWLClientError):
                raise
            raise UWLClientError(f"Error obteniendo datos históricos: {str(e)}")
    
    def get_current(
        self,
        station_id: Union[str, int],
        raw_content: bool = False
    ) -> Union[requests.Response, Dict]:
        """
        Obtiene las condiciones actuales de una estación
        
        Args:
            station_id: ID de la estación
            raw_content: Si True, retorna el objeto Response completo
            
        Returns:
            Datos actuales o Response completo
            
        Raises:
            UWLClientError: Si hay un error en la petición
        """
        try:
            query_params = {
                "api-key": self.get_config("api_key"),
                "station-id": station_id,
            }
            
            response = self.get_request("/current/{station_id}", params=query_params)
            return self._handle_response(response, raw_content=raw_content)
            
        except Exception as e:
            if isinstance(e, UWLClientError):
                raise
            raise UWLClientError(f"Error obteniendo datos actuales: {str(e)}")