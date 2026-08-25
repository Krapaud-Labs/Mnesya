# User stories et critères

| ID | Priorité | Story | Critères vérifiables | Statut |
| --- | --- | --- | --- | --- |
| US-001 | Must | En tant qu aidant, je crée un compte pour gérer des profils. | email unique, mot de passe validé, réponse sans hash exposé. | Implémenté, tests à revalider. |
| US-002 | Must | En tant qu aidant, je crée et consulte un profil accompagné. | création réservée à l aidant, accès refusé hors propriété. | Implémenté. |
| US-003 | Must | En tant qu aidant, je génère un code pour appairer un appareil. | code temporaire, usage unique, tentatives limitées. | Implémenté, durée documentaire divergente. |
| US-004 | Must | En tant que personne accompagnée, je réponds à un rappel. | statuts effectuée, reportée et impossible sont persistés et visibles par l aidant. | Implémenté. |
| US-005 | Must | En tant qu aidant, je programme un rappel. | validation des champs, propriété vérifiée, notification planifiée. | Implémenté. |
| US-006 | Should | En tant qu aidant, je consulte l activité récente. | seules mes personnes accompagnées apparaissent. | Implémenté. |
| US-007 | Should | En tant qu aidant, je gère un traitement. | médication liée au profil et rappels générés. | Implémenté, à revalider. |

## Cas limites

Code expiré ou consommé : refus sans appairage. Jeton invalide ou révoqué : `401`. Ressource hors propriété : `403`. Notification non reçue : le statut ne doit pas être présenté comme confirmé. Une réponse utilisateur erronée ne peut pas être annulée actuellement, limitation connue.

## Exigences transverses

Les écrans destinés aux personnes accompagnées privilégient contraste, texte lisible et actions limitées. Les endpoints protégés exigent un jeton et les secrets restent hors dépôt. Les tests et la revue visuelle restent des preuves requises avant livraison.
