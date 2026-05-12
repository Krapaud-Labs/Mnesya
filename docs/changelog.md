# Changelog — Mnesya

Toutes les modifications notables du projet sont documentées ici.
Format : `emoji vX.Y.Z — Titre` · Auteur · Date

---

## 06/03/2026

### 🏗️ v0.1 — Initialisation du projet

- Structure initiale du projet (frontend + backend + Docker)
- Navigation de base et écrans squelettes (Welcome, Login, Register)
- Documentation technique (README, diagrammes)

---

### 👤 v0.2 — Authentification & Profils (Back)

- API d'authentification caregiver (création de compte, login JWT)
- API utilisateur (création de profil, gestion des données)
- API caregiver (gestion des profils, édition)
- Tests unitaires complets sur les services

---

### 🔗 v0.3 — Pairing & Frontend Auth

- Système de code de pairing (6 chars, valide 24h)
- Intégration frontend ↔ backend (auth, profils, pairing)
- Persistance de session (AsyncStorage + tokenService)
- Logout avec nettoyage du token

---

### 📱 v0.4 — Rappels (Backend)

- API reminders (CRUD complet)
- API reminder status (DONE / POSTPONED / UNABLE / MISSED)
- Réponses enrichies avec noms des utilisateurs
- Cascade delete sur suppression de profil

---

### 📲 v0.5 — Rappels (Frontend)

- Écrans de création et liste des rappels
- Hooks dédiés (useCaregiver, useReminders, useReminderStatus)
- Intégration complète frontend ↔ backend reminders

---

### 🔔 v0.6 — Push Notifications

- Enregistrement / désenregistrement du token push au login/logout
- API backend de gestion des tokens push
- Notifications envoyées à l'utilisateur au moment du rappel
- Scheduler backend : 3 jobs (T+0, T+5, T+10 min) + alerte caregiver automatique

---

### ✨ v0.7 — UX & i18n

- Internationalisation complète FR/EN (i18next)
- Pickers custom cross-platform (date + heure) entièrement traduits
- Refactoring UX/UI global (grands boutons, texte 16px min, 3 boutons max)
- Animations pulse sur le dashboard
- FilterPickerModal pour la sélection de profil/date

---

### ⚙️ v0.8 — DevOps & Sécurité

- Containerisation Docker (frontend + backend)
- Déploiement VPS (Dokploy / Coolify)
- `SECRET_KEY` obligatoire (plus de fallback hardcodé)
- Rate limiting : Register (3/min), Login (5/min)
- Hardening de l'API (headers, CSRF, CORS)

---

### 🔒 v0.9 — Sécurité & Qualité

- Corrections de bugs critiques (tests + prod)
- ESLint v9 configuré → 0 erreurs, 0 warnings
- Optimisations de performance (requêtes scheduler, filtrage)
- Token refresh automatique (silent refresh JWT)

---

### 📊 v1.0 — Activity Log & Finalisation

- Journal d'activité caregiver (48h d'historique, badge non-lu)
- RateLimitModal (HTTP 429 → modale orange)
- Fonctionnalité Postpone sur les rappels
- Slow API / anti-flood backend
- 12 écrans opérationnels, 100% connectés front ↔ back
- Support bilingue complet sur tous les pickers et modales

---

### 🔐 v1.1 — Révocation JWT (Logout serveur)

- Claim `jti` (UUID v4) ajouté à chaque token généré
- Table `revoked_token` en base (`jti` + `revoked_at`, indexée)
- Migration Alembic `004_add_revoked_tokens_table`
- `POST /api/auth/logout` → retourne 204, blackliste le `jti`
- `verify_token` vérifie en base que le `jti` n'est pas révoqué → 401 si révoqué
- Tout appel avec un token après logout est rejeté, même si le token n'est pas encore expiré
- Job scheduler toutes les heures : nettoyage automatique des anciens `jti` révoqués
- Tests : `test_logout_revokes_token` vérifie qu'un token révoqué est bien rejeté sur `/api/auth/me`

---

### 🐛 v1.1.1 — Corrections scheduleur & notifications push

#### Backend — Scheduler

- `window_seconds` réduit de 90s → 55s : une seule fenêtre par tick CronTrigger, fini les doubles notifications
- `postpone_reminder()` : `scheduled_at` tronqué à la minute entière (`.replace(second=0, microsecond=0)`) → le tick CronTrigger capture désormais le reminder reporté exactement à la bonne minute
- `get_reminders_due_now()` : correction d'un `return` manquant dans la query filtrée (la requête n'était jamais retournée)

#### Frontend — Push notifications

- Correction `reminderId` (camelCase) → `reminder_id` (snake_case) dans `App.tsx` pour coller au payload backend → le `PUT /api/reminder/:id/postpone` ne tapait plus sur `undefined`

#### Frontend — UI

- `ActivityLogModal` : ajout de l'effet de flou de scroll + flèche chevron (identique aux autres listes) — disparaît automatiquement quand on atteint le bas de la liste

---

## 18/03/2026

### 🐛 v1.1.2 — Correction de navigation post-notification

#### Frontend — Notifications

- Correction de la redirection suite au clic sur une notification native OS : l'application navigue désormais correctement vers le bon écran au lieu de rester sur l'écran d'accueil

---

### 🐛 v1.1.3 — Corrections UX (Frontend)

#### Frontend — UI

- Corrections d'interface suite aux retours utilisateurs

---

### 🚀 v1.1.5 — Build TestFlight iOS

#### Infrastructure

- Premier build distribué via TestFlight pour les tests internes iOS

---

### ✨ v1.1.6 — Auto-refresh des données

#### Frontend — Data

- Ajout du rafraîchissement automatique des données côté Caregiver et côté User : les écrans se mettent à jour sans action manuelle de l'utilisateur

---

### 🐛 v1.1.7 — Correction marges boutons de réponse (User)

#### Frontend — UI

- Correction du margin côté User pour les boutons de réponse des reminders (Done / Remind later / Unable)

---

## 19/03/2026

### ⚡ v1.1.8 — Performance auto-refresh

#### Frontend — Data

- Correction et amélioration des performances du mécanisme d'auto-refresh : réduction des re-renders inutiles, meilleure gestion des intervalles et de la synchronisation des données côté Caregiver et User

---

## 05/05/2026

### 🔐 v1.1.9 — Corrections sécurité (Pentests)

#### Backend — Sécurité

- Correction des failles de sécurité identifiées lors des tests de pénétration (pentests)

---

## 12/05/2026

### ✨ v1.2.0 — Rappels récurrents (DAILY / WEEKLY / MONTHLY)

#### Backend — Récurrence

- `calculate_next_occurrence()` : calcule la prochaine occurrence en sautant les dates passées, avec clamping sur les mois courts (ex. 31 jan → 28 fév) et wrap décembre → janvier
- `schedule_next_occurrence()` : replanifie automatiquement le reminder après chaque déclenchement et crée un nouveau statut PENDING ; retourne `False` quand la date de fin est dépassée
- `ReminderCreate` schema : validation cross-champs — `recurrence_type` obligatoire si `is_recurring`, `recurrence_days` obligatoire pour WEEKLY, jours validés entre 0 (lundi) et 6 (dimanche)

#### Frontend — Modal de programmation

- Date, heure et récurrence déplacés dans un unique modal `pageSheet` → le formulaire principal ne nécessite plus de scroll
- Switch de récurrence enveloppé dans un container gris `#F5F5F5` pour contraster sur fond blanc
- Sélecteur de jours pour WEEKLY (lundi → dimanche) ; validation bloquante si aucun jour sélectionné (haptic error)
- Affichage des jours sélectionnés en ligne avec séparateur `·` (2 lignes max si tous les jours cochés)
- Description dynamique sous les chips de type (ex. *Tous les jours à 09:30 · jusqu'au 31/12/2026*)
- Card de résumé `#EEF4FC` sur le formulaire principal avec icône de récurrence

#### Frontend — UI

- Correction `.sort()` → `.slice().sort()` pour éviter la mutation du state React (causait l'absence de description pour WEEKLY)
- Padding bas des boutons corrigé : `insets.bottom + 20` → `insets.bottom` sur WelcomeScreen, LoginScreen, RegisterScreen, CreateProfileScreen
