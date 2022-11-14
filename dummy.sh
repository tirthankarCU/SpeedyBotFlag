#!/bin/sh
kubectl delete deploy backend &
kubectl delete deploy frontend &
kubectl delete deploy redis &
kubectl delete service redis-svc &
kubectl delete service minio-svc &
kubectl delete service backend-svc &
kubectl delete service frontend-svc &
kubectl delete deploy logs &
kubectl delete ingress frontend-ingress & 

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f minio/minio-external-service.yaml

kubectl apply -f logs/logs-deployment.yaml

kubectl apply -f rest/front-end.yaml
kubectl apply -f rest/rest-ingress.yaml

kubectl apply -f worker/back-end.yaml
