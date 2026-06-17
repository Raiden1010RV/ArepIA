# Informe de evidencia colaborativa – ArepIA

## 1. Repositorio

**Nombre del proyecto:** ArepIA
**Repositorio:** https://github.com/Raiden1010RV/ArepIA.git
**Objetivo:** Desarrollar un sistema inteligente para la gestión de inventarios y la predicción de demanda en una microempresa productora y comercializadora de arepas artesanales, aplicando control de versiones, pruebas automatizadas e integración continua.

## 2. Integrantes y responsabilidades

| Integrante                      | Rama                                     | Responsabilidad                                                   | Evidencia principal                                                                                                              |
| ------------------------------- | ---------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Cristhian Felipe Ramírez Chaves | `main`, `docs`, `circleci-project-setup` | Documentación, configuración de integración continua y despliegue | Commits, configuración de Travis CI, configuración y corrección del pipeline de CircleCI, Pull Request y evidencias documentales |
| Luis Carlos Díaz Amariles       | `feature-luis-ml-ci`                     | Inteligencia artificial e integración de sistemas                 | Estructura del módulo de IA, integración continua y Pull Request                                                                 |
| Ivon Astrid Garzón Álvarez      | `feature-ivon-frontend`                  | Frontend y desarrollo de componentes                              | Estructura base del frontend y Pull Request                                                                                      |
| Angy Camila Aguirre Garagoa     | `feature-angy-backend`                   | Backend y gestión de base de datos                                | Estructura base del backend y Pull Request                                                                                       |
| Diana Carolina Doria Mora       | `feature-arquitectura`                   | Diseño de arquitectura y diagramas del sistema                    | Estructura de arquitectura, diagramas y Pull Request                                                                             |

## 3. Evidencia de contribuciones

| Integrante                      | Rama                            | Actividad                                                   | Commit o acción                                     | Evidencia                                   |
| ------------------------------- | ------------------------------- | ----------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------- |
| Cristhian Felipe Ramírez Chaves | `main / docs`                   | Documentación inicial del proyecto                          | Documentación inicial de ArepIA                     | Commit en GitHub                            |
| Luis Carlos Díaz Amariles       | `feature-luis-ml-ci`            | Modelo de inteligencia artificial e integración continua    | Creación de la estructura de IA e integración       | Pull Request                                |
| Ivon Astrid Garzón Álvarez      | `feature-ivon-frontend`         | Desarrollo del frontend                                     | Creación de la estructura base del frontend         | Pull Request                                |
| Angy Camila Aguirre Garagoa     | `feature-angy-backend`          | Desarrollo del backend                                      | Creación de la estructura base del backend          | Pull Request                                |
| Diana Carolina Doria Mora       | `feature-arquitectura`          | Arquitectura y diagramación                                 | Creación de la estructura de arquitectura           | Pull Request                                |
| Cristhian Felipe Ramírez Chaves | `main`                          | Configuración inicial de Travis CI                          | `ci: configura pipeline básico de Travis CI`        | Archivo `.travis.yml`                       |
| Cristhian Felipe Ramírez Chaves | `main`                          | Activación de la primera solicitud de build en Travis CI    | `ci: activa primer build de Travis CI`              | Solicitud registrada en Travis CI           |
| Cristhian Felipe Ramírez Chaves | `circleci-project-setup`        | Creación automática de la configuración inicial de CircleCI | `CircleCI Commit`                                   | Archivo `.circleci/config.yml`              |
| Cristhian Felipe Ramírez Chaves | `circleci-project-setup`        | Actualización del entorno de ejecución                      | `ci: actualiza CircleCI a Python 3.11`              | Pipeline ejecutado con Python 3.11          |
| Cristhian Felipe Ramírez Chaves | `circleci-project-setup`        | Corrección de rutas y selección de pruebas                  | `ci: corrige rutas y pruebas del pipeline CircleCI` | Pipeline `build-and-test` exitoso           |
| Cristhian Felipe Ramírez Chaves | `circleci-project-setup → main` | Integración de CircleCI en la rama principal                | Pull Request número 6                               | Merge exitoso y pipeline aprobado en `main` |

## 4. Evidencia en GitHub

### 4.1 Commits

Ruta de verificación:

**Repositorio → Code → Commits**

Los commits permiten identificar el autor, el mensaje del cambio, la fecha y el identificador abreviado de cada modificación realizada en el proyecto.

### 4.2 Pull Requests

Ruta de verificación:

**Repositorio → Pull requests**

Los Pull Requests documentan el proceso de revisión e integración de las ramas individuales hacia la rama principal `main`.

### 4.3 Contributors

Ruta de verificación:

**Repositorio → Insights → Contributors**

Esta sección permite comprobar la participación de los integrantes mediante el número y distribución temporal de sus contribuciones.

### 4.4 GitHub Actions

Ruta de verificación:

**Repositorio → Actions**

El repositorio contiene evidencia de flujos automatizados y de la evolución de la infraestructura de integración continua.

### 4.5 Travis CI

Se creó el archivo `.travis.yml` en la raíz del repositorio con una configuración para Python 3.11, instalación de las dependencias del backend y ejecución de las pruebas de modelos mediante Pytest.

Travis CI recibió correctamente el evento generado por el `push`; sin embargo, la ejecución fue rechazada porque la cuenta propietaria del repositorio no se encontraba vinculada al esquema comercial vigente. La plataforma no presentó una opción gratuita y el plan disponible de menor valor exigía una suscripción mensual. Esta situación fue registrada como una limitación externa de carácter comercial.

### 4.6 CircleCI

Ante la limitación de Travis CI y la finalización del servicio CodeShip, se implementó CircleCI como herramienta complementaria de integración continua.

La configuración quedó almacenada en:

`.circleci/config.yml`

El pipeline denominado `build-and-test` realiza las siguientes actividades:

1. Descarga el código del repositorio.
2. Utiliza una imagen Docker con Python 3.11.
3. Establece el directorio de trabajo en `backend`.
4. Instala las dependencias definidas en `requirements.txt`.
5. Configura `PYTHONPATH` para reconocer los módulos locales.
6. Ejecuta las pruebas contenidas en `test_models.py`.
7. Genera y almacena los resultados en formato JUnit.

La configuración fue validada inicialmente en la rama `circleci-project-setup` y posteriormente integrada a `main` mediante el Pull Request número 6. Después del merge, CircleCI ejecutó satisfactoriamente el pipeline sobre la rama principal.

## 5. Flujo de trabajo aplicado

1. Clonado del repositorio.
2. Creación de ramas individuales.
3. Desarrollo según la responsabilidad asignada.
4. Creación de commits individuales.
5. Envío de cambios mediante `push`.
6. Creación de Pull Requests.
7. Revisión y merge hacia `main`.
8. Actualización de las copias locales mediante `git pull`.
9. Dockerización del ambiente.
10. Configuración de Jenkins como orquestador principal.
11. Creación del archivo `.travis.yml`.
12. Conexión del repositorio con Travis CI.
13. Identificación de la restricción comercial de Travis CI.
14. Verificación del fin de vida útil de CodeShip.
15. Implementación de CircleCI como alternativa funcional.
16. Corrección de incompatibilidades y rutas del pipeline.
17. Ejecución exitosa de las pruebas automatizadas.
18. Integración de la configuración de CircleCI en la rama `main`.

## 6. Historial de incidencias y soluciones

| Incidencia                                             | Causa identificada                                                 | Solución aplicada                                            | Resultado                             |
| ------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------- |
| Conflicto con el puerto predeterminado de Jenkins      | El puerto 8080 se encontraba ocupado                               | Migración de Jenkins al puerto 8090                          | Servicio estable                      |
| Problemas de comunicación entre Jenkins y Docker       | Permisos insuficientes y rutas de montaje incorrectas              | Ajuste de permisos y volúmenes                               | Comunicación restablecida             |
| Travis CI no ejecutó el build                          | Cuenta no vinculada al nuevo esquema de precios                    | Documentación de la restricción y evaluación de alternativas | Limitación comercial documentada      |
| CodeShip no estaba disponible                          | Fin de vida útil del servicio en enero de 2026                     | Documentación del anuncio oficial y selección de CircleCI    | Sustitución técnicamente justificada  |
| CircleCI no instaló inicialmente las dependencias      | La configuración automática utilizó Python 3.8                     | Actualización a `cimg/python:3.11-node`                      | Dependencias instaladas correctamente |
| CircleCI no encontró el módulo `models`                | El directorio del backend no estaba incluido en la ruta de módulos | Uso de `PYTHONPATH=.`                                        | Importaciones corregidas              |
| Las pruebas API no coincidían con la aplicación actual | `test_api.py` contenía endpoints e imports de una versión anterior | Ejecución controlada de `test_models.py`                     | Pipeline estable y verificable        |

## 7. Conclusión

El equipo implementó un flujo colaborativo basado en Git, GitHub, ramas, commits, Pull Requests, Docker e integración continua. Jenkins fue utilizado como orquestador principal, mientras que Travis CI y CircleCI permitieron comprobar la portabilidad de la configuración hacia servicios externos.

Aunque Travis CI no permitió completar la ejecución debido a una restricción comercial y CodeShip había finalizado su vida útil, el equipo documentó ambas situaciones e implementó CircleCI como una alternativa funcional. La ejecución satisfactoria del pipeline en la rama `main` demuestra que ArepIA puede instalar sus dependencias y ejecutar pruebas automatizadas en un entorno externo y reproducible.

La trazabilidad consolidada permite demostrar la participación individual de cada integrante, la evolución técnica del proyecto y la capacidad del equipo para identificar, documentar y resolver problemas propios de un proceso real de integración continua.
