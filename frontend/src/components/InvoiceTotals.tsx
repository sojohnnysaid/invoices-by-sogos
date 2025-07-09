import React from 'react';

interface InvoiceTotalsProps {
  subtotal: number;
  taxRate: number;
  tax: number;
  discount: number;
  shipping: number;
  total: number;
  amountPaid: number;
  balanceDue: number;
  onTaxRateChange: (value: number) => void;
  onDiscountChange: (value: number) => void;
  onShippingChange: (value: number) => void;
  onAmountPaidChange: (value: number) => void;
  currencySymbol?: string;
}

const InvoiceTotals: React.FC<InvoiceTotalsProps> = ({
  subtotal,
  taxRate,
  tax,
  discount,
  shipping,
  total,
  amountPaid,
  balanceDue,
  onTaxRateChange,
  onDiscountChange,
  onShippingChange,
  onAmountPaidChange,
  currencySymbol = '$'
}) => {
  return (
    <div className="space-y-3">
      {/* Subtotal */}
      <div className="flex justify-between items-center">
        <span className="text-gray-700">Subtotal</span>
        <span className="font-medium">{currencySymbol}{subtotal.toFixed(2)}</span>
      </div>

      {/* Tax */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="text-gray-700">Tax</span>
          <div className="flex items-center">
            <input
              type="number"
              value={taxRate}
              onChange={(e) => onTaxRateChange(parseFloat(e.target.value) || 0)}
              className="w-16 px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center"
              min="0"
              max="100"
              step="0.01"
            />
            <span className="ml-1 text-gray-500">%</span>
          </div>
        </div>
        <span className="font-medium">{currencySymbol}{tax.toFixed(2)}</span>
      </div>

      {/* Discount */}
      <div className="flex justify-between items-center">
        <span className="text-gray-700">Discount</span>
        <div className="flex items-center">
          <span className="mr-1 text-gray-500">{currencySymbol}</span>
          <input
            type="number"
            value={discount}
            onChange={(e) => onDiscountChange(parseFloat(e.target.value) || 0)}
            className="w-24 px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-right"
            min="0"
            step="0.01"
          />
        </div>
      </div>

      {/* Shipping */}
      <div className="flex justify-between items-center">
        <span className="text-gray-700">Shipping</span>
        <div className="flex items-center">
          <span className="mr-1 text-gray-500">{currencySymbol}</span>
          <input
            type="number"
            value={shipping}
            onChange={(e) => onShippingChange(parseFloat(e.target.value) || 0)}
            className="w-24 px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-right"
            min="0"
            step="0.01"
          />
        </div>
      </div>

      {/* Total */}
      <div className="flex justify-between items-center pt-3 border-t border-gray-300">
        <span className="text-lg font-semibold text-gray-900">Total</span>
        <span className="text-lg font-semibold text-gray-900">{currencySymbol}{total.toFixed(2)}</span>
      </div>

      {/* Amount Paid */}
      <div className="flex justify-between items-center">
        <span className="text-gray-700">Amount Paid</span>
        <div className="flex items-center">
          <span className="mr-1 text-gray-500">{currencySymbol}</span>
          <input
            type="number"
            value={amountPaid}
            onChange={(e) => onAmountPaidChange(parseFloat(e.target.value) || 0)}
            className="w-24 px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-right"
            min="0"
            step="0.01"
          />
        </div>
      </div>

      {/* Balance Due */}
      <div className="flex justify-between items-center pt-3 border-t-2 border-gray-300">
        <span className="text-lg font-semibold text-gray-900">Balance Due</span>
        <span className="text-lg font-semibold text-gray-900">{currencySymbol}{balanceDue.toFixed(2)}</span>
      </div>
    </div>
  );
};

export default InvoiceTotals;