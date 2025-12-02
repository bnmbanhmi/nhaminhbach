// src/components/ui/SearchBar.tsx
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { isGeoIdPattern, isUuid } from '../../utils/geoid';

interface SearchBarProps {
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  placeholder = "Nhập mã phòng (VD: AB1) hoặc tìm kiếm...",
  className = "",
  autoFocus = false
}) => {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    
    if (!trimmed) return;
    
    // If it looks like a GeoID, navigate directly to the listing
    if (isGeoIdPattern(trimmed)) {
      navigate(`/${trimmed.toUpperCase()}`);
      return;
    }
    
    // If it's a UUID, navigate to legacy route
    if (isUuid(trimmed)) {
      navigate(`/listings/${trimmed}`);
      return;
    }
    
    // Otherwise, treat as search query (future: implement search)
    // For now, just navigate to home with query param
    navigate(`/?q=${encodeURIComponent(trimmed)}`);
  }, [query, navigate]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  }, [handleSubmit]);

  return (
    <form onSubmit={handleSubmit} className={`relative w-full ${className}`}>
      <div className={`
        flex items-center w-full bg-white border-2 rounded-full
        transition-all duration-200 ease-in-out
        ${isFocused 
          ? 'border-primary shadow-lg ring-4 ring-primary/10' 
          : 'border-gray-200 shadow-md hover:shadow-lg hover:border-gray-300'
        }
      `}>
        {/* Search Icon */}
        <div className="pl-4 pr-2 text-gray-400">
          <svg 
            className="w-5 h-5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
            />
          </svg>
        </div>
        
        {/* Input */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="
            flex-1 py-3 pr-4 text-base sm:text-lg
            bg-transparent border-none outline-none
            text-gray-900 placeholder-gray-400
          "
          autoComplete="off"
          spellCheck={false}
        />
        
        {/* Clear button (when there's text) */}
        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            className="pr-4 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
        
        {/* Search button */}
        <button
          type="submit"
          className="
            m-1.5 px-4 sm:px-6 py-2 
            bg-primary text-white font-medium
            rounded-full hover:bg-primary-dark
            transition-colors duration-200
            text-sm sm:text-base
          "
        >
          Tìm
        </button>
      </div>
      
      {/* Hint text */}
      {isFocused && query.length === 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 px-4 text-sm text-gray-500">
          💡 Gõ mã phòng (VD: <span className="font-mono font-semibold text-primary">AB1</span>) để xem ngay
        </div>
      )}
      
      {/* GeoID detection hint */}
      {query && isGeoIdPattern(query) && (
        <div className="absolute top-full left-0 right-0 mt-2 px-4 text-sm text-green-600 font-medium">
          ✓ Nhấn Enter để xem phòng <span className="font-mono">{query.toUpperCase()}</span>
        </div>
      )}
    </form>
  );
};

export default SearchBar;
