FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
COPY fixtures ./fixtures
RUN pip install --no-cache-dir .
EXPOSE 8080
CMD ["sdlc-control-tower", "serve", "--host", "0.0.0.0", "--port", "8080"]
