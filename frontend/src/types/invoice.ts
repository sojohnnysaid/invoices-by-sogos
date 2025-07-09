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
  paymentTerms?: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  currency: string;
  from: InvoiceParty;
  to: InvoiceParty;
  shipTo?: InvoiceParty;
  lineItems: LineItem[];
  subtotal: number;
  tax: number;
  taxRate: number;
  discount: number;
  shipping: number;
  total: number;
  amountPaid: number;
  balanceDue: number;
  notes?: string;
  terms?: string;
  createdAt?: string;
  updatedAt?: string;
}