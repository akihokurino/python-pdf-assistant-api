FROM python:3.13.1
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install
EXPOSE 8080