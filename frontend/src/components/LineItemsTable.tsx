import React from 'react';
import { LineItem } from '../types/invoice';

interface LineItemsTableProps {
  items: LineItem[];
  onUpdateItem: (index: number, field: keyof LineItem, value: string | number) => void;
  onRemoveItem: (index: number) => void;
  onAddItem: () => void;
  currencySymbol?: string;
}

const LineItemsTable: React.FC<LineItemsTableProps> = ({
  items,
  onUpdateItem,
  onRemoveItem,
  onAddItem,
  currencySymbol = '$'
}) => {
  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left py-3 px-2 font-semibold text-gray-700">Item</th>
              <th className="text-center py-3 px-2 font-semibold text-gray-700 w-24">Quantity</th>
              <th className="text-center py-3 px-2 font-semibold text-gray-700 w-32">Rate</th>
              <th className="text-right py-3 px-2 font-semibold text-gray-700 w-32">Amount</th>
              <th className="w-10"></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, index) => (
              <tr key={index} className="border-b border-gray-200">
                <td className="py-3 px-2">
                  <input
                    type="text"
                    value={item.description}
                    onChange={(e) => onUpdateItem(index, 'description', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Description of service or product"
                  />
                </td>
                <td className="py-3 px-2">
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => onUpdateItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center"
                    min="0"
                    step="0.01"
                  />
                </td>
                <td className="py-3 px-2">
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                      {currencySymbol}
                    </span>
                    <input
                      type="number"
                      value={item.unitPrice}
                      onChange={(e) => onUpdateItem(index, 'unitPrice', parseFloat(e.target.value) || 0)}
                      className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-right"
                      min="0"
                      step="0.01"
                    />
                  </div>
                </td>
                <td className="py-3 px-2 text-right font-medium">
                  {currencySymbol}{item.amount.toFixed(2)}
                </td>
                <td className="py-3 px-2">
                  <button
                    type="button"
                    onClick={() => onRemoveItem(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <button
        type="button"
        onClick={onAddItem}
        className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:text-blue-700 font-medium"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        Add Line Item
      </button>
    </div>
  );
};

export default LineItemsTable;