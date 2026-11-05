# IS2 - Trabajo Practico Final Integrador

## Ingenieria de Software II - UADER

Aplicacion cliente-servidor desarrollada en Python que
implementa los patrones Singleton, Proxy y Observer,
utilizando AWS DynamoDB como sistema de persistencia.

## Funcionalidades

- GET: consultar un registro corporativo.
- LIST: recuperar registros de CorporateData.
- SET: crear o actualizar registros corporativos.
- SUBSCRIBE: registrar clientes observadores.
- Auditoria: registrar operaciones en CorporateLog.

## Arquitectura

### Singleton
Gestiona el acceso compartido a las tablas
CorporateData y CorporateLog.

### Proxy
Procesa las solicitudes, valida las operaciones
y registra las auditorias.

### Observer
Administra suscripciones y distribuye notificaciones
cuando se actualizan datos corporativos.

## Componentes

- singletonproxyobserver.py: servidor HTTP/TCP.
- singletonclient.py: cliente GET, LIST y SET.
- observerclient.py: cliente de notificaciones.
- patterns/singleton.py: acceso a DynamoDB.
- patterns/proxy.py: procesamiento de solicitudes.
- patterns/observer.py: gestion de observadores.

## Pruebas verificadas

- 52 pruebas automatizadas aprobadas.
- Cobertura total: 85,87 %.
- Cobertura minima requerida: 85 %.
- Ruff y Black sin errores.

## Documentacion

La referencia tecnica de los modulos Python se
genera automaticamente mediante pdoc.

Consultar tambien README.md para instrucciones
de instalacion y ejecucion.
