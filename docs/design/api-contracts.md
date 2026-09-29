---
last_updated: 2026-09-29
---
# Contrats d interfaces

## Conventions communes

API REST/JSON sur HTTPS, réponses UTF-8 et erreurs structurées. Les routes protégées exigent un JWT non révoqué; les contrôles de propriété sont appliqués côté API. Les listes sont paginées si nécessaire. Les mutations acceptent un identifiant d'idempotence et renvoient 4xx pour entrée invalide ou ressource non autorisée. `/health` est public et ne divulgue aucun secret.

## API, événements et interfaces partagées

| ID | Consommateur | Opération ou événement | Entrée validée | Sortie ou erreur | Autorisation | Tests |
| --- | --- | --- | --- | --- | --- | --- |
| API-001 | Mobile | `GET /health` | aucune | `{ "status": "ok" }` ou 503 | public | pytest |
| API-002 | Aidant | profils, appairage, rappels et pilulier | schémas Pydantic, JWT | ressource ou erreur structurée | propriétaire aidant | pytest + intégration |
| API-003 | Accompagné | réponse effectuée/reportée/impossible | action, rappel, JWT | état et journal | profil appairé | pytest + Jest |
| API-004 | Service push | notification de rappel | événement interne minimal | statut de remise | service interne | test d'adaptateur |

## Exemple de contrat critique

```json
{
  "status": "ok"
}
```

## Compatibilité et dépréciation

Les contrats existants du MVP restent compatibles. Toute rupture exige une version explicite, une migration Alembic et une période de compatibilité mobile. Les champs sensibles ne sont jamais ajoutés à un payload push sans décision de sécurité documentée.
