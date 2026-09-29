---
last_updated: 2026-09-29
---
# User stories, règles métier et critères d acceptation

## Convention

Chaque story suit la forme : En tant que `<acteur>`, je veux `<action>`, afin de `<valeur>`. Les critères couvrent le succès, les validations, les erreurs, les permissions et les cas limites.

## Backlog priorisé

| ID | Priorité | User story | Règles métier | Critères d acceptation vérifiables | Tests ou preuve | Statut |
| --- | --- | --- | --- | --- | --- | --- |
| US-001 | haute | En tant qu'aidant, je veux créer un profil et l'appairer afin de programmer des rappels | seul le propriétaire accède au profil; code temporaire | création, appairage valide, code invalide et accès refusé testés | pytest + parcours mobile | MVP |
| US-002 | haute | En tant qu'aidant, je veux créer un rappel afin de suivre une routine | récurrence validée, notification minimale | rappel unitaire/récurrent et modification testés | pytest + push mock | MVP |
| US-003 | haute | En tant que personne accompagnée, je veux répondre à un rappel afin d'indiquer mon état | trois choix maximum, action idempotente | effectuée, reportée et impossible journalisés | Jest + pytest | MVP |
| US-004 | moyenne | En tant qu'aidant, je veux consulter le journal et le pilulier afin de suivre les réponses | données limitées au propriétaire | historique et états cohérents | pytest | MVP |

## Scénarios d erreur et cas limites

| Référence | Situation | Comportement attendu | Message ou retour | Test associé |
| --- | --- | --- | --- | --- |
| ERR-001 | code invalide ou expiré | refuser sans divulguer de profil | message de reprise | test appairage |
| ERR-002 | ressource d'un autre propriétaire | 403/404 selon contrat, aucune donnée | accès refusé | test ownership |

## Exigences non fonctionnelles liées

Les stories exigent validation d'entrée, ownership, révocation JWT, minimisation des push, textes d'au moins 16 px, zones tactiles larges et tests iOS/Android via CI ou environnement outillé.
