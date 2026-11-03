"""Cliente HTTP/TCP para operaciones corporativas."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPHandler, Request, build_opener

logger = logging.getLogger(__name__)


def send_request(
    host: str,
    port: int,
    payload: dict[str, Any],
) -> dict[str, Any] | list[Any]:
    """Enviar una solicitud JSON mediante HTTP POST."""
    url = f"http://{host}:{port}/"

    # Comprobar que la URL utiliza un esquema permitido.
    if urlsplit(url).scheme not in {"http", "https"}:
        raise ValueError("Esquema de URL no permitido.")

    body = json.dumps(payload).encode("utf-8")

    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    # Utilizar un manejador HTTP explícito.
    opener = build_opener(HTTPHandler())

    with opener.open(request, timeout=10) as response:
        result: dict[str, Any] | list[Any] = json.load(response)

    return result


def main() -> int:
    """Leer argumentos, enviar solicitud y mostrar respuesta."""
    parser = argparse.ArgumentParser(description="Cliente corporativo IS2 TPFI")

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Archivo JSON de solicitud",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Archivo JSON de respuesta",
    )
    parser.add_argument(
        "-s",
        "--server",
        default="localhost",
        help="Servidor de aplicaciones",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="Puerto TCP",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Activar mensajes de diagnóstico",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    try:
        with Path(args.input).open(encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, dict):
            raise ValueError("La solicitud debe ser un objeto JSON.")

        result = send_request(
            args.server,
            args.port,
            payload,
        )

        output_text = json.dumps(
            result,
            ensure_ascii=False,
            indent=4,
        )

        print(output_text)

        if args.output:
            Path(args.output).write_text(
                output_text,
                encoding="utf-8",
            )

        return 0

    except (OSError, ValueError, HTTPError, URLError) as error:
        logger.error(
            "Error en SingletonClient: %s",
            error,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
