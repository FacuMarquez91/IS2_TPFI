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
            "DATA": {"telefono": "123456"},
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
    """Rechazar acciones desconocidas."""
    data = MagicMock()
    log = MagicMock()
    proxy = CorporateProxy(data, log)

    result = proxy.process({"UUID": "CPU-1", "ACTION": "delete"})

    assert result == {"Error": "Acción no válida"}
    data.get.assert_not_called()
    log.save.assert_not_called()


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
