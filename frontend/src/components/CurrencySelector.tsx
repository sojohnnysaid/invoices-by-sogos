import React from 'react';

interface CurrencySelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const currencies = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' },
  { code: 'CNY', symbol: '¥', name: 'Chinese Yuan' },
  { code: 'INR', symbol: '₹', name: 'Indian Rupee' },
];

const CurrencySelector: React.FC<CurrencySelectorProps> = ({ value, onChange }) => {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="px-3 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
    >
      {currencies.map((currency) => (
        <option key={currency.code} value={currency.code}>
          {currency.code} - {currency.symbol}
        </option>
      ))}
    </select>
  );
};

export default CurrencySelector;