import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLotes, signLote, sendLote } from '../services/api';
import { FileJson, Loader2, Send, PenTool, Download } from 'lucide-react';
import { useAlert } from '../context/AlertContext';

export default function Lotes() {
  const queryClient = useQueryClient();
  const { showAlert } = useAlert();

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
        'SIGNED': 'bg-blue-100 text-blue-700 border-blue-200',
        'SENT': 'bg-emerald-100 text-emerald-700 border-emerald-200',
        'PROCESSING': 'bg-indigo-100 text-indigo-700 border-indigo-200',
        'PROCESSED': 'bg-green-100 text-green-700 border-green-200',
        'ERROR': 'bg-red-100 text-red-700 border-red-200',
     };
     
     const label = styles[status] ? status : 'UNKNOWN';
     return (
        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${styles[status]}`}>
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

                                    {/* Botão Download */}
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
    </div>
  );
}