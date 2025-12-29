import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { LoadingScreen } from './components/LoadingScreen';
import { Dashboard } from './components/Dashboard';
import { WalletView } from './components/WalletView';
import { HistoryView } from './components/HistoryView';
import { ProfileView } from './components/ProfileView';
import { BottomNav } from './components/BottomNav';
import { PaymentForm } from './components/PaymentForm';
import { ResultScreen } from './components/ResultScreen';
import { CalculatorModal } from './components/CalculatorModal';
import { WelcomeModal } from './components/WelcomeModal';
import { AppState, PaymentProvider, Language, TelegramUser } from './types';
import { Globe } from 'lucide-react';

// Mock Telegram WebApp type for development outside TG
declare global {
  interface Window {
    Telegram: {
      WebApp: {
        ready: () => void;
        expand: () => void;
        initData: string;
        initDataUnsafe: {
          user?: TelegramUser;
          [key: string]: any;
        };
        MainButton: {
            show: () => void;
            hide: () => void;
            setText: (text: string) => void;
            onClick: (cb: () => void) => void;
            offClick: (cb: () => void) => void;
        };
        close: () => void;
        openLink: (url: string) => void;
      }
    }
  }
}

export default function App() {
  const [view, setView] = useState<AppState['view']>('loading');
  const [provider, setProvider] = useState<PaymentProvider | null>(null);
  const [amount, setAmount] = useState<number>(0);
  const [lang, setLang] = useState<Language>('zh');
  const [user, setUser] = useState<TelegramUser | null>(null);
  
  // Modals state
  const [showCalculator, setShowCalculator] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    // Clear old cache on version change (for Telegram MiniApp cache busting)
    const APP_VERSION = '1.0.1'; // Update this when deploying new features
    const cachedVersion = localStorage.getItem('app_version');
    if (cachedVersion && cachedVersion !== APP_VERSION) {
      // Clear old cache
      localStorage.clear();
      sessionStorage.clear();
    }
    localStorage.setItem('app_version', APP_VERSION);
    
    // Initialize Telegram WebApp and sync user data
    const initializeApp = async () => {
      // Wait for Telegram WebApp script to load
      const checkTelegramWebApp = () => {
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.ready();
          window.Telegram.WebApp.expand();
          
          console.log("Telegram WebApp Initialized");
          console.log("initData:", window.Telegram.WebApp.initData);
          console.log("initDataUnsafe:", window.Telegram.WebApp.initDataUnsafe);
          
          const tgUser = window.Telegram.WebApp.initDataUnsafe?.user;
          if (tgUser) {
            console.log("User data found:", tgUser);
            setUser(tgUser);
            
            // Set language based on user preference
            if (tgUser.language_code === 'en') {
              setLang('en');
            }
            
            // Sync user data with backend
            try {
              const { apiClient } = await import('./api');
              apiClient.syncUser(tgUser).then(() => {
                console.log("User data synced with backend");
              }).catch((error) => {
                console.error("Failed to sync user data:", error);
              });
            } catch (error) {
              console.error("Failed to import apiClient:", error);
            }
          } else {
            console.warn("⚠️ No user data found in initDataUnsafe");
            console.warn("This usually means the app was opened outside Telegram or initData is missing");
            
            // Try to get user from initData directly
            if (window.Telegram.WebApp.initData) {
              console.log("Attempting to parse initData manually...");
              try {
                const urlParams = new URLSearchParams(window.Telegram.WebApp.initData);
                const userStr = urlParams.get('user');
                if (userStr) {
                  const userData = JSON.parse(decodeURIComponent(userStr));
                  console.log("Parsed user from initData:", userData);
                  setUser(userData);
                }
              } catch (e) {
                console.error("Failed to parse initData:", e);
              }
            }
          }
          return true;
        }
        return false;
      };
      
      // Check immediately
      if (!checkTelegramWebApp()) {
        // If not available, wait a bit and retry (for script loading delay)
        let retries = 0;
        const maxRetries = 10;
        const checkInterval = setInterval(() => {
          retries++;
          if (checkTelegramWebApp() || retries >= maxRetries) {
            clearInterval(checkInterval);
            if (retries >= maxRetries && !window.Telegram?.WebApp) {
              console.error("❌ Telegram WebApp not available after retries");
              console.error("Please ensure the app is opened from within Telegram");
            }
          }
        }, 100);
      }

      // Parse URL parameters
      const params = new URLSearchParams(window.location.search);
      const viewParam = params.get('view') as AppState['view'] | null;
      const providerParam = params.get('provider') as PaymentProvider | null;

      // Simulate connection security check
      const timer = setTimeout(() => {
        // Handle URL parameters
        if (viewParam) {
          if (viewParam === 'dashboard' && providerParam) {
            setProvider(providerParam);
            setView('payment');
          } else if (viewParam === 'calculator') {
            // Calculator is a modal, so set view to dashboard and show modal
            setView('dashboard');
            setShowCalculator(true);
          } else if (['wallet', 'history', 'profile'].includes(viewParam)) {
            setView(viewParam as AppState['view']);
          } else {
            setView('dashboard');
          }
        } else {
          setView('dashboard');
        }
        
        // Show welcome modal after loading (only if no specific view requested)
        if (!viewParam) {
          setShowWelcome(true);
        }
      }, 2500);

      return () => clearTimeout(timer);
    };

    initializeApp();
  }, []);

  const handleProviderSelect = (selected: PaymentProvider) => {
    setProvider(selected);
    setView('payment');
  };

  const handlePaymentSubmit = (val: number) => {
    setAmount(val);
    setView('result');
  };

  const handleBackToDashboard = () => {
    setView('dashboard');
    setProvider(null);
    setAmount(0);
  };

  const toggleLanguage = () => {
    setLang(prev => prev === 'en' ? 'zh' : 'en');
  };

  // Views that should show the bottom nav
  const mainTabs = ['dashboard', 'wallet', 'history', 'profile'];
  const showBottomNav = mainTabs.includes(view);

  return (
    <div className="min-h-screen w-full bg-tech-bg text-tech-text overflow-hidden relative selection:bg-champagne-200">
      {/* Tech Luxury Background - Light & Airy with Champagne Accents */}
      <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-blue-100/40 rounded-full blur-[100px] pointer-events-none mix-blend-multiply opacity-70" />
      <div className="absolute bottom-[-10%] left-[-20%] w-[500px] h-[500px] bg-champagne-200/50 rounded-full blur-[100px] pointer-events-none mix-blend-multiply opacity-60" />
      <div className="absolute top-[40%] left-[20%] w-[300px] h-[300px] bg-cyan-100/40 rounded-full blur-[80px] pointer-events-none mix-blend-multiply opacity-50" />
      
      {/* Language Toggle */}
      <div className="absolute top-4 right-4 z-50">
        <button 
          onClick={toggleLanguage}
          className="flex items-center space-x-2 bg-white/40 backdrop-blur-md border border-white/50 px-3 py-2 rounded-full shadow-soft hover:bg-white/60 transition-colors"
        >
          <Globe className="w-4 h-4 text-tech-sub" />
          <span className="text-xs font-bold text-tech-text uppercase w-5 text-center">{lang.toUpperCase()}</span>
        </button>
      </div>

      <main className="relative z-10 h-full max-w-md mx-auto p-4 flex flex-col min-h-screen">
        <AnimatePresence mode="wait">
          {view === 'loading' && (
            <LoadingScreen key="loading" lang={lang} />
          )}

          {view === 'dashboard' && (
            <Dashboard 
              key="dashboard" 
              onSelectProvider={handleProviderSelect} 
              onOpenCalculator={() => setShowCalculator(true)}
              onOpenHistory={() => setView('history')}
              onOpenProfile={() => setView('profile')}
              lang={lang} 
              user={user}
            />
          )}

          {view === 'wallet' && (
            <WalletView key="wallet" lang={lang} user={user} />
          )}

          {view === 'history' && (
            <HistoryView 
              key="history" 
              lang={lang} 
              onBack={() => setView('dashboard')} 
              isTab={showBottomNav}
            />
          )}

          {view === 'profile' && (
            <ProfileView key="profile" lang={lang} user={user} onToggleLang={toggleLanguage} />
          )}

          {view === 'payment' && provider && (
            <PaymentForm 
              key="payment" 
              provider={provider} 
              onBack={handleBackToDashboard}
              onSubmit={handlePaymentSubmit}
              lang={lang}
            />
          )}

          {view === 'result' && provider && (
            <ResultScreen 
              key="result"
              provider={provider}
              amount={amount}
              onClose={handleBackToDashboard}
              lang={lang}
            />
          )}
        </AnimatePresence>

        {/* Bottom Navigation */}
        <AnimatePresence>
            {showBottomNav && (
                <motion.div
                    initial={{ y: 100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 100, opacity: 0 }}
                >
                    <BottomNav currentView={view} onChange={setView} lang={lang} />
                </motion.div>
            )}
        </AnimatePresence>

        {/* Modals Overlay */}
        <AnimatePresence>
           {showCalculator && (
             <CalculatorModal key="calculator" lang={lang} onClose={() => setShowCalculator(false)} />
           )}
           {showWelcome && (
             <WelcomeModal key="welcome" user={user} lang={lang} onClose={() => setShowWelcome(false)} />
           )}
        </AnimatePresence>
      </main>
    </div>
  );
}