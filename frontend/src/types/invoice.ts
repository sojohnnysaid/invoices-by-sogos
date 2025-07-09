export interface InvoiceParty {
  name: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  email?: string;
  phone?: string;
}

export interface LineItem {
  id?: string;
  description: string;
  quantity: number;
  unitPrice: number;
  amount: number;
}

export interface Invoice {
  id?: string;
  invoiceNumber: string;
  issueDate: string;
  dueDate: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  from: InvoiceParty;
  to: InvoiceParty;
  lineItems: LineItem[];
  subtotal: number;
  tax: number;
  taxRate: number;
  total: number;
  notes?: string;
  terms?: string;
  createdAt?: string;
  updatedAt?: string;
}