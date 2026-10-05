#!/bin/bash
# =============================================
# Kubernetes Copilot — AWS EC2 Setup Script
# Run this ONCE after connecting to your EC2
# Usage: bash setup_ec2.sh
# =============================================

set -e  # Exit on error

echo "============================================="
echo " Kubernetes Copilot — EC2 Setup Script"
echo "============================================="

# 1. System update
echo "[1/8] Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

# 2. Install Docker
echo "[2/8] Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 3. Start Docker & add user to docker group
echo "[3/8] Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 4. Install Docker Compose (standalone)
echo "[4/8] Installing Docker Compose..."
COMPOSE_VERSION="v2.24.0"
sudo curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Docker version:         $(docker --version)"
echo "Docker Compose version: $(docker-compose --version)"

# 5. Install Git
echo "[5/8] Installing Git..."
sudo apt-get install -y git

# 6. Create app directory
echo "[6/8] Creating application directory..."
sudo mkdir -p /opt/kubernetes-copilot
sudo chown -R $USER:$USER /opt/kubernetes-copilot

echo "============================================="
echo " ✅ EC2 Setup Complete!"
echo ""
echo " Next steps:"
echo "  1. Re-login to apply Docker group: exit && ssh again"
echo "  2. Upload your project files"
echo "  3. Create your .env file with API keys"
echo "  4. Run: docker-compose up -d"
echo "============================================="
