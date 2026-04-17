import { useState } from 'react';
import { createPortal } from 'react-dom';
import { useQuery } from '@tanstack/react-query';
import { getDashboardResumo, getLote, downloadLotePDF, downloadEventoPDF } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { ArrowRight, BarChart3, Database, AlertTriangle, CheckCircle2, X, FileText, Download, Loader2, Eye, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAlert } from '../context/AlertContext';

export function Dashboard() {
  const { showAlert } = useAlert();
  const [selectedLote, setSelectedLote] = useState<any | null>(null);
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ['dashboard_resumo'],
    queryFn: getDashboardResumo,
    refetchInterval: 10000 // Atualiza a cada 10s
  });

  const handleVerDetalhes = async (id: string) => {
    setLoadingId(id);
    try {
      const loteCompleto = await getLote(id);
      setSelectedLote(loteCompleto);
    } catch (err) {
      showAlert("Erro", "Não foi possível carregar os detalhes do lote.", "error");
    } finally {
      setLoadingId(null);
    }
  };

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
            <div key={i} className="bg-app-bg border border-app-border p-6 rounded-lg shadow-sm hover:shadow-md transition-all group">
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
      <div className="bg-app-bg border border-app-border rounded-lg shadow-sm overflow-hidden">
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
                <th className="px-6 py-4 text-center">Status eSocial</th>
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
                  <td className="px-6 py-4 text-center">
                    <StatusBadge status={mapStatus(row.status) as any} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => handleVerDetalhes(row.id)}
                      disabled={loadingId === row.id}
                      className="px-3 py-1.5 rounded-md text-xs font-bold bg-blue-500/10 text-blue-600 border border-blue-500/20 hover:bg-blue-500/20 transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2 ml-auto"
                    >
                      {loadingId === row.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Eye className="w-3 h-3" />}
                      Detalhes
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de Detalhes - Estilo Glassmorphism */}
      {selectedLote && createPortal(
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="glass-card w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl animate-in zoom-in-95 duration-300">
            {/* Header do Modal */}
            <div className="p-6 border-b border-app-border flex justify-between items-center bg-app-bg/30">
              <div>
                <h2 className="text-xl font-bold text-app-text flex items-center gap-2">
                  <Database className="w-5 h-5 text-blue-500" />
                  Detalhes do Lote
                </h2>
                <p className="text-xs font-mono text-app-text/40 mt-1">ID Completo: {selectedLote.id}</p>
              </div>
              <button 
                onClick={() => setSelectedLote(null)}
                className="p-2 rounded-full hover:bg-app-bg transition-colors text-app-text/40 hover:text-app-text"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Conteúdo do Modal */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
              
              {/* Alerta de Erro Crítico (se houver) */}
              {(selectedLote.status === 'ERROR' || selectedLote.erro_mensagem) && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-md flex gap-4 items-start">
                   <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                   <div className="text-sm">
                      <p className="font-bold text-red-500 mb-1">Erro no Processamento do Lote</p>
                      <p className="text-app-text/70">{selectedLote.erro_mensagem || 'Ocorreu um erro inesperado na transmissão. Verifique a lista de eventos abaixo.'}</p>
                   </div>
                </div>
              )}

              {/* Tabela de Eventos */}
              <div>
                <h3 className="text-xs font-bold text-app-text opacity-40 uppercase tracking-widest mb-4">Eventos Enviados no Lote</h3>
                <div className="bg-black/5 rounded-md border border-app-border overflow-hidden">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="text-[10px] uppercase font-bold tracking-widest text-app-text/40 border-b border-app-border bg-app-bg/20">
                        <th className="px-4 py-3">Tipo</th>
                        <th className="px-4 py-3">ID eSocial / Referência</th>
                        <th className="px-4 py-3 text-center">Status</th>
                        <th className="px-4 py-3 text-right">Recibo</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-app-border">
                      {selectedLote.eventos?.map((evt: any) => (
                        <tr key={evt.id} className="text-xs hover:bg-app-bg/40 transition-colors">
                          <td className="px-4 py-3 font-bold text-blue-400">{evt.tipo}</td>
                          <td className="px-4 py-3 font-mono opacity-60">{(evt.evento_id_esocial || '').substring(0, 30)}...</td>
                          <td className="px-4 py-3 text-center">
                            <StatusBadge status={mapStatus(evt.status) as any} />
                          </td>
                          <td className="px-4 py-3 text-right group">
                            <div className="flex items-center justify-end gap-2">
                               <span className="font-mono opacity-40">{evt.nr_recibo || '---'}</span>
                               {evt.nr_recibo && (
                                  <button 
                                    onClick={() => downloadEventoPDF(evt.id)}
                                    className="p-1.5 rounded bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 border border-blue-500/20 transition-all"
                                  >
                                    <FileText className="w-3.5 h-3.5" />
                                  </button>
                               )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Footer do Modal (Ações) */}
            <div className="p-6 border-t border-app-border bg-app-bg/20 flex justify-between items-center">
              <div className="flex gap-3">
                <button 
                  onClick={() => downloadLotePDF(selectedLote.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-amber-950 rounded-md text-sm font-bold hover:bg-amber-400 transition-colors shadow-lg shadow-amber-500/20"
                >
                  <FileText className="w-4 h-4" />
                  Imprimir Comprovante
                </button>
                <button 
                  onClick={() => {
                    showAlert("Download XML", "O arquivo XML original está sendo preparado.", "info");
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-app-bg border border-app-border text-app-text/60 rounded-md text-sm font-bold hover:bg-app-bg/80 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Baixar XML Original
                </button>
              </div>
              <button 
                onClick={() => setSelectedLote(null)}
                className="px-6 py-2 bg-app-bg text-app-text font-bold rounded-md hover:bg-app-bg/80 transition-all border border-app-border"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}

    </div>
  );
}