import { useQuery } from '@tanstack/react-query';
import { getDashboardResumo } from '../services/api';

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboardResumo'],
    queryFn: getDashboardResumo
  });

  if (isLoading) return <div className="p-6 text-gray-500">Carregando dashboard..4.</div>;
  if (error) return <div className="p-6 text-red-500">Erro ao carregar dados do backend. Verifique se o FastAPI está rodando na porta 8000.</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
           <p className="text-sm text-gray-500 font-medium">Lotes Processados</p>
           <h3 className="text-3xl font-bold text-gray-800 mt-2">{data?.processados || 0}</h3>
           <p className="text-sm text-green-600 mt-2">Enviados ao gov</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
           <p className="text-sm text-gray-500 font-medium">Lotes Pendentes</p>
           <h3 className="text-3xl font-bold text-orange-600 mt-2">{data?.pendentes || 0}</h3>
           <p className="text-sm text-gray-500 mt-2">Aguardando processamento</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
           <p className="text-sm text-gray-500 font-medium">Erros de Validacção</p>
           <h3 className="text-3xl font-bold text-red-600 mt-2">{data?.com_erro || 0}</h3>
           <p className="text-sm text-gray-500 mt-2">Requer atenção</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
           <p className="text-sm text-gray-500 font-medium">Total de Lotes</p>
           <h3 className="text-,g font-bold text-primary-600 mt-2 truncate">{data?.total || 0} lotes</h3>
           <p className="text-sm text-gray-500 mt-2">Armazenados no sistema</p>
        </div>
      </div>
    </div>
  );
}