/**
 * API base URL configuration.
 *
 * In development with Expo Go, the IP is automatically detected from the
 * Expo dev server (Constants.expoConfig.hostUri). No manual change needed
 * when switching networks.
 *
 * In production, falls back to the production URL.
 *
 * @module api
 */

// ─── Constants ───────────────────────────────────────────────────────────────

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'https://api.mnesya.app';

export const BACKUP_API_URL = 'https://api.mnesya.app';
