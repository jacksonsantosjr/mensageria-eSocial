import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';

// Stubs for next modules
const Upload = () => <div className="glass-panel p-12 text-center text-slate-400">Página de Upload em Construção. Arraste e solte o Lote XML.</div>;
const LotesList = () => <div className="glass-panel p-12 text-center text-slate-400">Listagem de Eventos e Lotes.</div>;

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/events" element={<LotesList />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}