/**
 * Pure helpers for recurrence display and summary formatting.
 *
 * @module recurrenceUtils
 */

type TFunction = (key: string, options?: Record<string, unknown>) => string;

// ─── Date formatting ─────────────────────────────────────────────────────────

export const formatDate = (date: Date): string => {
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
};

export const formatTime = (date: Date): string => {
    const hour = date.getHours().toString().padStart(2, '0');
    const minute = date.getMinutes().toString().padStart(2, '0');
    return `${hour}:${minute}`;
};

// ─── Recurrence display ───────────────────────────────────────────────────────

/**
 * Short summary for the scheduling card (e.g. "Daily", "Mo, We, Fr").
 * Returns null when recurrence is off.
 */
export const getRecurrenceSummary = (
    isRecurring: boolean,
    recurrenceType: 'DAILY' | 'WEEKLY' | 'MONTHLY',
    recurrenceDays: number[],
    t: TFunction,
): string | null => {
    if (!isRecurring) return null;
    if (recurrenceType === 'DAILY') return t('CreateReminder.recurrence.types.DAILY');
    if (recurrenceType === 'MONTHLY') return t('CreateReminder.recurrence.types.MONTHLY');
    if (recurrenceType === 'WEEKLY') {
        if (recurrenceDays.length === 0) return '…';
        return recurrenceDays
            .slice()
            .sort((a, b) => a - b)
            .map((d) => t(`CreateReminder.recurrence.day_short.${d}`))
            .join(', ');
    }
    return null;
};

/**
 * Human-readable sentence shown below the type chips in the scheduling modal.
 */
export const getRecurrenceDescription = (
    recurrenceType: 'DAILY' | 'WEEKLY' | 'MONTHLY',
    recurrenceDays: number[],
    reminderDate: Date,
    recurrenceEndDate: Date | null,
    t: TFunction,
): string => {
    const time = formatTime(reminderDate);
    const endSuffix = recurrenceEndDate
        ? t('CreateReminder.recurrence.description.end_suffix', { date: formatDate(recurrenceEndDate) })
        : '';

    if (recurrenceType === 'DAILY') {
        return t('CreateReminder.recurrence.description.DAILY', { time, end: endSuffix });
    }
    if (recurrenceType === 'MONTHLY') {
        return t('CreateReminder.recurrence.description.MONTHLY', {
            day: reminderDate.getDate(),
            time,
            end: endSuffix,
        });
    }
    if (recurrenceType === 'WEEKLY') {
        if (recurrenceDays.length === 0) return '';
        const days = recurrenceDays
            .slice()
            .sort((a, b) => a - b)
            .map((d) => t(`CreateReminder.recurrence.day_short.${d}`))
            .join(', ');
        return t('CreateReminder.recurrence.description.WEEKLY', { days, time, end: endSuffix });
    }
    return '';
};

/**
 * One-line summary for the main form card (date + time + optional recurrence).
 */
export const getSchedulingSummary = (
    reminderDate: Date,
    isRecurring: boolean,
    recurrenceType: 'DAILY' | 'WEEKLY' | 'MONTHLY',
    recurrenceDays: number[],
    t: TFunction,
): string => {
    const base = `${formatDate(reminderDate)} à ${formatTime(reminderDate)}`;
    const rec = getRecurrenceSummary(isRecurring, recurrenceType, recurrenceDays, t);
    return rec ? `${base} · ${rec}` : base;
};

// ─── Validation ───────────────────────────────────────────────────────────────

/**
 * Returns true when the recurrence configuration is valid (can be submitted).
 */
export const isRecurrenceValid = (
    isRecurring: boolean,
    recurrenceType: 'DAILY' | 'WEEKLY' | 'MONTHLY',
    recurrenceDays: number[],
): boolean => {
    if (!isRecurring) return true;
    if (recurrenceType === 'WEEKLY' && recurrenceDays.length === 0) return false;
    return true;
};
