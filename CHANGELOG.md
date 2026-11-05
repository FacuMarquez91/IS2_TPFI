# Historial de cambios

## [0.1.0] - 2026-11-03

### Incorporado
- Estructura de proyecto Python basada en Cookiecutter.
- Gestión de CorporateData y CorporateLog mediante Singleton.
- Procesamiento de solicitudes mediante Proxy.
- Gestión de suscripciones y notificaciones mediante Observer.
- Servidor HTTP/TCP para solicitudes JSON.
- Cliente SingletonClient para get, list y set.
- Cliente ObserverClient para subscribe.
- Auditorías de operaciones en AWS DynamoDB.
- Pruebas unitarias e integradas con Pytest.
- Controles de formato, tipado y seguridad.
- Workflow de integración continua en GitHub Actions.

### Verificado
- Conexión real con AWS mediante Boto3.
- Lectura y listado de registros de CorporateData.
- Creación de registros nuevos.
- Actualización parcial conservando campos existentes.
- Recepción de notificaciones por ObserverClient.
- Auditorías de get, list, set y subscribe en CorporateLog.
- 52 pruebas aprobadas con cobertura del 85,90 %.

### Pendiente de validar
- Ejecución del workflow CI en GitHub.
- Publicación o generación final de documentación de API.
