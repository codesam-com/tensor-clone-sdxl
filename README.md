# Tensor Clone SDXL SaaS

Base cloud-first para construir un generador de imágenes tipo Tensor Art AI usando SDXL, API HTTP, worker GPU y almacenamiento externo.

## Objetivo

Este repositorio arranca una arquitectura SaaS para:
- recibir prompts por API
- crear jobs de generación
- ejecutar inferencia SDXL en workers GPU
- guardar imágenes en almacenamiento externo
- devolver estado y URL de resultado

## Arquitectura

```text
client -> FastAPI API -> job queue -> GPU worker -> object storage
```

## Componentes

- `api/`: API HTTP y endpoints de jobs
- `worker/`: generación SDXL preparada para CUDA
- `services/`: almacenamiento y utilidades comunes
- `.github/workflows/ci.yml`: validación básica de CI
- `docker-compose.yml`: stack local de desarrollo con Redis

## Endpoints iniciales

- `GET /health`
- `POST /v1/jobs`
- `GET /v1/jobs/{job_id}`

## Variables de entorno

Ver `.env.example`.

## Roadmap sugerido

1. Sustituir almacenamiento local por S3 compatible.
2. Añadir autenticación y cuotas.
3. Añadir cola real con Celery/RQ y persistencia de jobs.
4. Añadir base de datos para usuarios, créditos y auditoría.
5. Añadir frontend web tipo SaaS.

## Ejecución rápida

```bash
cp .env.example .env
docker compose up --build
```

## Nota

La generación SDXL queda preparada pero protegida por variables de entorno para no forzar descarga de pesos ni uso de GPU en entornos donde no aplique.
