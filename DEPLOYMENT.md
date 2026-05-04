# VPS Deployment Guide

This guide deploys the Coffee Commerce BI Platform to an Ubuntu VPS using Docker Compose. The public surface is Metabase behind Nginx on port `80`; PostgreSQL and pipeline services stay private inside Docker.

## 1. Prepare the VPS

SSH into the VPS:

```bash
ssh <user>@<vps-ip>
```

Install Docker and Git if they are not already installed:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git ufw
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Log out and log back in so the Docker group change applies.

## 2. Configure the Firewall

Allow SSH and HTTP only:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw deny 8080/tcp
sudo ufw --force enable
sudo ufw status
```

## 3. Clone and Configure

```bash
mkdir -p ~/apps
cd ~/apps
git clone https://github.com/brzaa/coffee-commerce-bi-platform.git
cd coffee-commerce-bi-platform
cp .env.example .env
```

Edit `.env` on the VPS:

```bash
nano .env
```

Recommended VPS changes:

```text
NGINX_PORT=80
POSTGRES_PASSWORD=<strong-postgres-password>
DB_PASSWORD=<same-strong-postgres-password>
MB_ADMIN_EMAIL=<your-demo-email>
MB_ADMIN_PASSWORD=<strong-metabase-password>
```

Do not commit `.env`.

## 4. Start the Public Demo

```bash
docker compose up -d --build warehouse metabase nginx
docker compose --profile pipeline run --rm pipeline
docker compose --profile setup run --rm metabase-setup
docker compose ps
```

Open:

```text
http://<vps-ip>/
```

Metabase will show the demo dashboard or allow login with the email and password from `.env`.

## 5. GitHub Actions Deployment

Add these repository secrets in GitHub:

```text
VPS_HOST=<vps-ip>
VPS_USER=<ssh-user>
VPS_SSH_KEY=<private-ssh-key-authorized-on-vps>
VPS_APP_DIR=/home/<ssh-user>/apps/coffee-commerce-bi-platform
```

On every push to `main`, the workflow will:

1. SSH into the VPS.
2. Clone or update the repo.
3. Build and start `warehouse`, `metabase`, and `nginx`.
4. Run the Prefect/dbt pipeline.
5. Attempt to create or refresh Metabase dashboard assets.

## 6. Operational Notes

- Keep only ports `22` and `80` open. Port `8080` must remain closed externally; Nginx receives public HTTP traffic on `80` and proxies to the internal Metabase container on Docker port `3000`.
- Do not expose PostgreSQL on the VPS firewall.
- Use synthetic data only; this repo is safe for a public portfolio demo.
- If the Metabase setup script cannot create cards because the API changes, the SQL assets remain in `metabase/sql/` and can be pasted into Metabase manually.
- If you later attach a domain, replace the Nginx setup with Caddy or Nginx plus Certbot for HTTPS.
