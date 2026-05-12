/**
 * Service for managing medications and the week schedule.
 *
 * @module medicationService
 */
import apiClient from './api';
import { CreateMedication, MedicationData, WeekResponse } from '../types/interfaces';

// ─── Endpoints ──────────────────────────────────────────────────────────────

/** Creates a new medication and auto-generates its reminders. */
export const createMedication = async (data: CreateMedication): Promise<MedicationData> => {
    const response = await apiClient.post('/api/medication', data);
    return response.data;
};

/** Returns all medications for a given user (caregiver view). */
export const getMedicationsForUser = async (userId: string): Promise<MedicationData[]> => {
    const response = await apiClient.get(`/api/medication/user/${userId}`);
    return response.data;
};

/** Returns a single medication by ID. */
export const getMedication = async (id: string): Promise<MedicationData> => {
    const response = await apiClient.get(`/api/medication/${id}`);
    return response.data;
};

/** Deletes a medication and its linked reminders. */
export const deleteMedication = async (id: string): Promise<void> => {
    await apiClient.delete(`/api/medication/${id}`);
};

/** Returns the 7-day semainier for the authenticated user. */
export const getWeekSchedule = async (dateParam?: string): Promise<WeekResponse> => {
    const url = dateParam
        ? `/api/medication/week?date_param=${dateParam}`
        : '/api/medication/week';
    const response = await apiClient.get(url);
    return response.data;
};
