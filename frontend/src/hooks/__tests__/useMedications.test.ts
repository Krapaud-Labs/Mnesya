/**
 * Unit tests for useMedications hook.
 *
 * @module useMedications.test
 */
import { renderHook, waitFor, act } from '@testing-library/react-native';
import { useMedications } from '../useMedications';
import { getMedicationsForUser } from '../../services/medicationService';

jest.mock('../../services/medicationService', () => ({
    getMedicationsForUser: jest.fn(),
}));

const mockMedications = [
    {
        id: 'med-1',
        caregiver_id: 'caregiver-1',
        user_id: 'user-1',
        name: 'Doliprane',
        dosage: '500mg',
        times: ['08:00', '20:00'],
        frequency: 'DAILY',
        start_date: '2026-05-01',
    },
];

describe('useMedications', () => {
    const mockOnAuthError = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('initial loading', () => {
        it('should fetch and return medications for a user', async () => {
            (getMedicationsForUser as jest.Mock).mockResolvedValue(mockMedications);

            const { result } = renderHook(() => useMedications('user-1', mockOnAuthError));

            expect(result.current.loading).toBe(true);

            await waitFor(() => {
                expect(result.current.loading).toBe(false);
            });

            expect(result.current.medications).toEqual(mockMedications);
            expect(result.current.error).toBeNull();
        });

        it('should return an empty list when no medications', async () => {
            (getMedicationsForUser as jest.Mock).mockResolvedValue([]);

            const { result } = renderHook(() => useMedications('user-1', mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            expect(result.current.medications).toEqual([]);
        });

        it('should set error on fetch failure', async () => {
            (getMedicationsForUser as jest.Mock).mockRejectedValue(new Error('Network error'));

            const { result } = renderHook(() => useMedications('user-1', mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            expect(result.current.medications).toBeNull();
            expect(result.current.error).toBe('medication.errors.failedToLoad');
        });
    });

    describe('null userId', () => {
        it('should not fetch when userId is null', async () => {
            const { result } = renderHook(() => useMedications(null, mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            expect(getMedicationsForUser).not.toHaveBeenCalled();
            expect(result.current.medications).toBeNull();
        });

        it('should fetch when userId changes from null to a value', async () => {
            (getMedicationsForUser as jest.Mock).mockResolvedValue(mockMedications);

            const { result, rerender } = renderHook(
                ({ userId }: { userId: string | null }) => useMedications(userId, mockOnAuthError),
                { initialProps: { userId: null } }
            );

            expect(getMedicationsForUser).not.toHaveBeenCalled();

            rerender({ userId: 'user-1' });

            await waitFor(() => {
                expect(result.current.medications).toEqual(mockMedications);
            });

            expect(getMedicationsForUser).toHaveBeenCalledWith('user-1');
        });
    });

    describe('reload', () => {
        it('should refetch medications when reload is called', async () => {
            const updated = [...mockMedications, { ...mockMedications[0], id: 'med-2' }];
            (getMedicationsForUser as jest.Mock)
                .mockResolvedValueOnce(mockMedications)
                .mockResolvedValueOnce(updated);

            const { result } = renderHook(() => useMedications('user-1', mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            await act(async () => {
                await result.current.reload();
            });

            await waitFor(() => {
                expect(result.current.medications).toHaveLength(2);
            });

            expect(getMedicationsForUser).toHaveBeenCalledTimes(2);
        });

        it('should not set loading on silentReload', async () => {
            (getMedicationsForUser as jest.Mock).mockResolvedValue(mockMedications);

            const { result } = renderHook(() => useMedications('user-1', mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            await act(async () => {
                await result.current.silentReload();
            });

            expect(result.current.loading).toBe(false);
            expect(getMedicationsForUser).toHaveBeenCalledTimes(2);
        });
    });

    describe('auth error handling', () => {
        it('should call onAuthError when error includes 401', async () => {
            (getMedicationsForUser as jest.Mock).mockRejectedValue(new Error('401 Unauthorized'));

            renderHook(() => useMedications('user-1', mockOnAuthError));

            await waitFor(() => {
                expect(mockOnAuthError).toHaveBeenCalledTimes(1);
            });
        });

        it('should not call onAuthError on non-auth errors', async () => {
            (getMedicationsForUser as jest.Mock).mockRejectedValue(new Error('Server error'));

            const { result } = renderHook(() => useMedications('user-1', mockOnAuthError));

            await waitFor(() => expect(result.current.loading).toBe(false));

            expect(mockOnAuthError).not.toHaveBeenCalled();
        });
    });
});
