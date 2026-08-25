# Direction artistique et expérience

## Intention

Une interface calme, rassurante et lisible pour la personne accompagnée, avec une gestion dense mais claire pour l aidant. Le principe historique est une navigation linéaire, du texte de 16 px minimum et un maximum de trois actions sur l écran de réponse.

| Élément | Décision documentée |
| --- | --- |
| Palette | bleu pour actions, vert pour effectué, orange pour reporté, rouge pour impossible |
| Typographie | titres 24 px gras, corps 16 px minimum, boutons 18 px |
| Zones tactiles | boutons 56 px minimum et cibles 44 x 44 px minimum |
| Contraste | objectif WCAG AA déclaré, audit visuel à refaire sur appareils |
| Motion | retours courts et non bloquants ; respecter `prefers-reduced-motion` lors de toute évolution |

## États obligatoires

Chaque écran doit traiter chargement, vide, erreur réseau, succès, action désactivée et focus accessible. La liste des rappels et le pillulier nécessitent une information claire si la synchronisation est inconnue. Les captures et tests sur iOS et Android restent à produire avant une nouvelle livraison.
