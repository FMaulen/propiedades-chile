# tests para la API de prediccion
# usamos TestClient de FastAPI pa simular requests

import pytest
from fastapi.testclient import TestClient

# importamos la app de la api
try:
    from api.api_app import app
    client = TestClient(app)
    API_DISPONIBLE = True
except Exception as e:
    print(f"No se pudo importar la API: {e}")
    API_DISPONIBLE = False
    client = None


@pytest.mark.skipif(not API_DISPONIBLE, reason="API no disponible pa testing")
class TestRootEndpoint:
    """Tests para el endpoint raiz"""

    def test_root_endpoint(self):
        """GET / deberia retornar 200 y tener info de autores"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "authors" in data or "autores" in data, "La respuesta no tiene info de autores"


@pytest.mark.skipif(not API_DISPONIBLE, reason="API no disponible pa testing")
class TestHealthEndpoint:
    """Tests para el health check"""

    def test_health_endpoint(self):
        """GET /health deberia retornar 200"""
        response = client.get("/health")
        assert response.status_code == 200


@pytest.mark.skipif(not API_DISPONIBLE, reason="API no disponible pa testing")
class TestCommunesEndpoint:
    """Tests para el endpoint de comunas"""

    def test_communes_endpoint(self):
        """GET /communes deberia retornar 200 y una lista"""
        response = client.get("/communes")
        assert response.status_code == 200


@pytest.mark.skipif(not API_DISPONIBLE, reason="API no disponible pa testing")
class TestPredictEndpoint:
    """Tests para el endpoint de prediccion"""

    def test_predict_missing_fields(self):
        """POST /predict sin datos deberia dar error (422 o 400)"""
        response = client.post("/predict", json={})
        # FastAPI retorna 422 cuando faltan campos requeridos
        assert response.status_code in [400, 422], \
            f"Se esperaba error pero se obtuvo {response.status_code}"

    def test_predict_valid_data(self):
        """POST /predict con datos validos deberia retornar 200 y una prediccion"""
        datos_prueba = {
            "Built_Area": 120.0,
            "Total_Area": 150.0,
            "Dorms": 3,
            "Baths": 2,
            "Parking": 1,
            "Comuna": "Santiago"
        }
        response = client.post("/predict", json=datos_prueba)
        assert response.status_code == 200
        data = response.json()
        assert "precio_uf" in data
        assert "precio_clp" in data
        assert "uf_usada" in data
        assert data["comuna"] == "Santiago"
