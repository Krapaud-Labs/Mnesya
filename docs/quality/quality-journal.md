# Journal qualité et risques

| ID | Date | Catégorie | Gravité | Description | Preuve | Statut |
| --- | --- | --- | --- | --- | --- | --- |
| QJ-001 | 2026-09-21 | supervision | élevée | `/health` est documenté mais absent du code et retourne `404` en production. | requête HTTPS publique et recherche dans le dépôt | open |
| QJ-002 | 2026-09-21 | tests frontend | élevée | Jest ne démarre plus car le preset React Native est séparé et non configuré. | `npm test -- --runInBand` | open |
| QJ-003 | 2026-09-21 | tests backend | moyenne | validation Docker non exécutée localement, moteur Docker indisponible lors de l audit. | sortie Docker CLI | blocked |
| QJ-004 | 2026-09-21 | documentation | moyenne | durées de jeton, révocation, versions et migrations divergent entre documents et code. | comparaison README, API, audit et code | open |

Une correction ne passe à `verified` qu après preuve indépendante. Les entrées de sécurité historiques doivent être relues contre le code actuel avant d être considérées comme fermées.
