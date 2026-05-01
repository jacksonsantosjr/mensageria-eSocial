import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import Empresas from './pages/Empresas';
import Lotes from './pages/Lotes';
import UploadLote from './pages/UploadLote';
import Configuracoes from './pages/Configuracoes';
import LandingPage from './pages/LandingPage';
import Terms from './pages/Terms';
import Privacy from './pages/Privacy';
import { AlertProvider } from './context/AlertContext';
import { AlertModal } from './components/AlertModal';
import { getSession } from './services/api';

// Inicializa o motor de busca de dados
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  const session = getSession();

  return (
    <QueryClientProvider client={queryClient}>
      <AlertProvider>
        <AlertModal />
        <BrowserRouter>
          <Routes>
            {/* Rota de Login (Pública) */}
            <Route path="/login" element={!session ? <LandingPage /> : <Navigate to="/" replace />} />
            <Route path="/termos" element={<Terms />} />
            <Route path="/privacidade" element={<Privacy />} />
            
            {/* Rotas Protegidas */}
            <Route element={session ? <Layout /> : <Navigate to="/login" replace />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<UploadLote />} />
              <Route path="/lotes" element={<Lotes />} />
              <Route path="/empresas" element={<Empresas />} />
              <Route path="/configuracoes" element={<Configuracoes />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AlertProvider>
    </QueryClientProvider>
  );
}