/**
 * Hook for fetching medications for a specific user (caregiver view).
 *
 * @module useMedications
 */
import { useState, useEffect, useCallback } from 'react';
import { getMedicationsForUser } from '../services/medicationService';
import type { MedicationData } from '../types/interfaces';

// ─── Types ───────────────────────────────────────────────────────────────────

interface UseMedicationsResult {
    medications: MedicationData[] | null;
    loading: boolean;
    error: string | null;
    reload: () => Promise<void>;
    silentReload: () => Promise<void>;
}

// ─── Hook ────────────────────────────────────────────────────────────────────

/**
 * Fetches all medications for a given user, visible to the caregiver.
 *
 * @param userId - The user's ID. Pass null to skip fetching.
 * @param onAuthError - Optional callback invoked on a 401 response.
 */
export const useMedications = (
    userId: string | null,
    onAuthError?: () => void
): UseMedicationsResult => {
    const [medications, setMedications] = useState<MedicationData[] | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const load = useCallback(
        async (silent = false) => {
            if (!userId) {
                setMedications(null);
                return;
            }
            try {
                if (!silent) setLoading(true);
                setError(null);
                const data = await getMedicationsForUser(userId);
                setMedications(data);
            } catch (err) {
                if (!silent) setError('medication.errors.failedToLoad');
                if (err instanceof Error && err.message.includes('401')) {
                    onAuthError?.();
                }
            } finally {
                if (!silent) setLoading(false);
            }
        },
        [userId, onAuthError]
    );

    useEffect(() => {
        load();
    }, [load]);

    const reload = useCallback(() => load(false), [load]);
    const silentReload = useCallback(() => load(true), [load]);

    return { medications, loading, error, reload, silentReload };
};
