import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getEmpresas, createEmpresa, updateEmpresa, getCNPJData, uploadLogo } from '../services/api';
import { Plus, Loader2, Building2, ShieldCheck, X, Image as ImageIcon, Camera } from 'lucide-react';
import { useAlert } from '../context/AlertContext';

export default function Empresas() {
  const queryClient = useQueryClient();
  const { showAlert } = useAlert();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isUploadingLogo, setIsUploadingLogo] = useState<string | null>(null);
  
  const logoMutation = useMutation({
    mutationFn: ({ id, file }: { id: string, file: File }) => uploadLogo(id, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['empresas'] });
      showAlert("Logo Atualizado", "O logotipo da empresa foi salvo com sucesso.", "success");
      setIsUploadingLogo(null);
    },
    onError: (err: any) => {
      showAlert("Erro no Upload", `Não foi possível salvar o logo: ${err}`, "error");
      setIsUploadingLogo(null);
    }
  });

  const handleLogoUpload = (empId: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setIsUploadingLogo(empId);
      logoMutation.mutate({ id: empId, file });
    }
  };
  
  // States do Formulário
  const [cnpj, setCnpj] = useState('');
  const [razaoSocial, setRazaoSocial] = useState('');
  const [certificadoBase64, setCertificadoBase64] = useState('');
  const [senhaCertificado, setSenhaCertificado] = useState('');

  const { data: empresas = [], isLoading } = useQuery({
    queryKey: ['empresas'],
    queryFn: getEmpresas
  });

  const mutation = useMutation({
    mutationFn: (data: any) => {
      if (editingId) {
        return updateEmpresa(editingId, data);
      }
      return createEmpresa(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['empresas'] });
      setIsModalOpen(false);
      resetForm();
      const action = editingId ? "Atualizada" : "Cadastrada";
      showAlert(`Empresa ${action}`, `Os dados da empresa foram salvos com sucesso.`, "success");
    },
    onError: (err: any) => showAlert("Erro na Operação", `Não foi possível salvar os dados: ${err}`, "error")
  });

  const resetForm = () => {
    setCnpj('');
    setRazaoSocial('');
    setCertificadoBase64('');
    setSenhaCertificado('');
    setEditingId(null);
  };

  const handleEdit = (emp: any) => {
    setEditingId(emp.id);
    setCnpj(emp.cnpj);
    setRazaoSocial(emp.razao_social);
    setCertificadoBase64(''); // Resetar p/ não mostrar base64 longo
    setSenhaCertificado('');
    setIsModalOpen(true);
  };

  const handleCnpjBlur = async () => {
    if (editingId) return; // Não buscar se estiver editando
    const cleanCnpj = cnpj.replace(/\D/g, '');
    if (cleanCnpj.length !== 14) return;

    setIsSearching(true);
    try {
      const data = await getCNPJData(cleanCnpj);
      setRazaoSocial(data.razao_social || data.nome_fantasia);
    } catch (err) {
      console.error('Falha ao buscar CNPJ', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64 = event.target?.result as string;
        // Remover o prefixo data:application/x-pkcs12;base64,
        setCertificadoBase64(base64.split(',')[1]);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: any = {
      cnpj: cnpj.replace(/\D/g, ''),
      razao_social: razaoSocial,
      ativo: true
    };

    // Se houver novo certificado, envia. Senão, mantém o que já está no banco.
    if (certificadoBase64) {
      payload.cert_base64 = certificadoBase64;
      payload.cert_password = senhaCertificado;
    }

    mutation.mutate(payload);
  };

  return (
    <div className="space-y-6">
      <div className="glass-card overflow-hidden">
        <div className="p-6 border-b border-glass-border flex justify-between items-center bg-black/5">
           <div>
              <h3 className="text-lg font-bold text-app-text">Gerenciar Empresas</h3>
              <p className="text-sm text-app-text/60">Cadastre os transmissores autorizados para envio do eSocial.</p>
           </div>
           <button 
             onClick={() => { resetForm(); setIsModalOpen(true); }}
             className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center shadow-lg shadow-primary-500/20 transition-all active:scale-95 font-bold"
           >
             <Plus className="w-4 h-4 mr-2" />
             Nova Empresa
           </button>
        </div>
        
        {isLoading ? (
          <div className="p-12 flex flex-col items-center">
            <Loader2 className="w-10 h-10 text-primary-500 animate-spin mb-2" />
            <p className="text-gray-400 font-medium">Carregando empresas...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-black/20 text-app-text/60 text-[10px] uppercase font-black tracking-widest">
                <tr>
                  <th className="px-6 py-4">Razão Social / CNPJ</th>
                  <th className="px-6 py-4">Certificado</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-glass-border">
                {empresas.length === 0 && (
                   <tr><td colSpan={4} className="px-6 py-12 text-center text-app-text/40 font-medium italic">Nenhuma empresa cadastrada. Clique em "Nova Empresa" para começar.</td></tr>
                )}
                {Array.isArray(empresas) && empresas.map((emp: any) => (
                  <tr key={emp.id} className="hover:bg-black/5 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="relative group p-0.5 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-xl">
                          <label className="cursor-pointer block">
                            <div className="w-12 h-12 rounded-[10px] overflow-hidden bg-black/40 flex items-center justify-center relative">
                              {isUploadingLogo === emp.id ? (
                                <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
                              ) : emp.logo_url ? (
                                <img src={emp.logo_url} alt="Logo" className="w-full h-full object-cover transition-transform group-hover:scale-110" />
                              ) : (
                                <Building2 className="w-6 h-6 text-app-text/30 group-hover:opacity-0 transition-opacity" />
                              )}
                              
                              <div className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                <Camera className="w-5 h-5 text-white" />
                              </div>
                            </div>
                            <input 
                              type="file" 
                              className="hidden" 
                              accept="image/*"
                              onChange={(e) => handleLogoUpload(emp.id, e)}
                            />
                          </label>
                        </div>
                        <div>
                          <p className="font-bold text-app-text">{emp.razao_social}</p>
                          <p className="text-xs text-app-text/40 font-mono">{emp.cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5")}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {emp.certificado_a1 ? (
                        <div className="flex items-center text-emerald-500 text-sm font-semibold">
                          <ShieldCheck className="w-4 h-4 mr-1" />
                          Configurado
                        </div>
                      ) : (
                        <span className="text-app-text/40 text-sm">Sem Certificado</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-lg text-[10px] uppercase font-black tracking-tight ${emp.ativo ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-red-500/10 text-red-500 border border-red-500/20'}`}>
                        {emp.ativo ? 'ATIVO' : 'INATIVO'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                       <button 
                        onClick={() => handleEdit(emp)}
                        className="text-sm text-app-text/40 hover:text-primary-500 font-bold transition"
                       >
                        Editar
                       </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal de Cadastro/Edição */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
          <div className="glass-card w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="p-6 border-b border-glass-border flex justify-between items-center bg-black/5">
              <h2 className="text-xl font-bold text-app-text">
                {editingId ? 'Editar Transmissora' : 'Cadastrar Nova Transmissora'}
              </h2>
              <button onClick={() => setIsModalOpen(false)} className="text-app-text/40 hover:text-app-text transition">
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-bold text-app-text/60 mb-1">CNPJ da Empresa</label>
                <div className="relative">
                  <input 
                    type="text" 
                    required 
                    readOnly={!!editingId}
                    placeholder="00.000.000/0000-00"
                    className={`w-full p-3 border border-glass-border rounded-lg outline-none font-medium transition ${editingId ? 'bg-black/20 text-app-text/40 cursor-not-allowed' : 'bg-black/5 text-app-text focus:ring-2 focus:ring-primary-500'}`}
                    value={cnpj}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCnpj(e.target.value)}
                    onBlur={handleCnpjBlur}
                  />
                  {isSearching && <Loader2 className="w-5 h-5 animate-spin text-primary-500 absolute right-3 top-3" />}
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-app-text/60 mb-1">Razão Social</label>
                <input 
                  type="text" 
                  required 
                  className="w-full p-3 border border-glass-border rounded-lg bg-black/10 outline-none font-semibold text-app-text"
                  value={razaoSocial}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setRazaoSocial(e.target.value)}
                  placeholder="Preenchido automaticamente..."
                />
              </div>

              <div className="pt-2">
                <label className="block text-sm font-bold text-app-text/60 mb-1">Certificado Digital A1 (.pfx)</label>
                <div className="flex items-center space-x-2">
                   <input 
                    type="file" 
                    accept=".pfx,.p12"
                    onChange={handleFileChange}
                    className="flex-1 text-sm text-app-text/40 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-500/10 file:text-primary-500 hover:file:bg-primary-500/20 transition cursor-pointer"
                  />
                </div>
                <p className="text-[10px] text-app-text/30 mt-1 uppercase font-black tracking-widest">Apenas arquivos .pfx ou .p12</p>
              </div>

              <div>
                <label className="block text-sm font-bold text-app-text/60 mb-1">Senha do Certificado</label>
                <input 
                  type="password" 
                  className="w-full p-3 border border-glass-border rounded-lg outline-none focus:ring-2 focus:ring-primary-500 bg-black/5 font-medium text-app-text transition"
                  value={senhaCertificado}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSenhaCertificado(e.target.value)}
                  placeholder="Obrigatória para assinatura automática"
                />
              </div>

              <div className="pt-4 flex space-x-3">
                <button 
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 px-4 py-3 border border-glass-border rounded-lg text-app-text/60 font-semibold hover:bg-black/5 transition active:scale-95"
                >
                  Cancelar
                </button>
                <button 
                  type="submit"
                  disabled={mutation.isPending}
                  className="flex-1 px-4 py-3 bg-primary-600 text-white rounded-lg font-bold shadow-lg shadow-primary-500/20 hover:bg-primary-700 transition-all flex items-center justify-center active:scale-95 disabled:bg-gray-400"
                >
                  {mutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Salvar Empresa'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}