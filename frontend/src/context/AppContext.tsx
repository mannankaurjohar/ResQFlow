import React, {
  createContext,
  useContext,
  useState,
  useEffect
} from 'react';

import {
  UserRole,
  CommunityRequest,
  User
} from '../types';

import api from '../services/api';

interface AppContextType {
  currentUser: User | null;
  isAuthenticated: boolean;
  passwordResetRequired: boolean;

  login: (
    username: string,
    password: string,
    role: UserRole
  ) => Promise<void>;

  logout: () => void;

  activeRole: UserRole | null;
  setActiveRole: (role: UserRole | null) => void;

  activeTab: string;
  setActiveTab: (tab: string) => void;

  isEmergencyMode: boolean;
  toggleEmergencyMode: () => void;

  isEscalated: boolean;
  triggerEscalation: () => Promise<void>;
  triggerReset: () => Promise<void>;

  traceIdInput: string;
  setTraceIdInput: (id: string) => void;

  activePriorityModalRequest: CommunityRequest | null;
  setActivePriorityModalRequest: (
    req: CommunityRequest | null
  ) => void;

  activeMatchModalRequest: CommunityRequest | null;
  setActiveMatchModalRequest: (
    req: CommunityRequest | null
  ) => void;

  notification: {
    message: string;
    type: 'success' | 'info' | 'warning' | 'error';
  } | null;

  showNotification: (
    message: string,
    type?: 'success' | 'info' | 'warning' | 'error'
  ) => void;
}

const AppContext = createContext<
  AppContextType | undefined
>(undefined);

export const AppProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const [currentUser, setCurrentUser] =
    useState<User | null>(null);

  const [activeRole, setActiveRole] =
    useState<UserRole | null>(null);

  const [isAuthenticated, setIsAuthenticated] =
    useState<boolean>(false);

  const [passwordResetRequired, setPasswordResetRequired] =
    useState<boolean>(false);

  const [activeTab, setActiveTab] =
    useState<string>('landing');

  const [isEmergencyMode, setIsEmergencyMode] =
    useState<boolean>(false);

  const [isEscalated, setIsEscalated] =
    useState<boolean>(false);

  const [traceIdInput, setTraceIdInput] =
    useState<string>('');

  const [
    activePriorityModalRequest,
    setActivePriorityModalRequest
  ] = useState<CommunityRequest | null>(null);

  const [
    activeMatchModalRequest,
    setActiveMatchModalRequest
  ] = useState<CommunityRequest | null>(null);

  const [notification, setNotification] =
    useState<{
      message: string;
      type:
        | 'success'
        | 'info'
        | 'warning'
        | 'error';
    } | null>(null);

  const showNotification = (
    message: string,
    type:
      | 'success'
      | 'info'
      | 'warning'
      | 'error' = 'info'
  ) => {
    setNotification({
      message,
      type
    });

    setTimeout(() => {
      setNotification(null);
    }, 5000);
  };

  const getRoleTab = (
    role: UserRole
  ): string => {
    switch (role) {
      case 'ADMIN':
        return 'landing';

      case 'EMERGENCY_COORDINATOR':
        return 'command';

      case 'COMMUNITY':
        return 'report';

      case 'VOLUNTEER':
        return 'volunteer';

      case 'NGO_MANAGER':
      case 'WAREHOUSE_MANAGER':
        return 'warehouse';

      case 'DONOR':
        return 'donor';

      default:
        return 'landing';
    }
  };

  const login = async (
    username: string,
    password: string,
    role: UserRole
  ) => {
    try {
      const data = await api.login(
        username,
        password,
        role
      );

      const resetRequired = Boolean(
        data.password_reset_required
      );

      setCurrentUser(data.user);
      setActiveRole(data.user.role);
      setIsAuthenticated(true);
      setPasswordResetRequired(resetRequired);

      if (resetRequired) {
        setActiveTab('change-password');
      } else {
        setActiveTab(
          getRoleTab(data.user.role)
        );
      }

      showNotification(
        `Welcome, ${
          data.user.full_name ||
          data.user.username
        }`,
        'success'
      );
    } catch (err) {
      setCurrentUser(null);
      setActiveRole(null);
      setIsAuthenticated(false);
      setPasswordResetRequired(false);

      throw err;
    }
  };

  const logout = () => {
    api.logout();

    setCurrentUser(null);
    setActiveRole(null);
    setIsAuthenticated(false);
    setPasswordResetRequired(false);
    setActiveTab('landing');

    showNotification(
      'You have been logged out',
      'info'
    );
  };

  useEffect(() => {
    const restoreSession = async () => {
      const token =
        localStorage.getItem(
          'resqflow_token'
        );

      if (!token) {
        return;
      }

      try {
        const user =
          await api.getCurrentUser();

        const resetRequired =
          localStorage.getItem(
            'resqflow_password_reset_required'
          ) === 'true';

        setCurrentUser(user);
        setActiveRole(user.role);
        setIsAuthenticated(true);
        setPasswordResetRequired(
          resetRequired
        );

        if (resetRequired) {
          setActiveTab(
            'change-password'
          );
        } else {
          setActiveTab(
            getRoleTab(user.role)
          );
        }
      } catch {
        api.logout();

        setCurrentUser(null);
        setActiveRole(null);
        setIsAuthenticated(false);
        setPasswordResetRequired(false);
      }
    };

    restoreSession();
  }, []);

  useEffect(() => {
    api
      .getSimulationStatus()
      .then(status => {
        setIsEscalated(
          status.is_escalated
        );
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setActivePriorityModalRequest(null);
    setActiveMatchModalRequest(null);
  }, [activeTab]);

  const toggleEmergencyMode = () => {
    setIsEmergencyMode(prev => {
      const next = !prev;

      showNotification(
        next
          ? '🚨 EMERGENCY MODE ACTIVATED: Prioritizing critical requests and shortage radar.'
          : 'Standard operational mode restored.',
        next
          ? 'warning'
          : 'info'
      );

      return next;
    });
  };

  const triggerEscalation = async () => {
    try {
      const res =
        await api.escalateSimulation();

      setIsEscalated(true);

      showNotification(
        res.message ||
          'Flood escalation simulated!',
        'error'
      );
    } catch {
      showNotification(
        'Failed to trigger simulation',
        'error'
      );
    }
  };

  const triggerReset = async () => {
    try {
      const res =
        await api.resetSimulation();

      setIsEscalated(false);

      showNotification(
        res.message ||
          'Simulation reset successfully',
        'success'
      );
    } catch {
      showNotification(
        'Failed to reset simulation',
        'error'
      );
    }
  };

  return (
    <AppContext.Provider
      value={{
        currentUser,
        isAuthenticated,
        passwordResetRequired,

        login,
        logout,

        activeRole,
        setActiveRole,

        activeTab,
        setActiveTab,

        isEmergencyMode,
        toggleEmergencyMode,

        isEscalated,
        triggerEscalation,
        triggerReset,

        traceIdInput,
        setTraceIdInput,

        activePriorityModalRequest,
        setActivePriorityModalRequest,

        activeMatchModalRequest,
        setActiveMatchModalRequest,

        notification,
        showNotification
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context =
    useContext(AppContext);

  if (!context) {
    throw new Error(
      'useApp must be used within AppProvider'
    );
  }

  return context;
};