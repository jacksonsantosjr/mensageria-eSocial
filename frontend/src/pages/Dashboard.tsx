import { useQuery } from '@tanstack/react-query';
import { getDashboardResumo } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { ArrowRight, BarChart3, Database, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export function Dashboard() {
  const { data } = useQuery({
    queryKey: ['dashboard_resumo'],
    queryFn: getDashboardResumo,
    refetchInterval: 10000 // Atualiza a cada 10s
  });

  const metrics = (data as any)?.metrics || { total: 0, pending: 0, processed: 0, errors: 0 };
  const recentLotes = (data as any)?.recent_lotes || [];

  const cards = [
    { title: 'Lotes Enviados', value: metrics.total, icon: Database, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { title: 'Pendentes / SOAP', value: metrics.pending, icon: BarChart3, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { title: 'Processados OK', value: metrics.processed, icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { title: 'Rejeitados', value: metrics.errors, icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-500/10' },
  ];

  const mapStatus = (status: string) => {
    switch (status) {
      case 'PENDING':
      case 'VALIDATING':
      case 'SIGNED':
        return 'PENDING';
      case 'SENT':
      case 'PROCESSING':
        return 'SENT';
      case 'PROCESSED':
        return 'PROCESSED';
      case 'ERROR':
        return 'ERROR';
      default:
        return 'PENDING';
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((c: any, i: number) => {
          const Icon = c.icon;
          return (
            <div key={i} className="bg-app-bg border border-app-border p-6 rounded-xl shadow-sm hover:shadow-md transition-all group">
              <div className="flex items-center gap-4 mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${c.bg} border-app-border border shadow-sm`}>
                  <Icon className={`w-5 h-5 ${c.color}`} />
                </div>
                <h3 className="text-xs font-bold text-app-text opacity-60 tracking-widest uppercase">{c.title}</h3>
              </div>
              <p className="text-3xl font-extrabold text-app-text">{c.value}</p>
            </div>
          );
        })}
      </div>

      {/* Main Table */}
      <div className="bg-app-bg border border-app-border rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b border-app-border flex justify-between items-center bg-app-bg/50">
          <h3 className="text-lg font-bold text-app-text tracking-tight">Visão Geral dos Últimos Lotes</h3>
          <Link to="/lotes" className="text-sm font-bold text-blue-500 hover:text-blue-400 flex items-center gap-1 transition-colors">
            Ver Todos <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-app-border text-[10px] uppercase font-bold tracking-widest text-app-text opacity-40">
                <th className="px-6 py-4">Lote / ID</th>
                <th className="px-6 py-4">Data de Envio</th>
                <th className="px-6 py-4">Status eSocial</th>
                <th className="px-6 py-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-app-border text-sm text-app-text/70">
              {recentLotes.length === 0 && (
                <tr>
                   <td colSpan={4} className="px-6 py-12 text-center text-app-text/40 italic font-medium">Nenhum lote enviado recentemente.</td>
                </tr>
              )}
              {recentLotes.map((row: any) => (
                <tr key={row.id} className="hover:bg-app-bg/80 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded bg-app-tertiary flex items-center justify-center text-[10px] font-mono border border-app-border uppercase text-app-text/40">
                        XML
                      </div>
                      <span className="font-bold text-app-text/80 tracking-tight">Lote #{row.id.substring(0, 8)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-app-text/80 font-mono text-xs">
                    {new Date(row.created_at).toLocaleString('pt-BR')}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={mapStatus(row.status) as any} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="px-3 py-1.5 rounded-md text-xs font-bold bg-blue-500/10 text-blue-600 border border-blue-500/20 hover:bg-blue-500/20 transition-all active:scale-95">
                      Detalhes
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
    </div>
  );
}