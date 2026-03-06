# Deployment Guide for School Management System

## Prerequisites
- Ubuntu 22.04 LTS server
- Domain name pointed to server IP
- Docker and Docker Compose installed
- Git installed

---

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

---

## Step 2: Environment Configuration

1. Clone the repository.
   ```bash
   git clone <YOUR-REPO-URL> school-platform
   cd school-platform
   ```

2. Create the `.env` file using the example:
   ```bash
   cp .env.example .env
   # Edit .env and change default values!
   nano .env
   ```

---

## Step 3: Run the Application

```bash
# Build the Docker images
docker-compose build

# Start the services in detached mode
docker-compose up -d
```

The database migrations (`alembic upgrade head`), static file collection, and admin seeding happen automatically when the `app` container starts up.

---

## Security Checklist

Before exposing the server to the public, ensure the following steps are completed:

- [ ] **Change Default Credentials:** Make sure `POSTGRES_PASSWORD`, `SECRET_KEY`, and initially seeded Admin user passwords are secure and complex.
- [ ] **HTTPS / Let's Encrypt:** Uncomment the SSL/HTTPS blocks in `nginx/nginx.conf` and issue a certificate using Certbot:
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d yourdomain.uz -d www.yourdomain.uz
  ```
- [ ] **Firewall (UFW):** Restrict open ports.
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 'Nginx Full'
  sudo ufw enable
  ```
- [ ] **Disable Debugging:** Ensure `ENVIRONMENT=production` in `.env` to disable Swagger API docs and detailed stack traces.
- [ ] **Rate Limiting:** Nginx rate-limiting logic is recommended to prevent basic DDoS and brute-force attacks on the `/api/auth/` routes.
- [ ] **Backups:** Set up chron jobs to backup the PostgreSQL volume `postgres_data` securely to an offsite S3 bucket daily.

---

## Scalability Roadmap

Once the school grows beyond initial expectations, the architecture can be evolved:

### Phase 1: High Availability
- **External Managed Database:** Migrate from a Dockerized container DB to a Managed PostgreSQL (e.g., AWS RDS, DigitalOcean Managed Database) to allow the app to scale across multiple droplets.
- **S3 / CDN for Media:** Use AWS S3 or Cloudflare R2 for storing generated PDF certificates and thumbnails rather than Docker named volumes. Configure FastAPI to sign upload URLs securely.

### Phase 2: Microservices & Async Workers
- **Celery Worker Integration:** Currently, PDF rendering (using `reportlab`) logic executes inline via `BackgroundTasks`. For large volumes, offload this to a dedicated `Celery` worker queue backed by the existing `Redis` container.
- **Load Balancing:** Add a Load Balancer in front of Nginx, spinning up multiples instances of the `app` Docker service automatically depending on CPU thresholds.

### Phase 3: Global Edge Delivery
- **Cloudflare caching:** Put the `yourdomain.uz` domain behind Cloudflare to cache the server-rendered HTML pages extensively, drastically lowering the read load on the database for public routes. 