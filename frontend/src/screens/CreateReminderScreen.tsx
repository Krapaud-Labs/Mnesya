/**
 * Screen for creating a reminder for a user profile.
 *
 * @module CreateReminderScreen
 */
import React, { useState, useRef, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    TextInput,
    Image,
    Modal,
    SafeAreaView,
    ScrollView,
    ActivityIndicator,
    Animated,
    Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useTranslation } from 'react-i18next';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../types/index';
import { commonStyles } from '../styles/commonStyles';
import {
    PlatformDatePicker,
    PlatformTimePicker,
    FilterPickerModal,
    ConfirmationModal,
} from '../components';
import { useUserProfiles } from '../hooks';
import { createReminder } from '../services/reminderService';
import { createPulseAnimation, getPulseScale } from '../utils/animations';

// ─── Types ───────────────────────────────────────────────────────────────────

type Props = NativeStackScreenProps<RootStackParamList, 'CreateReminder'>;

// ─── Screen ──────────────────────────────────────────────────────────────────

const CreateReminderScreen: React.FC<Props> = ({ navigation }) => {
    const { t } = useTranslation();
    const insets = useSafeAreaInsets();

    const { userData, loading: loadingProfiles, error: profilesError } = useUserProfiles();

    const [reminderTitle, setReminderTitle] = useState<string>('');
    const [reminderMessage, setReminderMessage] = useState<string>('');
    const [reminderDate, setReminderDate] = useState<Date>(() => {
        const d = new Date();
        const totalMinutes = d.getHours() * 60 + d.getMinutes() + 5;
        const snapped = Math.round(totalMinutes / 5) * 5;
        d.setHours(Math.floor(snapped / 60) % 24, snapped % 60, 0, 0);
        return d;
    });

    const [showProfilePicker, setShowProfilePicker] = useState<boolean>(false);
    const [selectedProfile, setSelectedProfile] = useState<string>('');
    const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);

    // Scheduling modal
    const [showSchedulingModal, setShowSchedulingModal] = useState<boolean>(false);
    const [showDatePicker, setShowDatePicker] = useState<boolean>(false);
    const [showTimePicker, setShowTimePicker] = useState<boolean>(false);

    // Recurrence state
    const [isRecurring, setIsRecurring] = useState<boolean>(false);
    const [recurrenceType, setRecurrenceType] = useState<'DAILY' | 'WEEKLY' | 'MONTHLY'>('WEEKLY');
    const [recurrenceDays, setRecurrenceDays] = useState<number[]>([]);
    const [recurrenceEndDate, setRecurrenceEndDate] = useState<Date | null>(null);
    const [showEndDatePicker, setShowEndDatePicker] = useState<boolean>(false);

    const [profileError, setProfileError] = useState<string>('');
    const [titleError, setTitleError] = useState<string>('');
    const [messageError, setMessageError] = useState<string>('');
    const [showProfileError, setShowProfileError] = useState<boolean>(false);
    const [showTitleError, setShowTitleError] = useState<boolean>(false);
    const [showMessageError, setShowMessageError] = useState<boolean>(false);

    const selectedProfileData = userData?.find((p) => String(p.id) === selectedProfile);

    const pulseAnim = useRef(new Animated.Value(1)).current;
    useEffect(() => {
        createPulseAnimation(pulseAnim).start();
    }, [pulseAnim]);

    const formatDate = (date: Date): string => {
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    };

    const formatTime = (date: Date): string => {
        const hour = date.getHours().toString().padStart(2, '0');
        const minute = date.getMinutes().toString().padStart(2, '0');
        return `${hour}:${minute}`;
    };

    const getRecurrenceSummary = (): string | null => {
        if (!isRecurring) return null;
        if (recurrenceType === 'DAILY') return t('CreateReminder.recurrence.types.DAILY');
        if (recurrenceType === 'MONTHLY') return t('CreateReminder.recurrence.types.MONTHLY');
        if (recurrenceType === 'WEEKLY') {
            if (recurrenceDays.length === 0) return '…';
            return recurrenceDays
                .sort((a, b) => a - b)
                .map((d) => t(`CreateReminder.recurrence.day_short.${d}`))
                .join(', ');
        }
        return null;
    };

    /** One-line summary shown in the main form row */
    const getSchedulingSummary = (): string => {
        const base = `${formatDate(reminderDate)} à ${formatTime(reminderDate)}`;
        const rec = getRecurrenceSummary();
        return rec ? `${base} · ${rec}` : base;
    };

    const handleSaveReminder = () => {
        setShowProfileError(false);
        setShowTitleError(false);
        setShowMessageError(false);

        let hasError = false;

        if (!selectedProfile) {
            setProfileError(t('CreateReminder.errors.Please select a profile'));
            setShowProfileError(true);
            hasError = true;
        }

        if (!reminderTitle.trim()) {
            setTitleError(t('CreateReminder.errors.Please enter a title'));
            setShowTitleError(true);
            hasError = true;
        }

        if (!reminderMessage.trim()) {
            setMessageError(t('CreateReminder.errors.Please enter a message'));
            setShowMessageError(true);
            hasError = true;
        }

        if (isRecurring && recurrenceType === 'WEEKLY' && recurrenceDays.length === 0) {
            hasError = true;
        }

        if (hasError) {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
            return;
        }

        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        setShowConfirmModal(true);
    };

    const handleConfirmSave = async () => {
        setShowConfirmModal(false);

        try {
            const recurrencePayload = isRecurring
                ? {
                      is_recurring: true,
                      recurrence_type: recurrenceType,
                      recurrence_days: recurrenceType === 'WEEKLY' ? recurrenceDays : undefined,
                      recurrence_end_date: recurrenceEndDate
                          ? recurrenceEndDate.toISOString().split('T')[0]
                          : undefined,
                  }
                : {};

            await createReminder({
                title: reminderTitle,
                description: reminderMessage,
                scheduled_at: reminderDate.toISOString(),
                user_id: String(selectedProfile),
                ...recurrencePayload,
            });

            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            navigation.navigate('Dashboard');
        } catch {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
            setMessageError(t('CreateReminder.errors.Error scheduling notification'));
            setShowMessageError(true);
        }
    };

    const handleCancelSave = () => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        setShowConfirmModal(false);
    };

    return (
        <View style={commonStyles.container}>
            {/* Header */}
            <View style={commonStyles.header}>
                <TouchableOpacity
                    onPress={() => {
                        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                        navigation.navigate('Dashboard');
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

            {/* Page title */}
            <View style={styles.titleSection}>
                <Text style={styles.title}>{t('CreateReminder.Title')}</Text>
            </View>

            {/* Form content */}
            <View style={styles.formContainer}>
                {/* Profile */}
                <Text style={styles.label}>{t('CreateReminder.fields.For Profile')}</Text>
                {profilesError && <Text style={styles.errorText}>{profilesError}</Text>}
                <TouchableOpacity
                    style={[styles.input, showProfileError && commonStyles.inputError]}
                    onPress={() => setShowProfilePicker(true)}
                >
                    <View style={styles.rowBetween}>
                        <Text>
                            {selectedProfileData
                                ? `${selectedProfileData.first_name} ${selectedProfileData.last_name}`
                                : t('common.pickersText.Select a profile')}
                        </Text>
                        {loadingProfiles ? (
                            <ActivityIndicator size="small" color="#999999" />
                        ) : (
                            <Ionicons name="chevron-down" size={20} color="#999999" />
                        )}
                    </View>
                </TouchableOpacity>
                <Text style={[styles.errorText, { opacity: showProfileError ? 1 : 0 }]}>
                    {profileError || t('CreateReminder.errors.Please select a profile')}
                </Text>

                {!showProfilePicker && (
                    <>
                        {/* Title */}
                        <Text style={styles.label}>
                            {t('CreateReminder.fields.Reminder Title')}
                        </Text>
                        <View style={[styles.input, showTitleError && commonStyles.inputError]}>
                            <TextInput
                                placeholder={t('CreateReminder.placeholders.Ex. : Take Medication')}
                                onChangeText={(newText) => {
                                    setShowTitleError(false);
                                    setReminderTitle(newText);
                                }}
                                defaultValue={reminderTitle}
                            />
                        </View>
                        <Text style={[styles.errorText, { opacity: showTitleError ? 1 : 0 }]}>
                            {titleError || t('CreateReminder.errors.Please enter a title')}
                        </Text>

                        {/* Message */}
                        <Text style={styles.label}>Message</Text>
                        <View
                            style={[
                                styles.input,
                                styles.messageInput,
                                showMessageError && commonStyles.inputError,
                            ]}
                        >
                            <TextInput
                                multiline={true}
                                numberOfLines={4}
                                maxLength={120}
                                placeholder={t(
                                    'CreateReminder.placeholders.Enter the description about your reminder'
                                )}
                                onChangeText={(newText) => {
                                    setShowMessageError(false);
                                    setReminderMessage(newText);
                                }}
                                defaultValue={reminderMessage}
                            />
                        </View>
                        <Text style={[styles.errorText, { opacity: showMessageError ? 1 : 0 }]}>
                            {messageError || t('CreateReminder.errors.Please enter a message')}
                        </Text>

                        <Animated.Text style={[styles.warningText, getPulseScale(pulseAnim)]}>
                            {t(
                                'CreateReminder.message.Be careful not to enter sensitive confidential information.'
                            )}
                        </Animated.Text>

                        {/* Scheduling summary row */}
                        <Text style={styles.label}>{t('CreateReminder.fields.scheduling') || 'Programmation'}</Text>
                        <TouchableOpacity
                            style={styles.summaryRow}
                            onPress={() => {
                                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                                setShowSchedulingModal(true);
                            }}
                        >
                            <View style={styles.summaryLeft}>
                                <Ionicons name="calendar-outline" size={16} color="#4A90E2" />
                                <Text style={styles.summaryText}>{getSchedulingSummary()}</Text>
                            </View>
                            <Ionicons name="chevron-forward" size={16} color="#4A90E2" />
                        </TouchableOpacity>
                    </>
                )}
            </View>

            {/* Save button */}
            <View style={[styles.buttonsContainer, { paddingBottom: insets.bottom + 20 }]}>
                {!showProfilePicker && (
                    <TouchableOpacity
                        style={commonStyles.primaryButton}
                        onPress={handleSaveReminder}
                    >
                        <Text style={commonStyles.primaryButtonText}>
                            {t('CreateReminder.buttons.Save Reminder')}
                        </Text>
                    </TouchableOpacity>
                )}
            </View>

            {/* ── Scheduling modal (date, heure, récurrence) ── */}
            <Modal
                visible={showSchedulingModal}
                animationType="slide"
                presentationStyle="pageSheet"
                onRequestClose={() => setShowSchedulingModal(false)}
            >
                <SafeAreaView style={styles.modalContainer}>
                    {/* Modal header */}
                    <View style={styles.modalHeader}>
                        <Text style={styles.modalTitle}>
                            {t('CreateReminder.fields.scheduling') || 'Programmation'}
                        </Text>
                        <TouchableOpacity onPress={() => setShowSchedulingModal(false)}>
                            <Ionicons name="close" size={24} color="#333333" />
                        </TouchableOpacity>
                    </View>

                    <ScrollView style={styles.modalContent} keyboardShouldPersistTaps="handled">
                        {/* Date */}
                        <Text style={styles.label}>Date</Text>
                        <TouchableOpacity
                            style={styles.pickerButton}
                            onPress={() => {
                                setShowDatePicker(true);
                                setShowTimePicker(false);
                                setShowEndDatePicker(false);
                            }}
                        >
                            <View style={styles.rowBetween}>
                                <Text>{formatDate(reminderDate)}</Text>
                                <Ionicons name="calendar-outline" size={20} color="#999999" />
                            </View>
                        </TouchableOpacity>

                        {/* Time */}
                        <Text style={styles.label}>{t('CreateReminder.fields.Time')}</Text>
                        <TouchableOpacity
                            style={styles.pickerButton}
                            onPress={() => {
                                setShowTimePicker(true);
                                setShowDatePicker(false);
                                setShowEndDatePicker(false);
                            }}
                        >
                            <View style={styles.rowBetween}>
                                <Text>{formatTime(reminderDate)}</Text>
                                <Ionicons name="time-outline" size={20} color="#999999" />
                            </View>
                        </TouchableOpacity>

                        {/* Recurrence toggle */}
                        <View style={styles.recurrenceRow}>
                            <Text style={styles.label}>
                                {t('CreateReminder.recurrence.toggle')}
                            </Text>
                            <Switch
                                value={isRecurring}
                                onValueChange={(val) => {
                                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                                    setIsRecurring(val);
                                    if (!val) setRecurrenceDays([]);
                                }}
                                trackColor={{ false: '#CCCCCC', true: '#4A90E2' }}
                                thumbColor="#FFFFFF"
                            />
                        </View>

                        {isRecurring && (
                            <>
                                {/* Type chips */}
                                <View style={styles.typeRow}>
                                    {(['DAILY', 'WEEKLY', 'MONTHLY'] as const).map((type) => (
                                        <TouchableOpacity
                                            key={type}
                                            style={[
                                                styles.typeChip,
                                                recurrenceType === type && styles.typeChipActive,
                                            ]}
                                            onPress={() => {
                                                Haptics.impactAsync(
                                                    Haptics.ImpactFeedbackStyle.Light
                                                );
                                                setRecurrenceType(type);
                                                if (type !== 'WEEKLY') setRecurrenceDays([]);
                                            }}
                                        >
                                            <Text
                                                style={[
                                                    styles.typeChipText,
                                                    recurrenceType === type &&
                                                        styles.typeChipTextActive,
                                                ]}
                                            >
                                                {t(`CreateReminder.recurrence.types.${type}`)}
                                            </Text>
                                        </TouchableOpacity>
                                    ))}
                                </View>

                                {/* Day picker (WEEKLY only) */}
                                {recurrenceType === 'WEEKLY' && (
                                    <>
                                        <Text style={styles.label}>
                                            {t('CreateReminder.recurrence.days_label')}
                                        </Text>
                                        {recurrenceDays.length === 0 && (
                                            <Text style={styles.errorText}>
                                                {t('CreateReminder.recurrence.days_required')}
                                            </Text>
                                        )}
                                        <View style={styles.daysRow}>
                                            {[0, 1, 2, 3, 4, 5, 6].map((day) => {
                                                const selected = recurrenceDays.includes(day);
                                                return (
                                                    <TouchableOpacity
                                                        key={day}
                                                        style={[
                                                            styles.dayChip,
                                                            selected && styles.dayChipActive,
                                                        ]}
                                                        onPress={() => {
                                                            Haptics.impactAsync(
                                                                Haptics.ImpactFeedbackStyle.Light
                                                            );
                                                            setRecurrenceDays((prev) =>
                                                                selected
                                                                    ? prev.filter((d) => d !== day)
                                                                    : [...prev, day]
                                                            );
                                                        }}
                                                    >
                                                        <Text
                                                            style={[
                                                                styles.dayChipText,
                                                                selected && styles.dayChipTextActive,
                                                            ]}
                                                        >
                                                            {t(
                                                                `CreateReminder.recurrence.day_short.${day}`
                                                            )}
                                                        </Text>
                                                    </TouchableOpacity>
                                                );
                                            })}
                                        </View>
                                    </>
                                )}

                                {/* End date */}
                                <Text style={styles.label}>
                                    {t('CreateReminder.recurrence.end_date_label')}
                                </Text>
                                <TouchableOpacity
                                    style={styles.pickerButton}
                                    onPress={() => {
                                        setShowEndDatePicker(true);
                                        setShowDatePicker(false);
                                        setShowTimePicker(false);
                                    }}
                                >
                                    <View style={styles.rowBetween}>
                                        <Text>
                                            {recurrenceEndDate
                                                ? formatDate(recurrenceEndDate)
                                                : t('CreateReminder.recurrence.no_end_date')}
                                        </Text>
                                        <Ionicons
                                            name="calendar-outline"
                                            size={20}
                                            color="#999999"
                                        />
                                    </View>
                                </TouchableOpacity>
                                {recurrenceEndDate && (
                                    <TouchableOpacity
                                        onPress={() => setRecurrenceEndDate(null)}
                                        style={styles.clearEndDate}
                                    >
                                        <Text style={styles.clearEndDateText}>
                                            {t('CreateReminder.recurrence.clear_end_date')}
                                        </Text>
                                    </TouchableOpacity>
                                )}
                            </>
                        )}

                        <View style={{ height: 20 }} />
                    </ScrollView>

                    {/* Validate */}
                    <View style={[styles.modalFooter, { paddingBottom: insets.bottom + 16 }]}>
                        <TouchableOpacity
                            style={commonStyles.primaryButton}
                            onPress={() => {
                                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                                setShowSchedulingModal(false);
                            }}
                        >
                            <Text style={commonStyles.primaryButtonText}>
                                {t('common.buttons.Validate')}
                            </Text>
                        </TouchableOpacity>
                    </View>

                    {/* Pickers inside modal */}
                    <PlatformDatePicker
                        value={reminderDate}
                        onChange={setReminderDate}
                        visible={showDatePicker}
                        onClose={() => setShowDatePicker(false)}
                    />
                    <PlatformTimePicker
                        value={reminderDate}
                        onChange={setReminderDate}
                        visible={showTimePicker}
                        onClose={() => setShowTimePicker(false)}
                    />
                    <PlatformDatePicker
                        value={recurrenceEndDate ?? new Date()}
                        onChange={(d) => setRecurrenceEndDate(d)}
                        visible={showEndDatePicker}
                        onClose={() => setShowEndDatePicker(false)}
                    />
                </SafeAreaView>
            </Modal>

            {/* Profile picker */}
            <FilterPickerModal
                title={t('common.pickersText.Select a profile')}
                items={
                    userData?.map((item) => ({
                        value: String(item.id),
                        label: `${item.first_name} ${item.last_name}`,
                    })) ?? []
                }
                selectedValue={selectedProfile}
                onSelect={setSelectedProfile}
                visible={showProfilePicker}
                onClose={() => setShowProfilePicker(false)}
            />

            {/* Confirmation Modal */}
            <ConfirmationModal
                visible={showConfirmModal}
                title={t('CreateReminder.modal.title')}
                message={t('CreateReminder.modal.message')}
                confirmText={t('CreateReminder.modal.confirm')}
                cancelText={t('CreateReminder.modal.cancel')}
                onConfirm={handleConfirmSave}
                onClose={handleCancelSave}
                icon="notifications-outline"
                iconColor="#4A90E2"
            />
        </View>
    );
};

// ─── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
    // ========== LAYOUT ==========
    titleSection: {
        width: '100%',
        paddingLeft: 10,
        marginTop: 10,
        marginBottom: 10,
    },
    formContainer: {
        flex: 1,
        width: '100%',
    },
    buttonsContainer: {},

    // ========== TYPOGRAPHY ==========
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        marginBottom: 6,
    },
    label: {
        fontSize: 18,
        fontWeight: '500',
        marginBottom: 6,
        marginTop: 2,
    },
    warningText: {
        fontSize: 12,
        color: '#FF0000',
        marginBottom: 4,
        paddingRight: 4,
    },

    // ========== FORM ELEMENTS ==========
    input: {
        backgroundColor: '#F5F5F5',
        padding: 12,
        borderRadius: 20,
        marginBottom: 4,
        width: '100%',
    },
    messageInput: {
        height: 70,
        marginBottom: 2,
    },
    errorText: {
        color: '#FF0000',
        fontSize: 12,
        textAlign: 'right',
        marginTop: -2,
        marginBottom: 2,
        minHeight: 14,
        lineHeight: 14,
        paddingRight: 10,
    },
    rowBetween: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },

    // ========== SCHEDULING SUMMARY ROW ==========
    summaryRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#EEF4FC',
        borderRadius: 14,
        paddingHorizontal: 14,
        paddingVertical: 12,
    },
    summaryLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        flex: 1,
    },
    summaryText: {
        fontSize: 14,
        color: '#4A90E2',
        fontWeight: '500',
        flex: 1,
    },

    // ========== MODAL ==========
    modalContainer: {
        flex: 1,
        backgroundColor: '#FFFFFF',
    },
    modalHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingTop: 20,
        paddingBottom: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#F0F0F0',
    },
    modalTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333333',
    },
    modalContent: {
        flex: 1,
        paddingHorizontal: 20,
        paddingTop: 16,
    },
    modalFooter: {
        paddingHorizontal: 20,
        paddingTop: 12,
    },

    // ========== PICKERS ==========
    pickerButton: {
        backgroundColor: '#F5F5F5',
        padding: 14,
        borderRadius: 20,
        marginBottom: 8,
        width: '100%',
    },

    // ========== RECURRENCE ==========
    recurrenceRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: 8,
        marginBottom: 4,
    },
    typeRow: {
        flexDirection: 'row',
        gap: 8,
        marginBottom: 16,
    },
    typeChip: {
        flex: 1,
        paddingVertical: 12,
        borderRadius: 16,
        backgroundColor: '#F0F0F0',
        alignItems: 'center',
    },
    typeChipActive: {
        backgroundColor: '#4A90E2',
    },
    typeChipText: {
        fontSize: 13,
        fontWeight: '500',
        color: '#666666',
    },
    typeChipTextActive: {
        color: '#FFFFFF',
    },
    daysRow: {
        flexDirection: 'row',
        gap: 6,
        marginBottom: 16,
    },
    dayChip: {
        flex: 1,
        paddingVertical: 12,
        borderRadius: 12,
        backgroundColor: '#F0F0F0',
        alignItems: 'center',
    },
    dayChipActive: {
        backgroundColor: '#4A90E2',
    },
    dayChipText: {
        fontSize: 12,
        fontWeight: '600',
        color: '#666666',
    },
    dayChipTextActive: {
        color: '#FFFFFF',
    },
    clearEndDate: {
        alignSelf: 'flex-end',
        marginTop: -4,
        marginBottom: 8,
        paddingRight: 4,
    },
    clearEndDateText: {
        fontSize: 12,
        color: '#FF3B30',
    },
});

export default CreateReminderScreen;
