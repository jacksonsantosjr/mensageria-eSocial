import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import Empresas from './pages/Empresas';
import Lotes from './pages/Lotes';
import UploadLote from './pages/UploadLote';
import { AlertProvider } from './context/AlertContext';
import { AlertModal } from './components/AlertModal';

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
  return (
    <QueryClientProvider client={queryClient}>
      <AlertProvider>
        <AlertModal />
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<UploadLote />} />
              <Route path="/lotes" element={<Lotes />} />
              <Route path="/configuracoes" element={<Empresas />} />
              
              {/* Fallback para home */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AlertProvider>
    </QueryClientProvider>
  );
}