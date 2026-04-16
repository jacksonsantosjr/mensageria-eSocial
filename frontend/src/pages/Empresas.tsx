import { useQuery } from '@tanstack/react-query';
import { getEmpresas } from '../services/api';
import { Plus, Loader2 } from 'lucide-react';

export default function Empresas() {
  const { data: empresas = [], isLoading } = useQuery({
    queryKey: ['empresas'],
    queryFn: getEmpresas
  });
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200 flex justify-between items-center bg-white">
         <h3 className="text-lg font-semibold text-gray-800">Gerenciar Empresas</h3>
         <button className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center shadow-sm transition">
           <Plus className="w-4 h-4 mr-2" />
           Nova Empresa
         </button>
      </div>
      {isLoading ? (
        <div className="p-12 flex justify-center"><Loader2 className="w-8 h-8 text-primary-500 animate-spin" /></div>
      ) : (
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 text-gray-600 text-sm border-b">
              <th className="p-4 font-medium">ID (UUID)</th>
              <th className="p-4 font-medium">Razão Social</th>
              <th className="p-4 font-medium">CNPJ</th>
              <th className="p-4 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {empresas.length === 0 && (
               <tr><td colSpan={4} className="p-6 text-center text-gray-500">Nenhuma empresa encontrada via API.</td></tr>
            )}
            {empresas.map((emp: any) => (
              <tr key={emp.id} className="hover:bg-gray-50 transition">
                <td className="p-4 text-xs text-gray-500 font-mono truncate max-w-[100px]">{emp.id}</td>
                <td className="p-4 font-semibold text-gray-800">{emp.razao_social}</td>
                <td className="p-4 text-gray-600">{emp.cnpj}</td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${emp.ativo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {emp.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}