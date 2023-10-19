#!/bin/bash
kubectl config use-context k3d-loan-predictor-local 
docker build -t server:latest -f docker/loan-predictor-server.Dockerfile .
k3d image import --cluster loan-predictor-local server:latest
kubectl rollout restart deployment server-deployment -n default
docker build -t celery:latest -f docker/celery.Dockerfile .
k3d image import --cluster loan-predictor-local celery:latest
kubectl rollout restart deployment celery-deployment -n default