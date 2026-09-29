---
last_updated: 2026-09-29
---
# Parcours utilisateur

## Inventaire des parcours

| ID | Déclencheur | Acteur | Résultat attendu | Échecs et reprises | Stories liées |
| --- | --- | --- | --- | --- | --- |
| FLOW-001 | aidant démarre un profil | aidant | profil appairé | code invalide, accès refusé | US-001 |
| FLOW-002 | rappel reçu | personne accompagnée | réponse journalisée | push manquant, action répétée | US-002, US-003 |

## Diagramme des parcours critiques

```mermaid
flowchart TD
    A[Utilisateur authentifié] --> B{Profil appairé ?}
    B -->|Non| C[Entrer code]
    C -->|Valide| D[Profil disponible]
    C -->|Invalide| E[Erreur et reprise]
    B -->|Oui| F[Rappel affiché]
    F --> G{Réponse}
    G -->|Effectuée / reportée / impossible| H[Journal mis à jour]
```

Les flux critiques couvrent appairage, réponse à un rappel et persistance du journal.

## Détails par parcours

### FLOW-001

- Préconditions : aidant authentifié et profil non appairé.
- Étapes nominales : créer profil, générer code, saisir code, confirmer appairage.
- Validations et erreurs : code borné et expiré selon règle à confirmer; ownership et erreurs réseau testés.
- Annulation, reprise et persistance : annulation sans création partielle; état persistant après succès.
- Critères de sortie : profil appairé et visible uniquement aux acteurs autorisés.
