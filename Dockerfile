FROM python:3-alpine
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]