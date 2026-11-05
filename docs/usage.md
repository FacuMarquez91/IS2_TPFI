# Uso del aplicativo - IS2 TPFI

## Descripcion

Aplicacion cliente-servidor desarrollada en Python que implementa
los patrones Singleton, Proxy y Observer con AWS DynamoDB.

## Componentes

- singletonproxyobserver.py: servidor HTTP/TCP.
- singletonclient.py: cliente de operaciones GET, LIST y SET.
- observerclient.py: cliente de suscripciones.
- patterns/singleton.py: acceso a CorporateData y CorporateLog.
- patterns/proxy.py: validacion, procesamiento y auditoria.
- patterns/observer.py: gestion de notificaciones.

## Iniciar el servidor

python -m is2_tpfi.singletonproxyobserver -p 8080 -v

## Iniciar ObserverClient

Desde una segunda terminal:

python -m is2_tpfi.observerclient -s 127.0.0.1 -p 8080 -v

## Ejecutar operaciones

Las solicitudes se almacenan en archivos JSON.

GET: consultar un registro existente.
LIST: recuperar todos los registros.
SET: crear o actualizar un registro.

Para enviar una solicitud:

python -m is2_tpfi.singletonclient -i solicitud.json -s 127.0.0.1 -p 8080 -v

El archivo solicitud.json debe contener UUID, ACTION y,
cuando corresponda, ID y los campos a modificar.

## Auditoria

El Proxy registra las solicitudes en CorporateLog.

## Notificaciones

Cuando se ejecuta una operacion SET exitosa,
el Observer notifica a los clientes suscriptos.

## Pruebas automatizadas

python -m pytest --cov=is2_tpfi --cov-branch --cov-report=term-missing

## Calidad de codigo

ruff check .
black --check .
mypy src tests
pyright
bandit -r src

## Documentacion automatica

python -m pdoc is2_tpfi -o site/pdoc
