"""Proxy para procesar solicitudes de datos corporativos."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from is2_tpfi.patterns.singleton import (
    CorporateDataSingleton,
    CorporateLogSingleton,
)


class CorporateProxy:
    """Controlar el acceso a los datos corporativos."""

    def __init__(
        self,
        data_manager: CorporateDataSingleton | None = None,
        log_manager: CorporateLogSingleton | None = None,
    ) -> None:
        """Preparar los gestores de datos y auditoría."""
        self.data_manager = (
            data_manager if data_manager is not None else CorporateDataSingleton()
        )
        self.log_manager = (
            log_manager if log_manager is not None else CorporateLogSingleton()
        )

    def process(self, request: dict[str, Any]) -> dict[str, Any] | list[dict[str, Any]]:
        """Procesar una solicitud get, set o list."""
        action = request.get("ACTION")
        cpu_uuid = request.get("UUID")
        record_id = request.get("ID")

        if action not in ("get", "set", "list"):
            return {"Error": "Acción no válida"}

        if not isinstance(cpu_uuid, str) or not cpu_uuid.strip():
            return {"Error": "UUID obligatorio"}

        if action in ("get", "set"):
            if not isinstance(record_id, str) or not record_id.strip():
                return {"Error": "ID obligatorio"}

        try:
            if action == "get":
                if not isinstance(record_id, str):
                    return {"Error": "ID obligatorio"}

                result_get = self.data_manager.get(record_id)
                self._audit(cpu_uuid, action, record_id)

                if result_get is None:
                    return {"Error": "Registro no encontrado"}

                return result_get

            if action == "list":
                result_list = self.data_manager.list_all()
                self._audit(cpu_uuid, action, None)
                return result_list

            if not isinstance(record_id, str):
                return {"Error": "ID obligatorio"}

            data = request.get("DATA", {})

            if not isinstance(data, dict):
                return {"Error": "DATA debe ser un objeto JSON"}

            result_set = self.data_manager.set(record_id, data)
            self._audit(cpu_uuid, action, record_id)
            return result_set

        except (ValueError, TypeError) as error:
            return {"Error": str(error)}

    def _audit(
        self,
        cpu_uuid: str,
        action: str,
        record_id: str | None,
    ) -> None:
        """Registrar la operación en CorporateLog."""
        entry = {
            "id": str(uuid4()),
            "UUID": cpu_uuid,
            "session": str(uuid4()),
            "ACTION": action,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if record_id is not None:
            entry["ID"] = record_id

        self.log_manager.save(entry)
