import { useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileUp, Activity, Inbox, ShieldAlert, Sun, Moon, Settings } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getSystemConfig } from '../services/api';
import { clsx } from 'clsx';
import { useESocialNotifications } from '../hooks/useESocialNotifications';
import { ToastContainer } from './ToastContainer';

export function Layout() {
  const location = useLocation();
  const [isDark, setIsDark] = useState(true);
  
  // Ativa o observador de notificações global
  useESocialNotifications();

  const { data: config } = useQuery({
    queryKey: ['systemConfig'],
    queryFn: getSystemConfig,
    refetchInterval: 15000 // Verifica troca de ambiente a cada 15s
  });

  const isProd = config?.value === 'PRODUCTION';

  // Inicializa o modo dark no root html (garante comportamento correto on load)
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Empresas', path: '/empresas', icon: ShieldAlert },
    { name: 'Upload Lote', path: '/upload', icon: FileUp },
    { name: 'Meus Lotes', path: '/lotes', icon: Inbox },
    { name: 'Configurações', path: '/configuracoes', icon: Settings },
  ];

  return (
    <div className="flex h-screen overflow-hidden text-slate-200 transition-colors duration-300">
      
      {/* Sidebar - Premium Glass */}
      <aside className="w-64 glass-panel border-r-0 border-y-0 rounded-r-lg m-2 my-4 ml-4 flex flex-col relative z-20">
        <div className="p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-neon-blue">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gradient leading-tight tracking-tight">eSocial</h1>
              <p className="text-xs text-slate-400 font-medium tracking-widest uppercase">Mensageria</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2 relative">
          {navItems.map((item: any) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            
            return (
              <NavLink 
                key={item.path} 
                to={item.path}
                className={({ isActive }) => clsx(
                  "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-300",
                  isActive 
                    ? "bg-blue-500/10 text-cyan-300 border border-blue-500/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]" 
                    : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
                )}
              >
                <Icon className={clsx("w-5 h-5 transition-transform duration-300", isActive && "scale-110 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]")} />
                {item.name}
              </NavLink>
            );
          })}
        </nav>

        {/* System Status / Network Indicator */}
        <div className="p-4 m-4 rounded-lg bg-black/20 border border-white/5 backdrop-blur-sm">
          <div className="flex items-center gap-2 mb-2">
            <ShieldAlert className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-medium text-slate-300">Ambiente de Transmissão</span>
          </div>
          <div className={clsx(
            "flex items-center justify-center py-1.5 px-3 rounded text-xs font-bold tracking-widest shadow-inner",
            isProd 
              ? "bg-red-500/20 text-red-400 border border-red-500/30 shadow-[0_0_8px_rgba(239,68,68,0.2)]" 
              : "bg-amber-500/10 text-amber-500 border border-amber-500/20 shadow-[0_0_8px_rgba(245,158,11,0.2)]"
          )}>
            {isProd ? 'PRODUÇÃO SERPRO' : 'HOMOLOGAÇÃO'}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <div className="absolute top-[-10%] sm:right-[-10%] w-[500px] h-[500px] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none transition-opacity duration-300" />
        
        <header className="h-20 flex items-center justify-between px-8 z-10 glass-panel border-x-0 border-t-0 rounded-b-lg mx-4 shadow-sm">
          <h2 className="text-xl font-medium text-white tracking-wide">
            {navItems.find((i: any) => i.path === location.pathname)?.name || 'Monitor'}
          </h2>
          <div className="flex items-center">
            
            {/* Theme Toggle Button */}
            <button 
              onClick={toggleTheme}
              className="relative p-2 rounded-full glass-card hover:scale-110 transition-transform flex items-center justify-center group"
              title="Alternar Tema Escuro/Claro"
            >
              {isDark ? (
                 <Sun className="w-5 h-5 text-amber-300 group-hover:text-amber-400 drop-shadow-[0_0_8px_rgba(252,211,77,0.8)]" />
              ) : (
                 <Moon className="w-5 h-5 text-indigo-500 group-hover:text-indigo-600" />
              )}
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8 z-10 custom-scrollbar">
          <Outlet />
        </div>
      </main>
      
      <ToastContainer />
    </div>
  );
}
