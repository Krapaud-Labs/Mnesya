/**
 * Root component — sets up navigation and notifications.
 *
 * @module App
 */
import React, { useEffect, useRef } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AppState as RNAppState, AppStateStatus } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import './i18n'; // Initialize internationalization before any component renders
import AppNavigator from './navigation/AppNavigator';
import { registerForPushNotifications, cancelNotifications } from './utils/notifications';
import * as Notifications from 'expo-notifications';
import { navigationRef } from './services/navigationService';
import { getToken } from './services/tokenService';
import { refreshCaregiverToken } from './services/api';

// Set the notification behavior
Notifications.setNotificationHandler({
    handleNotification: async () => ({
        shouldShowBanner: true, // Show banner notification
        shouldShowList: true, // Show in notification list
        shouldPlaySound: true, // Play notification sound
        shouldSetBadge: true, // Update app badge count
    }),
});

// ─── Component ──────────────────────────────────────────────────────────────

/** Decode a JWT payload without a library. */
function decodeJwtPayload(token: string): Record<string, unknown> | null {
    try {
        const b64 = (token.split('.')[1] ?? '').replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4)));
    } catch {
        return null;
    }
}

const App: React.FC = () => {
    const appState = useRef<AppStateStatus>(RNAppState.currentState);

    useEffect(() => {
        // Refresh the caregiver token proactively when the app comes to the foreground.
        // This covers the case where the token is still valid but close to expiry
        // after the app has been in the background for a while.
        const handleAppStateChange = async (nextAppState: AppStateStatus) => {
            if (appState.current.match(/inactive|background/) && nextAppState === 'active') {
                const token = await getToken();
                if (token) {
                    const payload = decodeJwtPayload(token);
                    const now = Math.floor(Date.now() / 1000);
                    const isCaregiverToken =
                        payload?.['sub'] !== undefined &&
                        payload?.['email'] !== undefined &&
                        payload?.['firstname'] === undefined;
                    const exp = payload?.['exp'] as number | undefined;

                    if (isCaregiverToken && exp !== undefined && exp > now && exp - now < 24 * 60 * 60) {
                        try {
                            await refreshCaregiverToken(token);
                        } catch {
                            // Token already expired or refresh failed — the next API call
                            // will trigger the 401 handler and redirect to Login.
                        }
                    }
                }
            }
            appState.current = nextAppState;
        };

        const subscription = RNAppState.addEventListener('change', handleAppStateChange);
        return () => subscription.remove();
    }, []);

    useEffect(() => {
        const setupNotifications = async () => {
            await registerForPushNotifications();
        };
        setupNotifications();

        // Listen for notification clicks
        const subscription = Notifications.addNotificationResponseReceivedListener(
            async (response) => {
                const data = response.notification.request.content.data as {
                    reminder_id: string;
                    title?: string;
                    message: string;
                    profileId: string | number;
                    profile_id?: string;
                    isUserNotification?: boolean;
                    isCaregiverAlert?: boolean;
                    type?: string;
                };

                // If it's a user notification, cancel all other remaining notifications
                if (data.isUserNotification && data.reminder_id) {
                    try {
                        const storageKey = `notification_ids_${data.reminder_id}`;
                        const storedIds = await AsyncStorage.getItem(storageKey);

                        if (storedIds) {
                            const notificationIds = JSON.parse(storedIds) as string[];
                            await cancelNotifications(notificationIds);
                            await AsyncStorage.removeItem(storageKey);
                            await Notifications.setBadgeCountAsync(0);
                        }
                    } catch (_error) {}
                }

                // Navigate to ReminderNotificationScreen with notification data
                // Exclude caregiver alerts: locally scheduled ones use `isCaregiverAlert`,
                // server-sent T10 escalations use `type === "caregiver_alert"`.
                if (navigationRef.current && data && !data.isCaregiverAlert && data.type !== 'caregiver_alert') {
                    navigationRef.current.navigate('ReminderNotification', {
                        reminderId: data.reminder_id,
                        title: data.title,
                        message: data.message,
                        profileId: data.profileId,
                    });
                } else if (navigationRef.current && data && (data.isCaregiverAlert || data.type === 'caregiver_alert')) {
                    const profileId = data.profile_id ?? (data.profileId != null ? String(data.profileId) : undefined);
                    if (profileId) {
                        navigationRef.current.navigate('UserProfileDetails', { profileId });
                    } else {
                        navigationRef.current.navigate('Dashboard', { screen: 'Reminders' });
                    }
                }
            }
        );

        // Cleanup listener on component unmount
        return () => subscription.remove();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleNotificationNavigation = async () => {
        // eslint-disable-next-line @typescript-eslint/no-deprecated
        const lastResponse = await Notifications.getLastNotificationResponseAsync();
        if (!lastResponse) return;

        // Avoid re-navigating if this notification was already handled in a previous session
        const notifId = lastResponse.notification.request.identifier;
        const handledKey = `handled_notif_${notifId}`;
        const alreadyHandled = await AsyncStorage.getItem(handledKey);
        if (alreadyHandled) return;
        await AsyncStorage.setItem(handledKey, '1');

        const data = lastResponse.notification.request.content.data as {
            reminder_id: string;
            title?: string;
            message: string;
            profileId: string | number;
            profile_id?: string;
            isUserNotification?: boolean;
            isCaregiverAlert?: boolean;
            type?: string;
        };

        if (data.isUserNotification && data.reminder_id) {
            try {
                const storageKey = `notification_ids_${data.reminder_id}`;
                const storedIds = await AsyncStorage.getItem(storageKey);
                if (storedIds) {
                    const notificationIds = JSON.parse(storedIds) as string[];
                    await cancelNotifications(notificationIds);
                    await AsyncStorage.removeItem(storageKey);
                    await Notifications.setBadgeCountAsync(0);
                }
            } catch (_error) {}
        }

        if (data && !data.isCaregiverAlert && data.type !== 'caregiver_alert') {
            navigationRef.current?.navigate('ReminderNotification', {
                reminderId: data.reminder_id,
                title: data.title,
                message: data.message,
                profileId: data.profileId,
            });
        } else if (data && (data.isCaregiverAlert || data.type === 'caregiver_alert')) {
            const profileId = data.profile_id ?? String(data.profileId);
            if (profileId) {
                navigationRef.current?.navigate('UserProfileDetails', { profileId });
            } else {
                navigationRef.current?.navigate('Dashboard', { screen: 'Reminders' });
            }
        }
    };

    return (
        <SafeAreaProvider>
            <NavigationContainer ref={navigationRef} onReady={handleNotificationNavigation}>
                <AppNavigator />
            </NavigationContainer>
        </SafeAreaProvider>
    );
};

export default App;
