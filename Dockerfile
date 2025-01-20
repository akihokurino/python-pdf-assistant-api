FROM python:3.13.1
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
COPY . .
EXPOSE 8080