import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import en from './translations/en';
import hi from './translations/hi';
import mr from './translations/mr';

export type SupportedLanguage = 'en' | 'hi' | 'mr';

export interface LanguageContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const STORAGE_KEY = 'resqflow_language';

const dictionaries: Record<SupportedLanguage, Record<string, string>> = {
  en,
  hi,
  mr
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<SupportedLanguage>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'hi' || saved === 'mr' || saved === 'en') {
        return saved;
      }
    } catch {
      // Ignore localStorage access failures
    }
    return 'en';
  });

  const setLanguage = (newLang: SupportedLanguage) => {
    setLanguageState(newLang);
    try {
      localStorage.setItem(STORAGE_KEY, newLang);
      document.documentElement.lang = newLang;
    } catch {
      // Ignore localStorage failures
    }
  };

  useEffect(() => {
    try {
      document.documentElement.lang = language;
    } catch {
      // Ignore DOM setup errors
    }
  }, [language]);

  const t = (key: string, params?: Record<string, string | number>): string => {
    const currentDict = dictionaries[language] || dictionaries.en;
    let translation = currentDict[key];

    // Fall back to English if missing in target language
    if (translation === undefined) {
      translation = dictionaries.en[key];
    }

    // If still undefined, fallback to key itself
    if (translation === undefined) {
      translation = key;
    }

    // Handle parameter interpolation: {name} or {count}
    if (params) {
      Object.entries(params).forEach(([paramKey, paramValue]) => {
        translation = translation.replace(new RegExp(`\\{${paramKey}\\}`, 'g'), String(paramValue));
      });
    }

    return translation;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useTranslation = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};

export const useLanguage = useTranslation;
export default LanguageContext;
