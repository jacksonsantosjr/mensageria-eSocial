import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLotes, createLote, getEmpresas, signLote, sendLote } from '../services/api';
import { FileJson, Upload, CheckCircle, AlertCircle, Clock, Loader2, Send, PenTool, Download } from 'lucide-react';

export default function Lotes() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [empresaId, setEmpresaId] = useState('');

  const { data: lotes = [], isLoading: loadingLotes } = useQuery({ queryKey: ['lotes'], queryFn: getLotes });
  const { data: empresas = [], isLoading: loadingEmpresas } = useQuery({ queryKey: ['empresas'], queryFn: getEmpresas });

  const mutation = useMutation({
    mutationFn: (file: File) => createLote(file, empresaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lotes'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardResumo'] });
      if (fileInputRef.current) fileInputRef.current.value = '';
    },
    onError: (err: any) => {
      alert(`Erro ao adicionar lote: ${err}`);
    }
  });

  const signMutation = useMutation({
    mutationFn: (loteId: string) => signLote(loteId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lotes'] }),
    onError: (err: any) => alert(`Erro ao assinar: ${err}`)
  });

  const sendMutation = useMutation({
    mutationFn: (loteId: string) => sendLote(loteId),
    onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['lotes'] });
        alert("Lote enviado com sucesso ao eSocial!");
    },
    onError: (err: any) => alert(`Erro ao enviar: ${err}`)
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!empresaId) return alert('Selecione uma empresa antes de fazer upload.');
    const file = e.target.files?.[0];
    if (file) mutation.mutate(file);
  };

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
      
      {/* Seleção de Empresa */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
         <h3 className="text-md font-semibold text-gray-700 mb-3">Empresa Transmissora</h3>
         {loadingEmpresas ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : (
            <select
              className="p-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-primary-500 bg-gray-50 font-medium"
              value={empresaId} 
              onChange={e => setEmpresaId(e.target.value)}
            >
              <option value="">-- Selecione uma empresa pré-cadastrada --</option>
              {empresas.map((e:any) => <option key={e.id} value={e.id}>{e.razao_social} ({e.cnpj})</option>)}
            </select>
         )}
      </div>

      {/* Area de Upload */}
      <div 
         className={`bg-white p-6 rounded-xl shadow-sm flex flex-col items-center justify-center border-dashed border-2 py-12 transition cursor-pointer
           ${mutation.isPending ? 'bg-gray-100 border-gray-300' : 'bg-gray-50/50 hover:bg-gray-50 border-gray-300'}`}
         onClick={() => fileInputRef.current?.click()}
      >
        <input type="file" ref={fileInputRef} className="hidden" accept=".xml" onChange={handleFileChange} disabled={mutation.isPending} />
        {mutation.isPending ? (
           <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-3" />
        ) : (
           <Upload className="w-10 h-10 text-primary-400 mb-3" />
        )}
        <p className="text-gray-700 font-semibold text-lg">Clique para enviar o XML do Lote</p>
        <p className="text-gray-500 text-sm mt-1">S-1.3 (Eventos de Tabela, Não Periódicos ou Periódicos)</p>
      </div>

      {/* Histórico e Ações */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
         <div className="p-6 border-b border-gray-200 flex justify-between items-center">
            <h3 className="text-lg font-bold text-gray-800">Gerenciamento de Lotes</h3>
            <button className="text-sm text-primary-600 font-semibold hover:underline" onClick={() => queryClient.invalidateQueries({ queryKey: ['lotes'] })}>
                Atualizar Lista
            </button>
         </div>
         
         {loadingLotes ? <div className="p-12 text-center"><Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-500" /></div> : (
           <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-gray-50/80 text-gray-600 text-xs uppercase font-bold tracking-wider">
                    <tr>
                        <th className="px-6 py-4">Lote / Data</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4 text-center">Eventos</th>
                        <th className="px-6 py-4 text-right">Ações</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {lotes.length === 0 && (
                        <tr><td colSpan={4} className="px-6 py-12 text-center text-gray-500 font-medium">Nenhum lote processado neste ambiente.</td></tr>
                    )}
                    {lotes.map((l: any) => (
                        <tr key={l.id} className="hover:bg-gray-50/80 transition-colors">
                            <td className="px-6 py-4">
                                <div className="flex items-center space-x-3">
                                    <div className="p-2 bg-primary-100 rounded-lg text-primary-600">
                                        <FileJson className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="font-mono text-sm text-gray-700 font-bold">{l.id.substring(0, 13)}...</p>
                                        <p className="text-xs text-gray-400">{new Date(l.created_at).toLocaleString('pt-BR')}</p>
                                    </div>
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                <StatusBadge status={l.status} />
                            </td>
                            <td className="px-6 py-4 text-center text-sm font-semibold text-gray-600">
                                {l.total_eventos}
                            </td>
                            <td className="px-6 py-4">
                                <div className="flex items-center justify-end space-x-2">
                                    {/* Botão Assinar */}
                                    {l.status === 'PENDING' && (
                                        <button 
                                            title="Assinar Lote"
                                            className="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition shadow-sm border border-blue-200"
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
                                            className="p-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition shadow-sm border border-emerald-200"
                                            onClick={() => sendMutation.mutate(l.id)}
                                            disabled={sendMutation.isPending}
                                        >
                                            {sendMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                        </button>
                                    )}

                                    {/* Botão Download */}
                                    <button 
                                        title="Baixar XML Original"
                                        className="p-2 bg-gray-50 text-gray-500 rounded-lg hover:bg-gray-100 transition border border-gray-200"
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