# JobMatch AI 

> Plateforme intelligente de mise en relation CV/offres d'emploi pour le marché tunisien, propulsée par le NLP et le NER.

##  Architecture

**Modular Monolith** — FastAPI (Python) + Flutter (Mobile) + PostgreSQL + Redis + Celery
##  Stack technique

| Couche | Technologies |
|---|---|
| Mobile | Flutter · Riverpod · Dio · Hive |
| Backend | FastAPI · SQLAlchemy · Alembic · Celery |
| IA / NLP | spaCy · TF-IDF · cosine similarity · pdfplumber |
| Base de données | PostgreSQL · Redis |
| Sécurité | JWT · bcrypt · rate limiting · CORS |
| Infrastructure | Docker · GitHub Actions (CI/CD) |

##  Sécurité

- JWT access token (15min) + refresh token (7j) avec rotation
- bcrypt cost factor 12 pour les mots de passe
- Brute force protection (5 tentatives → lockout 15min via Redis)
- Rate limiting (100 req/min global, 5 req/min sur /auth/login)
- CORS strict avec whitelist des origines
- Vérification magic bytes sur upload PDF

##  Installation

### Prérequis
- Python 3.11+
- Conda
- Docker
- Flutter SDK

### Backend

```bash
# Cloner le repo
git clone https://github.com/hiba255/JobMatch-AI-.git
cd jobmatch-ai

# Créer l environnement Conda
conda create -n jobmatch python=3.11
conda activate jobmatch

# Installer les dépendances
cd backend
pip install -r requirements.txt

# Configurer les variables d environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# Démarrer les services (PostgreSQL + Redis)
docker compose up -d

# Lancer le serveur
uvicorn main:app --reload
```

### Frontend (bientôt)
```bash
cd frontend
flutter pub get
flutter run
```

## Dataset

- **Offres d'emploi** — scraping légal TanitJobs (robots.txt vérifié )
- **CVs** — générateur synthétique tunisien (500+ CVs avec annotations NER)

##  Roadmap

- [x] Architecture & setup
- [x] Modèles PostgreSQL
- [x] Sécurité (JWT + bcrypt)
- [ ] Docker Compose
- [ ] Auth endpoints
- [ ] Pipeline NLP/NER
- [ ] Matching engine
- [ ] Flutter app
- [ ] CI/CD GitHub Actions
- [ ] Déploiement production

