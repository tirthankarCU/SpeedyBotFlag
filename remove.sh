#!/bin/sh
kubectl delete deploy frontend &
kubectl delete service frontend-svc &
