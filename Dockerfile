FROM python:3.8-slim


RUN apt-get update && \
    apt-get install -y libpq-dev gcc


WORKDIR /app

COPY . /app


RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "app.py"]