FROM python:3.10-alpine
WORKDIR /app
RUN python -m pip install -U pip
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY . .
RUN mkdir egrul_data
CMD ["gunicorn", "egrul.wsgi:application", "--bind", "0:8000" ]
LABEL author="vgolosyandriya@yandex.ru" version=0.1