FROM node:22-bookworm-slim AS frontend
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv && rm -rf /var/lib/apt/lists/*
COPY . .
RUN python3 -m venv /opt/docs && /opt/docs/bin/pip install mkdocs==1.6.1
RUN /opt/docs/bin/python scripts/build_web_assets.py && npm ci --prefix frontend/studio && npm run build --prefix frontend/studio
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 prabha
COPY core-py/prabha core-py/prabha
COPY spec spec
COPY blocks-lib blocks-lib
COPY peman.prabha .
COPY frontend/web frontend/web
COPY --from=frontend /build/frontend/studio/dist frontend/studio/dist
USER prabha
ENV HOST=0.0.0.0 PORT=8000 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["python", "frontend/web/server.py"]
