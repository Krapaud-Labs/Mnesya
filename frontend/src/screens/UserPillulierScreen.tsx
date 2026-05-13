/**
 * Today's medication schedule for the logged-in user.
 *
 * @module UserPillulierScreen
 */
import React, { useCallback, useRef, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    ActivityIndicator,
    RefreshControl,
    Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from 'react-i18next';
import { useFocusEffect } from '@react-navigation/native';
import { commonStyles } from '../styles/commonStyles';
import { useWeekSchedule, useAutoRefresh } from '../hooks';

// ─── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
    DONE: '#34C759',
    MISSED: '#FF3B30',
    PENDING: '#4A90E2',
    POSTPONED: '#FF9500',
};

const STATUS_ICONS: Record<string, keyof typeof Ionicons.glyphMap> = {
    DONE: 'checkmark-circle',
    MISSED: 'close-circle',
    PENDING: 'time-outline',
    POSTPONED: 'arrow-redo-circle',
};

const FR_DAYS = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
const FR_MONTHS = [
    'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
];

function formatTodayHeader(): string {
    const now = new Date();
    return `${FR_DAYS[now.getDay()]} ${now.getDate()} ${FR_MONTHS[now.getMonth()]}`;
}

function todayStr(): string {
    return new Date().toISOString().split('T')[0];
}

// ─── Screen ──────────────────────────────────────────────────────────────────

const UserPillulierScreen: React.FC = () => {
    const { t } = useTranslation();
    const { weekData, loading, error, reload, silentReload } = useWeekSchedule();
    const [refreshing, setRefreshing] = useState(false);
    const isFirstFocus = useRef(true);

    useAutoRefresh(silentReload, 20_000);

    useFocusEffect(
        useCallback(() => {
            if (isFirstFocus.current) {
                isFirstFocus.current = false;
                return;
            }
            silentReload();
        }, [silentReload])
    );

    const [showScrollFade, setShowScrollFade] = useState(true);
    const [isScrollable, setIsScrollable] = useState(false);
    const scrollContainerHeight = useRef(0);

    const handleContentSizeChange = (_: number, contentHeight: number) => {
        setIsScrollable(contentHeight > scrollContainerHeight.current);
    };

    const handleScroll = (event: {
        nativeEvent: {
            contentOffset: { y: number };
            layoutMeasurement: { height: number };
            contentSize: { height: number };
        };
    }) => {
        const { contentOffset, layoutMeasurement, contentSize } = event.nativeEvent;
        setShowScrollFade(contentOffset.y + layoutMeasurement.height < contentSize.height - 10);
    };

    const handleRefresh = async () => {
        setRefreshing(true);
        await reload();
        setRefreshing(false);
    };

    const today = todayStr();
    const todayData = weekData?.days.find(d => d.date === today) ?? null;

    return (
        <View style={styles.screen}>
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

            {/* Title */}
            <View style={styles.titleSection}>
                <Text style={styles.title}>{t('medication.today')}</Text>
                <Text style={styles.dateLabel}>{formatTodayHeader()}</Text>
            </View>

            {loading ? (
                <View style={commonStyles.loadingContainer}>
                    <ActivityIndicator size="large" color="#4A90E2" />
                    <Text style={commonStyles.loadingText}>{t('common.messages.loading')}</Text>
                </View>
            ) : error ? (
                <View style={commonStyles.errorContainer}>
                    <Ionicons name="alert-circle-outline" size={48} color="#FF3B30" />
                    <Text style={commonStyles.errorText}>{t(error)}</Text>
                </View>
            ) : (
                <View style={styles.listWrapper}>
                    <ScrollView
                        style={{ flex: 1 }}
                        refreshControl={
                            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
                        }
                        showsVerticalScrollIndicator={false}
                        onScroll={handleScroll}
                        scrollEventThrottle={16}
                        onLayout={(e) => {
                            scrollContainerHeight.current = e.nativeEvent.layout.height;
                        }}
                        onContentSizeChange={handleContentSizeChange}
                        contentContainerStyle={styles.scrollContent}
                    >
                        {!todayData || todayData.entries.length === 0 ? (
                            <View style={styles.emptyState}>
                                <Ionicons name="checkmark-circle-outline" size={52} color="#DDDDDD" />
                                <Text style={styles.emptyText}>{t('medication.noMeds')}</Text>
                            </View>
                        ) : (
                            todayData.entries.map((entry) => {
                                const status = entry.status ?? 'PENDING';
                                const color = STATUS_COLORS[status] ?? '#AAAAAA';
                                const icon = STATUS_ICONS[status] ?? 'time-outline';
                                const isDone = status !== 'PENDING';
                                return (
                                    <View
                                        key={entry.reminder_id}
                                        style={[styles.card, isDone && styles.cardDone]}
                                    >
                                        <View style={[styles.cardAccent, { backgroundColor: color }]} />
                                        <View style={styles.cardBody}>
                                            <View style={styles.cardTop}>
                                                <Text style={[styles.entryName, isDone && styles.entryNameDone]}>
                                                    {entry.name}
                                                </Text>
                                                <Text style={styles.entryMoment}>
                                                    {t(`medication.moments.${entry.moment}`, { defaultValue: entry.moment })}
                                                </Text>
                                            </View>
                                            {entry.dosage ? (
                                                <Text style={styles.entryDosage}>{entry.dosage}</Text>
                                            ) : null}
                                        </View>
                                        <Ionicons name={icon} size={26} color={color} style={styles.statusIcon} />
                                    </View>
                                );
                            })
                        )}

                        {/* Legend */}
                        {todayData && todayData.entries.length > 0 && (
                            <View style={styles.legend}>
                                {Object.entries(STATUS_COLORS).map(([key, color]) => (
                                    <View key={key} style={styles.legendItem}>
                                        <View style={[styles.legendDot, { backgroundColor: color }]} />
                                        <Text style={styles.legendLabel}>{t(`medication.status.${key}`)}</Text>
                                    </View>
                                ))}
                            </View>
                        )}

                        <View style={{ height: 20 }} />
                    </ScrollView>

                    {showScrollFade && isScrollable && (
                        <View style={styles.scrollFade} pointerEvents="none">
                            <Ionicons name="chevron-down" size={24} color="#4A90E2" />
                        </View>
                    )}
                </View>
            )}
        </View>
    );
};

// ─── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
    screen: {
        flex: 1,
        backgroundColor: '#FFFFFF',
    },
    titleSection: {
        width: '100%',
        paddingHorizontal: 20,
        marginTop: 20,
        marginBottom: 16,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#333333',
    },
    dateLabel: {
        fontSize: 14,
        color: '#AAAAAA',
        marginTop: 2,
        textTransform: 'capitalize',
    },
    listWrapper: {
        flex: 1,
        position: 'relative',
    },
    scrollContent: {
        paddingHorizontal: 16,
        paddingTop: 4,
        flexGrow: 1,
    },
    scrollFade: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 40,
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(255,255,255,0.85)',
    },

    // ── Empty state ──
    emptyState: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        gap: 12,
    },
    emptyText: {
        fontSize: 15,
        color: '#CCCCCC',
    },

    // ── Entry card ──
    card: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F8F9FF',
        borderRadius: 14,
        marginBottom: 10,
        overflow: 'hidden',
    },
    cardDone: {
        opacity: 0.55,
    },
    cardAccent: {
        width: 4,
        alignSelf: 'stretch',
    },
    cardBody: {
        flex: 1,
        paddingVertical: 14,
        paddingHorizontal: 14,
    },
    cardTop: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    entryName: {
        fontSize: 15,
        fontWeight: '600',
        color: '#333333',
        flex: 1,
    },
    entryNameDone: {
        color: '#AAAAAA',
    },
    entryMoment: {
        fontSize: 11,
        fontWeight: '500',
        color: '#888888',
        marginLeft: 8,
        flexShrink: 1,
        textAlign: 'right',
    },
    entryDosage: {
        fontSize: 12,
        color: '#999999',
        marginTop: 2,
    },
    statusIcon: {
        marginRight: 14,
    },

    // ── Legend ──
    legend: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 12,
        justifyContent: 'center',
        marginTop: 16,
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
