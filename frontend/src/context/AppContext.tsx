import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserRole, CommunityRequest } from '../types';
import api from '../services/api';

interface AppContextType {
  activeRole: UserRole;
  setActiveRole: (role: UserRole) => void;
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
  setActivePriorityModalRequest: (req: CommunityRequest | null) => void;
  activeMatchModalRequest: CommunityRequest | null;
  setActiveMatchModalRequest: (req: CommunityRequest | null) => void;
  notification: { message: string; type: 'success' | 'info' | 'warning' | 'error' } | null;
  showNotification: (message: string, type?: 'success' | 'info' | 'warning' | 'error') => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeRole, setActiveRole] = useState<UserRole>('AUTHORITY');
  const [activeTab, setActiveTab] = useState<string>('landing');
  const [isEmergencyMode, setIsEmergencyMode] = useState<boolean>(false);
  const [isEscalated, setIsEscalated] = useState<boolean>(false);
  const [traceIdInput, setTraceIdInput] = useState<string>('RELIEF-2026-00482');
  const [activePriorityModalRequest, setActivePriorityModalRequest] = useState<CommunityRequest | null>(null);
  const [activeMatchModalRequest, setActiveMatchModalRequest] = useState<CommunityRequest | null>(null);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'info' | 'warning' | 'error' } | null>(null);

  const showNotification = (message: string, type: 'success' | 'info' | 'warning' | 'error' = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  useEffect(() => {
    api.getSimulationStatus().then(status => {
      setIsEscalated(status.is_escalated);
    }).catch(() => {});
  }, []);
  useEffect(() => {
  setActivePriorityModalRequest(null);
  setActiveMatchModalRequest(null);
}, [activeTab]);

  const toggleEmergencyMode = () => {
    setIsEmergencyMode(prev => {
      const next = !prev;
      showNotification(
        next ? '🚨 EMERGENCY MODE ACTIVATED: Prioritizing critical requests and shortage radar.' : 'Standard operational mode restored.',
        next ? 'warning' : 'info'
      );
      return next;
    });
  };

  const triggerEscalation = async () => {
    try {
      const res = await api.escalateSimulation();
      setIsEscalated(true);
      showNotification(res.message || 'Flood escalation simulated!', 'error');
    } catch (err) {
      showNotification('Failed to trigger simulation', 'error');
    }
  };

  const triggerReset = async () => {
    try {
      const res = await api.resetSimulation();
      setIsEscalated(false);
      showNotification(res.message || 'Simulation reset successfully', 'success');
    } catch (err) {
      showNotification('Failed to reset simulation', 'error');
    }
  };

  return (
    <AppContext.Provider value={{
      activeRole, setActiveRole,
      activeTab, setActiveTab,
      isEmergencyMode, toggleEmergencyMode,
      isEscalated, triggerEscalation, triggerReset,
      traceIdInput, setTraceIdInput,
      activePriorityModalRequest, setActivePriorityModalRequest,
      activeMatchModalRequest, setActiveMatchModalRequest,
      notification, showNotification
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
};
