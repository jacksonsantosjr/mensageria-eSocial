import axios from 'axios';

// A URL base aponta para o backend FastAPI (Hugging Face redireciona via proxy ou porta local)
export const api = axios.create({
  // @ts-ignore
  baseURL: (import.meta as any).env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Configuração para chamadas diretas ao Supabase Auth
const supabaseUrl = (import.meta as any).env.VITE_SUPABASE_URL;
const supabaseAnonKey = (import.meta as any).env.VITE_SUPABASE_ANON_KEY;

export const authApi = axios.create({
  baseURL: `${supabaseUrl}/auth/v1`,
  headers: {
    'apikey': supabaseAnonKey,
    'Authorization': `Bearer ${supabaseAnonKey}`,
    'Content-Type': 'application/json'
  }
});

// Interceptor p/ erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail || error.message;
    console.error('API Error:', detail);
    return Promise.reject(detail);
  }
);

// --- Autenticação (Supabase REST) ---
export const login = async (email: string, password: string) => {
    const response = await authApi.post('/token?grant_type=password', {
        email,
        password
    });
    
    // Salvar o token e dados do usuário
    if (response.data.access_token) {
        localStorage.setItem('esocial_session', JSON.stringify(response.data));
    }
    
    return response.data;
};

export const logout = () => {
    localStorage.removeItem('esocial_session');
};

export const getSession = () => {
    const session = localStorage.getItem('esocial_session');
    return session ? JSON.parse(session) : null;
};

// --- Empresas ---
export const getEmpresas = async () => {
    const response = await api.get('/empresas');
    return response.data;
};

export const createEmpresa = async (data: any) => {
    const response = await api.post('/empresas', data);
    return response.data;
};

export const updateEmpresa = async (id: string, data: any) => {
    const response = await api.put(`/empresas/${id}`, data);
    return response.data;
};

export const deleteEmpresa = async (id: string) => {
    const response = await api.delete(`/empresas/${id}`);
    return response.data;
};

export const uploadLogo = async (id: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/empresas/${id}/logo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

// --- BrasilAPI (Consulta CNPJ) ---
export const getCNPJData = async (cnpj: string) => {
    // Limpar o CNPJ para manter apenas números
    const cleanCnpj = cnpj.replace(/\D/g, '');
    const response = await axios.get(`https://brasilapi.com.br/api/cnpj/v1/${cleanCnpj}`);
    return response.data;
};

// --- Lotes ---
export const getLotes = async () => {
    const response = await api.get('/lotes');
    return response.data;
};

export const getLote = async (id: string) => {
    const response = await api.get(`/lotes/${id}`);
    return response.data;
};

export const createLote = async (file: File, empresaId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/lotes/upload?empresa_id=${empresaId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

export const signLote = async (loteId: string) => {
    const response = await api.post(`/lotes/${loteId}/sign`);
    return response.data;
};

export const sendLote = async (loteId: string) => {
    const response = await api.post(`/lotes/${loteId}/send`);
    return response.data;
};

export const downloadLotePDF = async (id: string, fileName?: string) => {
    const response = await api.get(`/lotes/${id}/pdf`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName || `recibo_lote_${id.substring(0,8)}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
};

export const downloadEventoPDF = async (id: string, fileName?: string) => {
    const response = await api.get(`/eventos/${id}/pdf`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName || `recibo_evento_${id.substring(0,8)}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
};

export const getDashboardResumo = async () => {
    const response = await api.get('/dashboard/resumo');
    return response.data;
};

// --- Configurações ---
export const getSystemConfig = async () => {
    const response = await api.get('/config');
    return response.data;
};

export const updateSystemConfig = async (value: string) => {
    const response = await api.put('/config', { value });
    return response.data;
};