import React from 'react';

interface DatePickerProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

const DatePicker: React.FC<DatePickerProps> = ({ label, value, onChange, className = '' }) => {
  return (
    <div className={`space-y-1 ${className}`}>
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </div>
  );
};

export default DatePicker;