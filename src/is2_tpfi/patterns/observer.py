"""Implementación del patrón Observer para datos corporativos."""

import logging
from collections.abc import Callable
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

NotificationCallback = Callable[[dict[str, Any]], None]


class CorporateObserver:
    """Administrar suscripciones y notificaciones corporativas."""

    def __init__(self) -> None:
        """Inicializar el registro de observadores."""
        self._subscribers: dict[str, NotificationCallback] = {}
        self._lock = Lock()

    def subscribe(
        self,
        subscriber_id: str,
        callback: NotificationCallback,
    ) -> None:
        """Registrar un cliente para recibir notificaciones."""
        if not subscriber_id.strip():
            raise ValueError("El identificador es obligatorio.")

        with self._lock:
            self._subscribers[subscriber_id] = callback

    def unsubscribe(self, subscriber_id: str) -> None:
        """Eliminar un cliente del registro de suscriptores."""
        with self._lock:
            self._subscribers.pop(subscriber_id, None)

    def notify(self, data: dict[str, Any]) -> None:
        """Notificar a todos los clientes registrados."""
        with self._lock:
            subscribers = list(self._subscribers.items())

        for subscriber_id, callback in subscribers:
            try:
                callback(data)
            except (OSError, ConnectionError):
                logger.warning(
                    "Suscriptor desconectado: %s",
                    subscriber_id,
                )
                self.unsubscribe(subscriber_id)

    def subscriber_count(self) -> int:
        """Devolver la cantidad de suscriptores registrados."""
        with self._lock:
            return len(self._subscribers)
