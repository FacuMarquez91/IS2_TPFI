"""Pruebas unitarias del patrón Proxy."""

from unittest.mock import MagicMock

from is2_tpfi.patterns.proxy import CorporateProxy


def test_proxy_get() -> None:
    """Verificar la consulta de un registro."""
    data = MagicMock()
    log = MagicMock()
    data.get.return_value = {"id": "EMPRESA-1"}

    proxy = CorporateProxy(data, log)

    result = proxy.process({"UUID": "CPU-1", "ID": "EMPRESA-1", "ACTION": "get"})

    assert result == {"id": "EMPRESA-1"}
    data.get.assert_called_once_with("EMPRESA-1")
    log.save.assert_called_once()


def test_proxy_list() -> None:
    """Verificar la recuperación de registros."""
    data = MagicMock()
    log = MagicMock()
    data.list_all.return_value = [{"id": "EMPRESA-1"}]

    proxy = CorporateProxy(data, log)

    result = proxy.process({"UUID": "CPU-1", "ACTION": "list"})

    assert result == [{"id": "EMPRESA-1"}]
    data.list_all.assert_called_once()
    log.save.assert_called_once()


def test_proxy_set() -> None:
    """Verificar una actualización de datos."""
    data = MagicMock()
    log = MagicMock()
    data.set.return_value = {
        "id": "EMPRESA-1",
        "telefono": "123456",
    }

    proxy = CorporateProxy(data, log)

    result = proxy.process(
        {
            "UUID": "CPU-1",
            "ID": "EMPRESA-1",
            "ACTION": "set",
            "telefono": "123456",
        }
    )

    assert isinstance(result, dict)
    assert result["telefono"] == "123456"

    data.set.assert_called_once_with(
        "EMPRESA-1",
        {"telefono": "123456"},
    )
    log.save.assert_called_once()


def test_proxy_invalid_action() -> None:
    """Rechazar acciones desconocidas y registrar el intento."""
    data = MagicMock()
    log = MagicMock()

    proxy = CorporateProxy(data, log)

    result = proxy.process(
        {
            "UUID": "CPU-1",
            "ACTION": "delete",
        }
    )

    assert result == {"Error": "Acción no válida"}

    # No debe realizar ninguna operación sobre CorporateData.
    data.get.assert_not_called()
    data.set.assert_not_called()
    data.list_all.assert_not_called()

    # La solicitud rechazada sí debe registrarse en CorporateLog.
    log.save.assert_called_once()

    entry = log.save.call_args.args[0]

    assert entry["UUID"] == "CPU-1"
    assert entry["ACTION"] == "delete"
    assert "timestamp" in entry
    assert "session" in entry


def test_proxy_missing_uuid() -> None:
    """Rechazar una solicitud sin UUID."""
    proxy = CorporateProxy(MagicMock(), MagicMock())

    result = proxy.process({"ACTION": "list"})

    assert result == {"Error": "UUID obligatorio"}


def test_proxy_missing_id() -> None:
    """Rechazar consultas sin identificador."""
    proxy = CorporateProxy(MagicMock(), MagicMock())

    result = proxy.process({"UUID": "CPU-1", "ACTION": "get"})

    assert result == {"Error": "ID obligatorio"}


def test_proxy_set_notifies_observers() -> None:
    """Verificar que set notifique el registro actualizado."""
    data = MagicMock()
    log = MagicMock()
    observer = MagicMock()

    updated = {
        "id": "EMPRESA-1",
        "telefono": "123456",
    }
    data.set.return_value = updated

    proxy = CorporateProxy(data, log, observer)

    result = proxy.process(
        {
            "UUID": "CPU-1",
            "ID": "EMPRESA-1",
            "ACTION": "set",
            "telefono": "123456",
        }
    )

    assert result == updated
    data.set.assert_called_once_with(
        "EMPRESA-1",
        {"telefono": "123456"},
    )
    log.save.assert_called_once()
    observer.notify.assert_called_once_with(updated)


def test_proxy_get_does_not_notify() -> None:
    """Verificar que una consulta no genere notificaciones."""
    data = MagicMock()
    log = MagicMock()
    observer = MagicMock()

    data.get.return_value = {"id": "EMPRESA-1"}

    proxy = CorporateProxy(data, log, observer)

    proxy.process(
        {
            "UUID": "CPU-1",
            "ID": "EMPRESA-1",
            "ACTION": "get",
        }
    )

    observer.notify.assert_not_called()


def test_proxy_list_does_not_notify() -> None:
    """Verificar que un listado no genere notificaciones."""
    data = MagicMock()
    log = MagicMock()
    observer = MagicMock()

    data.list_all.return_value = [{"id": "EMPRESA-1"}]

    proxy = CorporateProxy(data, log, observer)

    proxy.process(
        {
            "UUID": "CPU-1",
            "ACTION": "list",
        }
    )

    observer.notify.assert_not_called()


def test_proxy_audit_contains_required_fields() -> None:
    """Verificar los datos mínimos del registro de auditoría."""
    data = MagicMock()
    log = MagicMock()
    observer = MagicMock()

    data.get.return_value = {"id": "EMPRESA-1"}

    proxy = CorporateProxy(data, log, observer)

    proxy.process(
        {
            "UUID": "CPU-123",
            "ACTION": "get",
            "ID": "EMPRESA-1",
        }
    )

    log.save.assert_called_once()

    entry = log.save.call_args.args[0]

    assert entry["UUID"] == "CPU-123"
    assert entry["ACTION"] == "get"
    assert entry["ID"] == "EMPRESA-1"
    assert isinstance(entry["id"], str)
    assert isinstance(entry["session"], str)
    assert isinstance(entry["timestamp"], str)


def test_proxy_audits_rejected_action() -> None:
    """Verificar la auditoría de una acción no permitida."""
    data = MagicMock()
    log = MagicMock()
    observer = MagicMock()

    proxy = CorporateProxy(data, log, observer)

    result = proxy.process(
        {
            "UUID": "CPU-123",
            "ACTION": "delete",
            "ID": "EMPRESA-1",
        }
    )

    assert result == {"Error": "Acción no válida"}

    log.save.assert_called_once()

    entry = log.save.call_args.args[0]

    assert entry["UUID"] == "CPU-123"
    assert entry["ACTION"] == "delete"
    assert entry["ID"] == "EMPRESA-1"
