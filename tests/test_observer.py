"""Pruebas unitarias del patrón Observer."""

from unittest.mock import MagicMock

import pytest

from is2_tpfi.patterns.observer import CorporateObserver


def test_subscribe() -> None:
    """Verificar el registro de un observador."""
    observer = CorporateObserver()
    callback = MagicMock()

    observer.subscribe("cliente-1", callback)

    assert observer.subscriber_count() == 1


def test_notify() -> None:
    """Verificar que los observadores reciban notificaciones."""
    observer = CorporateObserver()
    first = MagicMock()
    second = MagicMock()

    observer.subscribe("cliente-1", first)
    observer.subscribe("cliente-2", second)

    data = {"id": "EMPRESA-1", "telefono": "123456"}
    observer.notify(data)

    first.assert_called_once_with(data)
    second.assert_called_once_with(data)


def test_unsubscribe() -> None:
    """Verificar que se elimine un suscriptor."""
    observer = CorporateObserver()
    callback = MagicMock()

    observer.subscribe("cliente-1", callback)
    observer.unsubscribe("cliente-1")
    observer.notify({"id": "EMPRESA-1"})

    callback.assert_not_called()
    assert observer.subscriber_count() == 0


def test_duplicate_subscription() -> None:
    """Verificar que un identificador reemplace su callback."""
    observer = CorporateObserver()
    first = MagicMock()
    second = MagicMock()

    observer.subscribe("cliente-1", first)
    observer.subscribe("cliente-1", second)
    observer.notify({"id": "EMPRESA-1"})

    assert observer.subscriber_count() == 1
    first.assert_not_called()
    second.assert_called_once()


def test_invalid_subscriber() -> None:
    """Rechazar identificadores vacíos."""
    observer = CorporateObserver()

    with pytest.raises(ValueError):
        observer.subscribe("", MagicMock())


def test_disconnected_subscriber() -> None:
    """Eliminar un observador cuya conexión falla."""
    observer = CorporateObserver()
    callback = MagicMock(side_effect=ConnectionError("Sin conexión"))

    observer.subscribe("cliente-1", callback)
    observer.notify({"id": "EMPRESA-1"})

    assert observer.subscriber_count() == 0
