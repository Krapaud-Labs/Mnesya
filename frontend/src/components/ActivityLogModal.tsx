/**
 * Activity log modal component for the caregiver dashboard.
 *
 * Displays user interactions (DONE, POSTPONED, UNABLE, MISSED) across all
 * reminders managed by the caregiver over the last 7 days.
 * Supports filtering by status and by user, grouped by day.
 *
 * @module ActivityLogModal
 */

import React, { useRef, useState, useMemo } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    Modal,
    ScrollView,
    ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from 'react-i18next';
import { commonStyles } from '../styles/commonStyles';
import type { ActivityLogEntry } from '../types/interfaces';

// ─── Status configuration ───────────────────────────────────────────────────

type StatusKey = 'DONE' | 'POSTPONED' | 'UNABLE' | 'MISSED';

const STATUS_CONFIG: Record<
    StatusKey,
    { icon: keyof typeof Ionicons.glyphMap; color: string; labelKey: string }
> = {
    DONE: {
        icon: 'checkmark-circle',
        color: '#4CAF50',
        labelKey: 'dashboard.activityLog.statusDone',
    },
    POSTPONED: {
        icon: 'time-outline',
        color: '#2196F3',
        labelKey: 'dashboard.activityLog.statusPostponed',
    },
    UNABLE: {
        icon: 'close-circle',
        color: '#F44336',
        labelKey: 'dashboard.activityLog.statusUnable',
    },
    MISSED: {
        icon: 'alert-circle-outline',
        color: '#E53935',
        labelKey: 'dashboard.activityLog.statusMissed',
    },
};

const ALL_STATUSES: StatusKey[] = ['DONE', 'POSTPONED', 'UNABLE', 'MISSED'];

type EntryType = 'ALL' | 'REMINDER' | 'MEDICATION';

const MONTHS: Record<string, string[]> = {
    fr: ['jan', 'fév', 'mars', 'avr', 'mai', 'juin', 'juil', 'août', 'sep', 'oct', 'nov', 'déc'],
    en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

const getTime = (iso: string): string => {
    const d = new Date(iso);
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

// ─── Sub-component: single log entry ────────────────────────────────────────

interface LogEntryProps {
    entry: ActivityLogEntry;
}

const LogEntryRow: React.FC<LogEntryProps> = ({ entry }) => {
    const { t } = useTranslation();
    const config = STATUS_CONFIG[entry.status as StatusKey] ?? STATUS_CONFIG['MISSED'];

    return (
        <View style={styles.entryRow}>
            <Ionicons name={config.icon} size={24} color={config.color} style={styles.entryIcon} />
            <View style={styles.entryContent}>
                <View style={styles.entryTitleRow}>
                    <Text style={styles.entryTitle} numberOfLines={1}>
                        {entry.reminder_title}
                    </Text>
                    <View style={[styles.typeTag, entry.is_medication ? styles.typeTagMed : styles.typeTagReminder]}>
                        <Ionicons
                            name={entry.is_medication ? 'medkit-outline' : 'alarm-outline'}
                            size={10}
                            color={entry.is_medication ? '#9C27B0' : '#4A90E2'}
                        />
                    </View>
                </View>
                <Text style={styles.entryMeta}>
                    {entry.user_first_name} {entry.user_last_name}
                    {'  ·  '}
                    <Text style={[styles.entryStatus, { color: config.color }]}>
                        {t(config.labelKey)}
                    </Text>
                </Text>
            </View>
            <Text style={styles.entryTime}>{getTime(entry.occurred_at)}</Text>
        </View>
    );
};

// ─── Main component ──────────────────────────────────────────────────────────

interface ActivityLogModalProps {
    visible: boolean;
    onClose: () => void;
    entries: ActivityLogEntry[] | null;
    loading: boolean;
    error: string | null;
}

const ActivityLogModal: React.FC<ActivityLogModalProps> = ({
    visible,
    onClose,
    entries,
    loading,
    error,
}) => {
    const { t, i18n } = useTranslation();
    const [activeStatuses, setActiveStatuses] = useState<StatusKey[]>([]);
    const [selectedUser, setSelectedUser] = useState<string | null>(null);
    const [activeType, setActiveType] = useState<EntryType>('ALL');
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

    const uniqueUsers = useMemo(() => {
        if (!entries) return [];
        const seen = new Set<string>();
        const users: string[] = [];
        for (const e of entries) {
            const key = `${e.user_first_name} ${e.user_last_name}`;
            if (!seen.has(key)) { seen.add(key); users.push(key); }
        }
        return users;
    }, [entries]);

    const statusCounts = useMemo(() => {
        const counts: Partial<Record<StatusKey, number>> = {};
        for (const e of entries ?? []) {
            const s = e.status as StatusKey;
            counts[s] = (counts[s] ?? 0) + 1;
        }
        return counts;
    }, [entries]);

    const filteredEntries = (entries ?? []).filter(e => {
        const statusOk = activeStatuses.length === 0 || activeStatuses.includes(e.status as StatusKey);
        const userOk = selectedUser === null || `${e.user_first_name} ${e.user_last_name}` === selectedUser;
        const typeOk = activeType === 'ALL'
            || (activeType === 'MEDICATION' && e.is_medication)
            || (activeType === 'REMINDER' && !e.is_medication);
        return statusOk && userOk && typeOk;
    });

    const groupedByDay = (() => {
        const map = new Map<string, ActivityLogEntry[]>();
        for (const e of filteredEntries) {
            const dayKey = e.occurred_at.slice(0, 10);
            if (!map.has(dayKey)) map.set(dayKey, []);
            map.get(dayKey)!.push(e);
        }
        const now = new Date();
        const todayMs = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
        const yesterdayMs = todayMs - 86400000;
        const months = MONTHS[i18n.language] ?? MONTHS['en'];

        return Array.from(map.entries()).map(([dayKey, dayEntries]) => {
            const d = new Date(dayKey + 'T12:00:00');
            const dayMs = new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
            let label: string;
            if (dayMs === todayMs) label = t('dashboard.activityLog.today');
            else if (dayMs === yesterdayMs) label = t('dashboard.activityLog.yesterday');
            else {
                const yearSuffix = d.getFullYear() !== now.getFullYear() ? ` ${d.getFullYear()}` : '';
                label = `${d.getDate()} ${months[d.getMonth()]}${yearSuffix}`;
            }
            return { dayKey, label, entries: dayEntries };
        });
    })();

    const toggleStatus = (status: StatusKey) => {
        setActiveStatuses(prev =>
            prev.includes(status) ? prev.filter(s => s !== status) : [...prev, status]
        );
    };

    const hasData = !loading && !error && entries && entries.length > 0;

    const renderFilters = () => (
        <View style={styles.filtersContainer}>
            {/* Type filter */}
            <View style={styles.typeFilterRow}>
                {(['ALL', 'REMINDER', 'MEDICATION'] as EntryType[]).map(type => {
                    const isActive = activeType === type;
                    const icon = type === 'MEDICATION' ? 'medkit-outline' : type === 'REMINDER' ? 'alarm-outline' : null;
                    const labelKey = type === 'ALL'
                        ? 'dashboard.activityLog.typeAll'
                        : type === 'REMINDER'
                        ? 'dashboard.activityLog.typeReminder'
                        : 'dashboard.activityLog.typeMedication';
                    const color = type === 'MEDICATION' ? '#9C27B0' : '#4A90E2';
                    return (
                        <TouchableOpacity
                            key={type}
                            style={[styles.typeChip, isActive && { backgroundColor: color, borderColor: color }]}
                            onPress={() => setActiveType(type)}
                            activeOpacity={0.7}
                        >
                            {icon && (
                                <Ionicons
                                    name={icon}
                                    size={13}
                                    color={isActive ? '#FFFFFF' : color}
                                />
                            )}
                            <Text style={[styles.typeChipText, { color: isActive ? '#FFFFFF' : color }]}>
                                {t(labelKey)}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </View>

            {/* Status chips — act as both summary and filter */}
            <View style={styles.statusFilterRow}>
                {ALL_STATUSES.map(status => {
                    const cfg = STATUS_CONFIG[status];
                    const count = statusCounts[status] ?? 0;
                    const isActive = activeStatuses.includes(status);
                    const isFiltering = activeStatuses.length > 0;
                    return (
                        <TouchableOpacity
                            key={status}
                            style={[
                                styles.statusChip,
                                { borderColor: cfg.color },
                                isActive && { backgroundColor: cfg.color },
                                isFiltering && !isActive && styles.statusChipDimmed,
                            ]}
                            onPress={() => toggleStatus(status)}
                            activeOpacity={0.7}
                        >
                            <Ionicons
                                name={cfg.icon}
                                size={13}
                                color={isActive ? '#FFFFFF' : (isFiltering && !isActive ? '#CCCCCC' : cfg.color)}
                            />
                            <Text
                                style={[
                                    styles.statusChipText,
                                    { color: isActive ? '#FFFFFF' : (isFiltering && !isActive ? '#CCCCCC' : cfg.color) },
                                ]}
                            >
                                {count}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </View>

            {/* User filter — only shown when multiple users */}
            {uniqueUsers.length > 1 && (
                <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.userFilterContent}
                    style={styles.userFilterRow}
                >
                    <TouchableOpacity
                        style={[styles.userChip, selectedUser === null && styles.userChipActive]}
                        onPress={() => setSelectedUser(null)}
                    >
                        <Text style={[styles.userChipText, selectedUser === null && styles.userChipTextActive]}>
                            {t('dashboard.activityLog.allUsers')}
                        </Text>
                    </TouchableOpacity>
                    {uniqueUsers.map(user => (
                        <TouchableOpacity
                            key={user}
                            style={[styles.userChip, selectedUser === user && styles.userChipActive]}
                            onPress={() => setSelectedUser(prev => prev === user ? null : user)}
                        >
                            <Text style={[styles.userChipText, selectedUser === user && styles.userChipTextActive]}>
                                {user}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            )}
        </View>
    );

    const renderContent = () => {
        if (loading) {
            return (
                <View style={styles.centeredState}>
                    <ActivityIndicator size="large" color="#4A90E2" />
                </View>
            );
        }
        if (error) {
            return (
                <View style={styles.centeredState}>
                    <Ionicons name="alert-circle-outline" size={40} color="#9E9E9E" />
                    <Text style={styles.emptyText}>{t(error)}</Text>
                </View>
            );
        }
        if (!entries || entries.length === 0) {
            return (
                <View style={styles.centeredState}>
                    <Ionicons name="time-outline" size={40} color="#9E9E9E" />
                    <Text style={styles.emptyText}>{t('dashboard.activityLog.empty')}</Text>
                </View>
            );
        }
        if (filteredEntries.length === 0) {
            return (
                <View style={styles.centeredState}>
                    <Ionicons name="search-outline" size={40} color="#9E9E9E" />
                    <Text style={styles.emptyText}>{t('dashboard.activityLog.noResults')}</Text>
                </View>
            );
        }
        return (
            <View style={styles.listWrapper}>
                <ScrollView
                    style={styles.list}
                    contentContainerStyle={styles.listContent}
                    showsVerticalScrollIndicator={false}
                    onScroll={handleScroll}
                    onContentSizeChange={handleContentSizeChange}
                    onLayout={(e) => { scrollContainerHeight.current = e.nativeEvent.layout.height; }}
                    scrollEventThrottle={16}
                >
                    {groupedByDay.map(({ dayKey, label, entries: dayEntries }) => (
                        <View key={dayKey}>
                            <View style={styles.dayHeader}>
                                <View style={styles.dayHeaderLine} />
                                <Text style={styles.dayHeaderText}>{label}</Text>
                                <View style={styles.dayHeaderLine} />
                            </View>
                            {dayEntries.map(entry => (
                                <LogEntryRow key={entry.status_id} entry={entry} />
                            ))}
                        </View>
                    ))}
                </ScrollView>
                {showScrollFade && isScrollable && (
                    <View style={styles.scrollFade} pointerEvents="none">
                        <Ionicons name="chevron-down" size={24} color="#4A90E2" />
                    </View>
                )}
            </View>
        );
    };

    return (
        <Modal visible={visible} transparent={true} animationType="slide" onRequestClose={onClose}>
            <View style={commonStyles.modalOverlay}>
                <View style={styles.modalContent}>
                    {/* Header */}
                    <View style={styles.header}>
                        <Text style={styles.modalTitle}>{t('dashboard.activityLog.title')}</Text>
                    </View>
                    <Text style={styles.subtitle}>{t('dashboard.activityLog.subtitle')}</Text>

                    {/* Filters */}
                    {hasData && renderFilters()}

                    {/* Content */}
                    <View style={styles.contentArea}>{renderContent()}</View>

                    {/* Close */}
                    <TouchableOpacity style={styles.closeButton} onPress={onClose}>
                        <Text style={styles.closeButtonText}>{t('common.buttons.Close')}</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </Modal>
    );
};

// ─── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
    modalContent: {
        backgroundColor: '#FFFFFF',
        borderRadius: 15,
        padding: 24,
        width: '92%',
        maxHeight: '85%',
        alignItems: 'center',
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        marginBottom: 4,
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#333333',
    },
    subtitle: {
        fontSize: 13,
        color: '#888888',
        marginBottom: 12,
        textAlign: 'center',
    },

    // ── Filters ──
    filtersContainer: {
        width: '100%',
        marginBottom: 12,
        gap: 8,
    },
    typeFilterRow: {
        flexDirection: 'row',
        gap: 6,
    },
    typeChip: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 4,
        paddingVertical: 6,
        borderRadius: 20,
        borderWidth: 1.5,
        borderColor: '#DDDDDD',
        backgroundColor: 'transparent',
    },
    typeChipText: {
        fontSize: 12,
        fontWeight: '600',
    },
    statusFilterRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        gap: 6,
    },
    statusChip: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 4,
        paddingVertical: 6,
        borderRadius: 20,
        borderWidth: 1.5,
        backgroundColor: 'transparent',
    },
    statusChipDimmed: {
        borderColor: '#DDDDDD',
        backgroundColor: 'transparent',
    },
    statusChipText: {
        fontSize: 13,
        fontWeight: '700',
    },
    userFilterRow: {
        maxHeight: 36,
    },
    userFilterContent: {
        flexDirection: 'row',
        gap: 6,
    },
    userChip: {
        paddingHorizontal: 12,
        paddingVertical: 5,
        borderRadius: 14,
        borderWidth: 1,
        borderColor: '#DDDDDD',
        backgroundColor: 'transparent',
    },
    userChipActive: {
        borderColor: '#4A90E2',
        backgroundColor: '#4A90E2',
    },
    userChipText: {
        fontSize: 13,
        color: '#666666',
    },
    userChipTextActive: {
        color: '#FFFFFF',
        fontWeight: '600',
    },

    // ── Content ──
    contentArea: {
        width: '100%',
        minHeight: 80,
        maxHeight: 340,
    },
    centeredState: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 32,
        gap: 12,
    },
    emptyText: {
        fontSize: 15,
        color: '#9E9E9E',
        textAlign: 'center',
    },
    listWrapper: {
        width: '100%',
        position: 'relative',
    },
    list: {
        width: '100%',
    },
    listContent: {
        paddingBottom: 4,
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

    // ── Day sections ──
    dayHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 12,
        marginBottom: 4,
        gap: 8,
    },
    dayHeaderLine: {
        flex: 1,
        height: 1,
        backgroundColor: '#EEEEEE',
    },
    dayHeaderText: {
        fontSize: 12,
        fontWeight: '600',
        color: '#AAAAAA',
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },

    // ── Entry row ──
    entryRow: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 9,
        borderBottomWidth: 1,
        borderBottomColor: '#F0F0F0',
        gap: 10,
    },
    entryIcon: {
        flexShrink: 0,
    },
    entryContent: {
        flex: 1,
    },
    entryTitleRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 5,
    },
    entryTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333333',
        flexShrink: 1,
    },
    typeTag: {
        width: 18,
        height: 18,
        borderRadius: 9,
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
    },
    typeTagMed: {
        backgroundColor: '#F3E5F5',
    },
    typeTagReminder: {
        backgroundColor: '#E3F2FD',
    },
    entryMeta: {
        fontSize: 12,
        color: '#666666',
        marginTop: 1,
    },
    entryStatus: {
        fontWeight: '600',
    },
    entryTime: {
        fontSize: 12,
        color: '#AAAAAA',
        flexShrink: 0,
    },

    // ── Close button ──
    closeButton: {
        marginTop: 18,
        backgroundColor: '#4A90E2',
        borderRadius: 10,
        paddingVertical: 12,
        paddingHorizontal: 40,
    },
    closeButtonText: {
        color: '#FFFFFF',
        fontWeight: 'bold',
        fontSize: 16,
    },
});

export default ActivityLogModal;
