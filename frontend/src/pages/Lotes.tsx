import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLotes, createLote, getEmpresas } from '../services/api';
import { FileJson, Upload, CheckCircle, AlertCircle, Clock, Loader2 } from 'lucide-react';

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
      alert("Lote enviado com sucesso!");
      if (fileInputRef.current) fileInputRef.current.value = '';
    },
    onError: (err) => {
      alert("Erro ao enviar lote. Selecione uma empresa e tente novamente.");
      console.error(err);
    }
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!empresaId) return alert('Selecione uma empresa antes de fazer upload.');
    const file = e.target.files?.[0];
    if (file) mutation.mutate(file);
  };

  const StatusIcon = ({ status }: { status: string }) => {
     if (status === 'PROCESSED' || status === 'SENT') return <CheckCircle className="w-5 h-5 text-green-500" />;
     if (status === 'ERROR') return <AlertCircle className="w-5 h-5 text-red-500" />;
     return <Clock className="w-5 h-5 text-orange-500" />;
  }

  return (
    <div className="space-y-6">
      
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
         <h3 className="text-md font-semibold text-gray-700 mb-3">Empresa Transmissora</h3>
         {loadingEmpresas ? <Loader2 className="w-5 h-5 animate-spin" /> : (
            <select
              className="p-2 border border-gray-300 rounded-lg outline-none focus:ring=2 focus:ring-primary-500"
              value={empresaId} 
              onChange={e => setEmpresaId(e.target.value)}
            >
              <option value="">-- Selecione uma empresa pré-cadastrada --</option>
              {empresas.map((e:any) => <option key={e.id} value={e.id}>{e.razao_social} ({e.cnpj})</option>)}
            </select>
         )}
      </div>

      <div 
         className={`bg-white p-6 rounded-xl shadow-sm flex flex-col items-center justify-center border-dashed border-2 py-12 transition cursor-pointer
           ${mutation.isPending ? 'bg-gray-100 border-gray-300' : 'bg-gray-50/50 hover:bg-gray-50 border-gray-300'}`}
         onClick=y() => fileInputRef.current?.click()}
      >
        <input type="file" ref={fileInputRef} className="hidden" accept=".xml" onChange={handleFileChange} disabled={mutation.isPending} />
        {mutation.isPending ? (
           <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-3" />
        ) : (
           <Upload className="w-10 h-10 text-gray-400 mb-3" />
        )}
        <p className="text-gray-700 font-medium">Clique para enviar o XML do Lote (eSocial S-1.3)</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
         <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">Histórico de Lotes</h3>
         </div>
         {loadingLotes ? <div className="p-6"><Loader2 className="w-6 h-6 animate-spin mx-auto text-primary-500" /></div> : (
           <div className="divide-y">
              {lotes.length === 0 && <p className="p-6 text-center text-gray-500">Nenhum lote enviado ainda.</p>}
              {lotes.map((l: any) => (
                 <div key={l.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                    <div className="flex items-center space-x-4">
                       <div className="p-3 bg-primary-50 rounded-lg text-primary-600">
                         <FileJson className="w-6 h-6" />
                       </div>
                       <div>
                         <p className="font-mono text-sm text-gray-800">{l.id}</p>
                         <p className="text-xs text-gray-500 mt-1">{new Date(l.created_at).toLocaleString('pt-BR')}</p>
                       </div>
                    </div>
                    <div className="flex items-center space-x-3">
                       <StatusIcon status={l.status} />
                       <span className="text-gray-600 text-sm font-bold">{l.status}</span>
                    </div>
                 </div>
              ))}
           </div>
         )}
      </div>
    </div>
  );
}