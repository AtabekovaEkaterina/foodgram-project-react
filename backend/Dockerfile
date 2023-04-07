FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get -y install libpq-dev gcc

RUN pip3 install -r requirements.txt --no-cache-dir

COPY foodgram_project/ .

CMD ["gunicorn", "foodgram_project.wsgi:application", "--bind", "0:8000" ]