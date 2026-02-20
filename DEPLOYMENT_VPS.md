# Guide de Déploiement sur VPS

**Projet:** Classification des Manchots Palmer - Architecture NoSQL Multi-bases  
**Domain:** `penguin-lrm-analysis.duckdns.org`  
**Date:** 2026-02-20

## 🎯 Configuration Résumée

- **Domaine:** penguin-lrm-analysis.duckdns.org
- **Port offset:** +7000 (évite les conflits de ports)
- **Nginx:** Intégré dans Docker Compose
- **Exposition:**
  - Frontend: Port 80/443 (via Nginx)
  - API Swagger: `/docs` (via Nginx)
  - Databases: Ports internes avec offset +7000

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Connexion au VPS](#connexion-au-vps)
3. [Installation des dépendances](#installation-des-dépendances)
4. [Configuration DuckDNS](#configuration-duckdns)
5. [Déploiement du projet](#déploiement-du-projet)
6. [Configuration SSL (HTTPS)](#configuration-ssl)
7. [Vérification et Tests](#vérification-et-tests)
8. [Maintenance](#maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Prérequis

### Sur votre machine locale
- Git installé
- SSH client (OpenSSH inclus dans Windows 10+)
- Accès au code source du projet

### Informations reçues
- ✅ IP VPS
- ✅ Mot de passe root
- ✅ Accès SSH sur port 22 (par défaut)

---

## Connexion au VPS

### 1. Se connecter via SSH

```powershell
# Depuis PowerShell Windows
ssh root@<VOTRE_IP_VPS>
```

**Saisir le mot de passe** quand demandé.

### 2. Première connexion - Sécurité

```bash
# Mettre à jour le système
apt update && apt upgrade -y

# (Optionnel) Créer un utilisateur non-root pour plus de sécurité
adduser deployer
usermod -aG sudo deployer
usermod -aG docker deployer
```

---

## Installation des Dépendances

### 1. Installer Docker

```bash
# Télécharger et installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Démarrer le service Docker
systemctl start docker
systemctl enable docker

# Vérifier l'installation
docker --version
```

**Résultat attendu:** `Docker version 24.0.x` (ou supérieur)

### 2. Installer Docker Compose

```bash
# Installer Docker Compose
apt install docker-compose -y

# Vérifier l'installation
docker-compose --version
```

**Résultat attendu:** `docker-compose version 1.29.x` (ou supérieur)

### 3. Installer Git (si nécessaire)

```bash
apt install git -y
git --version
```

---

## Configuration DuckDNS

### 1. Configurer votre domaine DuckDNS

Avant le déploiement, assurez-vous que votre domaine pointe vers votre VPS:

1. Allez sur https://www.duckdns.org et connectez-vous
2. Trouvez votre domaine: `penguin-lrm-analysis`
3. Mettez à jour l'IP avec celle de votre VPS

**Ou via commande:**
```bash
# Remplacez YOUR_TOKEN par votre token DuckDNS
curl "https://www.duckdns.org/update?domains=penguin-lrm-analysis&token=YOUR_TOKEN&ip=<VOTRE_IP_VPS>"
```

### 2. Configuration automatique (recommandé)

Pour mettre à jour automatiquement l'IP si elle change:

```bash
# Créer le script de mise à jour
nano /root/update-duckdns.sh
```

**Contenu:**
```bash
#!/bin/bash
curl -s "https://www.duckdns.org/update?domains=penguin-lrm-analysis&token=YOUR_TOKEN&ip=" > /dev/null
```

```bash
# Rendre exécutable
chmod +x /root/update-duckdns.sh

# Ajouter au crontab (toutes les 5 minutes)
crontab -e
# Ajouter: */5 * * * * /root/update-duckdns.sh
```

### 3. Vérifier la configuration DNS

```bash
# Tester la résolution DNS
nslookup penguin-lrm-analysis.duckdns.org
dig penguin-lrm-analysis.duckdns.org

# Ou simplement
ping penguin-lrm-analysis.duckdns.org
```

---

## Déploiement du Projet

### Option A: Depuis un repository Git

```bash
# Se placer dans le répertoire home
cd ~

# Cloner le repository
git clone <URL_DE_VOTRE_REPO> penguins-project

# Aller dans le dossier
cd penguins-project
```

### Option B: Transfert manuel via SCP

**Depuis votre machine Windows:**

```powershell
# Compresser le projet
Compress-Archive -Path "C:\Users\LouisMarriott\Desktop\SDV 2025\Projet NOSQL 2\*" -DestinationPath projet.zip

# Transférer vers le VPS
scp projet.zip root@<VOTRE_IP_VPS>:~/

# Ensuite sur le VPS:
```

```bash
# Décompresser
apt install unzip -y
unzip projet.zip -d penguins-project
cd penguins-project
```

### Option C: Utiliser rsync (recommandé)

**Depuis votre machine Windows:**

```powershell
# Installer rsync (via WSL ou Git Bash)
rsync -avz --exclude 'node_modules' --exclude '.venv' --exclude '__pycache__' `
  "C:/Users/LouisMarriott/Desktop/SDV 2025/Projet NOSQL 2/" `
  root@<VOTRE_IP_VPS>:~/penguins-project/
```

---

## Lancement avec Docker Compose

### 1. Préparer l'environnement

```bash
cd ~/penguins-project

# Vérifier la structure des fichiers
ls -la
```

**Fichiers requis:**
- ✅ `docker-compose.prod.yml` (version production avec Nginx)
- ✅ `docker-compose-sharded.yml` (version avec sharding MongoDB)
- ✅ `backend/`, `frontend/`, `data/`, `nginx/`

### 2. Configuration des ports (déjà appliqué)

Le fichier `docker-compose.prod.yml` utilise un offset de +7000 sur les ports:

```
MongoDB:    27017 → 34017 (externe) / 27017 (interne)
Cassandra:  9042  → 16042 (externe) / 9042 (interne)
Redis:      6379  → 13379 (externe) / 6379 (interne)
API:        8000  → Interne seulement (via Nginx)
Frontend:   3000  → Interne seulement (via Nginx)
Nginx:      80, 443 → Expose publiquement
```

### 3. Démarrer les services

#### Version Production (recommandé)

```bash
# Lancer tous les services (MongoDB, Cassandra, Redis, API, Frontend, Nginx)
docker-compose -f docker-compose.prod.yml up -d

# Suivre les logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Version Shardée (si besoin de sharding)

```bash
docker-compose -f docker-compose-sharded.yml up -d
```

### 4. Vérifier le démarrage

```bash
# Voir les containers en cours
docker-compose -f docker-compose.prod.yml ps

# Vérifier Nginx spécifiquement
docker logs penguins-nginx

# Suivre les logs de l'API
docker logs -f penguins-api
```

**Attendre 1-2 minutes** pour l'initialisation complète des services.

---

## Configuration SSL

### Option 1: Let's Encrypt avec Certbot (Recommandé pour Production)

```bash
# Installer Certbot
apt update
apt install certbot -y

# Arrêter temporairement les containers pour libérer le port 80
docker-compose -f docker-compose.prod.yml down

# Obtenir le certificat
certbot certonly --standalone -d penguin-lrm-analysis.duckdns.org

# Copier les certificats dans le projet
mkdir -p ~/penguins-project/nginx/ssl
cp /etc/letsencrypt/live/penguin-lrm-analysis.duckdns.org/fullchain.pem ~/penguins-project/nginx/ssl/
cp /etc/letsencrypt/live/penguin-lrm-analysis.duckdns.org/privkey.pem ~/penguins-project/nginx/ssl/
chmod 644 ~/penguins-project/nginx/ssl/fullchain.pem
chmod 600 ~/penguins-project/nginx/ssl/privkey.pem
```

### Option 2: Configuration manuelle SSL

Si vous avez déjà des certificats:

```bash
# Copier vos certificats
cp /path/to/your/fullchain.pem ~/penguins-project/nginx/ssl/
cp /path/to/your/privkey.pem ~/penguins-project/nginx/ssl/
```

### Activer HTTPS dans Nginx

```bash
# Éditer la configuration nginx
nano ~/penguins-project/nginx/nginx.conf
```

**Dans le fichier:**
1. Décommenter le bloc "HTTP server - redirect to HTTPS"
2. Décommenter le bloc "HTTPS server"  
3. Commenter ou supprimer le bloc "Main HTTP server"

```bash
# Redémarrer les services
cd ~/penguins-project
docker-compose -f docker-compose.prod.yml up -d

# Vérifier Nginx
docker logs penguins-nginx
```

### Renouvellement automatique SSL

```bash
# Créer script de renouvellement
nano /root/renew-ssl.sh
```

**Contenu:**
```bash
#!/bin/bash
certbot renew --quiet

# Copier les nouveaux certificats
cp /etc/letsencrypt/live/penguin-lrm-analysis.duckdns.org/fullchain.pem ~/penguins-project/nginx/ssl/
cp /etc/letsencrypt/live/penguin-lrm-analysis.duckdns.org/privkey.pem ~/penguins-project/nginx/ssl/

# Redémarrer Nginx
cd ~/penguins-project && docker-compose -f docker-compose.prod.yml restart nginx
```

```bash
# Rendre exécutable
chmod +x /root/renew-ssl.sh

# Ajouter au crontab (le 1er de chaque mois)
crontab -e
# Ajouter: 0 0 1 * * /root/renew-ssl.sh
```

---

## Vérification et Tests

### 1. Vérifier les services Docker

```bash
# Voir tous les containers (devrait montrer 7 services)
docker ps

# Services attendus:
# - penguins-nginx (port 80, 443)
# - penguins-api
# - penguins-frontend
# - penguins-mongo
# - penguins-cassandra
# - penguins-redis
# - penguins-db-init (completed)

# Vérifier MongoDB
docker exec -it penguins-mongo mongosh --eval "db.adminCommand('ping')"

# Vérifier Cassandra
docker exec -it penguins-cassandra nodetool status

# Vérifier Redis
docker exec -it penguins-redis redis-cli ping

# Vérifier Nginx
docker logs penguins-nginx | tail -20
```

### 2. Tester l'API (accès interne)

```bash
# Test via l'API interne
docker exec -it penguins-api curl http://localhost:8000/api/health

# Ou depuis le VPS vers Nginx
curl http://localhost/api/health
curl http://localhost/docs
```

### 3. Tester depuis votre navigateur

**Via HTTP (avant SSL):**
```
Frontend:        http://penguin-lrm-analysis.duckdns.org
API Health:      http://penguin-lrm-analysis.duckdns.org/api/health
API Swagger:     http://penguin-lrm-analysis.duckdns.org/docs
OpenAPI Schema:  http://penguin-lrm-analysis.duckdns.org/openapi.json
```

**Via HTTPS (après configuration SSL):**
```
Frontend:        https://penguin-lrm-analysis.duckdns.org
API Health:      https://penguin-lrm-analysis.duckdns.org/api/health
API Swagger:     https://penguin-lrm-analysis.duckdns.org/docs
```

### 4. Tests fonctionnels de l'API

```bash
# Test des statistiques (Part 1)
curl http://penguin-lrm-analysis.duckdns.org/api/part1/stats

# Test classification (Part 2)
curl -X POST http://penguin-lrm-analysis.duckdns.org/api/part2/classify \
  -H "Content-Type: application/json" \
  -d '{"culmen_length_mm": 39.5, "culmen_depth_mm": 17.8, "flipper_length_mm": 186, "body_mass_g": 3800}'

# Test benchmark
curl http://penguin-lrm-analysis.duckdns.org/api/benchmark/all
```

### 5. Vérifier les ports

```bash
# Vérifier quels ports sont ouverts
netstat -tulpn | grep LISTEN

# Ports attendus sur l'hôte:
# - 80 (Nginx HTTP)
# - 443 (Nginx HTTPS)
# - 34017 (MongoDB - optionnel, pour accès externe)
# - 16042 (Cassandra - optionnel, pour accès externe)
# - 13379 (Redis - optionnel, pour accès externe)
```

### 6. Configurer le firewall

```bash
# Installer UFW si nécessaire
apt install ufw -y

# Autoriser SSH, HTTP, HTTPS
ufw allow 22/tcp    # SSH (obligatoire!)
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Optionnel: autoriser accès direct aux bases (déconseillé en production)
# ufw allow 34017/tcp  # MongoDB
# ufw allow 16042/tcp  # Cassandra
# ufw allow 13379/tcp  # Redis

# Activer le firewall
ufw enable

# Vérifier le statut
ufw status numbered
```

---

## Maintenance

### Voir les logs

```bash
# Logs de tous les services
docker-compose -f docker-compose.prod.yml logs -f

# Logs spécifiques
docker logs penguins-nginx -f      # Nginx (reverse proxy)
docker logs penguins-api -f        # API FastAPI
docker logs penguins-frontend      # Frontend React
docker logs penguins-mongo         # MongoDB
docker logs penguins-cassandra     # Cassandra
docker logs penguins-redis         # Redis

# Dernières 100 lignes
docker logs --tail 100 penguins-api

# Depuis une date
docker logs --since 1h penguins-nginx
```

### Redémarrer les services

```bash
# Redémarrer tous les services
docker-compose -f docker-compose.prod.yml restart

# Redémarrer un seul service
docker restart penguins-nginx
docker restart penguins-api

# Reconstruire si code modifié
docker-compose -f docker-compose.prod.yml up -d --build

# Reconstruire un service spécifique
docker-compose -f docker-compose.prod.yml up -d --build api
```

### Arrêter les services

```bash
# Arrêter tout
docker-compose -f docker-compose.prod.yml down

# Arrêter sans supprimer les volumes (garde les données)
docker-compose -f docker-compose.prod.yml stop

# Arrêter et supprimer les volumes (ATTENTION: supprime les données)
docker-compose -f docker-compose.prod.yml down -v
```

### Mettre à jour le projet

```bash
cd ~/penguins-project

# Si Git
git pull origin main

# Si transfert manuel, re-transférer les fichiers

# Reconstruire et redémarrer
docker-compose -f docker-compose.prod.yml up -d --build

# Ou redémarrer sans rebuild si seule la config a changé
docker-compose -f docker-compose.prod.yml restart
```

### Surveiller les ressources

```bash
# Utilisation en temps réel
docker stats

# Espace disque
df -h

# Utilisation mémoire
free -h

# Nettoyer les ressources Docker inutilisées
docker system prune -a
```

---

## Troubleshooting

### Problème: Container qui ne démarre pas

```bash
# Voir les logs détaillés
docker logs <nom_container>

# Exemple avec l'API
docker logs penguins-api

# Inspecter le container
docker inspect penguins-api

# Vérifier les ressources
docker stats

# Relancer un container spécifique
docker-compose -f docker-compose.prod.yml up -d <service_name>
```

### Problème: Nginx ne démarre pas

```bash
# Vérifier les logs Nginx
docker logs penguins-nginx

# Tester la configuration
docker exec -it penguins-nginx nginx -t

# Vérifier que les ports ne sont pas utilisés
netstat -tulpn | grep -E ':(80|443)'

# Si un processus utilise le port, le tuer
kill -9 <PID>

# Redémarrer nginx
docker restart penguins-nginx
```

### Problème: Cannot connect to domain

```bash
# Vérifier que le domaine résout correctement
nslookup penguin-lrm-analysis.duckdns.org
ping penguin-lrm-analysis.duckdns.org

# Vérifier que Nginx écoute
docker exec -it penguins-nginx netstat -tuln | grep 80

# Vérifier le firewall
ufw status

# Tester localement sur le VPS
curl http://localhost/api/health

# Si ça marche localement mais pas de l'extérieur, c'est probablement le firewall
ufw allow 80/tcp
ufw allow 443/tcp
```

### Problème: SSL certificate errors

```bash
# Vérifier que les certificats existent
ls -la ~/penguins-project/nginx/ssl/

# Vérifier les permissions
chmod 644 ~/penguins-project/nginx/ssl/fullchain.pem
chmod 600 ~/penguins-project/nginx/ssl/privkey.pem

# Vérifier que les certificats sont montés dans le container
docker exec -it penguins-nginx ls -la /etc/nginx/ssl/

# Test de la configuration SSL
docker exec -it penguins-nginx nginx -t
```

### Problème: Port déjà utilisé

```bash
# Voir quel processus utilise le port
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Tuer le processus (après avoir identifié le PID)
kill -9 <PID>

# Ou si c'est un service système
systemctl stop nginx  # Si nginx système est installé
systemctl stop apache2
```

### Problème: MongoDB ne se connecte pas

```bash
# Vérifier que MongoDB est démarré
docker logs penguins-mongo

# Vérifier depuis l'API
docker exec -it penguins-api python -c "from pymongo import MongoClient; print(MongoClient('mongodb://mongodb:27017').admin.command('ping'))"

# Tester la connexion
docker exec -it penguins-mongo mongosh --eval "db.adminCommand('ping')"
```

### Problème: API returns 502 Bad Gateway

```bash
# L'API n'est probablement pas démarrée ou a crashé
docker logs penguins-api

# Vérifier que l'API répond
docker exec -it penguins-nginx curl http://api:8000/api/health

# Si l'API ne répond pas, la redémarrer
docker restart penguins-api

# Vérifier les logs de démarrage
docker logs -f penguins-api
```

### Problème: Frontend shows blank page

```bash
# Vérifier les logs du frontend
docker logs penguins-frontend

# Vérifier que le frontend est accessible via nginx
docker exec -it penguins-nginx curl http://frontend:80

# Vérifier la configuration nginx
docker exec -it penguins-nginx cat /etc/nginx/nginx.conf | grep frontend

# Reconstruire le frontend
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

### Problème: Manque de mémoire

```bash
# Vérifier l'utilisation RAM
free -h

# Voir la consommation par container
docker stats

# Augmenter la swap (temporaire)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Réduire la mémoire des services
# Éditer docker-compose.prod.yml et ajouter des limites:
# services:
#   mongodb:
#     deploy:
#       resources:
#         limits:
#           memory: 512M
```

### Problème: Cannot access databases from external tools

Les bases de données sont accessibles sur des ports avec offset +7000:

```bash
# MongoDB: port 34017
mongo "mongodb://<VOTRE_IP_VPS>:34017/penguins"

# Cassandra: port 16042
cqlsh <VOTRE_IP_VPS> 16042

# Redis: port 13379
redis-cli -h <VOTRE_IP_VPS> -p 13379

# Vérifier que le firewall autorise ces ports
ufw allow 34017/tcp  # MongoDB
ufw allow 16042/tcp  # Cassandra
ufw allow 13379/tcp  # Redis
```

---

## Sécurité Production

### 1. Activer HTTPS (Optionnel mais recommandé)

```bash
# Installer Certbot (pour Let's Encrypt)
apt install certbot python3-certbot-nginx -y

# Obtenir un certificat (nécessite un nom de domaine)
certbot --nginx -d votre-domaine.com

# Renouvellement automatique
systemctl enable certbot.timer
```

### 2. Variables d'environnement sensibles

```bash
# Créer un fichier .env
nano ~/penguins-project/.env
```

**Contenu:**
```env
MONGO_URL=mongodb://mongos:27017/penguins
CASSANDRA_HOST=cassandra
CASSANDRA_PORT=9042
REDIS_HOST=redis
REDIS_PORT=6379
ENV=production
```

### 3. Backup automatique

```bash
# Créer script de backup
nano /root/backup-penguins.sh
```

**Contenu:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/backups"

mkdir -p $BACKUP_DIR

# Backup MongoDB
docker exec penguins-mongos mongodump --out /tmp/dump
docker cp penguins-mongos:/tmp/dump $BACKUP_DIR/mongo_$DATE

# Backup volumes (optionnel)
docker run --rm -v penguins-mongo-data:/data -v $BACKUP_DIR:/backup ubuntu tar czf /backup/volumes_$DATE.tar.gz /data

echo "Backup completed: $DATE"
```

```bash
# Rendre exécutable
chmod +x /root/backup-penguins.sh

# Ajouter au cron (tous les jours à 2h du matin)
crontab -e
# Ajouter: 0 2 * * * /root/backup-penguins.sh
```

---

## Checklist Déploiement

### Avant déploiement
- [ ] Code du projet prêt
- [ ] IP VPS et mot de passe disponibles
- [ ] DuckDNS configuré et pointant vers le VPS
- [ ] docker-compose.prod.yml configuré avec offset de ports
- [ ] nginx/ directory avec Dockerfile et nginx.conf

### Installation
- [ ] Connexion SSH réussie
- [ ] Docker installé et fonctionnel
- [ ] Docker Compose installé
- [ ] Certbot installé (pour SSL)
- [ ] Projet transféré sur VPS

### Déploiement
- [ ] Containers démarrés avec docker-compose.prod.yml
- [ ] Logs vérifiés (pas d'erreurs)
- [ ] MongoDB opérationnel (test ping)
- [ ] Cassandra opérationnel (nodetool status)
- [ ] Redis fonctionnel (redis-cli ping)
- [ ] API accessible en interne
- [ ] Frontend accessible en interne
- [ ] Nginx démarré et configuré

### Configuration réseau
- [ ] DuckDNS résolvant correctement (nslookup)
- [ ] Firewall configuré (ports 22, 80, 443)
- [ ] Nginx proxy fonctionnel
- [ ] Accès HTTP au frontend via domaine
- [ ] Accès HTTP à /docs via domaine
- [ ] Accès HTTP à /api via domaine

### SSL/HTTPS (optionnel)
- [ ] Certificats Let's Encrypt obtenus
- [ ] Certificats copiés dans nginx/ssl/
- [ ] nginx.conf modifié pour HTTPS
- [ ] Services redémarrés
- [ ] Accès HTTPS fonctionnel
- [ ] Redirection HTTP → HTTPS active
- [ ] Renouvellement automatique configuré

### Tests
- [ ] Frontend accessible: https://penguin-lrm-analysis.duckdns.org
- [ ] API Health: https://penguin-lrm-analysis.duckdns.org/api/health
- [ ] API Swagger: https://penguin-lrm-analysis.duckdns.org/docs
- [ ] Tests fonctionnels API (classification, stats, etc.)
- [ ] Performance acceptable

### Production
- [ ] Backups configurés
- [ ] Monitoring en place
- [ ] Logs accessibles
- [ ] Plan de maintenance défini
- [ ] Documentation à jour

---

## Contacts et Support

**Projet:** Classification Manchots Palmer  
**Domaine:** penguin-lrm-analysis.duckdns.org  
**Port Offset:** +7000  

**URLs de Production:**
- Frontend: https://penguin-lrm-analysis.duckdns.org
- API Docs: https://penguin-lrm-analysis.duckdns.org/docs
- API Health: https://penguin-lrm-analysis.duckdns.org/api/health

**Ports exposés:**
- 80/443: Nginx (HTTP/HTTPS)
- 34017: MongoDB (optionnel)
- 16042: Cassandra (optionnel)
- 13379: Redis (optionnel)

**Documentation:**
- [README.md](README.md)
- [rapport_analyse.md](rapport_analyse.md)
- [nginx/ssl/README.md](nginx/ssl/README.md)

**Logs:**
- Docker: `docker logs <container_name>`
- Nginx: `docker logs penguins-nginx`
- Toutes les logs: `docker-compose -f docker-compose.prod.yml logs -f`

---

## Résumé en 5 minutes

```bash
# 1. Connexion
ssh root@<VOTRE_IP_VPS>

# 2. Installation
curl -fsSL https://get.docker.com | sh
apt install docker-compose git certbot -y

# 3. Configuration DuckDNS
curl "https://www.duckdns.org/update?domains=penguin-lrm-analysis&token=YOUR_TOKEN&ip=<VOTRE_IP_VPS>"

# 4. Déploiement
git clone <votre-repo> penguins-project
cd penguins-project
docker-compose -f docker-compose.prod.yml up -d

# 5. Configurer SSL (optionnel mais recommandé)
docker-compose -f docker-compose.prod.yml down
certbot certonly --standalone -d penguin-lrm-analysis.duckdns.org
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/penguin-lrm-analysis.duckdns.org/*.pem nginx/ssl/
# Décommenter le bloc HTTPS dans nginx/nginx.conf
docker-compose -f docker-compose.prod.yml up -d

# 6. Configurer le firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 7. Test
curl http://penguin-lrm-analysis.duckdns.org/api/health
```

**Accès:**
- Frontend: http://penguin-lrm-analysis.duckdns.org
- API Docs: http://penguin-lrm-analysis.duckdns.org/docs
- API Health: http://penguin-lrm-analysis.duckdns.org/api/health

**C'est prêt !** 🚀

---

## Commandes Rapides

```bash
# Démarrer tout
cd ~/penguins-project && docker-compose -f docker-compose.prod.yml up -d

# Arrêter tout
docker-compose -f docker-compose.prod.yml down

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f

# Logs d'un service spécifique
docker logs -f penguins-nginx
docker logs -f penguins-api

# Redémarrer un service
docker restart penguins-nginx
docker restart penguins-api

# Status des services
docker-compose -f docker-compose.prod.yml ps

# Reconstruire après changement de code
docker-compose -f docker-compose.prod.yml up -d --build

# Nettoyer (ATTENTION: supprime tout)
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a

# Voir l'utilisation des ressources
docker stats

# Vérifier les ports
netstat -tulpn | grep LISTEN
```

---

## Architecture de Production

```
Internet
    ↓
penguin-lrm-analysis.duckdns.org (Port 80/443)
    ↓
[Nginx Container] ← Configuration dans nginx/nginx.conf
    ↓
    ├── / → [Frontend Container:80] (React App)
    ├── /api/ → [API Container:8000] (FastAPI)
    └── /docs → [API Container:8000/docs] (Swagger)
         ↓
    ┌────┴─────┬─────────┬──────────┐
    ↓          ↓         ↓          ↓
[MongoDB]  [Cassandra] [Redis]  [DB-Init]
Port:34017 Port:16042  Port:13379
(+7000)    (+7000)     (+7000)
```

**Volumes persistants:**
- `penguins_mongo_data` - Données MongoDB
- `penguins_cassandra_data` - Données Cassandra
- `penguins_redis_data` - Cache Redis
- `penguins_nginx_cache` - Cache Nginx
