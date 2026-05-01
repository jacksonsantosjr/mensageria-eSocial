import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ShieldCheck, ScrollText, Scale } from 'lucide-react';
import { BACKGROUND_ESOCIAL } from '../assets/images';

export default function Terms() {
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
                <ScrollText className="w-5 h-5 text-white" />
            </div>
            <span className="font-black tracking-tighter text-white text-xl">eSocial <span className="text-blue-500">IA</span></span>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-10 max-w-4xl mx-auto px-8 py-12">
        <div className="glass-card p-8 md:p-12 border-blue-500/10 shadow-2xl slide-in-bottom">
          <header className="mb-10 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
              <Scale className="w-8 h-8 text-blue-500" />
            </div>
            <h1 className="text-4xl font-black text-white mb-4 tracking-tight">Termos de Uso</h1>
            <p className="text-slate-400 text-sm">Última atualização: 01 de Maio de 2026</p>
          </header>

          <div className="space-y-8 prose prose-invert prose-blue max-w-none">
            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">01</span>
                Aceitação dos Termos
              </h2>
              <p className="leading-relaxed opacity-80">
                Ao acessar e utilizar a plataforma **Mensageria eSocial IA**, você concorda em cumprir e estar vinculado aos seguintes termos e condições de uso. Se você não concordar com qualquer parte destes termos, não deverá utilizar nossos serviços.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">02</span>
                Descrição do Serviço
              </h2>
              <p className="leading-relaxed opacity-80">
                Nossa plataforma oferece serviços de mensageria para o eSocial, utilizando inteligência artificial para auxiliar na conversão, validação e transmissão de eventos. O sistema atua como um intermediário técnico entre o usuário e o ambiente do Governo Federal.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">03</span>
                Responsabilidades do Usuário
              </h2>
              <ul className="list-disc pl-5 space-y-2 opacity-80">
                <li>O usuário é responsável pela veracidade e integridade de todos os dados inseridos na plataforma.</li>
                <li>A guarda e sigilo das credenciais de acesso são de responsabilidade exclusiva do usuário.</li>
                <li>O uso da plataforma deve respeitar as leis vigentes e as normas técnicas do eSocial.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">04</span>
                Limitação de Responsabilidade
              </h2>
              <p className="leading-relaxed opacity-80">
                Embora utilizemos tecnologias avançadas de IA para validação, a conferência final dos dados enviados ao governo é de responsabilidade do profissional legalmente habilitado pela empresa. Não nos responsabilizamos por multas ou sanções decorrentes de dados incorretos fornecidos pelo usuário.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400 text-xs">05</span>
                Modificações
              </h2>
              <p className="leading-relaxed opacity-80">
                Reservamo-nos o direito de alterar estes termos a qualquer momento. Alterações significativas serão notificadas através da plataforma ou via e-mail.
              </p>
            </section>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10 flex justify-center">
            <button 
              onClick={() => navigate('/login')}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-md transition-all active:scale-95 shadow-lg shadow-blue-500/20"
            >
              Compreendo e Aceito
            </button>
          </div>
        </div>
      </main>

      {/* Footer minimalista */}
      <footer className="py-12 text-center text-slate-600 text-[10px] font-bold uppercase tracking-widest">
        © 2026 Mensageria eSocial IA. Todos os direitos reservados.
      </footer>
    </div>
  );
}
