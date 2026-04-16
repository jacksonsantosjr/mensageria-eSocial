import React from 'react';
import { X, CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';
import { useAlert } from '../context/AlertContext';

export const AlertModal: React.FC = () => {
  const { alert, hideAlert } = useAlert();

  if (!alert.isOpen) return null;

  const getTypeStyles = () => {
    switch (alert.type) {
      case 'success':
        return {
          icon: <CheckCircle2 className="w-8 h-8 text-emerald-500" />,
          border: 'border-emerald-500/20',
          bg: 'bg-emerald-500/5',
          button: 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-500/20'
        };
      case 'error':
        return {
          icon: <XCircle className="w-8 h-8 text-rose-500" />,
          border: 'border-rose-500/20',
          bg: 'bg-rose-500/5',
          button: 'bg-rose-600 hover:bg-rose-700 shadow-rose-500/20'
        };
      case 'warning':
        return {
          icon: <AlertTriangle className="w-8 h-8 text-amber-500" />,
          border: 'border-amber-500/20',
          bg: 'bg-amber-500/5',
          button: 'bg-amber-600 hover:bg-amber-700 shadow-amber-500/20'
        };
      default:
        return {
          icon: <Info className="w-8 h-8 text-blue-500" />,
          border: 'border-blue-500/20',
          bg: 'bg-blue-500/5',
          button: 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/20'
        };
    }
  };

  const styles = getTypeStyles();

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300"
        onClick={hideAlert}
      />
      
      {/* Modal Container */}
      <div className={`relative w-full max-w-md glass-card ${styles.border} ${styles.bg} p-8 shadow-2xl animate-in zoom-in-95 duration-300 rounded-lg`}>
        {/* Close button */}
        <button 
          onClick={hideAlert}
          className="absolute top-4 right-4 p-1 rounded-full hover:bg-black/10 transition-colors text-app-text/40"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex flex-col items-center text-center">
          <div className="mb-4">
            {styles.icon}
          </div>
          
          <h2 className="text-xl font-black text-app-text mb-2 tracking-tight">
            {alert.title}
          </h2>
          
          <p className="text-app-text/60 font-medium leading-relaxed mb-6">
            {alert.message}
          </p>

          <button
            onClick={hideAlert}
            className={`w-full py-3 ${styles.button} text-white font-bold rounded-lg transition-all active:scale-95 shadow-lg`}
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
};
