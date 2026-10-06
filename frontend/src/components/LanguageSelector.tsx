import React from 'react';
import { useTranslation, SupportedLanguage } from '../i18n/LanguageContext';
import { Globe } from 'lucide-react';

interface LanguageSelectorProps {
  className?: string;
  variant?: 'navbar' | 'standalone' | 'mobile';
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  className = '',
  variant = 'navbar'
}) => {
  const { language, setLanguage } = useTranslation();

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLanguage(e.target.value as SupportedLanguage);
  };

  if (variant === 'mobile') {
    return (
      <div className={`flex items-center justify-between px-3 py-2 bg-navy-800 rounded-md border border-slate/30 ${className}`}>
        <div className="flex items-center space-x-2 text-slate-light text-xs font-semibold">
          <Globe className="w-4 h-4 text-terracotta" />
          <span>Language / भाषा / भाषा</span>
        </div>
        <select
          value={language}
          onChange={handleLanguageChange}
          className="bg-navy border border-slate/40 text-ivory text-xs px-2.5 py-1 rounded font-medium focus:outline-none focus:ring-1 focus:ring-terracotta cursor-pointer"
          aria-label="Select Language"
        >
          <option value="en">English</option>
          <option value="hi">हिंदी (Hindi)</option>
          <option value="mr">मराठी (Marathi)</option>
        </select>
      </div>
    );
  }

  if (variant === 'standalone') {
    return (
      <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-navy/15 bg-white text-navy text-xs shadow-sm hover:border-navy/30 transition-colors ${className}`}>
        <Globe className="w-4 h-4 text-terracotta shrink-0" />
        <select
          value={language}
          onChange={handleLanguageChange}
          className="bg-transparent text-navy text-xs font-medium cursor-pointer focus:outline-none pr-1"
          aria-label="Select Language"
        >
          <option value="en">English</option>
          <option value="hi">हिंदी (Hindi)</option>
          <option value="mr">मराठी (Marathi)</option>
        </select>
      </div>
    );
  }

  return (
    <div className={`relative inline-flex items-center ${className}`}>
      <div className="flex items-center space-x-1.5 bg-navy-800 border border-slate/30 rounded-md px-2.5 py-1.5 text-ivory text-xs hover:border-slate/60 transition-colors">
        <Globe className="w-3.5 h-3.5 text-terracotta shrink-0" />
        <select
          value={language}
          onChange={handleLanguageChange}
          className="bg-transparent text-ivory text-xs font-medium cursor-pointer focus:outline-none pr-1"
          aria-label="Select Language"
        >
          <option value="en" className="bg-navy text-ivory">English</option>
          <option value="hi" className="bg-navy text-ivory">हिंदी (Hindi)</option>
          <option value="mr" className="bg-navy text-ivory">मराठी (Marathi)</option>
        </select>
      </div>
    </div>
  );
};

export default LanguageSelector;
