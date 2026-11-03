"""Pruebas de integración HTTP del servidor corporativo."""

import json
from http.server import ThreadingHTTPServer
from threading import Thread
from unittest.mock import MagicMock, patch
from urllib.request import Request, urlopen

import pytest

from is2_tpfi.singletonproxyobserver import CorporateRequestHandler


def test_server_get() -> None:
    """Comprobar una solicitud HTTP POST utilizando un Proxy simulado."""
    proxy = MagicMock()
    proxy.process.return_value = {
        "id": "EMPRESA-1",
        "telefono": "123456",
    }

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        CorporateRequestHandler,
    )

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with patch(
            "is2_tpfi.singletonproxyobserver.CorporateProxy",
            return_value=proxy,
        ):
            payload = {
                "UUID": "CPU-PRUEBA",
                "ACTION": "get",
                "ID": "EMPRESA-1",
            }

            request = Request(
                f"http://127.0.0.1:{server.server_port}/",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urlopen(request, timeout=5) as response:
                result = json.load(response)

        assert result == {
            "id": "EMPRESA-1",
            "telefono": "123456",
        }

        proxy.process.assert_called_once_with(payload)

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_server_subscribe_receives_notification() -> None:
    """Comprobar una suscripción HTTP y una notificación real."""
    from threading import Event
    from urllib.request import Request, urlopen

    from is2_tpfi.singletonproxyobserver import shared_observer

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        CorporateRequestHandler,
    )
    server.daemon_threads = True

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    event_received = Event()

    try:
        with patch("is2_tpfi.singletonproxyobserver.CorporateProxy") as proxy_class:
            payload = {
                "UUID": "CPU-PRUEBA",
                "ACTION": "subscribe",
            }

            request = Request(
                f"http://127.0.0.1:{server.server_port}/",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urlopen(request, timeout=5) as response:
                subscribed = json.loads(response.readline())

                assert subscribed["event"] == "subscribed"

                notification = {
                    "id": "EMPRESA-1",
                    "telefono": "123456",
                }

                shared_observer.notify(notification)

                received = json.loads(response.readline())

                assert received == {
                    "event": "update",
                    "data": notification,
                }

                event_received.set()

            proxy_class.return_value._audit.assert_called_once()

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert event_received.is_set()


@pytest.mark.parametrize(
    ("path", "payload", "expected_status"),
    [
        ("/incorrecta", b"{}", 404),
        ("/", b"", 400),
        ("/", b"{json incorrecto", 400),
        ("/", b"[]", 400),
        ("/", b'{"ACTION":"delete","UUID":"CPU-1"}', 400),
    ],
)
def test_server_rejects_invalid_requests(
    path: str,
    payload: bytes,
    expected_status: int,
) -> None:
    """Comprobar las validaciones HTTP del servidor."""
    from urllib.error import HTTPError

    import pytest

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        CorporateRequestHandler,
    )
    server.daemon_threads = True

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with patch("is2_tpfi.singletonproxyobserver.CorporateProxy") as proxy_class:
            proxy_class.return_value.process.return_value = {
                "Error": "Acción no válida"
            }

            request = Request(
                f"http://127.0.0.1:{server.server_port}{path}",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with pytest.raises(HTTPError) as captured:
                urlopen(request, timeout=5)

            assert captured.value.code == expected_status

            result = json.loads(captured.value.read())
            assert "Error" in result

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_server_handles_internal_error() -> None:
    """Comprobar que una excepción interna genere HTTP 500."""
    from urllib.error import HTTPError

    import pytest

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        CorporateRequestHandler,
    )
    server.daemon_threads = True

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with patch(
            "is2_tpfi.singletonproxyobserver.CorporateProxy",
            side_effect=RuntimeError("Error simulado"),
        ):
            request = Request(
                f"http://127.0.0.1:{server.server_port}/",
                data=b'{"UUID":"CPU-1","ACTION":"list"}',
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with pytest.raises(HTTPError) as captured:
                urlopen(request, timeout=5)

            assert captured.value.code == 500

            result = json.loads(captured.value.read())
            assert result == {"Error": "Error interno del servidor"}

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_server_set_notifies_subscribers() -> None:
    """Verificar que set notifique a un observador mediante HTTP."""
    from unittest.mock import MagicMock

    from is2_tpfi.patterns.observer import CorporateObserver

    observer = CorporateObserver()
    received: list[dict[str, object]] = []

    observer.subscribe(
        "cliente-prueba",
        lambda event: received.append(event),
    )

    data = MagicMock()
    log = MagicMock()

    updated = {
        "id": "EMPRESA-1",
        "telefono": "999999",
    }
    data.set.return_value = updated

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        CorporateRequestHandler,
    )
    server.daemon_threads = True

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        from is2_tpfi.patterns.proxy import CorporateProxy

        proxy = CorporateProxy(data, log, observer)

        with patch(
            "is2_tpfi.singletonproxyobserver.CorporateProxy",
            return_value=proxy,
        ):
            payload = {
                "UUID": "CPU-PRUEBA",
                "ACTION": "set",
                "ID": "EMPRESA-1",
                "telefono": "999999",
            }

            request = Request(
                f"http://127.0.0.1:{server.server_port}/",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urlopen(request, timeout=5) as response:
                result = json.load(response)

        assert result == updated
        assert received == [updated]

        data.set.assert_called_once_with(
            "EMPRESA-1",
            {"telefono": "999999"},
        )
        log.save.assert_called_once()

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
