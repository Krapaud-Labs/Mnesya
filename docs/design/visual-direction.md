---
last_updated: 2026-09-29
---
# Direction artistique et expérience visuelle

## Statut et intention

Statut : review

L'interface doit être calme, lisible et rassurante, avec une hiérarchie évidente pour une personne accompagnée et son aidant.

## Références et anti-références

- Références : interfaces de santé accessibles, sobres et à fort contraste
- Anti-références : interfaces denses, alarmistes ou dépendantes de la couleur seule
- Différenciation attendue : réponse à un rappel en trois actions maximum

## Système visuel

| Élément | Décision | Justification produit | Exemple ou token |
| --- | --- | --- | --- |
| Palette | neutres chauds, bleu de confiance, états distincts | lisibilité et calme | contraste WCAG à vérifier |
| Typographie | système natif, corps minimum 16 px | lecture mobile | `fontSize >= 16` |
| Espacement | grille 8 px, zones tactiles larges | réduit les erreurs | minimum 44 px ciblé |
| Formes et profondeur | cartes simples, ombres discrètes | hiérarchie sans surcharge | rayon modéré |
| Iconographie et illustration | icônes accompagnées de libellés | ne dépend pas de la couleur | états texte + icône |

## Composants, états et motion

Documenter les composants réutilisables, les états loading, vide, erreur, succès, focus et désactivé. Décrire les transitions, durées, courbes, déclencheurs et comportement avec `prefers-reduced-motion`.

Les composants couvrent loading, vide, erreur, succès, focus et désactivé. Les transitions sont courtes et supprimées ou réduites lorsque l'utilisateur demande moins d'animation.

## Responsive, accessibilité et performance

Le mobile est prioritaire; les zones tactiles sont grandes, les libellés accessibles et le contraste vérifié. Les écrans chargent les données nécessaires au parcours courant et évitent les animations bloquantes.

## Validation visuelle

Captures attendues : parcours appairage, réponse à un rappel, pilulier
Parcours vérifiés : appairage, effectuée/reportée/impossible, navigation aidant
Auditeur : à désigner
Date : 2026-09-29
