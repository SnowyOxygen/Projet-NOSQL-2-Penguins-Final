# SSL Certificate Setup Instructions

This directory should contain your SSL certificates for HTTPS support.

## Quick Setup with Let's Encrypt (Recommended)

### Option 1: Using Certbot on VPS (Before Docker)

1. Install Certbot on your VPS:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot

# CentOS/RHEL
sudo yum install certbot
```

2. Stop any services using port 80:
```bash
sudo systemctl stop nginx
sudo systemctl stop apache2
```

3. Generate certificates:
```bash
sudo certbot certonly --standalone -d penguin-lrm-analysis.duckdns.org
```

4. Copy certificates to this directory:
```bash
sudo cp /etc/letsencrypt/live/penguin-lrm-analysis.duckdns.org/fullchain.pem ./fullchain.pem
sudo cp /etc/letsencrypt/live/penguin-lrm-analysis.duckdns.org/privkey.pem ./privkey.pem
sudo chmod 644 ./fullchain.pem
sudo chmod 600 ./privkey.pem
```

5. Uncomment the HTTPS server block in `nginx.conf`

6. Start your Docker containers

### Option 2: Using Certbot with Docker

Add this service to your `docker-compose.prod.yml`:

```yaml
  certbot:
    image: certbot/certbot
    container_name: ${PROJECT_NAME:-penguins}-certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - ./nginx/certbot-webroot:/var/www/certbot
    command: certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d penguin-lrm-analysis.duckdns.org
```

Then:
1. Ensure the nginx service is running with HTTP only
2. Run: `docker-compose -f docker-compose.prod.yml run --rm certbot`
3. Uncomment HTTPS server block in nginx.conf
4. Restart nginx: `docker-compose -f docker-compose.prod.yml restart nginx`

### Certificate Renewal

Let's Encrypt certificates expire every 90 days. Set up automatic renewal:

**Cron job on VPS:**
```bash
# Add to crontab (crontab -e)
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/penguin-lrm-analysis.duckdns.org/*.pem /path/to/project/nginx/ssl/ && docker-compose -f /path/to/project/docker-compose.prod.yml restart nginx
```

## Option 3: Self-Signed Certificates (Testing Only)

⚠️ **Not recommended for production!**

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem \
  -out fullchain.pem \
  -subj "/CN=penguin-lrm-analysis.duckdns.org"
```

## File Structure

After setup, this directory should contain:
```
ssl/
├── fullchain.pem  (Public certificate + chain)
└── privkey.pem    (Private key)
```

## Security Notes

- **Never commit SSL private keys to version control**
- Keep `privkey.pem` permissions set to 600 (read/write for owner only)
- `fullchain.pem` should be 644 (readable by all, writable by owner)
- Rotate certificates before expiration

## Troubleshooting

### Certificate not found error
- Verify files exist: `ls -la nginx/ssl/`
- Check file permissions
- Ensure docker-compose volume mapping is correct

### Certificate validation fails
- Verify domain DNS points to your VPS IP
- Check firewall allows ports 80 and 443
- Ensure no other service is using these ports

### DuckDNS Specific
DuckDNS provides free dynamic DNS. To update your IP:
```bash
# One-time update
curl "https://www.duckdns.org/update?domains=penguin-lrm-analysis&token=YOUR_TOKEN&ip="

# Add to crontab for automatic updates (every 5 min)
*/5 * * * * curl -s "https://www.duckdns.org/update?domains=penguin-lrm-analysis&token=YOUR_TOKEN&ip=" > /dev/null
```

Replace `YOUR_TOKEN` with your DuckDNS token from https://www.duckdns.org/
