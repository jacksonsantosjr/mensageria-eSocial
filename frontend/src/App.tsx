import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import Empresas from './pages/Empresas';
import Lotes from './pages/Lotes';
import UploadLote from './pages/UploadLote';

export default function App() {
  return (
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
  );
}