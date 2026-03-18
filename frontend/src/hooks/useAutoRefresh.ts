/**
 * Hook that calls a refresh function on a fixed interval.
 *
 * Uses a ref to always call the latest version of the callback
 * without needing to re-register the interval.
 *
 * @module useAutoRefresh
 */
import { useEffect, useRef } from 'react';

const DEFAULT_INTERVAL_MS = 10_000;

export function useAutoRefresh(refresh: () => void, intervalMs = DEFAULT_INTERVAL_MS) {
    const refreshRef = useRef(refresh);
    refreshRef.current = refresh;

    useEffect(() => {
        const id = setInterval(() => refreshRef.current(), intervalMs);
        return () => clearInterval(id);
    }, [intervalMs]);
}
