# Contrats API

## Conventions

L API utilise JSON sur HTTPS, des UUID et des dates ISO 8601 UTC. Les endpoints protégés utilisent `Authorization: Bearer <token>`. Les erreurs sont renvoyées sous la forme `{ "detail": "..." }`. Les limites observées sont 3 inscriptions et 5 connexions par minute, avec limitation de vérification d appairage.

## Domaines publics

| Domaine | Opérations | Autorisation |
| --- | --- | --- |
| `/api/auth` | inscription, connexion, profil, refresh, logout | public ou aidant selon opération |
| `/api/users` et `/api/caregivers` | profils et mises à jour | aidant propriétaire, ou utilisateur pour `/me` |
| `/api/pairing` | génération, vérification et refresh | aidant ou code temporaire |
| `/api/reminder` et `/api/reminder-status` | rappels, statuts, historique, activité | propriétaire ou utilisateur appairé |
| `/api/push-tokens` | enregistrement de terminal | jeton valide |
| `/api/medication` | pillulier et semaine | aidant propriétaire ou utilisateur autorisé |

## Contrat critique : appairage

`POST /api/pairing/verify` accepte un code. Un code inconnu, expiré ou consommé est refusé. En cas de succès, la réponse fournit l identifiant utilisateur, les informations de profil minimales, un jeton Bearer et sa durée. Le code doit être consommé de manière atomique.

## Compatibilité

La documentation API historique indique encore une durée de jeton utilisateur de 90 jours et une absence de révocation, tandis que le code actuel montre 14 jours pour le jeton d appairage et une révocation serveur. Toute modification de client doit s appuyer sur le code et des tests, pas sur cette documentation historique seule.
