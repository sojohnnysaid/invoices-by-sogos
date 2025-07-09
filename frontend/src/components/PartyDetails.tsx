import React from 'react';
import { InvoiceParty } from '../types/invoice';

interface PartyDetailsProps {
  title: string;
  party: InvoiceParty;
  onChange: (field: keyof InvoiceParty, value: string) => void;
  showEmail?: boolean;
  compact?: boolean;
}

const PartyDetails: React.FC<PartyDetailsProps> = ({ 
  title, 
  party, 
  onChange, 
  showEmail = false,
  compact = false 
}) => {
  // Ensure party object exists with default values
  const safeParty = party || {
    name: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    country: '',
    email: '',
    phone: ''
  };
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      <div className={compact ? "space-y-2" : "space-y-3"}>
        <input
          type="text"
          value={safeParty.name || ''}
          onChange={(e) => onChange('name', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Name"
        />
        
        {showEmail && (
          <input
            type="email"
            value={safeParty.email || ''}
            onChange={(e) => onChange('email', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Email"
          />
        )}
        
        <input
          type="text"
          value={safeParty.address || ''}
          onChange={(e) => onChange('address', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Address"
        />
        
        <div className="flex gap-2">
          <input
            type="text"
            value={safeParty.city || ''}
            onChange={(e) => onChange('city', e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="City"
          />
          <input
            type="text"
            value={safeParty.state || ''}
            onChange={(e) => onChange('state', e.target.value)}
            className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="State"
          />
          <input
            type="text"
            value={safeParty.zipCode || ''}
            onChange={(e) => onChange('zipCode', e.target.value)}
            className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="ZIP"
          />
        </div>
        
        <input
          type="text"
          value={safeParty.country || ''}
          onChange={(e) => onChange('country', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Country"
        />
      </div>
    </div>
  );
};

export default PartyDetails;