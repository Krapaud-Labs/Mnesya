# Roadmap de maintenance

| Incrément | Objectif | Dépendances | Sortie attendue | État |
| --- | --- | --- | --- | --- |
| M-01 | Réparer et exécuter les tests frontend et backend Docker | moteur Docker, correction preset Jest | résultats reproductibles | planifié |
| M-02 | Aligner supervision et documentation | décision sur `/health` | endpoint ou documentation cohérente | planifié |
| M-03 | Mettre à jour les contrats et risques | M-01 et M-02 | API, guide utilisateur et audit alignés | planifié |
| M-04 | Revue sécurité et livraison | preuves M-01 à M-03 | audit indépendant et plan de retour | planifié |

## Validation et retour

Tester d abord avec `docker-compose.test.yml`, puis valider une instance locale séparée. Toute modification de production doit être précédée d une sauvegarde confirmée, d une migration réversible ou testée, d une vérification HTTPS et d une procédure de retour. La disponibilité VPS et la réception mobile sont des validations distinctes.
