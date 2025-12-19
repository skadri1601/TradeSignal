import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { companiesApi } from '../../api/companies';
import { Search, X } from 'lucide-react';
import type { Company } from '../../types';

interface CompanyAutocompleteProps {
  value: string;
  onChange: (ticker: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export default function CompanyAutocomplete({
  value,
  onChange,
  placeholder = 'Search by ticker (e.g., AAPL)...',
  disabled = false,
}: CompanyAutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState(value);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const {
    data: companiesData,
    isLoading,
    error,
  } = useQuery<Company[]>({
    queryKey: ['companies', 'all'],
    queryFn: () => companiesApi.getAllCompanies(),
    staleTime: 1000 * 60 * 10, // cache for 10 minutes
  });

  // Debug logging
  useEffect(() => {
    console.log('[CompanyAutocomplete] Query State:', {
      isLoading,
      itemsCount: companiesData?.length || 0,
      error: error?.message || null,
    });
  }, [isLoading, companiesData, error]);

  const companies = companiesData || [];

  const filteredCompanies = companies.filter((company) => {
    const search = searchTerm.toLowerCase();
    return (
      company.ticker.toLowerCase().includes(search) ||
      company.name.toLowerCase().includes(search)
    );
  }).slice(0, 10); // Limit to top 10 results

  // Sync searchTerm with value prop (e.g., when parent resets)
  useEffect(() => {
    setSearchTerm(value);
  }, [value]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (company: Company) => {
    setSearchTerm(company.ticker);
    onChange(company.ticker);
    setIsOpen(false);
  };

  const handleClear = () => {
    setSearchTerm('');
    onChange('');
    setIsOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled) return;
    e.preventDefault();
    e.stopPropagation();
    const newValue = e.target.value;
    setSearchTerm(newValue);
    setIsOpen(newValue.length > 0);
    onChange(newValue);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Prevent navigation on backspace when input is empty
    if (e.key === 'Backspace' && searchTerm.length === 0) {
      e.preventDefault();
      e.stopPropagation();
    }
    // Close dropdown on Escape
    if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div className="relative" ref={wrapperRef}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-4 w-4 text-gray-400" />
        </div>
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => !disabled && searchTerm.length > 0 && setIsOpen(true)}
          placeholder={placeholder}
          className="input pl-10 pr-10 disabled:opacity-50 disabled:cursor-not-allowed"
          autoComplete="off"
          disabled={disabled}
        />
        {searchTerm && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {isLoading ? (
            <div className="px-4 py-3 text-sm text-gray-500">Loading companies...</div>
          ) : filteredCompanies.length > 0 ? (
            <ul className="py-1">
              {filteredCompanies.map((company) => (
                <li key={company.id}>
                  <button
                    type="button"
                    onClick={() => handleSelect(company)}
                    className="w-full text-left px-4 py-2 hover:bg-blue-50 transition-colors focus:outline-none focus:bg-blue-50"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-semibold text-blue-600">{company.ticker}</span>
                        <span className="ml-2 text-sm text-gray-600">{company.name}</span>
                      </div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-3 text-sm text-gray-500">
              No companies found for "{searchTerm}"
            </div>
          )}
        </div>
      )}
    </div>
  );
}
