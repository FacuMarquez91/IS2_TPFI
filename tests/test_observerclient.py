"""Pruebas de recepción y reconexión del ObserverClient."""

import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from is2_tpfi.observerclient import listen, main


def test_observerclient_receives_update(
    tmp_path: Path,
) -> None:
    """Verificar la recepción y escritura de una notificación."""
    output = tmp_path / "notificaciones.json"

    messages = [
        {"event": "subscribed", "subscriber_id": "cliente-1"},
        {"event": "heartbeat"},
        {
            "event": "update",
            "data": {"id": "EMPRESA-1", "telefono": "123456"},
        },
    ]

    stream = io.BytesIO(
        b"".join((json.dumps(message) + "\n").encode("utf-8") for message in messages)
    )

    response = MagicMock()
    response.readline.side_effect = [
        stream.readline(),
        stream.readline(),
        stream.readline(),
        b"",
    ]
    response.__enter__.return_value = response

    with (
        patch(
            "is2_tpfi.observerclient.urlopen",
            return_value=response,
        ) as mock_urlopen,
        patch(
            "is2_tpfi.observerclient.time.sleep",
            side_effect=KeyboardInterrupt,
        ),
        pytest.raises(KeyboardInterrupt),
    ):
        listen(
            host="localhost",
            port=8080,
            output=output,
            reconnect_seconds=1,
        )

    saved = output.read_text(encoding="utf-8")
    notification = json.loads(saved)

    assert notification == {
        "id": "EMPRESA-1",
        "telefono": "123456",
    }

    mock_urlopen.assert_called_once()


def test_observerclient_retries_after_connection_error() -> None:
    """Verificar que se espere antes de reconectar."""
    with (
        patch(
            "is2_tpfi.observerclient.urlopen",
            side_effect=ConnectionError("Servidor caído"),
        ),
        patch(
            "is2_tpfi.observerclient.time.sleep",
            side_effect=KeyboardInterrupt,
        ) as mock_sleep,
        pytest.raises(KeyboardInterrupt),
    ):
        listen(
            host="localhost",
            port=8080,
            reconnect_seconds=30,
        )

    mock_sleep.assert_called_once_with(30)


def test_observerclient_rejects_invalid_interval() -> None:
    """Rechazar intervalos de reconexión inválidos."""
    with pytest.raises(ValueError):
        listen(
            host="localhost",
            port=8080,
            reconnect_seconds=0,
        )


def test_observerclient_main_success() -> None:
    """Verificar que main interprete los argumentos."""
    with (
        patch(
            "sys.argv",
            [
                "observerclient",
                "--server",
                "127.0.0.1",
                "--port",
                "9000",
                "--reconnect",
                "15",
                "--verbose",
            ],
        ),
        patch("is2_tpfi.observerclient.listen") as mock_listen,
    ):
        result = main()

    assert result == 0
    mock_listen.assert_called_once_with(
        host="127.0.0.1",
        port=9000,
        output=None,
        reconnect_seconds=15,
    )


def test_observerclient_main_keyboard_interrupt() -> None:
    """Verificar una detención manual del cliente."""
    with (
        patch("sys.argv", ["observerclient"]),
        patch(
            "is2_tpfi.observerclient.listen",
            side_effect=KeyboardInterrupt,
        ),
    ):
        result = main()

    assert result == 0


def test_observerclient_main_invalid_configuration() -> None:
    """Verificar el rechazo de una configuración inválida."""
    with (
        patch(
            "sys.argv",
            ["observerclient", "--reconnect", "0"],
        ),
        patch(
            "is2_tpfi.observerclient.listen",
            side_effect=ValueError("El intervalo debe ser positivo."),
        ),
    ):
        result = main()

    assert result == 1
