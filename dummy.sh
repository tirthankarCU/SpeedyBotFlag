#!/bin/sh
kubectl delete deploy frontend &
kubectl delete deploy redis &
kubectl get service
kubectl delete service redis-svc &
kubectl delete service minio-svc &
kubectl delete service frontend-svc &

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f minio/minio-external-service.yaml

kubectl apply -f rest/front-end.yaml
kubectl apply -f rest/rest-ingress.yaml
