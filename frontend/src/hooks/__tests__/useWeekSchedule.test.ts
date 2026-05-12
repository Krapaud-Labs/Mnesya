/**
 * Unit tests for useWeekSchedule hook.
 *
 * @module useWeekSchedule.test
 */
import { renderHook, waitFor, act } from '@testing-library/react-native';
import { useWeekSchedule } from '../useWeekSchedule';
import { getWeekSchedule } from '../../services/medicationService';

jest.mock('../../services/medicationService', () => ({
    getWeekSchedule: jest.fn(),
}));

const makeWeekResponse = (weekStart: string) => ({
    week_start: weekStart,
    days: Array.from({ length: 7 }, (_, i) => {
        const d = new Date(weekStart + 'T12:00:00');
        d.setDate(d.getDate() + i);
        return { date: d.toISOString().split('T')[0], entries: [] };
    }),
});

describe('useWeekSchedule', () => {
    const mockOnAuthError = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('initial loading', () => {
        it('should fetch and return the current week', async () => {
            const weekData = makeWeekResponse('2026-05-11');
            (getWeekSchedule as jest.Mock).mockResolvedValue(weekData);

            const { result } = renderHook(() => useWeekSchedule(mockOnAuthError));

            expect(result.current.loading).toBe(true);

            await waitFor(() => {
                expect(result.current.loading).toBe(false);
            });

            expect(result.current.weekData).toEqual(weekData);
            expect(result.current.error).toBeNull();
            expect(result.current.weekData?.days).toHaveLength(7);
        });

        it('should set error on fetch failure', async () => {
            (getWeekSchedule as jest.Mock).mockRejectedValue(new Error('Network error'));

            const { result } = renderHook(() => useWeekSchedule(mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            expect(result.current.weekData).toBeNull();
            expect(result.current.error).toBe('medication.errors.failedToLoad');
        });

        it('should expose the current weekStart', async () => {
            (getWeekSchedule as jest.Mock).mockResolvedValue(makeWeekResponse('2026-05-11'));

            const { result } = renderHook(() => useWeekSchedule(mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            expect(result.current.weekStart).toMatch(/^\d{4}-\d{2}-\d{2}$/);
        });
    });

    describe('week navigation', () => {
        it('should fetch the previous week when goToPrevWeek is called', async () => {
            (getWeekSchedule as jest.Mock).mockResolvedValue(makeWeekResponse('2026-05-11'));

            const { result } = renderHook(() => useWeekSchedule(mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            const initialWeekStart = result.current.weekStart;

            (getWeekSchedule as jest.Mock).mockResolvedValue(makeWeekResponse('2026-05-04'));

            act(() => {
                result.current.goToPrevWeek();
            });

            await waitFor(() => {
                expect(result.current.weekStart).not.toBe(initialWeekStart);
            });

            const prevDate = new Date(result.current.weekStart);
            const initDate = new Date(initialWeekStart);
            expect(initDate.getTime() - prevDate.getTime()).toBe(7 * 24 * 60 * 60 * 1000);
        });

        it('should fetch the next week when goToNextWeek is called', async () => {
            (getWeekSchedule as jest.Mock).mockResolvedValue(makeWeekResponse('2026-05-11'));

            const { result } = renderHook(() => useWeekSchedule(mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            const initialWeekStart = result.current.weekStart;

            (getWeekSchedule as jest.Mock).mockResolvedValue(makeWeekResponse('2026-05-18'));

            act(() => {
                result.current.goToNextWeek();
            });

            await waitFor(() => {
                expect(result.current.weekStart).not.toBe(initialWeekStart);
            });

            const nextDate = new Date(result.current.weekStart);
            const initDate = new Date(initialWeekStart);
            expect(nextDate.getTime() - initDate.getTime()).toBe(7 * 24 * 60 * 60 * 1000);
        });

        it('should re-fetch when navigating weeks', async () => {
            (getWeekSchedule as jest.Mock).mockResolvedValue(makeWeekResponse('2026-05-11'));

            const { result } = renderHook(() => useWeekSchedule(mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            act(() => {
                result.current.goToNextWeek();
            });

            await waitFor(() => expect(result.current.loading).toBe(false));

            expect(getWeekSchedule).toHaveBeenCalledTimes(2);
        });
    });

    describe('reload', () => {
        it('should refetch the current week when reload is called', async () => {
            const weekData = makeWeekResponse('2026-05-11');
            (getWeekSchedule as jest.Mock).mockResolvedValue(weekData);

            const { result } = renderHook(() => useWeekSchedule(mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            await act(async () => {
                await result.current.reload();
            });

            expect(getWeekSchedule).toHaveBeenCalledTimes(2);
        });
    });

    describe('auth error handling', () => {
        it('should call onAuthError when error includes 401', async () => {
            (getWeekSchedule as jest.Mock).mockRejectedValue(new Error('401 Unauthorized'));

            renderHook(() => useWeekSchedule(mockOnAuthError));

            await waitFor(() => {
                expect(mockOnAuthError).toHaveBeenCalledTimes(1);
            });
        });

        it('should not call onAuthError on non-auth errors', async () => {
            (getWeekSchedule as jest.Mock).mockRejectedValue(new Error('Server error'));

            const { result } = renderHook(() => useWeekSchedule(mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            expect(mockOnAuthError).not.toHaveBeenCalled();
        });
    });
});
