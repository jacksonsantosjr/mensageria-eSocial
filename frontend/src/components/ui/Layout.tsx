import { Link, Outlet, useLocation } from 'react-router-dom';
import { Home, Building2, FileJson, Activity, LogOut } from 'lucide-react';

export default function Layout() {
  const loc = useLocation();
  const menu = [
    { name: 'Dashboard', icon: Home, path: '/' },
    { name: 'Empresas', icon: Building2, path: '/empresas' },
    { name: 'Consultas XML', icon: FileJson, path: '/lotes' },
    { name: 'Eventos', icon: Activity, path: '/eventos' },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-primary-900 text-white flex flex-col">
        <div className="p-4 bg-primary-800 text-center font-bold text-xl border-b border-primary-700">
          eSocial Mensageria
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {menu.map((item) => (
            <Link key={item.path} to={item.path} className={`flex items-center space-x-3 p-3 rounded-lg hover:bg-primary-700 transition ${loc.pathname === item.path ? 'bg-primary-800 border-l-4 border-primary-400' : ''}`}>
               <item.icon className="w-5 h-5" />
               <span>{item.name}</span>
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-primary-800">
           <button className="flex items-center space-x-3 text-red-300 hover:text-red-100 transition p-2 w-full roudend-lg">
             <LogOut className="w-5 h-5" /> <span>Sair</span>
           </button>
        </div>
      </aside>
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b flex items-center justify-between px-6 shadow-sm">
           <h2 className="text-xl font-semibold text-gray-800">{menu.find(m => m.path === loc.pathname)?.name || 'Aplicação'}</h2>
           <div className="flex items-center space-x-4">
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded-full border border-yellow-200">
                MOCK ENABLED
              </span>
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold border border-primary-300">
                AD
              </div>
           </div>
        </header>
        <div className="flex-1 overflow-auto p-6 bg-gray-50/50">
          <Outlet />
        </div>
      </main>
    </div>
  );
}