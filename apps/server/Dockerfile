FROM python:3.13.1-slim-bookworm

ENV PYTHONUNBUFFERED=True
WORKDIR /workspace

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

COPY pyproject.toml uv.lock /workspace/
RUN uv sync --frozen --no-install-workspace --package=myserver

COPY myserver mylib /workspace/
RUN uv sync --frozen --package=myserver

CMD ["/workspace/.venv/bin/python", "/workspace/myserver/src/myserver/run.py"]
