FROM python:3.10.13-alpine
WORKDIR /usr/loan-predictor-server
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt
COPY . .
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "-P" ,"eventlet"]
