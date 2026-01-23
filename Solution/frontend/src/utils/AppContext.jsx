import React, { createContext, useContext, useState, useEffect } from 'react';
import { translations } from './translations';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
    const [language, setLanguage] = useState(localStorage.getItem('language') || 'en');

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    useEffect(() => {
        document.documentElement.setAttribute('lang', language);
        document.documentElement.setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
        localStorage.setItem('language', language);
    }, [language]);

    const toggleTheme = () => {
        setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
    };

    const t = (key, variables = {}) => {
        const keys = key.split('.');
        let result = translations[language];
        for (const k of keys) {
            if (result && result[k]) {
                result = result[k];
            } else {
                return key;
            }
        }

        if (typeof result === 'string') {
            let processed = result;
            Object.keys(variables).forEach(v => {
                processed = processed.replace(`{${v}}`, variables[v]);
            });
            return processed;
        }
        return result;
    };

    return (
        <AppContext.Provider value={{ theme, toggleTheme, language, setLanguage, t }}>
            {children}
        </AppContext.Provider>
    );
};

export const useApp = () => useContext(AppContext);
