import axios from 'axios';

export const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const getEmpresas = async () => {
  const res = await api.get('/empresas');
  return res.data;
};

export const createLote = async (file: File, empresaId: string) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await api.post(`/lotes/upload?empresa_id=${empresaId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const getLotes = async () => {
  const res = await api.get('/lotes');
  return res.data;
};

export const getDashboardResumo = async () => {
  const res = await api.get('/dashboard/resumo');
  return res.data;
};