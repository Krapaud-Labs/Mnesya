---
last_updated: 2026-09-29
---
# Roadmap et plan de livraison

## Incréments

| Incrément | Objectif | Stories incluses | Dépendances | Risques | Critères de sortie | État |
| --- | --- | --- | --- | --- | --- | --- |
| MVP maintenance | fiabiliser le produit existant et la CI gratuite | US-001 à US-004 | environnement Python/Node, Docker | outils locaux absents, rétention et push à confirmer | tests, sécurité, docs, audit et rollback | en préparation |

## Plan de validation et retour

Valider localement avec Docker quand les images sont disponibles, sinon en CI gratuite. Exécuter lint, tests, build, sécurité et contrôles d'accessibilité. La production exige validation humaine; rollback par image/commit précédent et `/health` surveillé.

## Écarts de périmètre

Sont reportés la rétention exacte, la qualification réglementaire, les sauvegardes VPS et la preuve de réception push réelle, car ils exigent une décision ou un environnement de production.
