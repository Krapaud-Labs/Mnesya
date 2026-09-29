---
last_updated: 2026-09-29
---
# Tableau Trello du projet

## Paramétrage

- Nom du tableau : Mnesya
- URL : https://trello.com/b/6u9XcCJQ/mnesya
- Mode : tableau complet toujours généré ; synchronisation externe si intégration autorisée
- Responsable du tableau : Mnesya, project owner
- Dernière synchronisation : 2026-09-28, vérifiée

## Membres et rôles

| Membre | Rôle projet | Identifiant Trello | Cartes attribuées |
| --- | --- | --- | --- |
| Mnesya | project owner | ari:cloud:trello::workspace:member/Mnesya | selon cartes |

## Règle de synchronisation

Ce document est la source versionnée du tableau. Chaque carte possède un identifiant stable, un objectif, un périmètre, des dépendances, des critères d acceptation, une estimation, un responsable, une preuve attendue et un lien vers le work item. Le Coordinateur met à jour ce document avant toute création ou modification du tableau externe.

## Listes du tableau

1. Backlog validé
2. Prêt à concevoir
3. Conception en cours
4. Prêt à développer
5. En développement
6. En revue
7. En validation
8. Bloqué
9. Terminé

## Cartes détaillées

| ID | Liste | Feature | Titre | Description détaillée | Dépendances | Critères d acceptation | Preuve | Responsable | Estimation | Priorité |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MVP-001 | Prêt à concevoir | Fiabilisation | Santé API et parcours MVP | Vérifier `/health`, appairage et réponses | audit existant | tests reproductibles et contrats à jour | rapport d'audit | coordinateur | moyen | haute |

### Checklist Definition of Done de chaque carte

- [ ] Conception et contrat concernés mis à jour
- [ ] Code de la feature terminé sur sa branche dédiée
- [ ] Cas nominal et cas d erreur testés
- [ ] Sécurité et permissions vérifiées
- [ ] Accessibilité et responsive vérifiés si frontend
- [ ] Documentation et journal qualité mis à jour
- [ ] Revue indépendante effectuée
- [ ] Preuve reproductible ajoutée
- [ ] Pull Request validée et prête à fusionner

## Checklist de complétude

- Chaque user story du cahier est liée à une ou plusieurs cartes.
- Chaque carte est assez petite pour une branche et des commits atomiques.
- Les tâches de conception, développement, tests, sécurité, documentation et livraison sont présentes.
- Les dépendances et blocages sont explicites.
- Les critères d acceptation sont vérifiables.
- Les cartes terminées référencent une preuve et un identifiant du journal qualité.
