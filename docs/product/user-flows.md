# Parcours critiques

## Appairage et réponse

```mermaid
flowchart TD
  A[Aidant authentifié] --> B[Crée profil et code]
  B --> C{Code valide et inutilisé}
  C -->|oui| D[Appareil appairé et jeton utilisateur émis]
  C -->|non| E[Refus et demande d un nouveau code]
  D --> F[Réception d un rappel]
  F --> G{Réponse utilisateur}
  G -->|effectuée| H[Statut DONE]
  G -->|reportée| I[Statut POSTPONED et reprise]
  G -->|impossible| J[Statut UNABLE et alerte aidant]
```

## Gestion par l aidant

L aidant se connecte, crée ou sélectionne un profil dont il est propriétaire, crée ou modifie un rappel, puis consulte les statuts et l activité. Une authentification invalide, un UUID invalide ou un profil non détenu doit interrompre le parcours sans divulguer la donnée.

## Reprise

Le code expiré impose une nouvelle génération. Une notification manquée ne prouve pas une action utilisateur. L absence de support hors ligne est une limite ouverte : l interface doit signaler l erreur au lieu de confirmer une opération non synchronisée.
