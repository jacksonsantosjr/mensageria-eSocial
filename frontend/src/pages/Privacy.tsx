import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ShieldCheck, Lock, Database } from 'lucide-react';
import { BACKGROUND_ESOCIAL } from '../assets/images';

export default function Privacy() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-slate-950 font-sans antialiased text-slate-200" data-theme="dark">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-20"
        style={{ backgroundImage: `url(${BACKGROUND_ESOCIAL})` }}
      >
        <div className="absolute inset-0 bg-slate-950/80" />
      </div>

      {/* Header Fixo */}
      <nav className="relative z-20 flex items-center justify-between px-8 py-6 max-w-5xl mx-auto">
        <button 
          onClick={() => navigate('/login')}
          className="flex items-center gap-2 text-sm font-bold text-blue-400 hover:text-blue-300 transition-colors group"
        >
          <ChevronLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          Voltar para Início
        </button>
        <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <span className="font-black tracking-tighter text-white text-xl">eSocial <span className="text-blue-500">IA</span></span>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-10 max-w-4xl mx-auto px-8 py-12">
        <div className="glass-card p-8 md:p-12 border-blue-500/10 shadow-2xl slide-in-bottom">
          <header className="mb-10 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
              <Lock className="w-8 h-8 text-blue-500" />
            </div>
            <h1 className="text-4xl font-black text-white mb-4 tracking-tight">Política de Privacidade</h1>
            <p className="text-slate-400 text-sm">Última atualização: 01 de Maio de 2026</p>
          </header>

          <div className="space-y-8 prose prose-invert prose-blue max-w-none">
            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">01</span>
                Coleta de Dados
              </h2>
              <p className="leading-relaxed opacity-80">
                Coletamos apenas os dados estritamente necessários para o funcionamento da mensageria eSocial, incluindo informações cadastrais de empresas, dados de funcionários (conforme exigido pelos layouts oficiais) e arquivos XML de eventos.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">02</span>
                Finalidade do Tratamento
              </h2>
              <p className="leading-relaxed opacity-80">
                Os dados são processados com a finalidade exclusiva de validação técnica, conversão de formatos e transmissão para o ambiente nacional do eSocial. Utilizamos Inteligência Artificial para identificar inconsistências e prevenir erros de envio.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">03</span>
                Segurança e Criptografia
              </h2>
              <p className="leading-relaxed opacity-80">
                Todos os dados em trânsito e em repouso são protegidos por criptografia de nível militar (AES-256). As sessões de usuário são monitoradas e protegidas por tokens de autenticação seguros via Supabase.
              </p>
              <div className="mt-4 p-4 bg-blue-500/5 border border-blue-500/10 rounded-md flex gap-4">
                <Database className="w-6 h-6 text-blue-400 shrink-0" />
                <p className="text-xs text-slate-400">Armazenamento realizado em servidores de alta disponibilidade com redundância de dados e backup diário automático.</p>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">04</span>
                Compartilhamento com Terceiros
              </h2>
              <p className="leading-relaxed opacity-80">
                Não comercializamos ou compartilhamos dados com terceiros para fins publicitários. O compartilhamento ocorre apenas com os órgãos governamentais receptores dos eventos eSocial (Receita Federal, Ministério do Trabalho, etc.), conforme solicitado pelo usuário através do comando de envio.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">05</span>
                Seus Direitos (LGPD)
              </h2>
              <p className="leading-relaxed opacity-80">
                Conforme a LGPD, você tem direito a acessar, corrigir, anonimizar ou excluir seus dados da nossa plataforma a qualquer momento. Para isso, basta utilizar as ferramentas de configuração no dashboard ou entrar em contato com nosso suporte técnico.
              </p>
            </section>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10 flex justify-center">
            <button 
              onClick={() => navigate('/login')}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-md transition-all active:scale-95 shadow-lg shadow-blue-500/20"
            >
              Ciente da Política
            </button>
          </div>
        </div>
      </main>

      {/* Footer minimalista */}
      <footer className="py-12 text-center text-slate-600 text-[10px] font-bold uppercase tracking-widest">
        © 2026 Mensageria eSocial IA. Sua privacidade é nossa prioridade.
      </footer>
    </div>
  );
}
