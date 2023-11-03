FROM python:3.11
WORKDIR /usr/loan-predictor-server
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt
COPY . .
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "-P" ,"eventlet"]
