# Audit complet du projet Mnesya

Date : 2026-09-28
Périmètre : dépôt courant, documentation, configuration Docker, tests, sécurité, CI et exploitation.
Statut : audit initial, aucune correction produit appliquée pendant l'audit.

## Résumé

Le MVP est présent dans le dépôt et le périmètre fonctionnel est documenté. La livraison n'est toutefois pas prouvée : l'environnement local ne fournit pas npm, la CI produit n'exécute pas les tests, `/health` est absent, le fichier `frontend/google-services.json` est suivi par Git, et plusieurs sujets de sécurité, rétention et exploitation restent ouverts.

## Constats et cartes

| ID | Constat vérifié | Priorité | Carte |
| --- | --- | --- | --- |
| AUD-001 | Aucune CI produit de tests ; le workflow présent synchronise seulement le kit et utilise un runner self-hosted | critique | CI gratuite reproductible |
| AUD-002 | `frontend/package.json` n'expose pas de script `lint` et npm est indisponible dans l'environnement courant | haute | Outillage frontend et lint |
| AUD-003 | L'API expose `/` mais pas `/health`, alors que la documentation et la roadmap l'attendent | haute | Supervision API |
| AUD-004 | `frontend/google-services.json` est suivi par Git et doit être qualifié ou retiré selon son contenu | critique | Secrets et fichiers mobiles |
| AUD-005 | Les tests Compose contiennent des identifiants de test codés en clair ; ils doivent rester strictement isolés et contrôlés | haute | Hygiène des environnements de test |
| AUD-006 | Les migrations et la création automatique de tables doivent être vérifiées sur base vide et avec rollback | haute | Migrations et restauration |
| AUD-007 | Aucun parcours de récupération de mot de passe n'est disponible | moyenne | Récupération de compte |
| AUD-008 | La réception push réelle, les erreurs et les escalades ne sont pas prouvées sur appareil | haute | Fiabilité des notifications |
| AUD-009 | La rétention, l'effacement, les sauvegardes VPS et les droits infrastructure ne sont pas établis | critique | Données sensibles et conformité |
| AUD-010 | La suite backend est riche mais n'est pas exécutée dans cette session ; la suite mobile n'est pas exécutée faute de npm | haute | Régression reproductible |
| AUD-011 | Les parcours E2E et la revue visuelle accessibilité restent à prouver sur appareil | haute | E2E et accessibilité |
| AUD-012 | La documentation contient des divergences historiques et des limites non uniformisées | moyenne | Documentation de référence |
| OPT-001 | Le worker APScheduler et les requêtes de rappels doivent être profilés sur les index et le volume réel | moyenne | Performance du scheduler |
| OPT-002 | La configuration CORS et les hôtes de production sont codés en dur | moyenne | Configuration par environnement |
| OPT-003 | La supervision doit inclure logs structurés, métriques minimales et alertes exploitables | moyenne | Observabilité |
| OPT-004 | Les dépendances backend/frontend doivent être auditées et mises à jour avec compatibilité Expo vérifiée | moyenne | Maintenance des dépendances |

## Preuves collectées

- `frontend/package.json` contient Jest mais pas de script `lint`.
- `npm test` ne peut pas démarrer : commande `npm` absente de l'environnement courant.
- `docker compose -f docker/docker-compose.test.yml config` réussit.
- Le seul workflow produit visible est `.github/workflows/update-workspace-kit.yml`, sur runner self-hosted, sans tests applicatifs.
- `backend/app/main.py` expose `/` et aucun `/health`.
- `frontend/google-services.json` est suivi par Git.
- Les documents `docs/known-issues.md`, `docs/security-audit.md`, `docs/design/*` et `docs/delivery/roadmap.md` confirment les risques de rétention, notifications, récupération de compte et rollback.
- `bash .codex/scripts/doctor.sh` réussit ; `preflight.sh` échoue localement car Python ne fournit pas `tomllib`.

## Limites de l'audit

Les tests applicatifs, l'analyse de dépendances en ligne, l'exécution mobile sur appareil et la validation de production n'ont pas été simulés. Ils sont donc transformés en cartes et restent non vérifiés.
