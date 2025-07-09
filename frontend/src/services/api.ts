import axios from 'axios';
import { Invoice, InvoiceParty } from '../types/invoice';

// Use proxy in development, environment variable in production
const API_URL = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || '/api');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Transform frontend invoice to backend format
const toBackendFormat = (invoice: Partial<Invoice>) => {
  // Remove undefined values and provide defaults
  const transformed: any = {};
  
  // Required fields
  if (invoice.invoiceNumber !== undefined) transformed.invoice_number = invoice.invoiceNumber;
  if (invoice.issueDate !== undefined) {
    // Ensure date is in ISO format with time
    // If already contains 'T', it's already in ISO format
    const dateStr = invoice.issueDate.includes('T') ? invoice.issueDate : invoice.issueDate + 'T00:00:00';
    const date = new Date(dateStr);
    transformed.date = date.toISOString();
  }
  if (invoice.dueDate !== undefined) {
    // Ensure date is in ISO format with time
    // If already contains 'T', it's already in ISO format
    const dateStr = invoice.dueDate.includes('T') ? invoice.dueDate : invoice.dueDate + 'T00:00:00';
    const dueDate = new Date(dateStr);
    transformed.due_date = dueDate.toISOString();
  }
  if (invoice.status !== undefined) transformed.status = invoice.status;
  if (invoice.currency !== undefined) transformed.currency = invoice.currency;
  
  // Optional fields with defaults
  if (invoice.paymentTerms !== undefined) transformed.payment_terms = invoice.paymentTerms;
  if (invoice.subtotal !== undefined) transformed.subtotal = invoice.subtotal;
  if (invoice.taxRate !== undefined) transformed.tax_rate = invoice.taxRate;
  if (invoice.tax !== undefined) transformed.tax_amount = invoice.tax;
  if (invoice.discount !== undefined) transformed.discount_amount = invoice.discount;
  if (invoice.shipping !== undefined) transformed.shipping_amount = invoice.shipping;
  if (invoice.total !== undefined) transformed.total = invoice.total;
  if (invoice.amountPaid !== undefined) transformed.amount_paid = invoice.amountPaid;
  if (invoice.balanceDue !== undefined) transformed.balance_due = invoice.balanceDue;
  if (invoice.notes !== undefined) transformed.notes = invoice.notes;
  if (invoice.terms !== undefined) transformed.terms = invoice.terms;

  // Transform parties - only include if they have a name
  transformed.parties = [];
  if (invoice.from && invoice.from.name) {
    transformed.parties.push({
      party_type: 'from',
      ...toBackendParty(invoice.from),
    });
  }
  if (invoice.to && invoice.to.name) {
    transformed.parties.push({
      party_type: 'to',
      ...toBackendParty(invoice.to),
    });
  }
  if (invoice.shipTo && invoice.shipTo.name) {
    transformed.parties.push({
      party_type: 'ship_to',
      ...toBackendParty(invoice.shipTo),
    });
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
  const toParty = parties.find((p: any) => p.party_type === 'to');
  const shipToParty = parties.find((p: any) => p.party_type === 'ship_to');

  return {
    id: data.id,
    invoiceNumber: data.invoice_number,
    issueDate: data.date ? data.date.split('T')[0] : '',
    dueDate: data.due_date ? data.due_date.split('T')[0] : '',
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