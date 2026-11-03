"""Pruebas de los gestores DynamoDB sin utilizar AWS real."""

from unittest.mock import MagicMock

import pytest

from is2_tpfi.patterns.singleton import (
    CorporateDataSingleton,
    CorporateLogSingleton,
)


@pytest.fixture
def data_table(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Reemplazar la tabla real por una simulada."""
    table = MagicMock()
    manager = CorporateDataSingleton()
    monkeypatch.setattr(manager, "table", table)
    return table


@pytest.fixture
def log_table(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Reemplazar la tabla de auditoría por una simulada."""
    table = MagicMock()
    manager = CorporateLogSingleton()
    monkeypatch.setattr(manager, "table", table)
    return table


def test_get_existing_record(data_table: MagicMock) -> None:
    """Comprobar la recuperación de un registro existente."""
    record = {"id": "EMPRESA-1", "telefono": "123456"}

    data_table.get_item.return_value = {"Item": record}

    result = CorporateDataSingleton().get("EMPRESA-1")

    assert result == record
    data_table.get_item.assert_called_once_with(Key={"id": "EMPRESA-1"})


def test_get_missing_record(data_table: MagicMock) -> None:
    """Comprobar el resultado cuando un registro no existe."""
    data_table.get_item.return_value = {}

    result = CorporateDataSingleton().get("NO-EXISTE")

    assert result is None


def test_list_all_with_pagination(data_table: MagicMock) -> None:
    """Comprobar que se recuperan todas las páginas."""
    data_table.scan.side_effect = [
        {
            "Items": [{"id": "EMPRESA-1"}],
            "LastEvaluatedKey": {"id": "EMPRESA-1"},
        },
        {
            "Items": [{"id": "EMPRESA-2"}],
        },
    ]

    result = CorporateDataSingleton().list_all()

    assert len(result) == 2
    assert data_table.scan.call_count == 2
    data_table.scan.assert_any_call(ExclusiveStartKey={"id": "EMPRESA-1"})


def test_set_updates_record(data_table: MagicMock) -> None:
    """Comprobar la actualización de un atributo."""
    updated = {"id": "EMPRESA-1", "telefono": "654321"}
    data_table.update_item.return_value = {"Attributes": updated}

    result = CorporateDataSingleton().set(
        "EMPRESA-1",
        {"telefono": "654321"},
    )

    assert result == updated
    data_table.update_item.assert_called_once()


def test_set_rejects_empty_id(data_table: MagicMock) -> None:
    """Rechazar actualizaciones sin identificador."""
    with pytest.raises(ValueError):
        CorporateDataSingleton().set(
            "",
            {"telefono": "123456"},
        )

    data_table.update_item.assert_not_called()


def test_set_rejects_empty_data(data_table: MagicMock) -> None:
    """Rechazar actualizaciones sin atributos."""
    with pytest.raises(ValueError):
        CorporateDataSingleton().set("EMPRESA-1", {})

    data_table.update_item.assert_not_called()


def test_save_audit_log(log_table: MagicMock) -> None:
    """Comprobar la escritura de un registro de auditoría."""
    entry = {
        "id": "LOG-001",
        "UUID": "CPU-123",
        "ACTION": "get",
    }

    CorporateLogSingleton().save(entry)

    log_table.put_item.assert_called_once_with(Item=entry)


def test_save_requires_id(log_table: MagicMock) -> None:
    """Rechazar una auditoría sin identificador."""
    with pytest.raises(ValueError):
        CorporateLogSingleton().save({"ACTION": "get"})

    log_table.put_item.assert_not_called()


def test_set_preserves_unspecified_fields() -> None:
    """Comprobar que una actualización no borre otros atributos."""
    from unittest.mock import MagicMock

    from is2_tpfi.patterns.singleton import CorporateDataSingleton

    manager = CorporateDataSingleton()
    original_table = manager.table

    fake_table = MagicMock()
    fake_table.update_item.return_value = {
        "Attributes": {
            "id": "EMPRESA-1",
            "telefono": "999999",
            "domicilio": "CALLE ORIGINAL",
        }
    }

    try:
        manager.table = fake_table

        result = manager.set(
            "EMPRESA-1",
            {"telefono": "999999"},
        )

        assert result["telefono"] == "999999"
        assert result["domicilio"] == "CALLE ORIGINAL"

        arguments = fake_table.update_item.call_args.kwargs
        expression = arguments["UpdateExpression"]

        assert "SET" in expression
        assert arguments["Key"] == {"id": "EMPRESA-1"}
    finally:
        manager.table = original_table


def test_set_initializes_missing_fields() -> None:
    """Comprobar que set prepare atributos faltantes en blanco."""
    from unittest.mock import MagicMock

    from is2_tpfi.patterns.singleton import CorporateDataSingleton

    manager = CorporateDataSingleton()
    original_table = manager.table

    fake_table = MagicMock()
    fake_table.update_item.return_value = {
        "Attributes": {
            "id": "EMPRESA-NUEVA",
            "telefono": "123456",
            "domicilio": "",
        }
    }

    try:
        manager.table = fake_table

        manager.set(
            "EMPRESA-NUEVA",
            {"telefono": "123456"},
        )

        arguments = fake_table.update_item.call_args.kwargs
        expression = arguments["UpdateExpression"]

        assert "if_not_exists" in expression
    finally:
        manager.table = original_table
