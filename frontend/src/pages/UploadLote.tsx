import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getEmpresas, createLote } from '../services/api';
import { Upload, Loader2, Building2, FileCheck, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAlert } from '../context/AlertContext';

export default function UploadLote() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { showAlert } = useAlert();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [empresaId, setEmpresaId] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const { data: empresas = [], isLoading: loadingEmpresas } = useQuery({
    queryKey: ['empresas'],
    queryFn: getEmpresas
  });

  const mutation = useMutation({
    mutationFn: (file: File) => createLote(file, empresaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lotes'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardResumo'] });
      showAlert("Sucesso!", "Lote processado com sucesso!", "success");
      navigate('/lotes'); // Redireciona para a listagem
    },
    onError: (err: any) => {
      showAlert("Erro de Processamento", `Não foi possível processar o XML: ${err}`, "error");
    }
  });

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileUpload = (file: File) => {
    if (!empresaId) {
       showAlert("Empresa não selecionada", "Por favor, selecione a Empresa Transmissora primeiro antes de realizar o upload.", "warning");
       return;
    }
    if (!file.name.endsWith('.xml')) {
       showAlert("Arquivo Inválido", "Apenas arquivos XML são permitidos para transmissão ao eSocial.", "error");
       return;
    }
    mutation.mutate(file);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center space-x-3 mb-2">
         <div className="p-3 bg-blue-500/10 rounded-2xl shadow-sm border border-blue-500/20 text-blue-500">
            <Upload className="w-6 h-6" />
         </div>
         <div>
            <h2 className="text-2xl font-black text-app-text tracking-tight">Novo Lote eSocial</h2>
            <p className="text-app-text opacity-60 font-medium">Envie seus arquivos XML para validação e assinatura.</p>
         </div>
      </div>

      {/* 1. Seleção de Empresa */}
      <div className="bg-app-bg border border-app-border rounded-xl shadow-sm p-8 flex flex-col space-y-4">
         <div className="flex items-center space-x-2 text-app-text">
            <Building2 className="w-5 h-5 text-blue-500" />
            <h3 className="font-bold text-lg tracking-tight">Selecione a Empresa Transmissora</h3>
         </div>
         
         {loadingEmpresas ? (
            <div className="flex items-center p-4 bg-app-bg rounded-lg border border-app-border">
               <Loader2 className="w-5 h-5 animate-spin text-blue-500 mr-2" />
               <span className="text-app-text opacity-40 font-medium italic text-sm">Buscando empresas cadastradas...</span>
            </div>
         ) : empresas.length === 0 ? (
            <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-600 text-sm flex items-center">
               <AlertCircle className="w-5 h-5 mr-2" />
               Você ainda não cadastrou nenhuma empresa. <button onClick={() => navigate('/empresas')} className="ml-1 underline font-bold">Cadastrar agora.</button>
            </div>
         ) : (
            <select
              className="w-full p-4 border border-app-border rounded-lg outline-none focus:ring-4 focus:ring-blue-500/10 bg-app-bg font-bold text-app-text transition appearance-none cursor-pointer"
              value={empresaId} 
              onChange={e => setEmpresaId(e.target.value)}
            >
               <option value="" className="bg-app-bg text-app-text">-- Selecione a empresa --</option>
               {Array.isArray(empresas) && empresas.map((e:any) => (
                <option key={e.id} value={e.id} className="bg-app-bg text-app-text">
                  {e.razao_social} ({e.cnpj})
                </option>
               ))}
            </select>
         )}
      </div>

      {/* 2. Area de Drop/Upload */}
      <div 
         onDragEnter={handleDrag}
         onDragLeave={handleDrag}
         onDragOver={handleDrag}
         onDrop={handleDrop}
         onClick={() => !mutation.isPending && fileInputRef.current?.click()}
         className={`relative group bg-app-bg border border-app-border p-12 flex flex-col items-center justify-center border-2 border-dashed rounded-xl transition-all duration-300 cursor-pointer overflow-hidden shadow-sm
           ${dragActive ? 'border-blue-500 bg-blue-500/5 scale-[1.01]' : 'border-app-border hover:border-blue-500/50 hover:bg-app-bg/50'}
           ${mutation.isPending ? 'pointer-events-none opacity-80' : ''}`}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept=".xml" 
          onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])} 
        />
        
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
           <FileCheck className="w-48 h-48 -mr-12 -mt-12 text-app-text" />
        </div>

        {mutation.isPending ? (
           <div className="text-center">
              <div className="relative mb-6">
                 <Loader2 className="w-24 h-24 text-blue-500 animate-spin mx-auto" />
                 <div className="absolute inset-0 flex items-center justify-center">
                    <Upload className="w-8 h-8 text-blue-500" />
                 </div>
              </div>
              <h3 className="text-2xl font-black text-app-text mb-2">Processando XML...</h3>
              <p className="text-app-text opacity-60 font-medium">Extraindo eventos e validando esquema S-1.3</p>
           </div>
        ) : (
           <div className="text-center relative z-10">
              <div className="w-24 h-24 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                 <Upload className="w-12 h-12 text-blue-500" />
              </div>
              <h3 className="text-3xl font-black text-app-text mb-3 tracking-tight">Solte o seu arquivo aqui</h3>
              <p className="text-app-text opacity-60 font-bold mb-8">ou clique para selecionar do seu computador</p>
              
              <div className="inline-flex items-center space-x-2 bg-app-tertiary px-4 py-2 rounded-full text-[10px] font-black text-app-text opacity-40 uppercase tracking-widest">
                 <span>Formatos suportados:</span>
                 <span className="text-blue-500">.XML</span>
              </div>
           </div>
        )}
      </div>

      <div className="bg-blue-500/10 p-6 rounded-lg border border-blue-500/20 flex items-start space-x-4">
         <AlertCircle className="w-6 h-6 text-blue-500 shrink-0 mt-0.5" />
         <div className="text-sm">
            <p className="font-bold text-blue-500 mb-1">Dica de Transmissão</p>
            <p className="text-app-text/70 font-medium leading-relaxed">
               Lotes XML podem conter múltiplos eventos (S-1000, S-2200, etc.). 
               O sistema irá desmembrar cada evento para validação individual antes da assinatura final.
            </p>
         </div>
      </div>
    </div>
  );
}
