import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { format } from 'date-fns';
import { invoiceApi } from '../services/api';
import { Invoice, LineItem, InvoiceParty } from '../types/invoice';
import InvoiceHeader from '../components/InvoiceHeader';
import PartyDetails from '../components/PartyDetails';
import DatePicker from '../components/DatePicker';
import LineItemsTable from '../components/LineItemsTable';
import InvoiceTotals from '../components/InvoiceTotals';

function InvoiceForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = !!id;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [invoice, setInvoice] = useState<Omit<Invoice, 'id' | 'createdAt' | 'updatedAt'>>({
    invoiceNumber: '1',
    issueDate: format(new Date(), 'yyyy-MM-dd'),
    dueDate: format(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd'),
    paymentTerms: 'Net 30',
    status: 'draft',
    currency: 'USD',
    from: {
      name: 'John Yzaguirre',
      address: '',
      city: '',
      state: '',
      zipCode: '',
      country: '',
      email: '',
      phone: '',
    },
    to: {
      name: '',
      address: '',
      city: '',
      state: '',
      zipCode: '',
      country: '',
      email: '',
      phone: '',
    },
    shipTo: {
      name: '',
      address: '',
      city: '',
      state: '',
      zipCode: '',
      country: '',
      email: '',
      phone: '',
    },
    lineItems: [],
    subtotal: 0,
    tax: 0,
    taxRate: 0,
    discount: 0,
    shipping: 0,
    total: 0,
    amountPaid: 0,
    balanceDue: 0,
    notes: '',
    terms: '',
  });

  useEffect(() => {
    if (isEdit && id) {
      fetchInvoice(id);
    }
  }, [id, isEdit]);

  useEffect(() => {
    calculateTotals();
  }, [invoice.lineItems, invoice.taxRate, invoice.discount, invoice.shipping, invoice.amountPaid]);

  const fetchInvoice = async (invoiceId: string) => {
    try {
      setLoading(true);
      const data = await invoiceApi.getById(invoiceId);
      setInvoice(data);
    } catch (err) {
      setError('Failed to fetch invoice');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const calculateTotals = () => {
    const subtotal = invoice.lineItems.reduce((sum, item) => sum + item.amount, 0);
    const tax = subtotal * (invoice.taxRate / 100);
    const total = subtotal + tax - invoice.discount + invoice.shipping;
    const balanceDue = total - invoice.amountPaid;

    setInvoice(prev => ({
      ...prev,
      subtotal,
      tax,
      total,
      balanceDue,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      if (isEdit && id) {
        await invoiceApi.update(id, invoice);
      } else {
        await invoiceApi.create(invoice);
      }
      navigate('/');
    } catch (err) {
      setError('Failed to save invoice');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const updateParty = (party: 'from' | 'to' | 'shipTo', field: keyof InvoiceParty, value: string) => {
    setInvoice(prev => ({
      ...prev,
      [party]: party === 'shipTo' ? {
        ...prev.shipTo!,
        [field]: value,
      } : {
        ...prev[party],
        [field]: value,
      },
    }));
  };

  const addLineItem = () => {
    setInvoice(prev => ({
      ...prev,
      lineItems: [
        ...prev.lineItems,
        {
          description: '',
          quantity: 1,
          unitPrice: 0,
          amount: 0,
        },
      ],
    }));
  };

  const updateLineItem = (index: number, field: keyof LineItem, value: string | number) => {
    setInvoice(prev => {
      const newLineItems = [...prev.lineItems];
      newLineItems[index] = {
        ...newLineItems[index],
        [field]: value,
      };

      // Calculate amount if quantity or unitPrice changed
      if (field === 'quantity' || field === 'unitPrice') {
        newLineItems[index].amount = 
          newLineItems[index].quantity * newLineItems[index].unitPrice;
      }

      return {
        ...prev,
        lineItems: newLineItems,
      };
    });
  };

  const removeLineItem = (index: number) => {
    setInvoice(prev => ({
      ...prev,
      lineItems: prev.lineItems.filter((_, i) => i !== index),
    }));
  };

  const getCurrencySymbol = (currency: string) => {
    const symbols: { [key: string]: string } = {
      USD: '$',
      EUR: '€',
      GBP: '£',
      CAD: 'C$',
      AUD: 'A$',
      JPY: '¥',
      CNY: '¥',
      INR: '₹',
    };
    return symbols[currency] || '$';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-8 bg-white">
      <form onSubmit={handleSubmit}>
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Header Section */}
        <InvoiceHeader
          invoiceNumber={invoice.invoiceNumber}
          currency={invoice.currency}
          onInvoiceNumberChange={(value) => setInvoice({ ...invoice, invoiceNumber: value })}
          onCurrencyChange={(value) => setInvoice({ ...invoice, currency: value })}
        />

        {/* Bill To and Ship To Section */}
        <div className="grid grid-cols-2 gap-8 mt-8">
          <PartyDetails
            title="Bill To"
            party={invoice.to}
            onChange={(field, value) => updateParty('to', field, value)}
            showEmail={true}
          />
          <PartyDetails
            title="Ship To"
            party={invoice.shipTo!}
            onChange={(field, value) => updateParty('shipTo', field, value)}
            compact={true}
          />
        </div>

        {/* Dates and Payment Terms */}
        <div className="grid grid-cols-4 gap-4 mt-8">
          <DatePicker
            label="Date"
            value={invoice.issueDate}
            onChange={(value) => setInvoice({ ...invoice, issueDate: value })}
          />
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">Payment Terms</label>
            <select
              value={invoice.paymentTerms}
              onChange={(e) => setInvoice({ ...invoice, paymentTerms: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="Net 30">Net 30</option>
              <option value="Net 15">Net 15</option>
              <option value="Net 60">Net 60</option>
              <option value="Due on Receipt">Due on Receipt</option>
              <option value="EOM">EOM</option>
            </select>
          </div>
          <DatePicker
            label="Due Date"
            value={invoice.dueDate}
            onChange={(value) => setInvoice({ ...invoice, dueDate: value })}
          />
          <div className="flex items-end">
            <button
              type="button"
              className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              Save as Default
            </button>
          </div>
        </div>

        {/* Line Items */}
        <div className="mt-8">
          <LineItemsTable
            items={invoice.lineItems}
            onUpdateItem={updateLineItem}
            onRemoveItem={removeLineItem}
            onAddItem={addLineItem}
            currencySymbol={getCurrencySymbol(invoice.currency)}
          />
        </div>

        {/* Notes and Terms with Totals */}
        <div className="grid grid-cols-2 gap-8 mt-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
              <textarea
                value={invoice.notes}
                onChange={(e) => setInvoice({ ...invoice, notes: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Notes - any relevant information not already covered"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Terms</label>
              <textarea
                value={invoice.terms}
                onChange={(e) => setInvoice({ ...invoice, terms: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Terms and conditions - late fees, payment methods, delivery schedule"
              />
            </div>
          </div>

          <div className="bg-gray-50 p-6 rounded-lg">
            <InvoiceTotals
              subtotal={invoice.subtotal}
              taxRate={invoice.taxRate}
              tax={invoice.tax}
              discount={invoice.discount}
              shipping={invoice.shipping}
              total={invoice.total}
              amountPaid={invoice.amountPaid}
              balanceDue={invoice.balanceDue}
              onTaxRateChange={(value) => setInvoice({ ...invoice, taxRate: value })}
              onDiscountChange={(value) => setInvoice({ ...invoice, discount: value })}
              onShippingChange={(value) => setInvoice({ ...invoice, shipping: value })}
              onAmountPaidChange={(value) => setInvoice({ ...invoice, amountPaid: value })}
              currencySymbol={getCurrencySymbol(invoice.currency)}
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center mt-8">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-4 py-2 text-gray-600 hover:text-gray-700"
          >
            Cancel
          </button>
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              {loading ? 'Saving...' : (isEdit ? 'Update' : 'Save Draft')}
            </button>
            <button
              type="button"
              className="px-6 py-3 bg-green-500 text-white rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 font-medium"
            >
              Download
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

export default InvoiceForm;