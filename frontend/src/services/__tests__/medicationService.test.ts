/**
 * Unit tests for medicationService.
 *
 * @module medicationService.test
 */
import {
    createMedication,
    getMedicationsForUser,
    getMedication,
    deleteMedication,
    getWeekSchedule,
} from '../medicationService';
import apiClient from '../api';
import { CreateMedication, MedicationData, WeekResponse } from '../../types/interfaces';

jest.mock('../api', () => ({
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
}));

const mockMedication: MedicationData = {
    id: 'med-1',
    caregiver_id: 'caregiver-1',
    user_id: 'user-1',
    name: 'Doliprane',
    dosage: '500mg',
    moments: ['AFTER_BREAKFAST', 'AFTER_DINNER'],
    frequency: 'DAILY',
    start_date: '2026-05-01',
};

const mockWeekResponse: WeekResponse = {
    week_start: '2026-05-11',
    days: [
        { date: '2026-05-11', entries: [] },
        { date: '2026-05-12', entries: [
            {
                medication_id: 'med-1',
                name: 'Doliprane',
                dosage: '500mg',
                moment: 'AFTER_BREAKFAST',
                reminder_id: 'rem-1',
                status: 'PENDING',
            },
        ]},
        { date: '2026-05-13', entries: [] },
        { date: '2026-05-14', entries: [] },
        { date: '2026-05-15', entries: [] },
        { date: '2026-05-16', entries: [] },
        { date: '2026-05-17', entries: [] },
    ],
};

describe('medicationService', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('createMedication', () => {
        it('should create a daily medication and return data', async () => {
            const payload: CreateMedication = {
                user_id: 'user-1',
                name: 'Doliprane',
                dosage: '500mg',
                moments: ['AFTER_BREAKFAST', 'AFTER_DINNER'],
                frequency: 'DAILY',
                start_date: '2026-05-01',
            };
            (apiClient.post as jest.Mock).mockResolvedValue({ data: mockMedication });

            const result = await createMedication(payload);

            expect(apiClient.post).toHaveBeenCalledWith('/api/medication', payload);
            expect(result).toEqual(mockMedication);
        });

        it('should create a weekly medication with recurrence days', async () => {
            const payload: CreateMedication = {
                user_id: 'user-1',
                name: 'Aspirine',
                moments: ['DURING_LUNCH'],
                frequency: 'WEEKLY',
                recurrence_days: [0, 2, 4],
                start_date: '2026-05-01',
            };
            const weeklyMed: MedicationData = { ...mockMedication, frequency: 'WEEKLY', recurrence_days: [0, 2, 4] };
            (apiClient.post as jest.Mock).mockResolvedValue({ data: weeklyMed });

            const result = await createMedication(payload);

            expect(apiClient.post).toHaveBeenCalledWith('/api/medication', payload);
            expect(result.frequency).toBe('WEEKLY');
            expect(result.recurrence_days).toEqual([0, 2, 4]);
        });

        it('should create a medication with an end date', async () => {
            const payload: CreateMedication = {
                user_id: 'user-1',
                name: 'Antibiotique',
                moments: ['BEFORE_BREAKFAST'],
                frequency: 'DAILY',
                start_date: '2026-05-01',
                end_date: '2026-05-10',
            };
            const medWithEnd: MedicationData = { ...mockMedication, end_date: '2026-05-10' };
            (apiClient.post as jest.Mock).mockResolvedValue({ data: medWithEnd });

            const result = await createMedication(payload);

            expect(result.end_date).toBe('2026-05-10');
        });

        it('should throw on API error', async () => {
            (apiClient.post as jest.Mock).mockRejectedValue(new Error('Server error'));

            await expect(
                createMedication({ user_id: 'u-1', name: 'X', moments: ['AFTER_BREAKFAST'], frequency: 'DAILY', start_date: '2026-01-01' })
            ).rejects.toThrow('Server error');
        });
    });

    describe('getMedicationsForUser', () => {
        it('should return all medications for a user', async () => {
            (apiClient.get as jest.Mock).mockResolvedValue({ data: [mockMedication] });

            const result = await getMedicationsForUser('user-1');

            expect(apiClient.get).toHaveBeenCalledWith('/api/medication/user/user-1');
            expect(result).toHaveLength(1);
            expect(result[0]).toEqual(mockMedication);
        });

        it('should return an empty list when no medications', async () => {
            (apiClient.get as jest.Mock).mockResolvedValue({ data: [] });

            const result = await getMedicationsForUser('user-1');

            expect(result).toEqual([]);
        });

        it('should throw on unauthorized', async () => {
            (apiClient.get as jest.Mock).mockRejectedValue(new Error('403 Forbidden'));

            await expect(getMedicationsForUser('user-1')).rejects.toThrow('403 Forbidden');
        });
    });

    describe('getMedication', () => {
        it('should return a single medication by ID', async () => {
            (apiClient.get as jest.Mock).mockResolvedValue({ data: mockMedication });

            const result = await getMedication('med-1');

            expect(apiClient.get).toHaveBeenCalledWith('/api/medication/med-1');
            expect(result).toEqual(mockMedication);
        });

        it('should throw when medication not found', async () => {
            (apiClient.get as jest.Mock).mockRejectedValue(new Error('Not found'));

            await expect(getMedication('bad-id')).rejects.toThrow('Not found');
        });
    });

    describe('deleteMedication', () => {
        it('should delete a medication without returning data', async () => {
            (apiClient.delete as jest.Mock).mockResolvedValue({});

            await expect(deleteMedication('med-1')).resolves.toBeUndefined();
            expect(apiClient.delete).toHaveBeenCalledWith('/api/medication/med-1');
        });

        it('should throw on not found', async () => {
            (apiClient.delete as jest.Mock).mockRejectedValue(new Error('Not found'));

            await expect(deleteMedication('bad-id')).rejects.toThrow('Not found');
        });
    });

    describe('getWeekSchedule', () => {
        it('should return the week schedule without a date param', async () => {
            (apiClient.get as jest.Mock).mockResolvedValue({ data: mockWeekResponse });

            const result = await getWeekSchedule();

            expect(apiClient.get).toHaveBeenCalledWith('/api/medication/week');
            expect(result.week_start).toBe('2026-05-11');
            expect(result.days).toHaveLength(7);
        });

        it('should pass the date param when provided', async () => {
            (apiClient.get as jest.Mock).mockResolvedValue({ data: mockWeekResponse });

            await getWeekSchedule('2026-05-11');

            expect(apiClient.get).toHaveBeenCalledWith('/api/medication/week?date_param=2026-05-11');
        });

        it('should return days with entries and status', async () => {
            (apiClient.get as jest.Mock).mockResolvedValue({ data: mockWeekResponse });

            const result = await getWeekSchedule('2026-05-11');
            const dayWithEntry = result.days.find((d) => d.entries.length > 0);

            expect(dayWithEntry).toBeDefined();
            expect(dayWithEntry!.entries[0].name).toBe('Doliprane');
            expect(dayWithEntry!.entries[0].status).toBe('PENDING');
        });

        it('should throw on unauthorized', async () => {
            (apiClient.get as jest.Mock).mockRejectedValue(new Error('401 Unauthorized'));

            await expect(getWeekSchedule()).rejects.toThrow('401 Unauthorized');
        });
    });
});
