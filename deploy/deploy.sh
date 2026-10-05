#!/bin/bash
# =============================================
# Kubernetes Copilot — Deploy / Update Script
# Run this to deploy or update the application
# Usage: bash deploy.sh
# =============================================

set -e

APP_DIR="/opt/kubernetes-copilot"
echo "============================================="
echo " Deploying Kubernetes Copilot..."
echo "============================================="

cd $APP_DIR

# Pull latest (if using git)
# git pull origin main

# Build and start containers
echo "[1/3] Building Docker image..."
docker-compose build --no-cache

echo "[2/3] Starting containers..."
docker-compose up -d

echo "[3/3] Checking health..."
sleep 10
curl -s http://localhost:8000/api/health | python3 -m json.tool || echo "Health check failed — check logs: docker-compose logs"

echo ""
echo "============================================="
echo " ✅ Deployment Complete!"
echo " App running at: http://$(curl -s ifconfig.me)"
echo "============================================="
