import axios from 'axios';
import { Invoice, InvoiceParty, LineItem } from '../types/invoice';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Transform frontend invoice to backend format
const toBackendFormat = (invoice: Partial<Invoice>) => {
  const transformed: any = {
    invoice_number: invoice.invoiceNumber,
    date: invoice.issueDate,
    due_date: invoice.dueDate,
    payment_terms: invoice.paymentTerms,
    status: invoice.status,
    currency: invoice.currency,
    subtotal: invoice.subtotal,
    tax_rate: invoice.taxRate,
    tax_amount: invoice.tax,
    discount_amount: invoice.discount,
    shipping_amount: invoice.shipping,
    total: invoice.total,
    amount_paid: invoice.amountPaid,
    balance_due: invoice.balanceDue,
    notes: invoice.notes,
    terms: invoice.terms,
  };

  // Transform parties
  if (invoice.from || invoice.to || invoice.shipTo) {
    transformed.parties = [];
    if (invoice.from) {
      transformed.parties.push({
        party_type: 'from',
        ...toBackendParty(invoice.from),
      });
    }
    if (invoice.to) {
      transformed.parties.push({
        party_type: 'bill_to',
        ...toBackendParty(invoice.to),
      });
    }
    if (invoice.shipTo) {
      transformed.parties.push({
        party_type: 'ship_to',
        ...toBackendParty(invoice.shipTo),
      });
    }
  }

  // Transform line items
  if (invoice.lineItems) {
    transformed.line_items = invoice.lineItems.map((item, index) => ({
      description: item.description,
      quantity: item.quantity,
      rate: item.unitPrice,
      amount: item.amount,
      position: index,
    }));
  }

  return transformed;
};

// Transform backend party to frontend format
const toFrontendParty = (party: any): InvoiceParty => ({
  name: party.name || '',
  address: party.address || '',
  city: party.city || '',
  state: party.state || '',
  zipCode: party.zip_code || '',
  country: party.country || '',
  email: party.email,
  phone: party.phone,
});

// Transform backend party to backend format
const toBackendParty = (party: InvoiceParty) => ({
  name: party.name,
  address: party.address,
  city: party.city,
  state: party.state,
  zip_code: party.zipCode,
  country: party.country,
  email: party.email,
  phone: party.phone,
});

// Transform backend invoice to frontend format
const toFrontendFormat = (data: any): Invoice => {
  const parties = data.parties || [];
  const fromParty = parties.find((p: any) => p.party_type === 'from');
  const toParty = parties.find((p: any) => p.party_type === 'bill_to');
  const shipToParty = parties.find((p: any) => p.party_type === 'ship_to');

  return {
    id: data.id,
    invoiceNumber: data.invoice_number,
    issueDate: data.date,
    dueDate: data.due_date,
    paymentTerms: data.payment_terms,
    status: data.status,
    currency: data.currency,
    from: fromParty ? toFrontendParty(fromParty) : {
      name: '',
      address: '',
      city: '',
      state: '',
      zipCode: '',
      country: '',
    },
    to: toParty ? toFrontendParty(toParty) : {
      name: '',
      address: '',
      city: '',
      state: '',
      zipCode: '',
      country: '',
    },
    shipTo: shipToParty ? toFrontendParty(shipToParty) : undefined,
    lineItems: (data.line_items || []).map((item: any) => ({
      id: item.id,
      description: item.description,
      quantity: item.quantity,
      unitPrice: item.rate,
      amount: item.amount,
    })),
    subtotal: data.subtotal || 0,
    tax: data.tax_amount || 0,
    taxRate: data.tax_rate || 0,
    discount: data.discount_amount || 0,
    shipping: data.shipping_amount || 0,
    total: data.total || 0,
    amountPaid: data.amount_paid || 0,
    balanceDue: data.balance_due || 0,
    notes: data.notes,
    terms: data.terms,
    createdAt: data.created_at,
    updatedAt: data.updated_at,
  };
};

// Invoice API functions
export const invoiceApi = {
  // Get all invoices
  getAll: async (): Promise<Invoice[]> => {
    const response = await api.get('/invoices/');
    return response.data.map(toFrontendFormat);
  },

  // Get invoice by ID
  getById: async (id: string): Promise<Invoice> => {
    const response = await api.get(`/invoices/${id}`);
    return toFrontendFormat(response.data);
  },

  // Create new invoice
  create: async (invoice: Omit<Invoice, 'id' | 'createdAt' | 'updatedAt'>): Promise<Invoice> => {
    const backendData = toBackendFormat(invoice);
    const response = await api.post('/invoices/', backendData);
    return toFrontendFormat(response.data);
  },

  // Update invoice
  update: async (id: string, invoice: Partial<Invoice>): Promise<Invoice> => {
    const backendData = toBackendFormat(invoice);
    const response = await api.put(`/invoices/${id}`, backendData);
    return toFrontendFormat(response.data);
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