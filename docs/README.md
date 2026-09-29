---
last_updated: 2026-09-29
---
# Dossier de conception du projet

## Statut

review, 2026-09-29, coordinateur. Approval remains pending independent audit and human production decisions.

## Rôle

Ce dossier est la source de vérité entre le besoin métier, la conception et le code. Il doit permettre à un développeur, un testeur, un auditeur ou un nouveau membre de comprendre le projet sans déduire des règles implicites.

## Règles de qualité

- Toute affirmation distingue fait vérifié, hypothèse, décision et élément à valider.
- Toute user story possède des critères testables et une priorité.
- Toute interface, donnée sensible, permission, dépendance externe et erreur significative est documentée.
- Chaque diagramme est en Mermaid ou possède une source éditable versionnée.
- Toute évolution modifie, dans le même work item, le code, les tests et les documents touchés.
- Un document non applicable indique `Non applicable` avec une justification contextualisée.

## Index et traçabilité

| Artefact | Finalité | Référence de code ou test | Dernière mise à jour |
| --- | --- | --- | --- |
| Vision et périmètre | besoin, acteurs, limites | `product/vision-and-scope.md` | 2026-09-29 |
| User stories | comportements attendus | `product/user-stories.md` | 2026-09-29 |
| Parcours | étapes et erreurs utilisateur | `product/user-flows.md` | 2026-09-29 |
| Architecture | composants et flux | `design/architecture.md` | 2026-09-29 |
| Données | entités, règles, rétention | `design/data-model.md` | 2026-09-29 |
| Contrats | API, événements, interfaces | `design/api-contracts.md` | 2026-09-29 |
| Sécurité | menaces et protections | `design/security-design.md` | 2026-09-29 |
| Roadmap et décisions | plan et arbitrages | `delivery/roadmap.md`, `delivery/decision-log.md` | 2026-09-29 |
