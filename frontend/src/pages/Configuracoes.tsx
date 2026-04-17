import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSystemConfig, updateSystemConfig } from '../services/api';
import { Settings, ShieldAlert, Zap, Globe, Lock, Loader2 } from 'lucide-react';
import { useAlert } from '../context/AlertContext';

export default function Configuracoes() {
  const queryClient = useQueryClient();
  const { showAlert } = useAlert();

  const { data: config, isLoading } = useQuery({
    queryKey: ['systemConfig'],
    queryFn: getSystemConfig
  });

  const mutation = useMutation({
    mutationFn: (newValue: string) => updateSystemConfig(newValue),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['systemConfig'] });
      showAlert("Configuração Salva", "O ambiente de transmissão foi atualizado com sucesso.", "success");
    },
    onError: (err: any) => showAlert("Erro ao salvar", `Falha ao mudar ambiente: ${err}`, "error")
  });

  const isProd = config?.value === 'PRODUCTION';

  const handleToggleAmbiente = () => {
      const nextValue = isProd ? 'HOMOLOGATION' : 'PRODUCTION';
      mutation.mutate(nextValue);
  };

  if (isLoading) {
      return (
          <div className="flex flex-col items-center justify-center min-h-[400px]">
              <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
              <p className="mt-4 text-app-text/60">Carregando configurações...</p>
          </div>
      );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header Section */}
      <div className="flex items-center gap-4 mb-2">
        <div className="p-3 bg-blue-500/10 rounded-2xl border border-blue-500/20 shadow-md">
          <Settings className="w-8 h-8 text-blue-500" />
        </div>
        <div>
          <h1 className="text-3xl font-black text-app-text tracking-tight">Configurações do Sistema</h1>
          <p className="text-app-text opacity-50 font-bold">Gerencie as diretrizes de transmissão e segurança da mensageria.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Environment Security Card */}
        <div className="md:col-span-2 bg-app-bg border border-app-border rounded-xl shadow-sm p-8 relative overflow-hidden group">
            <div className={`absolute top-0 right-0 w-32 h-32 blur-[80px] -translate-y-1/2 translate-x-1/2 transition-colors duration-700 ${isProd ? 'bg-red-500/20' : 'bg-amber-500/20'}`} />
            
            <div className="relative z-10">
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <h3 className="text-xl font-bold text-app-text mb-2 flex items-center gap-2">
                            <Globe className="w-5 h-5 text-blue-500" />
                            Ambiente de Transmissão
                        </h3>
                        <p className="text-sm text-app-text opacity-60 max-w-sm">
                            Define para qual servidor do governo o eSocial enviará seus dados. 
                            Ambiente de Produção tem validade jurídica real.
                        </p>
                    </div>
                </div>

                <div className="flex items-center justify-between p-6 rounded-xl bg-app-bg border border-app-border shadow-inner">
                    <div className="flex flex-col">
                        <span className="text-[10px] uppercase font-black tracking-widest text-app-text/40 mb-1">Status Atual</span>
                        <div className={`text-sm font-bold flex items-center gap-2 ${isProd ? 'text-red-400' : 'text-amber-400'}`}>
                            <ShieldAlert className="w-4 h-4" />
                            {isProd ? 'MODO PRODUÇÃO (REAL)' : 'MODO HOMOLOGAÇÃO (TESTES)'}
                        </div>
                    </div>
                    
                    <button 
                        onClick={handleToggleAmbiente}
                        disabled={mutation.isPending}
                        className={`relative w-16 h-8 rounded-full transition-all duration-500 border-2 ${isProd ? 'bg-red-500/20 border-red-500/30' : 'bg-amber-500/10 border-amber-500/20'}`}
                    >
                        <div className={`absolute top-1 w-5 h-5 rounded-full transition-all duration-500 shadow-lg ${isProd ? 'left-9 bg-red-400 shadow-red-500/50' : 'left-1 bg-amber-400 shadow-amber-500/50'}`}>
                            {mutation.isPending && <Loader2 className="w-full h-full animate-spin p-1 text-black" />}
                        </div>
                    </button>
                </div>

                {isProd && (
                    <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 animate-pulse">
                        <p className="text-xs text-red-300 font-semibold leading-relaxed">
                            ⚠️ ATENÇÃO: Você está em ambiente de PRODUÇÃO. Todas as transmissões terão validade jurídica e fiscal perante a Receita Federal e o Ministério do Trabalho.
                        </p>
                    </div>
                )}
            </div>
        </div>

        {/* Quick Info / Tips */}
        <div className="bg-app-bg border border-app-border rounded-xl shadow-sm p-6 space-y-6 flex flex-col justify-center">
            <div className="flex gap-4">
                <div className="mt-1"><Zap className="w-5 h-5 text-blue-500" /></div>
                <div>
                    <h4 className="text-sm font-bold text-app-text mb-1">Assinatura Híbrida</h4>
                    <p className="text-xs text-app-text opacity-50">Suporta assinaturas automáticas (A1) e manuais (A3).</p>
                </div>
            </div>
            <div className="flex gap-4">
                <div className="mt-1"><Lock className="w-5 h-5 text-cyan-500" /></div>
                <div>
                    <h4 className="text-sm font-bold text-app-text mb-1">Criptografia mTLS</h4>
                    <p className="text-xs text-app-text opacity-50">Conexão segura ponto-a-ponto com os servidores do Governo.</p>
                </div>
            </div>
        </div>

      </div>

      {/* Other Settings (Placeholders for now) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-60 grayscale">
          <div className="bg-app-bg border-2 border-dashed border-app-border p-6 rounded-xl">
              <h4 className="text-sm font-bold text-app-text mb-2">Backups Automáticos</h4>
              <p className="text-xs text-app-text opacity-60">Configuração de espelhamento de eventos no seu próprio S3.</p>
          </div>
          <div className="bg-app-bg border-2 border-dashed border-app-border p-6 rounded-xl">
              <h4 className="text-sm font-bold text-app-text mb-2">Webhooks</h4>
              <p className="text-xs text-app-text opacity-60">Envio de notificações de recibos para o seu ERP.</p>
          </div>
      </div>

    </div>
  );
}
