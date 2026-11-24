---
last_updated: 2026-11-19
---
# Journal qualité, bugs et risques

## Règle de fonctionnement

Ce journal est le registre unique et chronologique des défauts, bugs, vulnérabilités, écarts de conception, régressions, résultats d audit et corrections. Tous les agents concernés lisent le journal avant leur audit et ajoutent ou mettent à jour les entrées dans le même work item. Les rapports spécialisés peuvent détailler une analyse, mais aucune anomalie ne doit exister uniquement dans un rapport isolé.

## Statuts autorisés

`open`, `in-progress`, `fixed`, `verified`, `accepted-risk`, `wont-fix`, `duplicate`, `blocked`.

Une entrée `fixed` n est pas résolue tant qu une preuve de vérification indépendante ne l a pas fait passer à `verified`. Une entrée `accepted-risk` exige une décision humaine identifiée, une échéance de révision et une mesure de réduction du risque.

## Registre principal

| ID | Date | Source | Catégorie | Gravité | Composant | Description et impact | Preuve | Responsable | Work item ou commit | Correction | Vérification | Statut | Date de clôture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QJ-001 | 2026-09-29 | initialisation | outillage | moyenne | scripts de contexte | Python système ne fournit pas `tomllib`; contexte et résolution de modèle échouent | sortie de `doctor.sh` et scripts | coordinateur | 2026-09-29-onboarding-reprise | utiliser un Python compatible ou documenter l'alternative | relecture et exécution des scripts | blocked | |
| QJ-002 | 2026-09-29 | conception | gouvernance | élevée | production | rétention, sauvegardes, qualification réglementaire et push réel non validés | PROJECT-BRIEF.md, design docs | demandeur | 2026-09-29-onboarding-reprise | obtenir décisions humaines avant production | audit conformité et validation demandeur | open | |
| QJ-003 | 2026-09-29 | audit de code | bug | critique | backend/authentication_schema.py | f-string invalide empêchant l'analyse et l'import du backend | compileall avant correction | coordinateur | 2026-09-29-full-code-audit | remplacer la construction invalide par une concaténation valide | compileall et Ruff ciblé réussis | verified | 2026-09-29 |
| QJ-004 | 2026-09-29 | audit de code | bug | élevée | backend/api/authentication.py | dépendance `require_caregiver_role` utilisée avant sa définition, provoquant une erreur d'import | import backend avant correction | coordinateur | 2026-09-29-full-code-audit | déplacer la dépendance avant les routes | import atteint désormais l'initialisation DB; pytest reste bloqué par PostgreSQL absent | verified | 2026-09-29 |
| QJ-005 | 2026-09-29 | audit de code | qualité/test | moyenne | frontend | script lint absent, erreurs TypeScript et dépendance Jest manquante | npm lint/tsc/tests avant correction | coordinateur | 2026-09-29-full-code-audit | ajouter le script lint et babel-jest, corriger les types et erreurs ESLint | ESLint, tsc et 16 suites/219 tests réussissent | verified | 2026-09-29 |
| QJ-006 | 2026-09-29 | audit de code | test/exploitation | élevée | backend/tests | tests backend non exécutables localement sans PostgreSQL; Docker daemon indisponible | pytest avec variables d'environnement éphémères | coordinateur | 2026-09-29-full-code-audit | exécuter la suite dans Docker/CI avec PostgreSQL disponible | bloqué par connexion refusée sur localhost:5432 | blocked | |
| QJ-007 | 2026-09-29 | audit de dépendances | sécurité | élevée | frontend | npm signale 13 vulnérabilités résiduelles, dont 2 élevées et 11 modérées, dans image-size/PostCSS et la chaîne Expo | sortie npm audit après `npm audit fix` | coordinateur | 2026-09-29-full-code-audit | appliquer les mises à jour non cassantes; planifier la montée Expo 57 séparément | 24 vulnérabilités corrigées; le reliquat nécessite une mise à niveau majeure Expo | open | |
| QJ-008 | 2026-09-29 | audit de code | test/contrat | moyenne | backend | quatre tests révélaient des attentes obsolètes ou un message d'erreur incohérent | suite Docker initiale: 162 passed, 4 failed | coordinateur | 2026-09-29-full-code-audit | aligner le message API, fournir le mot de passe courant pour les changements sensibles et corriger les données de test invalides | suite Docker finale: 166 passed | verified | 2026-09-29 |
| QJ-009 | 2026-11-19 | revue visuelle initialisation | accessibilité | élevée | frontend mobile | onglets sous 16 px, contrastes insuffisants et parcours pilulier non attesté | revues frontend/QA statiques et captures docs/img; détails dans design/visual-direction.md et MVP-008 | équipe produit | 2026-09-29-onboarding-reprise | corriger les écarts dans MVP-008 et fournir des rendus iOS/Android | revue QA indépendante après corrections; aucune modification de code dans cette initialisation | open | |

## Fiche détaillée obligatoire pour les niveaux élevé et critique

### QJ-002

- Détecté par : coordinateur
- Date et contexte : 2026-09-29, revue de conception
- Catégorie : bug, sécurité, conception, performance, accessibilité, test, documentation ou exploitation
- Gravité et justification : élevée, données sensibles et diffusion production concernées
- Actifs, utilisateurs ou composants affectés : profils, médication, journal, notifications
- Scénario reproductible : consulter le cahier; les décisions sont explicitement inconnues
- Preuves conservées : PROJECT-BRIEF.md et docs/design
- Cause racine ou hypothèse : décisions de production non encore fournies
- Correction choisie et alternatives écartées : conserver le périmètre et bloquer la production; ne pas inventer de politique
- Tests de non régression : non applicable avant décision
- Vérification indépendante : à effectuer par conformité et demandeur
- Risque résiduel et décision humaine éventuelle : décision humaine obligatoire

### QJ-009

- Détecté par : revues statiques frontend et QA
- Date et contexte : 2026-11-19, revue de complétude de conception
- Catégorie : accessibilité, conception et test
- Gravité et justification : élevée, les tailles de texte et contrastes observés contredisent les exigences explicites du cahier
- Actifs, utilisateurs ou composants affectés : personnes accompagnées et aidants; navigation mobile, réponse aux rappels et parcours pilulier
- Scénario reproductible : inspecter les styles d'onglets et de réponse au rappel; recalculer les ratios depuis les couleurs source
- Preuves conservées : docs/design/visual-direction.md, captures sous docs/img/, carte Trello MVP-008
- Cause racine ou hypothèse : la direction visuelle et l'implémentation n'ont pas encore été rapprochées par une validation rendue
- Correction choisie et alternatives écartées : conserver les constats ouverts dans MVP-008; aucune modification de code produit dans ce work item
- Tests de non régression : non exécutés; revues en lecture seule
- Vérification indépendante : à effectuer après corrections avec rendus iOS/Android et contrôle des seuils d'accessibilité
- Risque résiduel et décision humaine éventuelle : readiness reste review; la livraison visuelle doit attendre les preuves et corrections
