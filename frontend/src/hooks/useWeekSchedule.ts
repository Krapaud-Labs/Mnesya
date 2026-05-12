/**
 * Hook for fetching the 7-day medication schedule for the authenticated user.
 *
 * @module useWeekSchedule
 */
import { useState, useEffect, useCallback } from 'react';
import { getWeekSchedule } from '../services/medicationService';
import type { WeekResponse } from '../types/interfaces';

// ─── Types ───────────────────────────────────────────────────────────────────

interface UseWeekScheduleResult {
    weekData: WeekResponse | null;
    loading: boolean;
    error: string | null;
    reload: () => Promise<void>;
    goToPrevWeek: () => void;
    goToNextWeek: () => void;
    weekStart: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function addDays(dateStr: string, days: number): string {
    const d = new Date(dateStr);
    d.setDate(d.getDate() + days);
    return d.toISOString().split('T')[0];
}

function currentMonday(): string {
    const today = new Date();
    const day = today.getDay(); // 0=Sun
    const diff = day === 0 ? -6 : 1 - day;
    today.setDate(today.getDate() + diff);
    return today.toISOString().split('T')[0];
}

// ─── Hook ────────────────────────────────────────────────────────────────────

/**
 * Fetches the semainier for the logged-in user with week navigation.
 *
 * @param onAuthError - Optional callback invoked on a 401 response.
 */
export const useWeekSchedule = (onAuthError?: () => void): UseWeekScheduleResult => {
    const [weekStart, setWeekStart] = useState<string>(currentMonday());
    const [weekData, setWeekData] = useState<WeekResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const load = useCallback(
        async (dateParam: string) => {
            try {
                setLoading(true);
                setError(null);
                const data = await getWeekSchedule(dateParam);
                setWeekData(data);
            } catch (err) {
                setError('medication.errors.failedToLoad');
                if (err instanceof Error && err.message.includes('401')) {
                    onAuthError?.();
                }
            } finally {
                setLoading(false);
            }
        },
        [onAuthError]
    );

    useEffect(() => {
        load(weekStart);
    }, [weekStart, load]);

    const reload = useCallback(() => load(weekStart), [weekStart, load]);
    const goToPrevWeek = useCallback(() => setWeekStart((w) => addDays(w, -7)), []);
    const goToNextWeek = useCallback(() => setWeekStart((w) => addDays(w, 7)), []);

    return { weekData, loading, error, reload, goToPrevWeek, goToNextWeek, weekStart };
};
