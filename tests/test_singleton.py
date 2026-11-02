
"""Pruebas del patrón Singleton."""

from is2_tpfi.patterns.singleton import (
    CorporateDataSingleton,
    CorporateLogSingleton,
)


def test_corporate_data_singleton() -> None:
    """Verificar que CorporateData reutiliza la instancia."""
    first = CorporateDataSingleton()
    second = CorporateDataSingleton()

    assert first is second
    assert first.table_name == "CorporateData"


def test_corporate_log_singleton() -> None:
    """Verificar que CorporateLog reutiliza la instancia."""
    first = CorporateLogSingleton()
    second = CorporateLogSingleton()

    assert first is second
    assert first.table_name == "CorporateLog"


def test_singletons_are_independent() -> None:
    """Verificar que cada gestor utiliza su propia instancia."""
    data = CorporateDataSingleton()
    log = CorporateLogSingleton()

    assert data is not log
