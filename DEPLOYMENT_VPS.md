# Guide de Déploiement sur VPS

**Projet:** Classification des Manchots Palmer - Architecture NoSQL Multi-bases  
**VPS IP:** `<VOTRE_IP_VPS>`  
**Date:** 2026-02-18

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Connexion au VPS](#connexion-au-vps)
3. [Installation des dépendances](#installation-des-dépendances)
4. [Déploiement du projet](#déploiement-du-projet)
5. [Configuration Nginx (Reverse Proxy)](#configuration-nginx)
6. [Vérification et Tests](#vérification-et-tests)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

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
- ✅ `docker-compose.yml` (version standard)
- ✅ `docker-compose-sharded.yml` (version production)
- ✅ `backend/`, `frontend/`, `data/`

### 2. Choisir la configuration

#### Option 1: Version Standard (Tests)

```bash
docker-compose up -d
```

#### Option 2: Version Shardée (Production - Recommandé)

```bash
docker-compose -f docker-compose-sharded.yml up -d
```

### 3. Vérifier le démarrage

```bash
# Voir les containers en cours
docker-compose -f docker-compose-sharded.yml ps

# Suivre les logs en temps réel
docker logs -f penguins-api

# Vérifier tous les services
docker-compose -f docker-compose-sharded.yml logs
```

**Attendre 2-3 minutes** pour l'initialisation complète du cluster MongoDB.

---

## Configuration Nginx

### 1. Installer Nginx

```bash
apt install nginx -y

# Démarrer Nginx
systemctl start nginx
systemctl enable nginx
```

### 2. Créer la configuration

```bash
# Créer le fichier de configuration
nano /etc/nginx/sites-available/penguins
```

**Copier cette configuration:**

```nginx
server {
    listen 80;
    server_name <VOTRE_IP_VPS>;

    # Frontend React
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Documentation
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

**Sauvegarder:** `Ctrl+X`, puis `Y`, puis `Enter`

### 3. Activer la configuration

```bash
# Créer un lien symbolique
ln -s /etc/nginx/sites-available/penguins /etc/nginx/sites-enabled/

# Tester la configuration
nginx -t

# Redémarrer Nginx
systemctl restart nginx
```

### 4. Configurer le firewall

```bash
# Autoriser les ports HTTP/HTTPS
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS (pour plus tard)
ufw enable

# Vérifier le statut
ufw status
```

---

## Vérification et Tests

### 1. Vérifier les services Docker

```bash
# Voir tous les containers
docker ps

# Vérifier la santé de MongoDB
docker exec -it penguins-mongos mongosh --eval "db.adminCommand('ping')"

# Vérifier Cassandra
docker exec -it penguins-cassandra nodetool status

# Vérifier Redis
docker exec -it penguins-redis redis-cli ping
```

### 2. Tester l'API

```bash
# Test de santé
curl http://localhost:8000/api/health

# Test des bases de données
curl http://localhost:8000/api/health/databases

# Test d'un endpoint
curl http://localhost:8000/api/part1/stats
```

### 3. Accéder depuis l'extérieur

**Depuis votre navigateur:**

```
Frontend:       http://<VOTRE_IP_VPS>
API Docs:       http://<VOTRE_IP_VPS>/docs  
API Health:     http://<VOTRE_IP_VPS>/api/health
Benchmarks:     http://<VOTRE_IP_VPS>/api/benchmark/all
```

### 4. Tester le sharding

```bash
# Depuis le VPS
curl -X POST http://localhost:8000/api/benchmark/sharding/comparison | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"
```

---

## Maintenance

### Voir les logs

```bash
# Logs de l'API
docker logs penguins-api

# Logs de MongoDB
docker logs penguins-mongos

# Logs Cassandra
docker logs penguins-cassandra

# Logs du frontend
docker logs penguins-frontend

# Tous les logs
docker-compose -f docker-compose-sharded.yml logs -f
```

### Redémarrer les services

```bash
# Redémarrer tous les services
docker-compose -f docker-compose-sharded.yml restart

# Redémarrer un seul service
docker restart penguins-api

# Reconstruire si code modifié
docker-compose -f docker-compose-sharded.yml up -d --build
```

### Arrêter les services

```bash
# Arrêter tout
docker-compose -f docker-compose-sharded.yml down

# Arrêter et supprimer les volumes (ATTENTION: supprime les données)
docker-compose -f docker-compose-sharded.yml down -v
```

### Mettre à jour le projet

```bash
cd ~/penguins-project

# Si Git
git pull origin main

# Si transfert manuel, re-transférer les fichiers

# Reconstruire et redémarrer
docker-compose -f docker-compose-sharded.yml up -d --build
```

---

## Troubleshooting

### Problème: Container qui ne démarre pas

```bash
# Voir les logs détaillés
docker logs <nom_container>

# Inspecter le container
docker inspect <nom_container>

# Vérifier les ressources
docker stats
```

### Problème: Port déjà utilisé

```bash
# Voir quel processus utilise le port
netstat -tulpn | grep :8000

# Tuer le processus
kill -9 <PID>
```

### Problème: MongoDB ne se connecte pas

```bash
# Vérifier que mongos est prêt
docker logs penguins-mongos

# Vérifier les shards
docker exec -it penguins-mongos mongosh --eval "sh.status()"

# Vérifier la connexion
docker exec -it penguins-api python -c "from pymongo import MongoClient; print(MongoClient('mongodb://mongos:27017').admin.command('ping'))"
```

### Problème: Manque de mémoire

```bash
# Vérifier l'utilisation RAM
free -h

# Voir la consommation par container
docker stats

# Si nécessaire, redémarrer avec moins de services
docker-compose down
docker-compose up -d  # Version standard sans sharding
```

### Problème: Nginx ne redirige pas

```bash
# Voir les erreurs Nginx
tail -f /var/log/nginx/error.log

# Tester la config
nginx -t

# Redémarrer Nginx
systemctl restart nginx
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
- [ ] Fichiers docker-compose configurés
- [ ] Variables d'environnement définies

### Installation
- [ ] Connexion SSH réussie
- [ ] Docker installé et fonctionnel
- [ ] Docker Compose installé
- [ ] Projet transféré sur VPS

### Déploiement
- [ ] Containers démarrés avec docker-compose
- [ ] Logs vérifiés (pas d'erreurs)
- [ ] MongoDB cluster initialisé
- [ ] Cassandra opérationnel
- [ ] Redis fonctionnel

### Configuration réseau
- [ ] Nginx installé et configuré
- [ ] Firewall configuré (ports 80, 443, 22)
- [ ] Reverse proxy fonctionnel
- [ ] HTTPS activé (optionnel)

### Tests
- [ ] API accessible: http://<VOTRE_IP_VPS>/api/health
- [ ] Frontend accessible: http://<VOTRE_IP_VPS>
- [ ] Documentation API: http://<VOTRE_IP_VPS>/docs
- [ ] Benchmarks fonctionnels
- [ ] Sharding opérationnel

### Production
- [ ] Backups configurés
- [ ] Monitoring en place
- [ ] Logs accessibles
- [ ] Plan de maintenance défini

---

## Commandes Rapides

```bash
# Démarrer tout
cd ~/penguins-project && docker-compose -f docker-compose-sharded.yml up -d

# Arrêter tout
docker-compose -f docker-compose-sharded.yml down

# Voir les logs
docker-compose -f docker-compose-sharded.yml logs -f

# Redémarrer un service
docker restart penguins-api

# Status des services
docker-compose -f docker-compose-sharded.yml ps

# Nettoyer (ATTENTION: supprime tout)
docker-compose -f docker-compose-sharded.yml down -v
docker system prune -a
```

---

## Contacts et Support

**Projet:** Classification Manchots Palmer  
**VPS:** `<VOTRE_IP_VPS>`  
**Documentation:** 
- [SHARDING_GUIDE.md](SHARDING_GUIDE.md)
- [README.md](README.md)
- [rapport_analyse.md](rapport_analyse.md)

**Logs directory sur VPS:** `/var/log/nginx/` (Nginx) et `docker logs <container>` (Docker)

---

## Résumé en 5 minutes

```bash
# 1. Connexion
ssh root@<VOTRE_IP_VPS>

# 2. Installation
curl -fsSL https://get.docker.com | sh
apt install docker-compose nginx git -y

# 3. Déploiement
git clone <votre-repo> penguins-project
cd penguins-project
docker-compose -f docker-compose-sharded.yml up -d

# 4. Configuration Nginx (voir section dédiée)

# 5. Test
curl http://localhost:8000/api/health

# 6. Accès
# Frontend: http://<VOTRE_IP_VPS>
# API: http://<VOTRE_IP_VPS>/api
```

**C'est prêt !** 🚀
