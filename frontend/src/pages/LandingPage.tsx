import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, LogIn, ChevronRight, AlertCircle, Loader2 } from 'lucide-react';
import { login } from '../services/api';
import { BACKGROUND_ESOCIAL } from '../assets/images';

export default function LandingPage() {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(email, password);
      window.location.href = '/'; 
    } catch (err: any) {
      setError('E-mail ou senha inválidos. Tente novamente.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-slate-950 font-sans antialiased selection:bg-blue-500/30">
      {/* Background Image with Right-Aligned Gradient Shadow */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat blur-in"
        style={{ backgroundImage: `url(${BACKGROUND_ESOCIAL})` }}
      >
        {/* Overlay para contraste e alinhamento do gradiente à direita */}
        <div className="absolute inset-0 bg-gradient-to-l from-slate-950 via-slate-950/70 to-transparent" />
        <div className="absolute inset-0 bg-slate-950/20" />
      </div>

      {/* Main Content Container - Balanced Right Alignment */}
      <main className="relative z-10 flex min-h-screen items-center justify-end pr-10 md:pr-24 lg:pr-32">
        <div className="max-w-2xl text-right slide-in-right">
          {/* Top Navigation & Badge */}
          <div className="flex flex-col items-end gap-10 mb-12 slide-in-right">
            <div className="flex gap-6 text-[10px] font-bold uppercase tracking-widest text-slate-500">
              <button onClick={() => navigate('/termos')} className="hover:text-blue-400 transition-colors">Termos</button>
              <button onClick={() => navigate('/privacidade')} className="hover:text-blue-400 transition-colors">Privacidade</button>
            </div>
            
            <div className="px-3 py-1.5 rounded-md glass-card border-blue-500/30 flex items-center gap-2 animate-pulse-slow">
              <div className="w-1 h-1 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]" />
              <span className="text-[9px] font-bold tracking-[0.2em] text-blue-400 uppercase">Inteligência Artificial aplicada ao eSocial</span>
            </div>
          </div>

          <h1 className="text-4xl md:text-5xl font-black mb-6 tracking-tighter slide-in-right" style={{ lineHeight: '1.1' }}>
            <span className="block text-white drop-shadow-2xl">Mensageria</span>
            <span className="block text-gradient filter drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]">eSocial</span>
          </h1>

          <p className="text-sm md:text-base text-slate-300 max-w-lg ml-auto mb-10 font-light leading-relaxed blur-in">
            Conversão, validação e envio das informações ao governo com a ajuda da <span className="text-white font-semibold underline decoration-blue-500/50 decoration-2 underline-offset-4">inteligência artificial</span>. Simplicidade no compliance.
          </p>

          <div className="flex flex-col items-end gap-6 sm:flex-row sm:justify-end">
            <button
              onClick={() => setIsLoginModalOpen(true)}
              className="group relative flex items-center gap-2.5 overflow-hidden rounded-md bg-blue-600 px-6 py-3 text-base font-black text-white transition-all hover:bg-blue-500 active:scale-95 shadow-[0_0_20px_rgba(37,99,235,0.2)]"
            >
              <LogIn className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              Entrar no Sistema
              <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-500 group-hover:translate-x-full" />
            </button>
          </div>

          <div className="mt-12 flex justify-end gap-10 border-t border-white/10 pt-8 text-slate-400">
            <div>
              <div className="text-2xl font-bold text-white">100%</div>
              <div className="text-[11px] uppercase tracking-[0.2em] font-medium text-slate-500">Compliance</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">S-1.3</div>
              <div className="text-[11px] uppercase tracking-[0.2em] font-medium text-slate-500">Versão Oficial</div>
            </div>
          </div>
        </div>
      </main>

      {/* Login Modal (Glassmorphism) */}
      {isLoginModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
          <div 
            className="absolute inset-0 bg-slate-950/70"
            onClick={() => !loading && setIsLoginModalOpen(false)}
          />
          
          <div className="bg-white rounded-md shadow-2xl p-6 md:p-7 w-full max-w-[320px] border border-slate-100 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-cyan-400" />
            
            <div className="text-center mb-5">
              <h2 className="text-xl font-bold text-slate-800">Bem-vindo</h2>
              <p className="text-xs text-slate-500 mt-1">Entre com suas credenciais corporativas</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wider">E-mail Corporativo</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none text-slate-900"
                    placeholder="nome@empresa.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wider">Senha</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none text-slate-900"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-3 rounded-lg bg-red-50 p-5 text-sm text-red-600 border border-red-100 font-bold animate-shake">
                  <AlertCircle className="h-5 w-5 shrink-0" />
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="mt-3 flex w-full items-center justify-center gap-2.5 rounded-md bg-blue-600 py-3.5 text-[14px] font-black text-white transition-all hover:bg-blue-700 active:scale-[0.98] disabled:opacity-50 shadow-xl shadow-blue-500/30"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Autenticando...
                  </>
                ) : (
                  'Entrar no Sistema'
                )}
              </button>
            </form>

            <button
              onClick={() => setIsLoginModalOpen(false)}
              disabled={loading}
              className="mt-8 w-full text-sm font-bold text-slate-400 transition-colors hover:text-slate-900"
            >
              Cancelar e Voltar
            </button>
          </div>
        </div>
      )}

      {/* Footer minimalista */}
      <footer className="absolute bottom-8 left-0 right-0 z-10 px-8 text-slate-500 text-[10px] font-bold uppercase tracking-widest">
        <div className="flex justify-between items-center max-w-7xl mx-auto opacity-60">
          <p>© 2026 Mensageria eSocial IA. Compliance Garantido.</p>
        </div>
      </footer>
    </div>
  );
}
