import { BrowserBouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/ui/Layout';
import Dashboard from './pages/Dashboard';
import Empresas from './pages/Empresas';
import Lotes from './pages/Lotes';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
         <Routes>
            <Route path="/" element={<Layout />}>
               <Route index element={<Dashboard />} />
               <Route path="empresas" element={<Empresas />} />
               <Route path="lotes" element={<Lotes />} />
               <Route path="eventos" element={<div className="p-6 text-gray-500">Rastreamento de eventos em construção.</div>} />
            </Route>
         </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;