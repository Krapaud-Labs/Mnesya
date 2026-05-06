/**
 * Card showing a single reminder with its current status and a delete button.
 *
 * @module ReminderCard
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from 'react-i18next';
import { commonStyles } from '../styles/commonStyles';
import type { ReminderData } from '../types/interfaces';

// ─── Types ───────────────────────────────────────────────────────────────────

interface ReminderCardProps {
    reminder: ReminderData;
    onDelete: (id: string) => void;
}

// ─── Component ───────────────────────────────────────────────────────────────

const DAY_KEYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function recurrenceLabel(reminder: ReminderData, t: (k: string) => string): string | null {
    if (!reminder.is_recurring || !reminder.recurrence_type) return null;
    if (reminder.recurrence_type === 'DAILY') return t('reminders.recurrence.daily');
    if (reminder.recurrence_type === 'MONTHLY') return t('reminders.recurrence.monthly');
    if (reminder.recurrence_type === 'WEEKLY' && reminder.recurrence_days?.length) {
        const dayLabels = reminder.recurrence_days
            .sort((a, b) => a - b)
            .map((d) => t(`reminders.recurrence.day_short.${d}`));
        return dayLabels.join(', ');
    }
    return null;
}

const ReminderCard: React.FC<ReminderCardProps> = ({ reminder, onDelete }) => {
    const { t } = useTranslation();
    const currentStatus = reminder.current_status;
    const recLabel = recurrenceLabel(reminder, t);

    return (
        <View style={commonStyles.reminderCard}>
            <View style={commonStyles.reminderHeader}>
                <Text style={commonStyles.reminderTitle}>{reminder.title}</Text>
                <TouchableOpacity
                    hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                    onPress={() => onDelete(reminder.id)}
                >
                    <Ionicons name="trash-outline" size={24} color="#FF3B30" />
                </TouchableOpacity>
            </View>
            <View
                style={{
                    flexDirection: 'row',
                    justifyContent: 'space-between',
                    alignItems: 'flex-end',
                }}
            >
                <View style={commonStyles.reminderDetails}>
                    <View style={commonStyles.detailRow}>
                        <Ionicons name="person-outline" size={16} color="#666666" />
                        <Text style={commonStyles.detailText}>
                            {reminder.user_first_name && reminder.user_last_name
                                ? `${reminder.user_first_name} ${reminder.user_last_name}`
                                : reminder.user_id}
                        </Text>
                    </View>
                    <View style={commonStyles.detailRow}>
                        <Ionicons name="calendar-outline" size={16} color="#666666" />
                        <Text style={commonStyles.detailText}>
                            {new Date(reminder.scheduled_at).toLocaleDateString('fr-FR', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                            })}
                        </Text>
                    </View>
                    {recLabel && (
                        <View style={cardStyles.recurrenceBadge}>
                            <Ionicons name="repeat-outline" size={13} color="#4A90E2" />
                            <Text style={cardStyles.recurrenceBadgeText}>{recLabel}</Text>
                        </View>
                    )}
                </View>
                {currentStatus && (
                    <Text
                        style={[
                            commonStyles.statusText,
                            {
                                DONE: commonStyles.statusDone,
                                PENDING: commonStyles.statusPending,
                                POSTPONED: commonStyles.statusPostponed,
                                UNABLE: commonStyles.statusUnable,
                                MISSED: commonStyles.statusMissed,
                            }[currentStatus] ?? commonStyles.statusPending,
                        ]}
                    >
                        {t(
                            `reminders.status.${currentStatus.charAt(0).toUpperCase() + currentStatus.slice(1).toLowerCase()}`
                        )}
                    </Text>
                )}
            </View>
        </View>
    );
};

const cardStyles = StyleSheet.create({
    recurrenceBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 4,
        marginTop: 4,
    },
    recurrenceBadgeText: {
        fontSize: 12,
        color: '#4A90E2',
        fontWeight: '500',
    },
});

export default ReminderCard;
