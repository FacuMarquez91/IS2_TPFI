"""Gestores Singleton para las tablas corporativas de DynamoDB."""

from threading import Lock
from typing import Any

import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource


class SingletonMeta(type):
    """Mantener una instancia por cada clase gestionada."""

    _instances: dict[type, Any] = {}
    _lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Devolver la instancia existente o crearla si no existe."""
        with SingletonMeta._lock:
            if cls not in SingletonMeta._instances:
                instance = super().__call__(*args, **kwargs)
                SingletonMeta._instances[cls] = instance

            return SingletonMeta._instances[cls]


class CorporateDataSingleton(metaclass=SingletonMeta):
    """Centralizar el acceso a la tabla CorporateData."""

    def __init__(self) -> None:
        """Preparar el recurso y la referencia a la tabla."""
        self.table_name = "CorporateData"
        self.dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

    def get(self, record_id: str) -> dict[str, Any] | None:
        """Obtener un registro mediante su clave primaria."""
        response = self.table.get_item(Key={"id": record_id})
        return response.get("Item")

    def list_all(self) -> list[dict[str, Any]]:
        """Recuperar todos los registros mediante paginación."""
        items: list[dict[str, Any]] = []
        scan_kwargs: dict[str, Any] = {}

        while True:
            response = self.table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))

            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break

            scan_kwargs["ExclusiveStartKey"] = last_key

        return items

    def set(self, record_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Actualizar campos o crear un registro con valores vacíos."""
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("El ID debe ser un texto no vacío.")

        if not isinstance(data, dict):
            raise ValueError("Los datos deben ser un diccionario.")

        allowed_fields = (
            "cp",
            "CUIT",
            "domicilio",
            "idreq",
            "idSeq",
            "localidad",
            "provincia",
            "sede",
            "seqID",
            "telefono",
            "web",
        )

        attributes = {key: value for key, value in data.items() if key != "id"}

        if not attributes:
            raise ValueError("Debe indicar al menos un campo para actualizar.")

        unknown = attributes.keys() - allowed_fields
        if unknown:
            raise ValueError(f"Campos desconocidos: {sorted(unknown)}")

        names: dict[str, str] = {}
        values: dict[str, Any] = {}
        updates: list[str] = []

        for index, field in enumerate(allowed_fields):
            name = f"#f{index}"
            names[name] = field

            if field in attributes:
                value_key = f":v{index}"
                values[value_key] = attributes[field]
                updates.append(f"{name} = {value_key}")
            else:
                empty_key = f":empty{index}"
                values[empty_key] = ""
                updates.append(f"{name} = if_not_exists({name}, {empty_key})")

        response = self.table.update_item(
            Key={"id": record_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ReturnValues="ALL_NEW",
        )

        return response.get("Attributes", {})


class CorporateLogSingleton(metaclass=SingletonMeta):
    """Centralizar el acceso a la tabla CorporateLog."""

    def __init__(self) -> None:
        """Preparar el recurso y la referencia a CorporateLog."""
        self.table_name = "CorporateLog"
        self.dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

    def save(self, entry: dict[str, Any]) -> None:
        """Guardar un registro de auditoría."""
        if not entry.get("id"):
            raise ValueError("La auditoría debe contener un ID.")

        self.table.put_item(Item=entry)
