---
last_updated: 2026-11-19
---
# Tableau Trello du projet

## Paramétrage vérifié

- Nom : Mnesya
- URL : https://trello.com/b/6u9XcCJQ/mnesya
- Identifiant : `ari:cloud:trello::board/workspace/6974b8877e2c8c1b6d6c42f3/6aba1afc0fa60a57630a8d13`
- Workspace : Espace de travail de Mickael MUR
- Dernière activité observée : 2026-11-19T17:46:07.526Z
- État au 2026-11-19 : 15 cartes ouvertes, toutes dans `Ready`; chaque carte possède une checklist de base. MVP-001 a une checklist de base et une détaillée; MVP-008 a cinq éléments ouverts dans sa checklist de base. Aucune étiquette ni assignation de membre n'est présente sur ces cartes.
- La lecture dédiée des checklists a révélé des données que le résumé de `list_by_board` ne retournait pas. La lecture dédiée prévaut.
- Une deuxième checklist détaillée a été créée sur MVP-001 après le résumé incomplet. Elle contient neuf éléments. La checklist d'origine contient quatre éléments et a été renommée `Baseline delivery gates` pour éviter les noms en double.
- La description des cartes déclare des responsables, mais l'API Trello ne retourne aucun membre assigné. Les deux informations ne sont pas équivalentes.

## Listes relues depuis Trello

| Ordre | Liste | Identifiant |
| --- | --- | --- |
| 1 | Inbox | `ari:cloud:trello::list/workspace/6974b8877e2c8c1b6d6c42f3/6aba1b0243ed674a2b8b1a9d` |
| 2 | Ready | `ari:cloud:trello::list/workspace/6974b8877e2c8c1b6d6c42f3/6aba1b03cdffe237eddd3ee1` |
| 3 | In Progress | `ari:cloud:trello::list/workspace/6974b8877e2c8c1b6d6c42f3/6aba1b04a631fd1baaa8aac4` |
| 4 | Blocked | `ari:cloud:trello::list/workspace/6974b8877e2c8c1b6d6c42f3/6aba1b06467b259349429286` |
| 5 | Review | `ari:cloud:trello::list/workspace/6974b8877e2c8c1b6d6c42f3/6aba1b07e70e14f08f2e13bc` |
| 6 | Done | `ari:cloud:trello::list/workspace/6974b8877e2c8c1b6d6c42f3/6aba1b080d7a2fecad13884b` |
| 7 | Archived | `ari:cloud:trello::list/workspace/6974b8877e2c8c1b6d6c42f3/6aba1b0a6f93cda6fcacc86c` |

## Cartes relues depuis Trello

Les descriptions et critères ci-dessous reflètent la lecture distante du 2026-11-19. Les cartes sont toutes dans la liste `Ready`; les identifiants stables et les liens pointent vers les objets relus.

| ID | Phase | Titre | Responsable déclaré | Type | Priorité | Dépendances | Definition of Done et critères d'acceptation | Identifiant et URL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MVP-001 | MVP | Mettre en place une CI gratuite reproductible | Mickael MUR | DevOps | Critical | Aucune | Une CI gratuite exécute lint, tests backend/frontend et rapporte le résultat. Le workflow est versionné, sans secrets, les commandes sont documentées et un échec bloque la livraison. État observé : seul le workflow de synchronisation du kit existe et utilise un runner self-hosted. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1be492322bc561744e0c` · [carte](https://trello.com/c/Iy56VPUq/1-mvp-001-mettre-en-place-une-ci-gratuite-reproductible) |
| MVP-002 | MVP | Rendre l'outillage frontend exécutable | Mickael MUR | Frontend | High | MVP-001 | `npm ci`, lint et Jest sont disponibles et documentés. Le script lint, le preset Expo, le lockfile et la commande reproductible sont vérifiés. État observé : `package.json` n'a pas de script lint et npm était absent lors de l'audit. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1be5a0eb76afbd8fb1cd` · [carte](https://trello.com/c/lH6wFuRj/2-mvp-002-rendre-loutillage-frontend-ex%C3%A9cutable) |
| MVP-003 | MVP | Ajouter le contrat de supervision /health | Jordann Miso | Backend | High | MVP-001 | `/health` et sa documentation reflètent l'état utile de l'API. Vérifier la réponse nominale, le test, Compose et README. État observé : `main.py` expose `/` mais pas `/health`. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1be79ab458b59fc1a482` · [carte](https://trello.com/c/sly3G7DQ/3-mvp-003-ajouter-le-contrat-de-supervision-health) |
| MVP-004 | MVP | Sécuriser les fichiers et secrets mobiles | Mickael MUR | Security | Critical | Aucune | Aucun secret ou fichier sensible non qualifié n'est versionné. Qualifier le contenu, le retirer ou documenter la procédure officielle, activer le secret scanning CI et effectuer une rotation si nécessaire. État observé : `frontend/google-services.json` est suivi par Git. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1be840a448eeb1ab9c84` · [carte](https://trello.com/c/1rCbe4Lr/4-mvp-004-s%C3%A9curiser-les-fichiers-et-secrets-mobiles) |
| MVP-005 | MVP | Isoler les identifiants de test | Jordann Miso | Security | High | MVP-001 | Les tests utilisent des valeurs explicitement non productives et contrôlées. Séparer test et production, documenter et empêcher leur usage en production par un contrôle. État observé : `docker-compose.test.yml` contient des mots de passe de test en clair. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1be925a65cad16b12db0` · [carte](https://trello.com/c/qFwxQhJM/5-mvp-005-isoler-les-identifiants-de-test) |
| MVP-006 | MVP | Valider migrations et restauration | Jordann Miso | Data | High | MVP-001 | Les migrations depuis une base vide, le rollback et la restauration sont prouvés. Ajouter un test de migration, un plan de retour, une stratégie de sauvegarde et une preuve de restauration. État observé : Alembic coexiste avec `create_all` et la stratégie VPS n'est pas documentée. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1beb0f9755a65d2d6255` · [carte](https://trello.com/c/m1KMmTbO/6-mvp-006-valider-migrations-et-restauration) |
| MVP-007 | MVP | Prouver la régression backend et frontend | Jordann Miso | QA | High | MVP-001, MVP-002 | Les suites backend et frontend sont exécutées avec rapports archivés. Vérifier le résultat Docker backend, Jest, la couverture et le journal qualité. État observé : aucune suite n'avait été exécutée dans la session d'audit, npm étant alors indisponible. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1becd46f7a55028d130f` · [carte](https://trello.com/c/XbQhVMDb/7-mvp-007-prouver-la-r%C3%A9gression-backend-et-frontend) |
| MVP-008 | MVP | Valider les parcours E2E et l'accessibilité | Mickael MUR | QA | High | MVP-007 | Appairage, rappel, réponse et erreurs sont validés sur appareil ou émulateur. Vérifier les scénarios E2E, un texte d'au moins 16 px, des zones tactiles d'au moins 44 px, le contraste et la limite de trois actions. Revue statique du 2026-11-19 : l'écran de réponse propose bien trois actions, mais les onglets actifs utilisent 12 px; le texte blanc sur vert `#4CAF50` est à 2,78:1 et sur orange `#FF9800` à 2,16:1; le lien bleu `#4A90E2` sur blanc est à 3,29:1. Les captures sont des maquettes, pas des rendus actuels sur appareil. Le parcours pilulier et les tests au niveau écran ne sont pas présents. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1beead1fd96fe7b4c94e` · [carte](https://trello.com/c/O0ivYRGQ/8-mvp-008-valider-les-parcours-e2e-et-laccessibilit%C3%A9) |
| MVP-009 | MVP | Aligner la documentation de référence | Mickael MUR | Documentation | Medium | MVP-003, MVP-007 | README, API, guide, sécurité, roadmap et changelog décrivent le code vérifié. Résoudre les divergences sur `/health`, les tokens, les notifications et les limites. État observé : des divergences historiques sont recensées dans `known-issues` et `security-audit`. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1befbefd43e05961e142` · [carte](https://trello.com/c/uYCySnKZ/9-mvp-009-aligner-la-documentation-de-r%C3%A9f%C3%A9rence) |
| MVP-010 | MVP | Définir rétention, effacement et conformité | Mickael MUR | Security | Critical | MVP-006 | Le demandeur valide la rétention, l'effacement, les accès VPS et le rôle légal des données. Documenter la décision, la procédure d'effacement, les accès et sauvegardes. État observé : règles absentes; médication et routines sont sensibles par précaution. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1bf027049b652a08cf6c` · [carte](https://trello.com/c/OEnwKpJZ/10-mvp-010-d%C3%A9finir-r%C3%A9tention-effacement-et-conformit%C3%A9) |
| POST-MVP-001 | Post-MVP | Ajouter la récupération de compte | Jordann Miso | Feature | Medium | MVP-004, MVP-010 | La récupération par email est sécurisée et testée, avec expiration, anti-abus, audit et documentation. État observé : aucun parcours de mot de passe oublié. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1bf2b6bf3b14105637ef` · [carte](https://trello.com/c/L2j1CxTn/11-post-mvp-001-ajouter-la-r%C3%A9cup%C3%A9ration-de-compte) |
| POST-MVP-002 | Post-MVP | Fiabiliser les notifications push | Jordann Miso | Backend | High | MVP-007, MVP-008 | L'envoi, les erreurs, les retries, les tokens invalides et l'escalade sont observables. Ajouter test appareil, métriques, retries bornés et journal sans données personnelles. État observé : réception réelle non prouvée et tokens invalides à surveiller. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1bf3e9782f27faf26658` · [carte](https://trello.com/c/hRgBTbSE/12-post-mvp-002-fiabiliser-les-notifications-push) |
| POST-MVP-003 | Post-MVP | Profiler et optimiser le scheduler | Jordann Miso | Performance | Medium | MVP-007 | Les requêtes et index du worker sont mesurés et améliorés sur un volume représentatif. Mesurer p95, justifier les index et vérifier l'absence de doublons. État observé : worker APScheduler pour rappels, statuts et escalades, sans profil récent fourni. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1bf5479a47fa34a10a68` · [carte](https://trello.com/c/hiLLNgNf/13-post-mvp-003-profiler-et-optimiser-le-scheduler) |
| POST-MVP-004 | Post-MVP | Externaliser la configuration et observabilité | Mickael MUR | DevOps | Medium | MVP-003, MVP-010 | CORS, hôtes, logs, métriques et alertes sont configurables par environnement. Vérifier la configuration, les logs structurés, les alertes utiles et l'absence de secrets exposés. État observé : CORS est codé en dur et l'observabilité est peu documentée. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1bf68315f91a3af5ae9c` · [carte](https://trello.com/c/vVsOMAc2/14-post-mvp-004-externaliser-la-configuration-et-observabilit%C3%A9) |
| POST-MVP-005 | Post-MVP | Maintenir les dépendances compatibles | Jordann Miso | DevOps | Medium | MVP-001, MVP-007 | Les dépendances sont auditées et mises à jour de façon compatible, avec changelog. Vérifier CVE, matrice de compatibilité, mise à jour testée et rollback. État observé : les dépendances Expo, React Native, FastAPI et Python exigent une validation coordonnée. | `ari:cloud:trello::card/workspace/6974b8877e2c8c1b6d6c42f3/6aba1bf8091f91491346f54d` · [carte](https://trello.com/c/jeI65MT2/15-post-mvp-005-maintenir-les-d%C3%A9pendances-compatibles) |

## Checklists relues

La lecture dédiée de chaque carte a confirmé une checklist de quatre éléments initiaux, tous incomplets. Les quatre éléments communs sont `Conception et périmètre relus`, `Implémentation ou audit réalisé`, `Validation et preuve collectées` et la mise à jour/relecture de la documentation applicable avant la PR. MVP-008 contient les mêmes éléments dans un ordre différent et un cinquième élément ouvert pour les écarts visuels. MVP-001 en a une seconde, détaillée, de neuf éléments incomplets. Les identifiants relus sont :

| ID carte | ID checklist existante |
| --- | --- |
| MVP-001, Baseline delivery gates | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c18ae34be2c04effb9e` |
| MVP-001, Definition of Done | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aff1dc5d30e5c1a94c0dee7` |
| MVP-002 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c161016a49b358e134b` |
| MVP-003 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c1a7dd711cb0a2607bc` |
| MVP-004 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c19c4c288481c60e46f` |
| MVP-005 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c1c12a09a98f5c3a749` |
| MVP-006 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c1d8b2f4527cc3d8de5` |
| MVP-007 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c1e52a4b19ca248689c` |
| MVP-008 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c20cee0685884e811b1` |
| MVP-009 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c22b6ee91679305d469` |
| MVP-010 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c248d1493d695a92e82` |
| POST-MVP-001 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c25f0adc250186f690a` |
| POST-MVP-002 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c2624277d707498e428` |
| POST-MVP-003 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c28a1fd118c9b52f93d` |
| POST-MVP-004 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c29797a3bf1fa3819a8` |
| POST-MVP-005 | `ari:cloud:trello::checklist/workspace/6974b8877e2c8c1b6d6c42f3/6aba1c2c82826dca38077c13` |

Le cinquième élément de MVP-008 est `Corriger et vérifier le minimum de texte, le contraste, les zones tactiles, le rendu iOS/Android et le parcours pilulier` (ID `ari:cloud:trello::check-item/workspace/6974b8877e2c8c1b6d6c42f3/6aff35df285e818db15bbf46`), état incomplet.

La checklist détaillée de MVP-001, à neuf éléments, est :

- [ ] Conception et contrat concernés mis à jour
- [ ] Code terminé sur une branche dédiée
- [ ] Cas nominal et cas d'erreur vérifiés
- [ ] Sécurité et permissions vérifiées
- [ ] Accessibilité vérifiée si une interface est concernée
- [ ] Documentation et journal qualité mis à jour
- [ ] Revue indépendante effectuée
- [ ] Preuve reproductible ajoutée
- [ ] Pull Request validée selon le flux de livraison

Les checklists distantes sont des suivis de travail, pas des preuves de validation. La carte MVP-010 conserve en outre sa validation humaine de conformité.

## Règles de synchronisation

- Relire Trello avant chaque mise à jour et après chaque écriture.
- Vérifier séparément chaque checklist après sa création, avec son nom, son ordre, ses items et leur état.
- Les responsables écrits dans les descriptions ne prouvent pas qu'un membre est assigné dans Trello.
- L'état local est un relevé daté; toute divergence ultérieure doit être vérifiée à distance.
- Relecture distante Trello MVP-008 du 2026-11-20 09:05 UTC : la description a été remplacée par les résultats actuels (Jest 222, bundle JS iOS) et leurs limites; carte toujours In Progress, cinquième case et validation/preuve . Aucun natif ou lecteur d’écran revendiqué.
