import React from 'react';
import { useAlert } from '../context/AlertContext';
import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { clsx } from 'clsx';

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useAlert();

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
    error: <AlertCircle className="w-5 h-5 text-red-400" />,
    warning: <AlertTriangle className="w-5 h-5 text-amber-400" />,
    info: <Info className="w-5 h-5 text-blue-400" />,
  };

  const colors = {
    success: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-200',
    error: 'border-red-500/20 bg-red-500/10 text-red-200',
    warning: 'border-amber-500/20 bg-amber-500/10 text-amber-200',
    info: 'border-blue-500/20 bg-blue-500/10 text-blue-200',
  };

  return (
    <div className="fixed bottom-6 right-6 z-[60] flex flex-col gap-3 pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={clsx(
            "pointer-events-auto flex items-center gap-4 px-4 py-3 rounded-xl border backdrop-blur-md shadow-2xl animate-slide-in-right min-w-[300px]",
            colors[toast.type]
          )}
        >
          <div className="flex-shrink-0">
            {icons[toast.type]}
          </div>
          <p className="flex-1 text-sm font-medium">{toast.title}</p>
          <button
            onClick={() => removeToast(toast.id)}
            className="flex-shrink-0 p-1 hover:bg-white/10 rounded transition-colors"
          >
            <X className="w-4 h-4 opacity-70" />
          </button>
        </div>
      ))}
    </div>
  );
};
