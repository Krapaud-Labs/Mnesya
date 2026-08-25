# Conception de sécurité

## Actifs et contrôles

| Actif | Menace | Contrôles observés |
| --- | --- | --- |
| Comptes aidants | force brute, vol de session | bcrypt, JWT signé, limites de débit, révocation |
| Profils et rappels | accès inter profils | contrôles de propriété dans les routes |
| Codes d appairage | devinette ou réutilisation | génération cryptographique, expiration, usage unique, limite de vérification |
| Secrets et base | fuite de dépôt ou d infrastructure | variables d environnement, `.env` ignorés |
| API publique | injection et exposition | validation Pydantic, ORM, HTTPS et en-têtes de sécurité |

## Menaces résiduelles

La perte de mot de passe n a pas de parcours de récupération. La réception de notification sur appareil n est pas prouvée par les tests serveur. La conservation, les sauvegardes et les droits d accès VPS ne sont pas documentés comme preuves. La présence de données de médication impose une revue de conformité et de rétention avant diffusion étendue.

## Exigences de livraison

Ne jamais versionner de secret. Vérifier les droits de propriété sur chaque nouvelle route. Tester rejet, accès non autorisé et cas nominal. Maintenir les dépendances, les migrations et les journaux sans identifiants personnels. Toute action de production ou changement de données sensibles exige une validation humaine et un plan de retour.
