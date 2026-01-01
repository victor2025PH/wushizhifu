import React, { createContext, useContext, useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { LiveTicker } from './components/LiveTicker';
import { FeatureGrid } from './components/FeatureGrid';
import { ProcessSteps } from './components/ProcessSteps';
import { ComparisonTable } from './components/ComparisonTable';
import { DeveloperSection } from './components/DeveloperSection';
import { FAQ } from './components/FAQ';
import { Footer } from './components/Footer';
import { CustomerSupport } from './components/CustomerSupport';
import { FeesPage, UpdateLogPage, PrivacyPolicyPage, TermsPage } from './components/ContentPages';

// Theme Context Definition
type Theme = 'dark' | 'light';
interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

export const ThemeContext = createContext<ThemeContextType>({
  theme: 'dark',
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

// Navigation Type
export type PageView = 'home' | 'fees' | 'changelog' | 'privacy' | 'terms';

function App() {
  const [theme, setTheme] = useState<Theme>('dark');
  const [currentPage, setCurrentPage] = useState<PageView>('home');

  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleNavigate = (page: PageView) => {
    setCurrentPage(page);
    // If navigating to a new page, scroll to top is handled inside the component or here
    window.scrollTo(0, 0);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50 selection:bg-blue-500/30 selection:text-blue-600 dark:selection:bg-brand-blue/30 dark:selection:text-brand-blue transition-colors duration-300">
        <Navbar onNavigate={handleNavigate} />
        
        <main>
          {currentPage === 'home' && (
            <>
              <Hero />
              <LiveTicker />
              <FeatureGrid />
              <ProcessSteps />
              <ComparisonTable />
              <DeveloperSection />
              <FAQ />
            </>
          )}

          {currentPage === 'fees' && <FeesPage onBack={() => handleNavigate('home')} />}
          {currentPage === 'changelog' && <UpdateLogPage onBack={() => handleNavigate('home')} />}
          {currentPage === 'privacy' && <PrivacyPolicyPage onBack={() => handleNavigate('home')} />}
          {currentPage === 'terms' && <TermsPage onBack={() => handleNavigate('home')} />}
        </main>

        <CustomerSupport />
        <Footer onNavigate={handleNavigate} />
      </div>
    </ThemeContext.Provider>
  );
}

export default App;