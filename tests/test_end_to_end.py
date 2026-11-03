"""Prueba de integración de suscripciones y actualizaciones HTTP."""

import json
from http.server import ThreadingHTTPServer
from threading import Thread
from unittest.mock import MagicMock, patch
from urllib.request import Request, urlopen

from is2_tpfi.patterns.proxy import CorporateProxy
from is2_tpfi.singletonproxyobserver import (
    CorporateRequestHandler,
    shared_observer,
)


def test_subscriber_receives_set_update() -> None:
    """Verificar que un cliente suscripto reciba un cambio."""
    data = MagicMock()
    log = MagicMock()

    updated = {
        "id": "EMPRESA-1",
        "telefono": "555555",
    }
    data.set.return_value = updated

    proxy = CorporateProxy(
        data_manager=data,
        log_manager=log,
        observer=shared_observer,
    )

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        CorporateRequestHandler,
    )
    server.daemon_threads = True

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}/"

    try:
        with patch(
            "is2_tpfi.singletonproxyobserver.CorporateProxy",
            return_value=proxy,
        ):
            subscribe_request = Request(
                base_url,
                data=json.dumps(
                    {
                        "UUID": "CPU-OBSERVADOR",
                        "ACTION": "subscribe",
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urlopen(
                subscribe_request,
                timeout=5,
            ) as subscription:
                confirmation = json.loads(subscription.readline())
                assert confirmation["event"] == "subscribed"

                set_request = Request(
                    base_url,
                    data=json.dumps(
                        {
                            "UUID": "CPU-CLIENTE",
                            "ACTION": "set",
                            "ID": "EMPRESA-1",
                            "telefono": "555555",
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                with urlopen(set_request, timeout=5) as response:
                    result = json.load(response)

                assert result == updated

                notification = json.loads(subscription.readline())

                assert notification == {
                    "event": "update",
                    "data": updated,
                }

        data.set.assert_called_once_with(
            "EMPRESA-1",
            {"telefono": "555555"},
        )
        assert log.save.call_count == 2

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
