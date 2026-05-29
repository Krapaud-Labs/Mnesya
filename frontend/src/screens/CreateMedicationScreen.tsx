/**
 * Screen for creating a new medication with automatic reminder generation.
 *
 * @module CreateMedicationScreen
 */
import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    TextInput,
    Image,
    ScrollView,
    ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useTranslation } from 'react-i18next';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../types/index';
import { commonStyles } from '../styles/commonStyles';
import { PlatformDatePicker, ConfirmationModal } from '../components';
import { createMedication } from '../services/medicationService';
import { formatDate } from '../utils/recurrenceUtils';

// ─── Types ───────────────────────────────────────────────────────────────────

type Props = NativeStackScreenProps<RootStackParamList, 'CreateMedication'>;

type Frequency = 'DAILY' | 'WEEKLY';

const ALL_MOMENTS = [
    'BEFORE_BREAKFAST',
    'DURING_BREAKFAST',
    'AFTER_BREAKFAST',
    'BEFORE_LUNCH',
    'DURING_LUNCH',
    'AFTER_LUNCH',
    'BEFORE_DINNER',
    'DURING_DINNER',
    'AFTER_DINNER',
    'BEDTIME',
] as const;

// ─── Screen ──────────────────────────────────────────────────────────────────

const CreateMedicationScreen: React.FC<Props> = ({ navigation, route }) => {
    const { t } = useTranslation();
    const insets = useSafeAreaInsets();
    const { userId } = route.params;

    // Form fields
    const [name, setName] = useState('');
    const [dosage, setDosage] = useState('');
    const [frequency, setFrequency] = useState<Frequency>('DAILY');
    const [recurrenceDays, setRecurrenceDays] = useState<number[]>([]);
    const [selectedMoments, setSelectedMoments] = useState<string[]>([]);
    const [startDate, setStartDate] = useState<Date>(new Date());
    const [endDate, setEndDate] = useState<Date | null>(null);

    // Picker visibility
    const [showStartDatePicker, setShowStartDatePicker] = useState(false);
    const [showEndDatePicker, setShowEndDatePicker] = useState(false);

    // UI state
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [nameError, setNameError] = useState('');
    const [momentsError, setMomentsError] = useState('');
    const [daysError, setDaysError] = useState('');

    const DAY_SHORTS = ['L', 'M', 'Me', 'J', 'V', 'S', 'D'];

    const toggleDay = (day: number) => {
        setDaysError('');
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        setRecurrenceDays((prev) =>
            prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
        );
    };

    const toggleMoment = (moment: string) => {
        setMomentsError('');
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        setSelectedMoments((prev) =>
            prev.includes(moment) ? prev.filter((m) => m !== moment) : [...prev, moment]
        );
    };

    const handleSave = () => {
        let hasError = false;

        if (!name.trim()) {
            setNameError(t('medication.errors.nameRequired'));
            hasError = true;
        } else {
            setNameError('');
        }

        if (selectedMoments.length === 0) {
            setMomentsError(t('medication.errors.momentsRequired'));
            hasError = true;
        } else {
            setMomentsError('');
        }

        if (frequency === 'WEEKLY' && recurrenceDays.length === 0) {
            setDaysError(t('medication.errors.daysRequired'));
            hasError = true;
        } else {
            setDaysError('');
        }

        if (hasError) {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
            return;
        }

        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        setShowConfirmModal(true);
    };

    const handleConfirm = async () => {
        setShowConfirmModal(false);
        setSubmitting(true);
        try {
            await createMedication({
                user_id: userId,
                name: name.trim(),
                dosage: dosage.trim() || undefined,
                moments: selectedMoments,
                frequency,
                recurrence_days: frequency === 'WEEKLY' ? recurrenceDays : undefined,
                start_date: startDate.toISOString().split('T')[0],
                end_date: endDate ? endDate.toISOString().split('T')[0] : undefined,
            });
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            navigation.goBack();
        } catch {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <View style={commonStyles.container}>
            {/* Header */}
            <View style={commonStyles.header}>
                <TouchableOpacity
                    onPress={() => {
                        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                        navigation.goBack();
                    }}
                >
                    <View style={commonStyles.ArrowIconCircle}>
                        <Ionicons name="arrow-back" size={24} color="#4A90E2" />
                    </View>
                </TouchableOpacity>
                <View style={commonStyles.headerCenter}>
                    <Image
                        source={require('../../assets/mnesya-logo.png')}
                        style={commonStyles.logo}
                    />
                </View>
                <View style={commonStyles.headerSpacer} />
            </View>

            <ScrollView
                style={{ flex: 1 }}
                keyboardShouldPersistTaps="handled"
                showsVerticalScrollIndicator={false}
            >
                <View style={styles.titleSection}>
                    <Text style={styles.pageTitle}>{t('medication.createTitle')}</Text>
                </View>

                {/* Nom */}
                <Text style={styles.label}>{t('medication.fields.name')}</Text>
                <View style={[styles.input, nameError ? commonStyles.inputError : null]}>
                    <TextInput
                        placeholder={t('medication.placeholders.name')}
                        value={name}
                        onChangeText={(v) => { setNameError(''); setName(v); }}
                        maxLength={200}
                    />
                </View>
                {nameError ? <Text style={styles.errorText}>{nameError}</Text> : null}

                {/* Dosage */}
                <Text style={styles.label}>{t('medication.fields.dosage')}</Text>
                <View style={styles.input}>
                    <TextInput
                        placeholder={t('medication.placeholders.dosage')}
                        value={dosage}
                        onChangeText={setDosage}
                        maxLength={200}
                    />
                </View>

                {/* Fréquence */}
                <Text style={styles.label}>{t('medication.fields.frequency')}</Text>
                <View style={styles.chipRow}>
                    {(['DAILY', 'WEEKLY'] as Frequency[]).map((f) => (
                        <TouchableOpacity
                            key={f}
                            style={[styles.chip, frequency === f && styles.chipActive]}
                            onPress={() => {
                                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                                setFrequency(f);
                                if (f === 'DAILY') setRecurrenceDays([]);
                            }}
                        >
                            <Text style={[styles.chipText, frequency === f && styles.chipTextActive]}>
                                {t(`medication.frequency.${f}`)}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </View>

                {/* Jours (WEEKLY seulement) */}
                {frequency === 'WEEKLY' && (
                    <>
                        <Text style={styles.label}>{t('medication.fields.days')}</Text>
                        {daysError ? <Text style={styles.errorText}>{daysError}</Text> : null}
                        <View style={styles.daysRow}>
                            {[0, 1, 2, 3, 4, 5, 6].map((day) => {
                                const selected = recurrenceDays.includes(day);
                                return (
                                    <TouchableOpacity
                                        key={day}
                                        style={[styles.dayChip, selected && styles.dayChipActive]}
                                        onPress={() => toggleDay(day)}
                                    >
                                        <Text
                                            style={[
                                                styles.dayChipText,
                                                selected && styles.dayChipTextActive,
                                            ]}
                                        >
                                            {DAY_SHORTS[day]}
                                        </Text>
                                    </TouchableOpacity>
                                );
                            })}
                        </View>
                    </>
                )}

                {/* Moments de prise */}
                <Text style={styles.label}>{t('medication.fields.moments')}</Text>
                {momentsError ? <Text style={styles.errorText}>{momentsError}</Text> : null}
                <View style={styles.momentsGrid}>
                    {ALL_MOMENTS.map((moment) => {
                        const active = selectedMoments.includes(moment);
                        return (
                            <TouchableOpacity
                                key={moment}
                                style={[styles.momentChip, active && styles.momentChipActive]}
                                onPress={() => toggleMoment(moment)}
                                activeOpacity={0.7}
                            >
                                <Text style={[styles.momentChipText, active && styles.momentChipTextActive]}>
                                    {t(`medication.moments.${moment}`)}
                                </Text>
                            </TouchableOpacity>
                        );
                    })}
                </View>

                {/* Date de début */}
                <Text style={styles.label}>{t('medication.fields.startDate')}</Text>
                <TouchableOpacity
                    style={styles.datePicker}
                    onPress={() => setShowStartDatePicker(true)}
                >
                    <Text style={styles.dateText}>{formatDate(startDate)}</Text>
                    <Ionicons name="calendar-outline" size={18} color="#999999" />
                </TouchableOpacity>

                {/* Date de fin */}
                <Text style={styles.label}>{t('medication.fields.endDate')}</Text>
                <TouchableOpacity
                    style={styles.datePicker}
                    onPress={() => setShowEndDatePicker(true)}
                >
                    <Text style={styles.dateText}>
                        {endDate ? formatDate(endDate) : t('medication.noEndDate')}
                    </Text>
                    <Ionicons name="calendar-outline" size={18} color="#999999" />
                </TouchableOpacity>
                {endDate && (
                    <TouchableOpacity
                        onPress={() => setEndDate(null)}
                        style={styles.clearEndDate}
                    >
                        <Text style={styles.clearEndDateText}>
                            {t('medication.clearEndDate')}
                        </Text>
                    </TouchableOpacity>
                )}

                <View style={{ height: 20 }} />
            </ScrollView>

            {/* Save button */}
            <View style={{ paddingBottom: insets.bottom }}>
                <TouchableOpacity
                    style={[commonStyles.primaryButton, submitting && styles.disabledButton]}
                    onPress={handleSave}
                    disabled={submitting}
                >
                    {submitting ? (
                        <ActivityIndicator color="#FFFFFF" />
                    ) : (
                        <Text style={commonStyles.primaryButtonText}>
                            {t('medication.buttons.save')}
                        </Text>
                    )}
                </TouchableOpacity>
            </View>

            {/* Pickers */}
            <PlatformDatePicker
                value={startDate}
                onChange={setStartDate}
                visible={showStartDatePicker}
                onClose={() => setShowStartDatePicker(false)}
            />
            <PlatformDatePicker
                value={endDate ?? new Date()}
                onChange={(d) => setEndDate(d)}
                visible={showEndDatePicker}
                onClose={() => setShowEndDatePicker(false)}
            />
            {/* Confirmation */}
            <ConfirmationModal
                visible={showConfirmModal}
                title={t('medication.confirmModal.title')}
                message={t('medication.confirmModal.message')}
                confirmText={t('medication.buttons.save')}
                cancelText={t('common.buttons.Cancel')}
                onConfirm={handleConfirm}
                onClose={() => setShowConfirmModal(false)}
                icon="medical-outline"
                iconColor="#4A90E2"
            />
        </View>
    );
};

// ─── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
    // LAYOUT
    titleSection: {
        width: '100%',
        paddingLeft: 10,
        marginTop: 6,
        marginBottom: 6,
    },

    // TYPOGRAPHY
    pageTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333333',
        marginBottom: 4,
    },
    label: {
        fontSize: 15,
        fontWeight: '600',
        color: '#333333',
        marginBottom: 4,
        marginTop: 10,
    },
    input: {
        backgroundColor: '#F5F5F5',
        borderRadius: 14,
        paddingHorizontal: 14,
        paddingVertical: 10,
    },
    errorText: {
        color: '#FF3B30',
        fontSize: 12,
        marginTop: 4,
        paddingLeft: 4,
    },
    chipRow: {
        flexDirection: 'row',
        gap: 10,
    },
    chip: {
        flex: 1,
        paddingVertical: 10,
        borderRadius: 14,
        backgroundColor: '#F0F0F0',
        alignItems: 'center',
    },
    chipActive: {
        backgroundColor: '#4A90E2',
    },
    chipText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#666666',
    },
    chipTextActive: {
        color: '#FFFFFF',
    },
    daysRow: {
        flexDirection: 'row',
        gap: 6,
    },
    dayChip: {
        flex: 1,
        paddingVertical: 8,
        borderRadius: 12,
        backgroundColor: '#F0F0F0',
        alignItems: 'center',
    },
    dayChipActive: {
        backgroundColor: '#4A90E2',
    },
    dayChipText: {
        fontSize: 13,
        fontWeight: '600',
        color: '#666666',
    },
    dayChipTextActive: {
        color: '#FFFFFF',
    },
    momentsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        marginTop: 4,
    },
    momentChip: {
        paddingHorizontal: 14,
        paddingVertical: 9,
        borderRadius: 20,
        backgroundColor: '#F0F0F0',
        borderWidth: 1.5,
        borderColor: 'transparent',
    },
    momentChipActive: {
        backgroundColor: '#EBF3FD',
        borderColor: '#4A90E2',
    },
    momentChipText: {
        fontSize: 13,
        fontWeight: '500',
        color: '#666666',
    },
    momentChipTextActive: {
        color: '#4A90E2',
        fontWeight: '600',
    },
    datePicker: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#F5F5F5',
        borderRadius: 14,
        paddingHorizontal: 14,
        paddingVertical: 10,
    },
    dateText: {
        fontSize: 15,
        color: '#333333',
    },
    clearEndDate: {
        alignSelf: 'flex-end',
        marginTop: 4,
        paddingRight: 4,
    },
    clearEndDateText: {
        fontSize: 12,
        color: '#FF3B30',
    },
    disabledButton: {
        opacity: 0.6,
    },
});

export default CreateMedicationScreen;
