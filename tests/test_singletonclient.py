"""Pruebas del cliente de operaciones corporativas."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from is2_tpfi.singletonclient import main, send_request


def test_send_request_success() -> None:
    """Verificar el envío de una solicitud HTTP POST."""
    response = MagicMock()
    response.read.return_value = b'{"id": "EMPRESA-1"}'
    response.__enter__.return_value = response

    opener = MagicMock()
    opener.open.return_value = response

    with patch(
        "is2_tpfi.singletonclient.build_opener",
        return_value=opener,
    ) as mock_build_opener:
        result = send_request(
            "localhost",
            8080,
            {
                "UUID": "CPU-1",
                "ACTION": "get",
                "ID": "EMPRESA-1",
            },
        )

    assert result == {"id": "EMPRESA-1"}

    mock_build_opener.assert_called_once()
    opener.open.assert_called_once()

    request = opener.open.call_args.args[0]

    assert request.get_method() == "POST"
    assert request.full_url == "http://localhost:8080/"

    sent_data = json.loads(request.data)
    assert sent_data["ACTION"] == "get"


def test_main_success(tmp_path: Path) -> None:
    """Verificar la lectura y escritura de archivos JSON."""
    input_file = tmp_path / "entrada.json"
    output_file = tmp_path / "salida.json"

    input_file.write_text(
        json.dumps(
            {
                "UUID": "CPU-1",
                "ACTION": "list",
            }
        ),
        encoding="utf-8",
    )

    with (
        patch(
            "sys.argv",
            [
                "singletonclient",
                "-i",
                str(input_file),
                "-o",
                str(output_file),
            ],
        ),
        patch(
            "is2_tpfi.singletonclient.send_request",
            return_value=[{"id": "EMPRESA-1"}],
        ),
    ):
        status = main()

    assert status == 0

    result = json.loads(output_file.read_text(encoding="utf-8"))
    assert result == [{"id": "EMPRESA-1"}]


def test_main_invalid_json(tmp_path: Path) -> None:
    """Verificar el rechazo de archivos JSON inválidos."""
    input_file = tmp_path / "invalido.json"
    input_file.write_text("{incorrecto", encoding="utf-8")

    with patch(
        "sys.argv",
        ["singletonclient", "-i", str(input_file)],
    ):
        status = main()

    assert status == 1


def test_main_invalid_structure(tmp_path: Path) -> None:
    """Rechazar una solicitud que no sea un objeto JSON."""
    input_file = tmp_path / "lista.json"
    input_file.write_text("[]", encoding="utf-8")

    with patch(
        "sys.argv",
        ["singletonclient", "-i", str(input_file)],
    ):
        status = main()

    assert status == 1


def test_main_server_unavailable(tmp_path: Path) -> None:
    """Verificar el error cuando el servidor está caído."""
    input_file = tmp_path / "entrada.json"
    input_file.write_text(
        '{"UUID": "CPU-1", "ACTION": "list"}',
        encoding="utf-8",
    )

    with (
        patch(
            "sys.argv",
            ["singletonclient", "-i", str(input_file)],
        ),
        patch(
            "is2_tpfi.singletonclient.send_request",
            side_effect=URLError("Servidor no disponible"),
        ),
    ):
        status = main()

    assert status == 1
