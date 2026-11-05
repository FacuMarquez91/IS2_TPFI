# IS2 - Trabajo Práctico Final Integrador

Implementación de los patrones de diseño Singleton, Proxy y Observer en Python,
utilizando AWS DynamoDB como sistema de persistencia.

Proyecto de Ingeniería de Software II - UADER, Facultad de Ciencia y Tecnología.

## Objetivo

Desarrollar una aplicación cliente-servidor que permita consultar, listar y
modificar datos corporativos, registrar auditorías y notificar actualizaciones
a clientes suscriptos.

## Arquitectura

El sistema utiliza tres patrones de diseño:

- Singleton: administra el acceso a las tablas CorporateData y CorporateLog.
- Proxy: centraliza el procesamiento de solicitudes y las auditorías.
- Observer: administra las suscripciones y notifica modificaciones.

La comunicación entre clientes y servidor se realiza mediante HTTP POST
sobre TCP, utilizando mensajes JSON.

## Componentes

- singletonclient.py: cliente para ejecutar get, list y set.
- observerclient.py: cliente que recibe notificaciones.
- singletonproxyobserver.py: servidor de aplicaciones.
- patterns/singleton.py: acceso a DynamoDB.
- patterns/proxy.py: procesamiento y auditoría de solicitudes.
- patterns/observer.py: gestión de suscriptores.

## Requisitos

- Python 3.13 o superior.
- Entorno virtual Python.
- Dependencias de requirements.txt.
- Credenciales AWS válidas y configuradas localmente.
- Acceso a las tablas CorporateData y CorporateLog.

## Instalación

Crear y activar el entorno virtual en Windows con Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Instalar las dependencias y el paquete en modo editable:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

Configurar las credenciales AWS:

```bash
aws configure
```

Las credenciales son proporcionadas por la cátedra y no deben publicarse
ni incorporarse al repositorio.

## Ejecución

Iniciar el servidor:

```bash
python -m is2_tpfi.singletonproxyobserver -p 8080 -v
```

Ejecutar una consulta mediante el cliente:

```bash
python -m is2_tpfi.singletonclient -i test_get.json -v
```

Ejecutar un cliente observador:

```bash
python -m is2_tpfi.observerclient -s localhost -p 8080 -v
```

El servidor debe permanecer ejecutándose mientras los clientes realizan
sus solicitudes.

## Acciones disponibles

### get

Recupera un registro de CorporateData mediante su identificador.

```json
{
  "UUID": "IDENTIFICADOR_CPU",
  "ACTION": "get",
  "ID": "UADER-FCyT-IS2"
}
```

### list

Recupera todos los registros de CorporateData.

```json
{
  "UUID": "IDENTIFICADOR_CPU",
  "ACTION": "list"
}
```

### set

Crea o modifica un registro. Si existe, conserva los campos no informados.

```json
{
  "UUID": "IDENTIFICADOR_CPU",
  "ACTION": "set",
  "ID": "REGISTRO-DE-PRUEBA",
  "telefono": "03442-123456"
}
```

### subscribe

Registra un cliente observador para recibir notificaciones cuando se
modifican registros de CorporateData.

## Auditoría

Las solicitudes se registran en CorporateLog, incluyendo información
de la CPU, sesión, acción solicitada y fecha de ejecución.

## Pruebas automatizadas

Ejecutar:

```bash
python -m pytest --cov=is2_tpfi --cov-report=term-missing
```

La configuración exige una cobertura mínima del 85 %.

## Calidad de código

```bash
python -m black --check src tests
python -m ruff check src tests
python -m mypy src
python -m pyright src
python -m bandit -r src
```

## Documentación

La documentación de la API puede generarse utilizando Pdoc:

```bash
python -m pdoc is2_tpfi -o site/pdoc
```

Los diagramas UML y la documentación complementaria se encuentran
en el directorio docs, una vez generados.

## Integración continua

El proyecto contiene un workflow de GitHub Actions en
.github/workflows/ci.yml para automatizar las verificaciones.

## Licencia

MIT. Consultar el archivo LICENSE.

## Seguridad

No publicar claves AWS, archivos de credenciales ni datos secretos.
Los registros corporativos existentes deben tratarse como datos compartidos.
