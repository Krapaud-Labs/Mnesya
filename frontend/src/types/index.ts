/**
 * Navigation type definitions for the app.
 *
 * @module types
 */
import type { NavigatorScreenParams } from '@react-navigation/native';

// ─── Types ───────────────────────────────────────────────────────────────────

export type RootStackParamList = {
    Welcome: undefined;
    Login: undefined;
    Register: undefined;
    CreateProfile: undefined;
    UserPairing: undefined;
    Dashboard: NavigatorScreenParams<CaregiverTabsParamList> | undefined;
    CreateReminder: { profileId?: string };
    UserProfileDetails: { profileId: string };
    UserDashboard: undefined;
    ReminderNotification: {
        reminderId: string;
        message?: string;
        profileId?: string | number;
    };
};

export type CaregiverTabsParamList = {
    Home: undefined;
    Reminders: undefined;
    Profile: undefined;
};

export type UserTabsParamList = {
    Emergency: undefined;
    Refresh: undefined;
    Emergency: undefined;
};
