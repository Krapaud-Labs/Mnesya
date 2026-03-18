/**
 * Hook for fetching all reminders created by the caregiver.
 *
 * @module useCaregiverReminders
 */

import { useState, useEffect, useCallback } from 'react';
import { getCaregiverReminders } from '../services/reminderService';
import type { ReminderData } from '../types/interfaces';

// ─── Types ───────────────────────────────────────────────────────────────────

interface UseReminderResult {
    reminderData: ReminderData[] | null;
    loading: boolean;
    error: string | null;
    reload: () => Promise<void>;
    silentReload: () => Promise<void>;
}

// ─── Hook ───────────────────────────────────────────────────────────────────────

/**
 * Fetches all reminders created by the logged-in caregiver.
 *
 * @param onAuthError - Optional callback invoked on a 401 response.
 * @returns reminderData, loading flag, error key and a reload function.
 */
export const useCaregiverReminders = (onAuthError?: () => void): UseReminderResult => {
    const [reminderData, setReminderData] = useState<ReminderData[] | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadReminders = useCallback(async (silent = false) => {
        try {
            if (!silent) setLoading(true);
            setError(null);
            const reminders = await getCaregiverReminders();
            setReminderData(reminders);
        } catch (err) {
            if (!silent) setError('common.errors.failedToLoadReminders');
            if (err instanceof Error && err.message.includes('401')) {
                onAuthError?.();
            }
        } finally {
            if (!silent) setLoading(false);
        }
    }, [onAuthError]);
    useEffect(() => {
        loadReminders();
    }, [loadReminders]);
    const reload = useCallback(() => loadReminders(false), [loadReminders]);
    const silentReload = useCallback(() => loadReminders(true), [loadReminders]);

    return { reminderData, loading, error, reload, silentReload };
};
