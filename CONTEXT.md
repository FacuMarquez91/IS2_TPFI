# CONTEXT.md - Registro de uso de inteligencia artificial

## Proyecto

Trabajo Practico Final Integrador de Ingenieria de Software II.

Aplicativo Python que implementa los patrones Singleton, Proxy y Observer,
con persistencia y auditoria en AWS DynamoDB.

## Herramienta utilizada

ChatGPT (OpenAI).

La herramienta se utilizo como apoyo para el desarrollo, la comprension
del codigo, la depuracion, la verificacion y la documentacion del proyecto.

## Registro de interacciones

### 1. Preparacion del proyecto y entorno

Periodo: octubre de 2026.

Solicitudes realizadas:
- Asistencia para configurar Python y un ambiente virtual venv.
- Preparacion de la estructura del proyecto mediante Cookiecutter.
- Organizacion de paquetes, archivos y pruebas.
- Revision de pyproject.toml y dependencias.

Estas solicitudes se describen por tema y no representan una
transcripcion textual completa.

### 2. Implementacion de patrones de diseno

Periodo: octubre de 2026.

Solicitudes realizadas:
- Implementar dos gestores Singleton independientes para
  CorporateData y CorporateLog.
- Comprender la implementacion del patron Proxy para las
  operaciones GET, LIST y SET.
- Implementar y explicar las suscripciones y notificaciones
  mediante el patron Observer.
- Revisar la comunicacion entre los modulos del aplicativo.

### 3. Integracion con AWS DynamoDB

Periodo: octubre y noviembre de 2026.

Solicitudes realizadas:
- Configurar el acceso a las tablas CorporateData y CorporateLog.
- Implementar consultas, listados y actualizaciones.
- Verificar registros de auditoria.
- Analizar los resultados de operaciones exitosas y fallidas.

### 4. Pruebas y calidad

Periodo: octubre y noviembre de 2026.

Solicitudes realizadas:
- Preparar y ejecutar pruebas automatizadas con Pytest.
- Revisar la cobertura de codigo y ramas.
- Ejecutar Ruff, Black, MyPy, Pyright y Bandit.
- Analizar errores de formato y corregirlos.

Ejemplo de solicitud textual conservada:

"dame script para ejecutar ruff black y los otros tests"

Resultado verificado el 5 de noviembre de 2026:
- 52 pruebas aprobadas.
- Cobertura total: 85,87 %.
- Ruff sin errores.
- Black sin errores.

### 5. Manejo de errores y comunicaciones

Periodo: noviembre de 2026.

Ejemplo de solicitud textual conservada:

"necesito que el servidor diga, error registro no encontrado"

Se reviso el registro de errores cuando una solicitud GET intenta
consultar un identificador inexistente.

Tambien se analizaron problemas de conectividad entre los clientes
y el servidor, diferenciando localhost de 127.0.0.1.

### 6. Documentacion y preparacion de la defensa

Periodo: noviembre de 2026.

Solicitudes realizadas:
- Explicar el funcionamiento de los modulos principales.
- Preparar material para la defensa oral.
- Revisar los entregables de la consigna.
- Preparar diagramas UML y un informe tecnico.
- Generar documentacion automatica mediante pdoc.

## Alcance y limitaciones del registro

Este documento combina ejemplos textuales conservados de las
conversaciones con descripciones resumidas de otras solicitudes.

Las descripciones resumidas no deben interpretarse como citas
literales de los prompts originales.

No se atribuyen a la herramienta ejecuciones o verificaciones
que no hayan sido comprobadas.

Las decisiones de implementacion, la revision de los resultados
y la validacion final del aplicativo corresponden al autor
del proyecto.

## Actualizaciones

2026-11-05: registro inicial de uso de inteligencia artificial.
