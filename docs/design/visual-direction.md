---
last_updated: 2026-11-19
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

Le mobile est prioritaire; les zones tactiles sont grandes et les libellés accessibles. Le contraste WCAG reste à vérifier sur les écrans. Les écrans chargent les données nécessaires au parcours courant et évitent les animations bloquantes.

## Validation visuelle

Captures de référence disponibles : appairage (`docs/img/03-User-Pairing.png`), réponse à un rappel (`docs/img/14-Reminder-Action.png`) et accueil accompagné (`docs/img/13-User-Home.png`). Ce sont des maquettes sans date ni version; elles ne prouvent pas le rendu courant sur appareil.

Revue statique frontend et QA du 2026-11-19 :

- La réponse au rappel présente trois actions et associe libellés et icônes.
- Les onglets actifs de `UserTabs.tsx` et `CaregiverTabs.tsx` utilisent des libellés de 12 px, sous le minimum de 16 px du cahier. Des erreurs à 12 px et d'autres textes de 13 à 15 px sont aussi présents dans plusieurs écrans et modales.
- Le texte blanc sur le vert `#4CAF50` atteint 2,78:1 et sur l'orange `#FF9800` 2,16:1. Ces rapports sont sous 3:1 même pour le texte large de 26 px. Le lien `#4A90E2` sur blanc atteint 3,29:1, sous 4,5:1 pour son texte de 16 px.
- Le lien de retour du parcours d'appairage n'a pas de taille minimale ni de marge intérieure garantie; les cibles tactiles doivent être vérifiées au rendu.
- Aucun écran ni parcours de pilulier n'a été trouvé; les tests frontend existants ne couvrent pas les écrans ni leurs critères visuels.
- Les maquettes et le code statique ne vérifient pas les rendus iOS et Android, le responsive, l'agrandissement du texte ni les états de chargement et d'erreur sur appareil.

Parcours partiellement examinés : appairage, réponse effectuée/reportée/impossible et accueil accompagné. Revue indépendante visuelle complète : à effectuer après correction et preuves rendues. La carte Trello MVP-008 suit ces écarts. Le dossier reste `review`.
