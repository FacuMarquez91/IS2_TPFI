"""Cliente Observer con recepción continua y reconexión automática."""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPHandler, Request, build_opener
from uuid import getnode

logger = logging.getLogger(__name__)


def listen(
    host: str,
    port: int,
    output: Path | None = None,
    reconnect_seconds: int = 30,
) -> None:
    """Escuchar notificaciones y reconectarse si se pierde la conexión."""
    if reconnect_seconds < 1:
        raise ValueError("El intervalo de reconexión debe ser positivo.")

    url = f"http://{host}:{port}/"

    # Permitir exclusivamente protocolos HTTP o HTTPS.
    if urlsplit(url).scheme not in {"http", "https"}:
        raise ValueError("Esquema de URL no permitido.")

    payload = {
        "UUID": str(getnode()),
        "ACTION": "subscribe",
    }

    # Crear el mecanismo encargado de abrir conexiones HTTP.
    opener = build_opener(HTTPHandler())

    while True:
        try:
            request = Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            logger.info("Conectando a %s", url)

            with opener.open(request, timeout=35) as response:
                logger.info("Conexión establecida")

                while True:
                    line = response.readline()

                    if not line:
                        raise ConnectionError("El servidor cerró la conexión.")

                    message: Any = json.loads(line)

                    if not isinstance(message, dict):
                        logger.warning("Mensaje inesperado")
                        continue

                    event = message.get("event")

                    if event == "heartbeat":
                        logger.debug("Conexión activa")
                        continue

                    if event == "subscribed":
                        logger.info(
                            "Suscripción registrada: %s",
                            message.get("subscriber_id"),
                        )
                        continue

                    if event == "update":
                        text = json.dumps(
                            message.get("data"),
                            ensure_ascii=False,
                            indent=4,
                        )

                        print(text, flush=True)

                        if output is not None:
                            with output.open(
                                "a",
                                encoding="utf-8",
                            ) as file:
                                file.write(text + "\n")

                    else:
                        logger.warning(
                            "Evento desconocido: %s",
                            event,
                        )

        except (
            HTTPError,
            URLError,
            OSError,
            ConnectionError,
            ValueError,
        ) as error:
            logger.warning("Conexión interrumpida: %s", error)
            logger.info(
                "Reintentando en %s segundos",
                reconnect_seconds,
            )
            time.sleep(reconnect_seconds)


def main() -> int:
    """Leer la configuración e iniciar el cliente Observer."""
    parser = argparse.ArgumentParser(description="Cliente Observer IS2 TPFI")

    parser.add_argument(
        "-s",
        "--server",
        default="localhost",
        help="Dirección del servidor",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="Puerto del servidor",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Archivo donde guardar las notificaciones",
    )
    parser.add_argument(
        "-r",
        "--reconnect",
        type=int,
        default=30,
        help="Segundos entre intentos de reconexión",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Mostrar mensajes de diagnóstico",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        listen(
            host=args.server,
            port=args.port,
            output=Path(args.output) if args.output else None,
            reconnect_seconds=args.reconnect,
        )
    except KeyboardInterrupt:
        logger.info("Cliente detenido manualmente")
        return 0
    except ValueError as error:
        logger.error("%s", error)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
