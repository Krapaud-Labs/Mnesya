---
last_updated: 2026-09-29
---
# Conception de sécurité

## Périmètre et actifs à protéger

| Actif | Propriétaire | Sensibilité | Menace principale | Protection | Preuve |
| --- | --- | --- | --- | --- | --- |
| Données de profil et médication | demandeur | sensible | accès croisé | JWT, propriété API, TLS, base protégée | tests ownership |
| Jetons d'authentification | demandeur | secret | vol ou réutilisation | bcrypt, révocation, variables d'environnement | tests auth |
| Journal d'activité | demandeur | sensible | altération ou fuite | écriture contrôlée, minimisation | tests API |

## Authentification, autorisation et secrets

L'identité aidant est authentifiée par JWT avec bcrypt et révocation. Les ressources sont accessibles uniquement au propriétaire autorisé. Les secrets restent dans les variables d'environnement et ne sont jamais committés. La rotation et la durée exacte des tokens doivent être confirmées avant production.

## Analyse de menaces

| Menace | Vecteur | Impact | Probabilité | Mesure préventive | Détection | Risque résiduel |
| --- | --- | --- | --- | --- | --- | --- |
| IDOR | identifiant d'une autre ressource | élevé | moyenne | contrôles ownership systématiques | tests négatifs | revue indépendante |
| JWT volé | bearer token | élevé | moyenne | révocation, TLS, durée limitée | logs d'anomalies | durée à confirmer |
| fuite push | payload trop riche | élevé | faible | payload minimal | tests adaptateur | fournisseur à vérifier |

## Exigences de sécurité vérifiables

Les entrées sont validées par schémas, les accès sont journalisés sans secrets, les dépendances sont contrôlées et le trafic de production doit être TLS. Le script de baseline sécurité et les tests d'autorisation doivent être exécutés avant livraison. Les sauvegardes et la qualification réglementaire restent ouvertes.
