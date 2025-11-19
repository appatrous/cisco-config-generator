# Legacy Code Archive

Ce répertoire contient les anciennes versions du code qui ont été remplacées par la version v2.0 refactorisée.

## Fichiers Archivés

### `app_v1_legacy.py` (1776 lignes)
- **Version**: v1.0 (monolithique)
- **Date d'archivage**: 2025-11-19
- **Raison**: Remplacé par l'architecture modulaire v2.0

**Caractéristiques v1.0**:
- Application Flask monolithique
- Toutes les routes dans un seul fichier
- Stockage dans fichiers texte
- Pas d'authentification
- Pas de base de données
- SECRET_KEY hardcodé

**Remplacé par** (v2.0):
- `app.py` - Application modulaire avec blueprints
- `app_api.py` - API REST avec JWT
- `routes/` - Blueprints Flask séparés
- `services/` - Business logic layer
- `schemas/` - Validation Pydantic
- PostgreSQL + SQLAlchemy
- Celery + Redis
- Tests complets (>50% coverage)

## Migration

Pour migrer depuis v1.0 vers v2.0, consultez **[MIGRATION.md](../MIGRATION.md)**.

## Utilisation (si nécessaire pour rollback)

```bash
# ATTENTION: Ne pas utiliser en production !
# Uniquement pour référence ou rollback d'urgence

# Démarrer l'ancienne version
python legacy/app_v1_legacy.py
```

## Différences Principales

| Aspect | v1.0 (Legacy) | v2.0 (Actuel) |
|--------|---------------|---------------|
| **Fichier principal** | 1776 lignes | 60 lignes (app.py) |
| **Architecture** | Monolithique | Modulaire (35+ fichiers) |
| **Base de données** | Fichiers texte | PostgreSQL |
| **Auth** | Aucune | JWT + Multi-tenant |
| **Validation** | Manuelle | Pydantic |
| **Tests** | Minimaux | >50% coverage |
| **CI/CD** | Aucun | GitHub Actions |
| **Sécurité** | Secrets hardcodés | Variables d'environnement |

## Changelog

### 2025-11-19 - Phase 1 Refactoring
- ✅ Architecture modulaire avec blueprints
- ✅ Validation Pydantic
- ✅ Secrets externalisés
- ✅ Tests complets
- ✅ CI/CD GitHub Actions
- ✅ Documentation complète

## Support

- Pour la v2.0 : Voir [README.md](../README.md)
- Pour la migration : Voir [MIGRATION.md](../MIGRATION.md)
- Pour le développement : Voir [DEVELOPMENT.md](../DEVELOPMENT.md)

---

**⚠️ AVERTISSEMENT**: Le code legacy n'est plus maintenu et ne doit pas être utilisé en production.
