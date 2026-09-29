---
last_updated: 2026-09-29
---
# Vision, objectifs et périmètre

## Contexte et problème

Les rappels quotidiens et la médication sont difficiles à suivre sans coordination. Mnesya donne à l'aidant un suivi simple et à la personne accompagnée une réponse lisible et limitée.

## Parties prenantes et utilisateurs

| Acteur | Besoin | Fréquence | Niveau d accès | Attente de réussite |
| --- | --- | --- | --- | --- |
| Personne accompagnée | répondre aux rappels | quotidienne | réponses à ses rappels | parcours de réponse cohérent |
| Aidant | créer, programmer et consulter | quotidienne | profils et données associés | rappels configurables et journal |
| Conseiller technique | fiabiliser le système | ponctuelle | support technique | santé API et contrôles vérifiables |

## Objectifs mesurables

| Objectif | Indicateur | Valeur cible | Méthode de mesure | Horizon |
| --- | --- | --- | --- | --- |
| Parcours de rappel | réponses effectuée/reportée/impossible fonctionnelles | tests de parcours verts | CI MVP | chaque livraison |
| Fiabilité API | `/health` et ownership vérifiés | tests API | aucun accès croisé | chaque livraison |

## Périmètre de la première version

Authentification aidant, profils, appairage par code, rappels unitaires/récurrents, réponses, push, journal et pilulier. Dépendances : API FastAPI, PostgreSQL, Expo et fournisseur push.

## Hors périmètre et hypothèses

Hors périmètre : diagnostic médical, disponibilité clinique, hors ligne, récupération de mot de passe, statistiques avancées, messages vocaux et widget. Rétention, qualification réglementaire, sauvegardes VPS et réception push réelle restent à confirmer.

## Contraintes et critères de réussite

Plateformes iOS/Android, CI gratuite, texte minimum 16 px, grandes zones tactiles et trois actions maximum. Terminé signifie tests reproductibles, documentation alignée, sécurité et ownership vérifiés, audit indépendant et rollback documenté.
