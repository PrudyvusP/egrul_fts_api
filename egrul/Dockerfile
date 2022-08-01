FROM python:3.8-slim
WORKDIR /app
RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
LABEL author="vgolosyandriya@yandex.ru" version=0.1