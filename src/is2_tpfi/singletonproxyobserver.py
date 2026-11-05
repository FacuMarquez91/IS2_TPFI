"""Servidor HTTP/TCP con soporte para el patrón Observer."""

import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Empty, Full, Queue
from typing import Any
from uuid import uuid4

from is2_tpfi.patterns.observer import CorporateObserver
from is2_tpfi.patterns.proxy import CorporateProxy

logger = logging.getLogger(__name__)

MAX_REQUEST_BYTES = 1024 * 1024

# Un único registro de suscriptores para todas las conexiones.
shared_observer = CorporateObserver()


class CorporateRequestHandler(BaseHTTPRequestHandler):
    """Recibir operaciones JSON mediante HTTP sobre TCP."""

    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        """Procesar una solicitud POST."""
        if self.path != "/":
            self.send_json({"Error": "Ruta no encontrada"}, 404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))

            if not 0 < content_length <= MAX_REQUEST_BYTES:
                self.send_json(
                    {"Error": "Tamaño de solicitud inválido"},
                    400,
                )
                return

            content = self.rfile.read(content_length)
            request = json.loads(content)

            if not isinstance(request, dict):
                self.send_json(
                    {"Error": "Se espera un objeto JSON"},
                    400,
                )
                return

            if request.get("ACTION") == "subscribe":
                self.handle_subscribe(request)
                return

            proxy = CorporateProxy(observer=shared_observer)
            response = proxy.process(request)

            status = 400 if isinstance(response, dict) and "Error" in response else 200

            # Registrar errores y operaciones SET exitosas.
            if isinstance(response, dict) and "Error" in response:
                error_message = str(response["Error"])

                if (
                    request.get("ACTION") == "get"
                    and error_message == "Registro no encontrado"
                ):
                    logger.error(
                        "ERROR: Registro inexistente. ID solicitado: %s",
                        request.get("ID"),
                    )
                else:
                    logger.warning(
                        "Solicitud rechazada: %s",
                        error_message,
                    )

            elif request.get("ACTION") == "set":
                logger.info(
                    "Registro creado o actualizado correctamente "
                    "en CorporateData. ID: %s",
                    request.get("ID"),
                )

            self.send_json(response, status)

        except (ValueError, UnicodeDecodeError):
            self.send_json(
                {"Error": "Solicitud JSON inválida"},
                400,
            )
        except (OSError, ConnectionError):
            logger.warning("Conexión interrumpida")
            self.close_connection = True
        except Exception:
            logger.exception("Error al procesar la solicitud")
            try:
                self.send_json(
                    {"Error": "Error interno del servidor"},
                    500,
                )
            except OSError:
                self.close_connection = True

    def handle_subscribe(self, request: dict[str, Any]) -> None:
        """Mantener abierta la conexión de un observador."""
        cpu_uuid = request.get("UUID")

        if not isinstance(cpu_uuid, str) or not cpu_uuid.strip():
            self.send_json({"Error": "UUID obligatorio"}, 400)
            return

        subscriber_id = str(uuid4())
        notifications: Queue[dict[str, Any]] = Queue(maxsize=100)

        def enqueue(data: dict[str, Any]) -> None:
            """Encolar un evento sin bloquear al emisor."""
            try:
                notifications.put_nowait(data)
            except Full as error:
                raise ConnectionError("Cola de notificaciones llena") from error

        # Registrar la solicitud antes de confirmar la suscripción.
        proxy = CorporateProxy(observer=shared_observer)
        proxy._audit(cpu_uuid, "subscribe", None)

        shared_observer.subscribe(subscriber_id, enqueue)

        try:
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/x-ndjson; charset=utf-8",
            )
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()

            self.close_connection = True

            self.write_event(
                {
                    "event": "subscribed",
                    "subscriber_id": subscriber_id,
                }
            )

            while True:
                try:
                    event = notifications.get(timeout=10)
                    self.write_event({"event": "update", "data": event})
                except Empty:
                    self.write_event({"event": "heartbeat"})

        except (OSError, ConnectionError):
            logger.info(
                "Suscriptor desconectado: %s",
                subscriber_id,
            )
        finally:
            shared_observer.unsubscribe(subscriber_id)
            self.close_connection = True

    def write_event(self, data: dict[str, Any]) -> None:
        """Enviar una línea JSON por la conexión abierta."""
        payload = (json.dumps(data, ensure_ascii=False, default=str) + "\n").encode(
            "utf-8"
        )

        self.wfile.write(payload)
        self.wfile.flush()

    def send_json(
        self,
        data: dict[str, Any] | list[dict[str, Any]],
        status: int,
    ) -> None:
        """Responder una solicitud HTTP convencional."""
        payload = json.dumps(
            data,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        self.wfile.write(payload)


def main() -> None:
    """Iniciar el servidor corporativo."""
    parser = argparse.ArgumentParser(description="Servidor corporativo IS2 TPFI")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    server = ThreadingHTTPServer(
        ("127.0.0.1", args.port),
        CorporateRequestHandler,
    )
    server.daemon_threads = True

    logger.warning(
        "Servidor escuchando en puerto %s",
        args.port,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.warning("Servidor detenido manualmente")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
