/**
 * Unit tests for recurrence utility helpers.
 *
 * Tests cover:
 * - formatDate / formatTime
 * - getRecurrenceSummary: DAILY, WEEKLY, MONTHLY, off state, no days
 * - getRecurrenceDescription: all types, end date suffix, no days
 * - getSchedulingSummary: with and without recurrence
 * - isRecurrenceValid: WEEKLY/no days, all other cases
 */

import {
    formatDate,
    formatTime,
    getRecurrenceSummary,
    getRecurrenceDescription,
    getSchedulingSummary,
    isRecurrenceValid,
} from '../recurrenceUtils';

// ─── Mock t() ────────────────────────────────────────────────────────────────

const t = (key: string, opts?: Record<string, unknown>): string => {
    const map: Record<string, string> = {
        'CreateReminder.recurrence.types.DAILY': 'Daily',
        'CreateReminder.recurrence.types.MONTHLY': 'Monthly',
        'CreateReminder.recurrence.day_short.0': 'Mo',
        'CreateReminder.recurrence.day_short.1': 'Tu',
        'CreateReminder.recurrence.day_short.2': 'We',
        'CreateReminder.recurrence.day_short.3': 'Th',
        'CreateReminder.recurrence.day_short.4': 'Fr',
        'CreateReminder.recurrence.day_short.5': 'Sa',
        'CreateReminder.recurrence.day_short.6': 'Su',
        'CreateReminder.recurrence.description.DAILY': `Every day at ${opts?.time}${opts?.end}`,
        'CreateReminder.recurrence.description.WEEKLY': `Every ${opts?.days} at ${opts?.time}${opts?.end}`,
        'CreateReminder.recurrence.description.MONTHLY': `On the ${opts?.day}th of each month at ${opts?.time}${opts?.end}`,
        'CreateReminder.recurrence.description.end_suffix': ` · until ${opts?.date}`,
    };
    return map[key] ?? key;
};

// ─── Fixtures ────────────────────────────────────────────────────────────────

const d = new Date(2026, 0, 15, 9, 30); // Jan 15 2026 09:30

// ─── formatDate ───────────────────────────────────────────────────────────────

describe('formatDate', () => {
    it('formats a date as DD/MM/YYYY', () => {
        expect(formatDate(d)).toBe('15/01/2026');
    });

    it('pads single-digit day and month', () => {
        expect(formatDate(new Date(2026, 2, 5))).toBe('05/03/2026');
    });
});

// ─── formatTime ───────────────────────────────────────────────────────────────

describe('formatTime', () => {
    it('formats time as HH:MM', () => {
        expect(formatTime(d)).toBe('09:30');
    });

    it('pads single-digit hours and minutes', () => {
        expect(formatTime(new Date(2026, 0, 1, 8, 5))).toBe('08:05');
    });
});

// ─── getRecurrenceSummary ─────────────────────────────────────────────────────

describe('getRecurrenceSummary', () => {
    it('returns null when not recurring', () => {
        expect(getRecurrenceSummary(false, 'DAILY', [], t)).toBeNull();
    });

    it('returns "Daily" for DAILY', () => {
        expect(getRecurrenceSummary(true, 'DAILY', [], t)).toBe('Daily');
    });

    it('returns "Monthly" for MONTHLY', () => {
        expect(getRecurrenceSummary(true, 'MONTHLY', [], t)).toBe('Monthly');
    });

    it('returns sorted day abbreviations for WEEKLY', () => {
        expect(getRecurrenceSummary(true, 'WEEKLY', [4, 0, 2], t)).toBe('Mo, We, Fr');
    });

    it('returns "…" for WEEKLY with no days selected', () => {
        expect(getRecurrenceSummary(true, 'WEEKLY', [], t)).toBe('…');
    });

    it('returns a single day for WEEKLY with one day', () => {
        expect(getRecurrenceSummary(true, 'WEEKLY', [1], t)).toBe('Tu');
    });

    it('does not mutate the input days array', () => {
        const days = [4, 0, 2];
        getRecurrenceSummary(true, 'WEEKLY', days, t);
        expect(days).toEqual([4, 0, 2]);
    });
});

// ─── getRecurrenceDescription ─────────────────────────────────────────────────

describe('getRecurrenceDescription', () => {
    it('returns DAILY description without end date', () => {
        const result = getRecurrenceDescription('DAILY', [], d, null, t);
        expect(result).toBe('Every day at 09:30');
    });

    it('returns DAILY description with end date suffix', () => {
        const endDate = new Date(2026, 11, 31, 0, 0); // Dec 31 2026
        const result = getRecurrenceDescription('DAILY', [], d, endDate, t);
        expect(result).toBe('Every day at 09:30 · until 31/12/2026');
    });

    it('returns MONTHLY description with day-of-month', () => {
        const result = getRecurrenceDescription('MONTHLY', [], d, null, t);
        expect(result).toBe('On the 15th of each month at 09:30');
    });

    it('returns WEEKLY description with sorted days', () => {
        const result = getRecurrenceDescription('WEEKLY', [4, 0], d, null, t);
        expect(result).toBe('Every Mo, Fr at 09:30');
    });

    it('returns empty string for WEEKLY with no days', () => {
        expect(getRecurrenceDescription('WEEKLY', [], d, null, t)).toBe('');
    });

    it('does not mutate the input days array', () => {
        const days = [4, 0];
        getRecurrenceDescription('WEEKLY', days, d, null, t);
        expect(days).toEqual([4, 0]);
    });
});

// ─── getSchedulingSummary ─────────────────────────────────────────────────────

describe('getSchedulingSummary', () => {
    it('returns date and time only when not recurring', () => {
        expect(getSchedulingSummary(d, false, 'DAILY', [], t)).toBe('15/01/2026 à 09:30');
    });

    it('appends DAILY recurrence label', () => {
        expect(getSchedulingSummary(d, true, 'DAILY', [], t)).toBe('15/01/2026 à 09:30 · Daily');
    });

    it('appends WEEKLY days when selected', () => {
        expect(getSchedulingSummary(d, true, 'WEEKLY', [0, 4], t)).toBe(
            '15/01/2026 à 09:30 · Mo, Fr',
        );
    });

    it('appends "…" for WEEKLY with no days', () => {
        expect(getSchedulingSummary(d, true, 'WEEKLY', [], t)).toBe('15/01/2026 à 09:30 · …');
    });

    it('appends MONTHLY label', () => {
        expect(getSchedulingSummary(d, true, 'MONTHLY', [], t)).toBe(
            '15/01/2026 à 09:30 · Monthly',
        );
    });
});

// ─── isRecurrenceValid ────────────────────────────────────────────────────────

describe('isRecurrenceValid', () => {
    it('returns true when not recurring', () => {
        expect(isRecurrenceValid(false, 'WEEKLY', [])).toBe(true);
    });

    it('returns true for DAILY with no days', () => {
        expect(isRecurrenceValid(true, 'DAILY', [])).toBe(true);
    });

    it('returns true for MONTHLY with no days', () => {
        expect(isRecurrenceValid(true, 'MONTHLY', [])).toBe(true);
    });

    it('returns false for WEEKLY with no days selected', () => {
        expect(isRecurrenceValid(true, 'WEEKLY', [])).toBe(false);
    });

    it('returns true for WEEKLY with at least one day', () => {
        expect(isRecurrenceValid(true, 'WEEKLY', [0])).toBe(true);
    });

    it('returns true for WEEKLY with all days selected', () => {
        expect(isRecurrenceValid(true, 'WEEKLY', [0, 1, 2, 3, 4, 5, 6])).toBe(true);
    });
});
