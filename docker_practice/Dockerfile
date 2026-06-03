FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev postgresql-dev

RUN pip install --no-cache-dir flask psycopg2-binary

COPY app.py .

EXPOSE 8081

CMD ["python", "app.py"]
