import React, { useState } from 'react';
import { Menu, X, ShieldCheck, Zap, Briefcase } from 'lucide-react';
import { useTheme, PageView } from '../App';
import { openSupportChat } from '../utils/supportService';

interface NavbarProps {
  onNavigate: (page: PageView) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);
  const { theme, toggleTheme } = useTheme();
  
  // Assign customer service and open Telegram
  const handleOpenAccount = async (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    
    try {
      setIsAssigning(true);
      await openSupportChat('https://t.me/PayShieldSupport');
    } catch (error) {
      console.error('Error opening support chat:', error);
      window.open('https://t.me/PayShieldSupport', '_blank');
    } finally {
      setIsAssigning(false);
    }
  };

  const handleNavClick = (page: PageView, anchor?: string) => {
    onNavigate(page);
    setIsOpen(false);
    if (anchor) {
      setTimeout(() => {
        const element = document.getElementById(anchor);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    }
  };

  return (
    <nav className="fixed top-0 w-full z-50 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-white/10 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo Section */}
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => handleNavClick('home')}>
            <div className="relative">
               <ShieldCheck className="h-8 w-8 text-blue-600 dark:text-brand-blue transition-colors duration-300" />
               <div className="absolute inset-0 bg-blue-500 blur-lg opacity-20 dark:bg-brand-blue dark:opacity-40 rounded-full"></div>
            </div>
            <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
              伍拾支付 
              <span className="hidden sm:inline-block ml-2 text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-brand-blue/10 dark:text-brand-blue font-medium">
                Global
              </span>
            </span>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-6 lg:space-x-8">
              <button onClick={() => handleNavClick('home', 'features')} className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-brand-blue transition-colors px-2 py-2 rounded-md text-sm font-medium">
                功能特性
              </button>
              <button onClick={() => handleNavClick('home', 'api')} className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-brand-blue transition-colors px-2 py-2 rounded-md text-sm font-medium">
                开发者 API
              </button>
              <button onClick={() => handleNavClick('fees')} className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-brand-blue transition-colors px-2 py-2 rounded-md text-sm font-medium">
                费率
              </button>
              
              {/* Theme Toggle - Matches Screenshot 'Geek Mode' */}
              <button 
                onClick={toggleTheme}
                className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all border border-slate-200 dark:border-slate-600 group"
              >
                {theme === 'dark' ? (
                  <>
                    <Zap className="w-3.5 h-3.5 text-brand-blue group-hover:scale-110 transition-transform" />
                    <span className="text-xs font-bold text-slate-300 group-hover:text-white transition-colors">极客模式</span>
                  </>
                ) : (
                  <>
                    <Briefcase className="w-3.5 h-3.5 text-blue-600 group-hover:scale-110 transition-transform" />
                    <span className="text-xs font-bold text-slate-700 group-hover:text-slate-900 transition-colors">商务模式</span>
                  </>
                )}
              </button>

              {/* CTA Button - Matches Screenshot 'Open Account' color */}
              <a 
                href="#"
                onClick={handleOpenAccount}
                className={`bg-blue-600 hover:bg-blue-700 dark:bg-[#7000ff] dark:hover:bg-[#6000e0] text-white px-6 py-2 rounded-full text-sm font-bold transition-all shadow-lg shadow-blue-600/20 dark:shadow-[0_0_15px_rgba(112,0,255,0.4)] transform hover:scale-105 ${isAssigning ? 'opacity-50 cursor-wait' : ''}`}
              >
                {isAssigning ? '分配中...' : '立即开户'}
              </a>
            </div>
          </div>

          {/* Mobile Navigation Controls */}
          <div className="flex items-center gap-4 md:hidden">
             <button 
                onClick={toggleTheme}
                className="p-2 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
              >
                {theme === 'dark' ? <Zap className="w-5 h-5 text-brand-blue" /> : <Briefcase className="w-5 h-5 text-blue-600" />}
              </button>

            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white focus:outline-none"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-white/10 shadow-xl animate-in slide-in-from-top-2">
          <div className="px-4 pt-2 pb-6 space-y-2">
            <button onClick={() => handleNavClick('home', 'features')} className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white block px-3 py-3 rounded-lg text-base font-medium w-full text-left hover:bg-slate-50 dark:hover:bg-white/5 transition-colors">
              功能特性
            </button>
            <button onClick={() => handleNavClick('home', 'api')} className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white block px-3 py-3 rounded-lg text-base font-medium w-full text-left hover:bg-slate-50 dark:hover:bg-white/5 transition-colors">
              开发者 API
            </button>
            <button onClick={() => handleNavClick('fees')} className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white block px-3 py-3 rounded-lg text-base font-medium w-full text-left hover:bg-slate-50 dark:hover:bg-white/5 transition-colors">
              费率
            </button>
            <a 
              href="#"
              onClick={handleOpenAccount}
              className={`bg-blue-600 dark:bg-[#7000ff] text-white block px-3 py-3 rounded-lg text-base font-bold mt-6 text-center shadow-lg ${isAssigning ? 'opacity-50 cursor-wait' : ''}`}
            >
              {isAssigning ? '分配中...' : '立即开户'}
            </a>
          </div>
        </div>
      )}
    </nav>
  );
};