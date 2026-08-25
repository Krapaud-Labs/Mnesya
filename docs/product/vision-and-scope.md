# Vision, objectifs et périmètre

## Contexte

Mnesya aide une personne accompagnée à suivre ses rappels quotidiens. Un aidant crée les profils, programme les rappels et consulte les réponses. La valeur recherchée est la réduction des oublis sans surcharge cognitive ni parcours complexe.

## Acteurs

| Acteur | Besoin | Accès |
| --- | --- | --- |
| Personne accompagnée | recevoir, comprendre et répondre à un rappel | profil appairé, lecture et réponse |
| Aidant | gérer plusieurs profils et suivre les statuts | compte authentifié, droits de propriété |
| Conseiller technique | valider l architecture et les livraisons | revue sans accès produit implicite |

## Objectifs actifs

| Objectif | Indicateur | Preuve attendue |
| --- | --- | --- |
| Fiabiliser le produit déployé | suites et contrôles exécutables | sortie de tests, journal qualité et déploiement vérifié |
| Garder un parcours accessible | texte 16 px minimum, grandes zones tactiles, trois actions maximum pour la réponse | revue visuelle sur appareil |
| Préserver le suivi aidant | création, envoi, réponse et historique cohérents | scénario de bout en bout |

## Périmètre actuel

Authentification aidant, profils, appairage par code, rappels unitaires et récurrents, réponses effectuée, reportée ou impossible, notifications push, journal d activité et pillulier sont présents dans le dépôt. Les rappels récurrents et le pillulier sont des évolutions postérieures au MVP initial.

## Hors périmètre et limites

Pas de promesse de diagnostic médical, de disponibilité clinique, de support hors ligne, de réinitialisation de mot de passe, de statistiques avancées, de messages vocaux ou de widget. La qualification réglementaire, la rétention et le rôle légal des données doivent être validés avant diffusion élargie.

## Contraintes

Application iOS et Android, API FastAPI et PostgreSQL déployées sur VPS, Docker Compose comme environnement de référence. Les données de profil, routine et médication sont traitées comme sensibles par précaution. Maintenance et preuves de régression passent avant les nouvelles fonctions.
