# Instalación - IS2 TPFI

## Requisitos
- Python 3.13 o superior.
- Git.
- Credenciales AWS configuradas.
- Acceso a CorporateData y CorporateLog.

## Obtener el proyecto
git clone https://github.com/FacuMarquez91/IS2_TPFI.git
cd IS2_TPFI

## Crear el entorno virtual
python -m venv .venv
source .venv/Scripts/activate

## Instalar dependencias
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"

## Configurar AWS
aws configure

Las credenciales AWS no deben publicarse en GitHub.

## Verificar la instalación
python -c "import is2_tpfi; print('Instalacion correcta')"
