/**
 * Screen listing medications for a selected user profile (caregiver view).
 *
 * @module CaregiverPillulierScreen
 */
import React, { useCallback, useState, useRef } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    Image,
    ScrollView,
    RefreshControl,
    ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useTranslation } from 'react-i18next';
import { useFocusEffect, type CompositeScreenProps } from '@react-navigation/native';
import type { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList, CaregiverTabsParamList } from '../types/index';
import { commonStyles } from '../styles/commonStyles';
import { deleteMedication } from '../services/medicationService';
import { useMedications } from '../hooks';
import { useUserProfiles } from '../hooks';
import FilterPickerModal from '../components/FilterPickerModal';
import { ConfirmationModal } from '../components';

// ─── Types ───────────────────────────────────────────────────────────────────

type Props = CompositeScreenProps<
    BottomTabScreenProps<CaregiverTabsParamList, 'Pillulier'>,
    NativeStackScreenProps<RootStackParamList>
>;

// ─── Helpers ─────────────────────────────────────────────────────────────────

const DAY_LABELS: Record<number, string> = {
    0: 'Lun', 1: 'Mar', 2: 'Mer', 3: 'Jeu', 4: 'Ven', 5: 'Sam', 6: 'Dim',
};

function formatFrequency(
    frequency: string,
    recurrenceDays: number[] | undefined,
    t: (key: string) => string
): string {
    if (frequency === 'DAILY') return t('medication.frequency.DAILY');
    if (frequency === 'WEEKLY' && recurrenceDays?.length) {
        const labels = recurrenceDays
            .slice()
            .sort((a, b) => a - b)
            .map((d) => DAY_LABELS[d] ?? d)
            .join(' · ');
        return `${t('medication.frequency.WEEKLY')} · ${labels}`;
    }
    return t('medication.frequency.WEEKLY');
}

// ─── Screen ──────────────────────────────────────────────────────────────────

const CaregiverPillulierScreen: React.FC<Props> = ({ navigation }) => {
    const { t } = useTranslation();
    const { userData } = useUserProfiles();

    const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
    const [showProfilePicker, setShowProfilePicker] = useState(false);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
    const isFirstFocus = useRef(true);

    const { medications, loading, error, reload, silentReload } = useMedications(selectedUserId);

    useFocusEffect(
        useCallback(() => {
            if (isFirstFocus.current) {
                isFirstFocus.current = false;
                return;
            }
            silentReload();
        }, [silentReload])
    );

    const handleRefresh = useCallback(async () => {
        setIsRefreshing(true);
        await reload();
        setIsRefreshing(false);
    }, [reload]);

    const selectedProfile = userData?.find((u) => u.id === selectedUserId);

    const handleDelete = async () => {
        if (!deleteTargetId) return;
        try {
            await deleteMedication(deleteTargetId);
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            silentReload();
        } catch {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        } finally {
            setDeleteTargetId(null);
        }
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

            {/* Title */}
            <View style={styles.titleRow}>
                <Text style={styles.title}>{t('medication.title')}</Text>
                {selectedUserId && (
                    <TouchableOpacity
                        style={styles.addButton}
                        onPress={() => {
                            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                            navigation.navigate('CreateMedication', { userId: selectedUserId });
                        }}
                    >
                        <Ionicons name="add" size={24} color="#FFFFFF" />
                    </TouchableOpacity>
                )}
            </View>

            {/* Profile selector */}
            <TouchableOpacity
                style={styles.profileSelector}
                onPress={() => setShowProfilePicker(true)}
            >
                <View style={styles.profileSelectorContent}>
                    <Ionicons name="person-outline" size={18} color="#4A90E2" />
                    <Text style={styles.profileSelectorText}>
                        {selectedProfile
                            ? `${selectedProfile.first_name} ${selectedProfile.last_name}`
                            : t('medication.selectProfile')}
                    </Text>
                </View>
                <Ionicons name="chevron-down" size={18} color="#999999" />
            </TouchableOpacity>

            {/* Content */}
            {!selectedUserId ? (
                <View style={commonStyles.loadingContainer}>
                    <Ionicons name="medical-outline" size={48} color="#DDDDDD" />
                    <Text style={styles.emptyHint}>{t('medication.selectProfileHint')}</Text>
                </View>
            ) : loading ? (
                <View style={commonStyles.loadingContainer}>
                    <ActivityIndicator size="large" color="#4A90E2" />
                </View>
            ) : error ? (
                <View style={commonStyles.errorContainer}>
                    <Ionicons name="alert-circle-outline" size={40} color="#FF3B30" />
                    <Text style={commonStyles.errorText}>{t(error)}</Text>
                </View>
            ) : (
                <ScrollView
                    style={styles.list}
                    refreshControl={
                        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
                    }
                >
                    {medications && medications.length === 0 ? (
                        <View style={styles.emptyContainer}>
                            <Ionicons name="medical-outline" size={40} color="#DDDDDD" />
                            <Text style={styles.emptyText}>{t('medication.empty')}</Text>
                            <TouchableOpacity
                                style={styles.emptyAddButton}
                                onPress={() => {
                                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                                    navigation.navigate('CreateMedication', { userId: selectedUserId! });
                                }}
                            >
                                <Text style={styles.emptyAddButtonText}>
                                    {t('medication.addFirst')}
                                </Text>
                            </TouchableOpacity>
                        </View>
                    ) : (
                        medications?.map((med) => (
                            <View key={med.id} style={styles.card}>
                                <View style={styles.cardMain}>
                                    <View style={styles.cardHeader}>
                                        <Text style={styles.cardName}>{med.name}</Text>
                                        <TouchableOpacity
                                            onPress={() => {
                                                Haptics.impactAsync(
                                                    Haptics.ImpactFeedbackStyle.Light
                                                );
                                                setDeleteTargetId(med.id);
                                            }}
                                        >
                                            <Ionicons
                                                name="trash-outline"
                                                size={20}
                                                color="#FF3B30"
                                            />
                                        </TouchableOpacity>
                                    </View>

                                    {med.dosage ? (
                                        <Text style={styles.cardDosage}>{med.dosage}</Text>
                                    ) : null}

                                    <View style={styles.cardMeta}>
                                        <Ionicons name="repeat-outline" size={14} color="#4A90E2" />
                                        <Text style={styles.cardMetaText}>
                                            {formatFrequency(med.frequency, med.recurrence_days, t)}
                                        </Text>
                                    </View>

                                    <View style={styles.timesRow}>
                                        {med.times.map((time) => (
                                            <View key={time} style={styles.timeBadge}>
                                                <Ionicons
                                                    name="time-outline"
                                                    size={12}
                                                    color="#4A90E2"
                                                />
                                                <Text style={styles.timeBadgeText}>{time}</Text>
                                            </View>
                                        ))}
                                    </View>

                                    <Text style={styles.cardDates}>
                                        {t('medication.from')} {med.start_date}
                                        {med.end_date ? ` → ${med.end_date}` : ''}
                                    </Text>
                                </View>
                            </View>
                        ))
                    )}
                    <View style={{ height: 20 }} />
                </ScrollView>
            )}

            {/* Profile picker */}
            <FilterPickerModal
                title={t('common.pickersText.Select a profile')}
                items={
                    userData?.map((u) => ({
                        value: u.id,
                        label: `${u.first_name} ${u.last_name}`,
                    })) ?? []
                }
                selectedValue={selectedUserId ?? ''}
                onSelect={(val) => {
                    setSelectedUserId(val || null);
                    setShowProfilePicker(false);
                }}
                visible={showProfilePicker}
                onClose={() => setShowProfilePicker(false)}
            />

            {/* Delete confirmation */}
            <ConfirmationModal
                visible={!!deleteTargetId}
                title={t('medication.deleteModal.title')}
                message={t('medication.deleteModal.message')}
                confirmText={t('medication.deleteModal.confirm')}
                cancelText={t('common.buttons.Cancel')}
                onConfirm={handleDelete}
                onClose={() => setDeleteTargetId(null)}
                icon="trash-outline"
                iconColor="#FF3B30"
            />
        </View>
    );
};

// ─── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
    titleRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
        paddingLeft: 4,
    },
    title: {
        fontSize: 26,
        fontWeight: 'bold',
        color: '#333333',
    },
    addButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#4A90E2',
        alignItems: 'center',
        justifyContent: 'center',
    },
    profileSelector: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#F5F5F5',
        borderRadius: 16,
        paddingHorizontal: 16,
        paddingVertical: 12,
        marginBottom: 16,
    },
    profileSelectorContent: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
    },
    profileSelectorText: {
        fontSize: 15,
        color: '#333333',
    },
    emptyHint: {
        marginTop: 12,
        fontSize: 14,
        color: '#999999',
        textAlign: 'center',
    },
    list: {
        flex: 1,
    },
    emptyContainer: {
        alignItems: 'center',
        paddingTop: 60,
        gap: 12,
    },
    emptyText: {
        fontSize: 14,
        color: '#999999',
    },
    emptyAddButton: {
        backgroundColor: '#4A90E2',
        paddingHorizontal: 20,
        paddingVertical: 10,
        borderRadius: 12,
        marginTop: 4,
    },
    emptyAddButtonText: {
        color: '#FFFFFF',
        fontWeight: '600',
        fontSize: 14,
    },
    card: {
        backgroundColor: '#F8F9FF',
        borderRadius: 16,
        padding: 16,
        marginBottom: 12,
        borderLeftWidth: 4,
        borderLeftColor: '#4A90E2',
    },
    cardMain: {
        gap: 6,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    cardName: {
        fontSize: 17,
        fontWeight: '700',
        color: '#333333',
        flex: 1,
    },
    cardDosage: {
        fontSize: 14,
        color: '#666666',
    },
    cardMeta: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
    },
    cardMetaText: {
        fontSize: 13,
        color: '#4A90E2',
        fontWeight: '500',
    },
    timesRow: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 6,
        marginTop: 2,
    },
    timeBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 4,
        backgroundColor: '#EEF4FC',
        borderRadius: 10,
        paddingHorizontal: 10,
        paddingVertical: 4,
    },
    timeBadgeText: {
        fontSize: 13,
        color: '#4A90E2',
        fontWeight: '600',
    },
    cardDates: {
        fontSize: 12,
        color: '#999999',
        marginTop: 2,
    },
});

export default CaregiverPillulierScreen;
