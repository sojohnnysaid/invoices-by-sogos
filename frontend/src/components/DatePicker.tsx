import React from 'react';

interface DatePickerProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

const DatePicker: React.FC<DatePickerProps> = ({ label, value, onChange, className = '' }) => {
  // Ensure value is in yyyy-MM-dd format
  const formattedValue = value && value.includes('T') ? value.split('T')[0] : value;
  
  return (
    <div className={`space-y-1 ${className}`}>
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <input
        type="date"
        value={formattedValue}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </div>
  );
};

export default DatePicker;