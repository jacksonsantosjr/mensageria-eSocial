import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLotes, signLote, sendLote, downloadLotePDF, downloadEventoPDF, getLote } from '../services/api';
import { FileJson, Loader2, Send, PenTool, Download, FileText, Eye, X } from 'lucide-react';
import { useAlert } from '../context/AlertContext';
import { useState } from 'react';

export default function Lotes() {
  const queryClient = useQueryClient();
  const { showAlert } = useAlert();
  const [selectedLote, setSelectedLote] = useState<any | null>(null);
  const [loadingDetails, setLoadingDetails] = useState<string | null>(null);

  const { data: lotes = [], isLoading: loadingLotes } = useQuery({ 
    queryKey: ['lotes'], 
    queryFn: getLotes 
  });

  const signMutation = useMutation({
    mutationFn: (loteId: string) => signLote(loteId),
    onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['lotes'] });
        showAlert("Lote Assinado", "O lote foi assinado digitalmente com sucesso e está pronto para o envio.", "success");
    },
    onError: (err: any) => showAlert("Erro na Assinatura", `Não foi possível assinar o lote: ${err}`, "error")
  });

  const sendMutation = useMutation({
    mutationFn: (loteId: string) => sendLote(loteId),
    onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['lotes'] });
        showAlert("Lote Enviado", "Lote enviado com sucesso ao portal do eSocial!", "success");
    },
    onError: (err: any) => showAlert("Erro no Envio", `Não foi possível enviar o lote ao eSocial: ${err}`, "error")
  });

  const StatusBadge = ({ status }: { status: string }) => {
     const styles: Record<string, string> = {
        'PENDING': 'bg-orange-100 text-orange-700 border-orange-200',
        'VALIDATING': 'bg-indigo-100 text-indigo-700 border-indigo-200',
        'SIGNED': 'bg-blue-100 text-blue-700 border-blue-200',
        'SENT': 'bg-emerald-100 text-emerald-700 border-emerald-200',
        'PROCESSING': 'bg-indigo-100 text-indigo-700 border-indigo-200',
        'PROCESSED': 'bg-green-100 text-green-700 border-green-200',
        'ERROR': 'bg-red-100 text-red-700 border-red-200',
     };
     
     const label = styles[status] ? status : 'UNKNOWN';
     return (
        <span className={`px-3 py-1 rounded-lg text-xs font-bold border ${styles[status]}`}>
            {label}
        </span>
     );
  }

  return (
    <div className="space-y-6">
      {/* Histórico e Ações */}
      <div className="glass-card overflow-hidden">
         <div className="p-6 border-b border-glass-border flex justify-between items-center bg-black/5">
            <h3 className="text-lg font-bold text-app-text">Gerenciamento de Lotes</h3>
            <button className="text-sm text-primary-500 font-semibold hover:underline" onClick={() => queryClient.invalidateQueries({ queryKey: ['lotes'] })}>
                Atualizar Lista
            </button>
         </div>
         
         {loadingLotes ? <div className="p-12 text-center"><Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-500" /></div> : (
           <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-black/20 text-app-text/60 text-[10px] uppercase font-black tracking-widest">
                    <tr>
                        <th className="px-6 py-4">Lote / Data</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4 text-center">Evt.</th>
                        <th className="px-6 py-4 text-right">Ações</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-glass-border">
                    {lotes.length === 0 && (
                        <tr><td colSpan={4} className="px-6 py-12 text-center text-app-text/40 font-medium italic">Nenhum lote processado neste ambiente.</td></tr>
                    )}
                    {lotes.map((l: any) => (
                        <tr key={l.id} className="hover:bg-black/5 transition-colors">
                            <td className="px-6 py-4">
                                <div className="flex items-center space-x-3">
                                    <div className="p-2 bg-primary-500/10 rounded-lg text-primary-500">
                                        <FileJson className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="font-mono text-sm text-app-text font-bold">{l.id.substring(0, 13)}...</p>
                                        <p className="text-xs text-app-text/40">{new Date(l.created_at).toLocaleString('pt-BR')}</p>
                                    </div>
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                <StatusBadge status={l.status} />
                            </td>
                            <td className="px-6 py-4 text-center text-sm font-semibold text-app-text/80">
                                {l.total_eventos}
                            </td>
                            <td className="px-6 py-4">
                                <div className="flex items-center justify-end space-x-2">
                                    {/* Botão Assinar */}
                                    {l.status === 'PENDING' && (
                                        <button 
                                            title="Assinar Lote"
                                            className="p-2 bg-blue-500/10 text-blue-500 rounded-lg hover:bg-blue-500/20 transition border border-blue-500/20"
                                            onClick={() => signMutation.mutate(l.id)}
                                            disabled={signMutation.isPending}
                                        >
                                            {signMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <PenTool className="w-4 h-4" />}
                                        </button>
                                    )}

                                    {/* Botão Enviar */}
                                    {l.status === 'SIGNED' && (
                                        <button 
                                            title="Enviar para eSocial"
                                            className="p-2 bg-emerald-500/10 text-emerald-500 rounded-lg hover:bg-emerald-500/20 transition border border-emerald-500/20"
                                            onClick={() => sendMutation.mutate(l.id)}
                                            disabled={sendMutation.isPending}
                                        >
                                            {sendMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                        </button>
                                    )}

                                    {/* Botão Ver Detalhes */}
                                    <button 
                                        title="Ver Eventos do Lote"
                                        className="p-2 bg-blue-500/10 text-blue-500 rounded-lg hover:bg-blue-500/20 transition border border-blue-500/20 disabled:opacity-50"
                                        onClick={async () => {
                                            setLoadingDetails(l.id);
                                            try {
                                                const loteDetalhado = await getLote(l.id);
                                                setSelectedLote(loteDetalhado);
                                            } catch (e) {
                                                showAlert("Erro", "Falha ao carregar os eventos detalhados.", "error");
                                            } finally {
                                                setLoadingDetails(null);
                                            }
                                        }}
                                        disabled={loadingDetails === l.id}
                                    >
                                        {loadingDetails === l.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Eye className="w-4 h-4" />}
                                    </button>

                                    {/* Botão PDF Lote */}
                                    {(l.status === 'SENT' || l.status === 'PROCESSED' || l.status === 'ERROR') && (
                                        <button 
                                            title="Baixar Comprovante Lote (PDF)"
                                            className="p-2 bg-amber-500/10 text-amber-500 rounded-lg hover:bg-amber-500/20 transition border border-amber-500/20"
                                            onClick={() => downloadLotePDF(l.id)}
                                        >
                                            <FileText className="w-4 h-4" />
                                        </button>
                                    )}

                                    {/* Botão Download XML */}
                                    <button 
                                        title="Baixar XML Original"
                                        className="p-2 bg-black/5 text-app-text/40 rounded-lg hover:bg-black/10 transition border border-glass-border"
                                    >
                                        <Download className="w-4 h-4" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
              </table>
           </div>
         )}
      </div>

      {/* Modal de Eventos */}
      {selectedLote && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
          <div className="glass-card w-full max-w-4xl overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="p-6 border-b border-glass-border flex justify-between items-center bg-black/5">
              <div>
                <h2 className="text-xl font-bold text-app-text">Detalhes do Lote</h2>
                <p className="text-sm text-app-text/40 font-mono">{selectedLote.id}</p>
              </div>
              <button onClick={() => setSelectedLote(null)} className="text-app-text/40 hover:text-app-text transition">
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="p-6 max-h-[60vh] overflow-y-auto custom-scrollbar">
                <table className="w-full text-left">
                    <thead className="text-[10px] uppercase font-black tracking-widest text-app-text/40 border-b border-glass-border">
                        <tr>
                            <th className="py-3 px-2">Tipo</th>
                            <th className="py-3 px-2">ID Evento</th>
                            <th className="py-3 px-2 text-center">Status</th>
                            <th className="py-3 px-10 text-right">Recibo / Ações</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-glass-border">
                        {selectedLote.eventos?.map((evt: any) => (
                            <tr key={evt.id} className="hover:bg-white/5 transition-colors">
                                <td className="py-4 px-2 font-bold text-primary-400">{evt.tipo}</td>
                                <td className="py-4 px-2 text-xs font-mono text-app-text/60">{(evt.evento_id_esocial || '').substring(0, 30)}...</td>
                                <td className="py-4 px-2">
                                    <div className="flex justify-center">
                                        <StatusBadge status={evt.status} />
                                    </div>
                                </td>
                                <td className="py-4 px-0 pr-2">
                                    <div className="flex items-center justify-end gap-3">
                                        <span className="text-xs font-mono text-app-text/40">{evt.nr_recibo || '---'}</span>
                                        {(evt.status === 'PROCESSED' || evt.status === 'ERROR') && (
                                            <button 
                                                title="Baixar Recibo Individual (PDF)"
                                                onClick={() => downloadEventoPDF(evt.id)}
                                                className="p-1.5 bg-amber-500/10 text-amber-500 rounded hover:bg-amber-500/20 border border-amber-500/20"
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

            <div className="p-6 bg-black/10 border-t border-glass-border flex justify-end">
                <button 
                  onClick={() => setSelectedLote(null)}
                  className="px-6 py-2 bg-white/5 hover:bg-white/10 text-app-text/60 rounded-lg font-bold transition"
                >
                  Fechar
                </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}