import pytest

@pytest.mark.parametrize(
    "rota, status_esperado",
    [
        ("/", 200),
        ("/assets/css/variables.css", 200),
        ("/assets/css/layout.css", 200),
        ("/assets/css/modals.css", 200),
        ("/assets/js/main.js", 200),
        ("/assets/js/api.js", 200),
        ("/assets/js/ui.js", 200),
        ("/assets/images/logo-tv-full.jpeg", 200),
        ("/assets/images/logo-taciana-variedades.jpeg", 200),
        ("/assets/css/inexistente.css", 404),
    ]
)
def test_entrega_arquivos_interface(client, rota, status_esperado):
    response = client.get(rota)
    assert response.status_code == status_esperado
    response.close()
    