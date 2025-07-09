import React from 'react';
import CurrencySelector from './CurrencySelector';

interface InvoiceHeaderProps {
  invoiceNumber: string;
  currency: string;
  onInvoiceNumberChange: (value: string) => void;
  onCurrencyChange: (value: string) => void;
}

const InvoiceHeader: React.FC<InvoiceHeaderProps> = ({
  invoiceNumber,
  currency,
  onInvoiceNumberChange,
  onCurrencyChange,
}) => {
  return (
    <div className="bg-white rounded-lg">
      <div className="flex justify-between items-start">
        {/* Logo Upload Area */}
        <div className="w-32 h-32 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <svg className="w-8 h-8 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-xs text-gray-500 mt-2">Logo</p>
          </div>
        </div>

        {/* Invoice Details */}
        <div className="text-right space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">INVOICE</h1>
          <div className="flex items-center justify-end gap-2">
            <span className="text-gray-700 font-medium">#</span>
            <input
              type="text"
              value={invoiceNumber}
              onChange={(e) => onInvoiceNumberChange(e.target.value)}
              className="w-32 px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="1"
            />
          </div>
          <CurrencySelector
            value={currency}
            onChange={onCurrencyChange}
          />
        </div>
      </div>

      {/* Sender Info */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">John Yzaguirre</h2>
      </div>
    </div>
  );
};

export default InvoiceHeader;