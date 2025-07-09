import axios from 'axios';
import { Invoice } from '../types/invoice';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Invoice API functions
export const invoiceApi = {
  // Get all invoices
  getAll: async (): Promise<Invoice[]> => {
    const response = await api.get<Invoice[]>('/invoices');
    return response.data;
  },

  // Get invoice by ID
  getById: async (id: string): Promise<Invoice> => {
    const response = await api.get<Invoice>(`/invoices/${id}`);
    return response.data;
  },

  // Create new invoice
  create: async (invoice: Omit<Invoice, 'id' | 'createdAt' | 'updatedAt'>): Promise<Invoice> => {
    const response = await api.post<Invoice>('/invoices', invoice);
    return response.data;
  },

  // Update invoice
  update: async (id: string, invoice: Partial<Invoice>): Promise<Invoice> => {
    const response = await api.put<Invoice>(`/invoices/${id}`, invoice);
    return response.data;
  },

  // Delete invoice
  delete: async (id: string): Promise<void> => {
    await api.delete(`/invoices/${id}`);
  },

  // Generate PDF
  generatePDF: async (id: string): Promise<Blob> => {
    const response = await api.get(`/invoices/${id}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default api;