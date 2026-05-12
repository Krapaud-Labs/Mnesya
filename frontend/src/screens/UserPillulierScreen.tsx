/**
 * Semainier (7-day week view) showing medication schedule for the logged-in user.
 *
 * @module UserPillulierScreen
 */
import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ScrollView,
    ActivityIndicator,
    RefreshControl,
    Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useTranslation } from 'react-i18next';
import { commonStyles } from '../styles/commonStyles';
import { useWeekSchedule } from '../hooks';

// ─── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
    DONE: '#34C759',
    MISSED: '#FF3B30',
    PENDING: '#4A90E2',
    POSTPONED: '#FF9500',
};

const FR_DAYS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
const FR_MONTHS = [
    'jan', 'fév', 'mar', 'avr', 'mai', 'juin',
    'juil', 'aoû', 'sep', 'oct', 'nov', 'déc',
];

function formatDayHeader(dateStr: string): { day: string; date: string } {
    const d = new Date(dateStr + 'T12:00:00');
    const dayIdx = (d.getDay() + 6) % 7; // Mon=0
    return {
        day: FR_DAYS[dayIdx],
        date: `${d.getDate()} ${FR_MONTHS[d.getMonth()]}`,
    };
}

function isToday(dateStr: string): boolean {
    const today = new Date().toISOString().split('T')[0];
    return dateStr === today;
}

function formatWeekRange(weekStart: string): string {
    const start = new Date(weekStart + 'T12:00:00');
    const end = new Date(weekStart + 'T12:00:00');
    end.setDate(end.getDate() + 6);
    return `${start.getDate()} ${FR_MONTHS[start.getMonth()]} – ${end.getDate()} ${FR_MONTHS[end.getMonth()]} ${end.getFullYear()}`;
}

// ─── Screen ──────────────────────────────────────────────────────────────────

const UserPillulierScreen: React.FC = () => {
    const { t } = useTranslation();
    const { weekData, loading, error, reload, goToPrevWeek, goToNextWeek, weekStart } =
        useWeekSchedule();
    const [refreshing, setRefreshing] = React.useState(false);

    const handleRefresh = async () => {
        setRefreshing(true);
        await reload();
        setRefreshing(false);
    };

    return (
        <View style={commonStyles.container}>
            {/* Header */}
            <View style={commonStyles.header}>
                <View style={commonStyles.headerSpacer} />
                <View style={commonStyles.headerCenter}>
                    <Image
                        source={require('../../assets/mnesya-logo.png')}
                        style={commonStyles.logo}
                    />
                </View>
                <View style={commonStyles.headerSpacer} />
            </View>

            {/* Title + week navigation */}
            <View style={styles.titleSection}>
                <Text style={styles.title}>{t('medication.weekTitle')}</Text>
                <View style={styles.weekNav}>
                    <TouchableOpacity
                        onPress={() => {
                            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                            goToPrevWeek();
                        }}
                        style={styles.navBtn}
                    >
                        <Ionicons name="chevron-back" size={20} color="#4A90E2" />
                    </TouchableOpacity>
                    <Text style={styles.weekLabel}>{formatWeekRange(weekStart)}</Text>
                    <TouchableOpacity
                        onPress={() => {
                            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                            goToNextWeek();
                        }}
                        style={styles.navBtn}
                    >
                        <Ionicons name="chevron-forward" size={20} color="#4A90E2" />
                    </TouchableOpacity>
                </View>
            </View>

            {loading ? (
                <View style={commonStyles.loadingContainer}>
                    <ActivityIndicator size="large" color="#4A90E2" />
                    <Text style={commonStyles.loadingText}>{t('common.messages.loading')}</Text>
                </View>
            ) : error ? (
                <View style={commonStyles.errorContainer}>
                    <Ionicons name="alert-circle-outline" size={40} color="#FF3B30" />
                    <Text style={commonStyles.errorText}>{t(error)}</Text>
                </View>
            ) : (
                <ScrollView
                    style={{ flex: 1 }}
                    refreshControl={
                        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
                    }
                    showsVerticalScrollIndicator={false}
                >
                    {weekData?.days.map((day) => {
                        const { day: dayLabel, date: dateLabel } = formatDayHeader(day.date);
                        const today = isToday(day.date);

                        return (
                            <View
                                key={day.date}
                                style={[styles.dayCard, today && styles.dayCardToday]}
                            >
                                {/* Day header */}
                                <View style={styles.dayHeader}>
                                    <View style={[styles.dayBadge, today && styles.dayBadgeToday]}>
                                        <Text
                                            style={[
                                                styles.dayBadgeDay,
                                                today && styles.dayBadgeTextToday,
                                            ]}
                                        >
                                            {dayLabel}
                                        </Text>
                                        <Text
                                            style={[
                                                styles.dayBadgeDate,
                                                today && styles.dayBadgeTextToday,
                                            ]}
                                        >
                                            {dateLabel}
                                        </Text>
                                    </View>
                                    {today && (
                                        <View style={styles.todayBadge}>
                                            <Text style={styles.todayBadgeText}>
                                                {t('medication.today')}
                                            </Text>
                                        </View>
                                    )}
                                </View>

                                {/* Entries */}
                                {day.entries.length === 0 ? (
                                    <Text style={styles.noEntry}>{t('medication.noMeds')}</Text>
                                ) : (
                                    day.entries.map((entry) => {
                                        const color =
                                            STATUS_COLORS[entry.status ?? 'PENDING'] ??
                                            '#AAAAAA';
                                        return (
                                            <View key={entry.reminder_id} style={styles.entry}>
                                                <View
                                                    style={[
                                                        styles.statusDot,
                                                        { backgroundColor: color },
                                                    ]}
                                                />
                                                <View style={styles.entryInfo}>
                                                    <Text style={styles.entryName}>
                                                        {entry.name}
                                                    </Text>
                                                    {entry.dosage ? (
                                                        <Text style={styles.entryDosage}>
                                                            {entry.dosage}
                                                        </Text>
                                                    ) : null}
                                                </View>
                                                <Text style={styles.entryTime}>{entry.time}</Text>
                                            </View>
                                        );
                                    })
                                )}
                            </View>
                        );
                    })}

                    {/* Legend */}
                    <View style={styles.legend}>
                        {Object.entries(STATUS_COLORS).map(([key, color]) => (
                            <View key={key} style={styles.legendItem}>
                                <View style={[styles.legendDot, { backgroundColor: color }]} />
                                <Text style={styles.legendLabel}>{t(`medication.status.${key}`)}</Text>
                            </View>
                        ))}
                    </View>

                    <View style={{ height: 20 }} />
                </ScrollView>
            )}
        </View>
    );
};

// ─── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
    titleSection: {
        marginBottom: 12,
        gap: 8,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333333',
        paddingLeft: 4,
    },
    weekNav: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: '#F5F5F5',
        borderRadius: 14,
        paddingHorizontal: 8,
        paddingVertical: 6,
    },
    navBtn: {
        padding: 6,
    },
    weekLabel: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333333',
    },
    dayCard: {
        backgroundColor: '#F8F9FF',
        borderRadius: 16,
        padding: 14,
        marginBottom: 10,
    },
    dayCardToday: {
        borderWidth: 2,
        borderColor: '#4A90E2',
        backgroundColor: '#EEF4FC',
    },
    dayHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 10,
        gap: 8,
    },
    dayBadge: {
        backgroundColor: '#E5E5EA',
        borderRadius: 10,
        paddingHorizontal: 10,
        paddingVertical: 4,
        alignItems: 'center',
    },
    dayBadgeToday: {
        backgroundColor: '#4A90E2',
    },
    dayBadgeDay: {
        fontSize: 12,
        fontWeight: '700',
        color: '#666666',
    },
    dayBadgeDate: {
        fontSize: 11,
        color: '#666666',
    },
    dayBadgeTextToday: {
        color: '#FFFFFF',
    },
    todayBadge: {
        backgroundColor: '#4A90E2',
        borderRadius: 8,
        paddingHorizontal: 8,
        paddingVertical: 2,
    },
    todayBadgeText: {
        color: '#FFFFFF',
        fontSize: 11,
        fontWeight: '600',
    },
    noEntry: {
        fontSize: 13,
        color: '#AAAAAA',
        fontStyle: 'italic',
        paddingLeft: 4,
    },
    entry: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 10,
        paddingVertical: 6,
        borderTopWidth: 1,
        borderTopColor: '#EEEEEE',
    },
    statusDot: {
        width: 10,
        height: 10,
        borderRadius: 5,
        flexShrink: 0,
    },
    entryInfo: {
        flex: 1,
    },
    entryName: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333333',
    },
    entryDosage: {
        fontSize: 12,
        color: '#777777',
    },
    entryTime: {
        fontSize: 13,
        fontWeight: '700',
        color: '#4A90E2',
    },
    legend: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 12,
        justifyContent: 'center',
        marginTop: 8,
        paddingHorizontal: 4,
    },
    legendItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
    },
    legendDot: {
        width: 10,
        height: 10,
        borderRadius: 5,
    },
    legendLabel: {
        fontSize: 12,
        color: '#666666',
    },
});

export default UserPillulierScreen;
