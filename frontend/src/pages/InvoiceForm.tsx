import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { format } from 'date-fns';
import { invoiceApi } from '../services/api';
import { Invoice, LineItem, InvoiceParty } from '../types/invoice';

function InvoiceForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = !!id;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [invoice, setInvoice] = useState<Omit<Invoice, 'id' | 'createdAt' | 'updatedAt'>>({
    invoiceNumber: '',
    issueDate: format(new Date(), 'yyyy-MM-dd'),
    dueDate: format(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd'),
    status: 'draft',
    from: {
      name: '',
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
    lineItems: [],
    subtotal: 0,
    tax: 0,
    taxRate: 0,
    total: 0,
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
  }, [invoice.lineItems, invoice.taxRate]);

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
    const total = subtotal + tax;

    setInvoice(prev => ({
      ...prev,
      subtotal,
      tax,
      total,
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

  const updateParty = (party: 'from' | 'to', field: keyof InvoiceParty, value: string) => {
    setInvoice(prev => ({
      ...prev,
      [party]: {
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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8 divide-y divide-gray-200">
      <div className="space-y-8 divide-y divide-gray-200">
        <div>
          <h3 className="text-lg font-medium leading-6 text-gray-900">
            {isEdit ? 'Edit Invoice' : 'New Invoice'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Fill in the invoice details below.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Invoice Details */}
        <div className="pt-8">
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-2">
              <label htmlFor="invoiceNumber" className="block text-sm font-medium text-gray-700">
                Invoice Number
              </label>
              <input
                type="text"
                name="invoiceNumber"
                id="invoiceNumber"
                value={invoice.invoiceNumber}
                onChange={(e) => setInvoice({ ...invoice, invoiceNumber: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="issueDate" className="block text-sm font-medium text-gray-700">
                Issue Date
              </label>
              <input
                type="date"
                name="issueDate"
                id="issueDate"
                value={invoice.issueDate}
                onChange={(e) => setInvoice({ ...invoice, issueDate: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700">
                Due Date
              </label>
              <input
                type="date"
                name="dueDate"
                id="dueDate"
                value={invoice.dueDate}
                onChange={(e) => setInvoice({ ...invoice, dueDate: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>
          </div>
        </div>

        {/* From Section */}
        <div className="pt-8">
          <h4 className="text-md font-medium text-gray-900 mb-4">From</h4>
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <label htmlFor="from-name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <input
                type="text"
                id="from-name"
                value={invoice.from.name}
                onChange={(e) => updateParty('from', 'name', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="from-email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                id="from-email"
                value={invoice.from.email}
                onChange={(e) => updateParty('from', 'email', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div className="sm:col-span-6">
              <label htmlFor="from-address" className="block text-sm font-medium text-gray-700">
                Address
              </label>
              <input
                type="text"
                id="from-address"
                value={invoice.from.address}
                onChange={(e) => updateParty('from', 'address', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="from-city" className="block text-sm font-medium text-gray-700">
                City
              </label>
              <input
                type="text"
                id="from-city"
                value={invoice.from.city}
                onChange={(e) => updateParty('from', 'city', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="from-state" className="block text-sm font-medium text-gray-700">
                State
              </label>
              <input
                type="text"
                id="from-state"
                value={invoice.from.state}
                onChange={(e) => updateParty('from', 'state', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="from-zipCode" className="block text-sm font-medium text-gray-700">
                ZIP Code
              </label>
              <input
                type="text"
                id="from-zipCode"
                value={invoice.from.zipCode}
                onChange={(e) => updateParty('from', 'zipCode', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>
          </div>
        </div>

        {/* To Section */}
        <div className="pt-8">
          <h4 className="text-md font-medium text-gray-900 mb-4">To</h4>
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <label htmlFor="to-name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <input
                type="text"
                id="to-name"
                value={invoice.to.name}
                onChange={(e) => updateParty('to', 'name', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="to-email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                id="to-email"
                value={invoice.to.email}
                onChange={(e) => updateParty('to', 'email', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div className="sm:col-span-6">
              <label htmlFor="to-address" className="block text-sm font-medium text-gray-700">
                Address
              </label>
              <input
                type="text"
                id="to-address"
                value={invoice.to.address}
                onChange={(e) => updateParty('to', 'address', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="to-city" className="block text-sm font-medium text-gray-700">
                City
              </label>
              <input
                type="text"
                id="to-city"
                value={invoice.to.city}
                onChange={(e) => updateParty('to', 'city', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="to-state" className="block text-sm font-medium text-gray-700">
                State
              </label>
              <input
                type="text"
                id="to-state"
                value={invoice.to.state}
                onChange={(e) => updateParty('to', 'state', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="to-zipCode" className="block text-sm font-medium text-gray-700">
                ZIP Code
              </label>
              <input
                type="text"
                id="to-zipCode"
                value={invoice.to.zipCode}
                onChange={(e) => updateParty('to', 'zipCode', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>
          </div>
        </div>

        {/* Line Items */}
        <div className="pt-8">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-md font-medium text-gray-900">Line Items</h4>
            <button
              type="button"
              onClick={addLineItem}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Add Item
            </button>
          </div>

          <div className="space-y-4">
            {invoice.lineItems.map((item, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-12">
                  <div className="sm:col-span-6">
                    <label className="block text-sm font-medium text-gray-700">
                      Description
                    </label>
                    <input
                      type="text"
                      value={item.description}
                      onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Quantity
                    </label>
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => updateLineItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                      min="0"
                      step="0.01"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Unit Price
                    </label>
                    <input
                      type="number"
                      value={item.unitPrice}
                      onChange={(e) => updateLineItem(index, 'unitPrice', parseFloat(e.target.value) || 0)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      required
                      min="0"
                      step="0.01"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Amount
                    </label>
                    <div className="mt-1 px-3 py-2 bg-gray-100 rounded-md text-sm">
                      ${item.amount.toFixed(2)}
                    </div>
                  </div>

                  <div className="sm:col-span-12 flex justify-end">
                    <button
                      type="button"
                      onClick={() => removeLineItem(index)}
                      className="text-red-600 hover:text-red-700 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Totals */}
        <div className="pt-8">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div></div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Subtotal:</span>
                <span>${invoice.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span>Tax:</span>
                  <input
                    type="number"
                    value={invoice.taxRate}
                    onChange={(e) => setInvoice({ ...invoice, taxRate: parseFloat(e.target.value) || 0 })}
                    className="w-16 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    min="0"
                    step="0.01"
                  />
                  <span>%</span>
                </div>
                <span>${invoice.tax.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-lg font-medium">
                <span>Total:</span>
                <span>${invoice.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Notes and Terms */}
        <div className="pt-8">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                Notes
              </label>
              <textarea
                id="notes"
                name="notes"
                rows={4}
                value={invoice.notes}
                onChange={(e) => setInvoice({ ...invoice, notes: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label htmlFor="terms" className="block text-sm font-medium text-gray-700">
                Terms & Conditions
              </label>
              <textarea
                id="terms"
                name="terms"
                rows={4}
                value={invoice.terms}
                onChange={(e) => setInvoice({ ...invoice, terms: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Form Actions */}
      <div className="pt-5">
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            {loading ? 'Saving...' : (isEdit ? 'Update' : 'Create')}
          </button>
        </div>
      </div>
    </form>
  );
}

export default InvoiceForm;