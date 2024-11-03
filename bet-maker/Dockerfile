FROM python:3.10-slim
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
COPY ./bet-maker /app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
