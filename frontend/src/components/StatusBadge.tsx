import { clsx } from 'clsx';
import { CheckCircle2, Clock, AlertCircle, Send } from 'lucide-react';

type StatusType = 'PENDING' | 'SENT' | 'PROCESSED' | 'ERROR';

interface StatusBadgeProps {
  status: StatusType;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = {
    PENDING: {
      color: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
      icon: Clock,
      label: 'Novo / Pendente',
      glow: 'shadow-[0_0_10px_rgba(148,163,184,0.1)]'
    },
    SENT: {
      color: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      icon: Send,
      label: 'Enviado SOAP',
      glow: 'shadow-[0_0_10px_rgba(59,130,246,0.3)]'
    },
    PROCESSED: {
      color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      icon: CheckCircle2,
      label: 'Processado OK',
      glow: 'shadow-[0_0_10px_rgba(16,185,129,0.3)]'
    },
    ERROR: {
      color: 'bg-red-500/10 text-red-400 border-red-500/20',
      icon: AlertCircle,
      label: 'Rejeitado / Erro',
      glow: 'shadow-[0_0_10px_rgba(239,68,68,0.3)]'
    }
  };

  const { color, icon: Icon, label, glow } = config[status];

  return (
    <span className={clsx(
      "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border",
      color,
      glow
    )}>
      <Icon className="w-3.5 h-3.5" />
      {label}
    </span>
  );
}
