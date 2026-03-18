/**
 * Hook that calls a refresh function on a fixed interval.
 *
 * - Uses a ref to always call the latest version of the callback
 *   without needing to re-register the interval.
 * - Pauses automatically when the app goes to background to avoid
 *   unnecessary network requests and battery drain.
 *
 * @module useAutoRefresh
 */
import { useEffect, useRef } from 'react';
import { AppState, type AppStateStatus } from 'react-native';

const DEFAULT_INTERVAL_MS = 10_000;

export function useAutoRefresh(refresh: () => void, intervalMs = DEFAULT_INTERVAL_MS) {
    const refreshRef = useRef(refresh);
    refreshRef.current = refresh;

    useEffect(() => {
        let id: ReturnType<typeof setInterval> | null = null;

        const start = () => {
            if (id !== null) return;
            id = setInterval(() => refreshRef.current(), intervalMs);
        };

        const stop = () => {
            if (id === null) return;
            clearInterval(id);
            id = null;
        };

        const handleAppState = (next: AppStateStatus) => {
            next === 'active' ? start() : stop();
        };

        start();
        const subscription = AppState.addEventListener('change', handleAppState);

        return () => {
            stop();
            subscription.remove();
        };
    }, [intervalMs]);
}
