import React, { createContext, useContext, useState, useCallback } from 'react';

type AlertType = 'success' | 'error' | 'warning' | 'info';

interface AlertState {
  isOpen: boolean;
  title: string;
  message: string;
  type: AlertType;
}

interface Toast {
  id: string;
  title: string;
  type: AlertType;
}

interface AlertContextData {
  showAlert: (title: string, message: string, type?: AlertType) => void;
  hideAlert: () => void;
  showToast: (title: string, type?: AlertType) => void;
  removeToast: (id: string) => void;
  alert: AlertState;
  toasts: Toast[];
}

const AlertContext = createContext<AlertContextData>({} as AlertContextData);

export const AlertProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [alert, setAlert] = useState<AlertState>({
    isOpen: false,
    title: '',
    message: '',
    type: 'info',
  });

  const [toasts, setToasts] = useState<Toast[]>([]);

  const showAlert = useCallback((title: string, message: string, type: AlertType = 'info') => {
    setAlert({
      isOpen: true,
      title,
      message,
      type,
    });
  }, []);

  const hideAlert = useCallback(() => {
    setAlert(prev => ({ ...prev, isOpen: false }));
  }, []);

  const showToast = useCallback((title: string, type: AlertType = 'info') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts(prev => [...prev, { id, title, type }]);
    
    // Auto remover após 5 segundos
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <AlertContext.Provider value={{ showAlert, hideAlert, showToast, removeToast, alert, toasts }}>
      {children}
    </AlertContext.Provider>
  );
};

export const useAlert = () => {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error('useAlert deve ser usado dentro de um AlertProvider');
  }
  return context;
};
