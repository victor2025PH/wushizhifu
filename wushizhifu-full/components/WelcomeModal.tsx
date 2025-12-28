import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, Sparkles } from 'lucide-react';
import { Language, TelegramUser, TRANSLATIONS } from '../types';
import { Celebration } from './Celebration';

interface WelcomeModalProps {
  user: TelegramUser | null;
  lang: Language;
  onClose: () => void;
}

export const WelcomeModal: React.FC<WelcomeModalProps> = ({ user, lang, onClose }) => {
  const t = TRANSLATIONS[lang];
  const displayName = user?.first_name || t.guest;
  const [isCelebrating, setIsCelebrating] = useState(false);

  const handleStart = () => {
    setIsCelebrating(true);
    // Delay actual close to show the fireworks briefly (1.5 seconds)
    setTimeout(() => {
      onClose();
    }, 1500);
  };

  return (
    <>
      {isCelebrating && <Celebration />}
      
      <motion.div 
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1, backgroundColor: isCelebrating ? "rgba(0,0,0,0)" : "rgba(0,0,0,0.4)" }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
      >
        <AnimatePresence>
          {!isCelebrating && (
            <motion.div 
              className="w-full max-w-sm bg-white rounded-[2rem] p-8 shadow-2xl border border-champagne-200 relative overflow-hidden"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Background Decorations */}
              <div className="absolute top-[-50px] right-[-50px] w-32 h-32 bg-champagne-300/30 rounded-full blur-3xl" />
              <div className="absolute bottom-[-30px] left-[-30px] w-40 h-40 bg-tech-primary/10 rounded-full blur-3xl" />

              <div className="relative z-10 flex flex-col items-center text-center">
                <div className="w-20 h-20 bg-gradient-gold rounded-full flex items-center justify-center mb-6 shadow-gold p-1">
                   {user?.photo_url ? (
                     <img src={user.photo_url} alt="User" className="w-full h-full rounded-full object-cover border-2 border-white" />
                   ) : (
                     <div className="w-full h-full bg-white rounded-full flex items-center justify-center">
                       <ShieldCheck className="w-8 h-8 text-champagne-600" />
                     </div>
                   )}
                </div>

                <h2 className="text-2xl font-extrabold text-tech-text mb-2">
                  {t.welcome}, <span className="text-champagne-600">{displayName}</span>
                </h2>
                
                <p className="text-tech-sub text-sm mb-8 leading-relaxed">
                  {t.welcomeMessage}
                </p>

                <button 
                  onClick={handleStart}
                  className="w-full py-4 rounded-2xl bg-tech-text text-white font-bold text-lg shadow-lg hover:shadow-xl transition-all flex items-center justify-center space-x-2"
                >
                  <Sparkles className="w-5 h-5 text-champagne-300" />
                  <span>{t.getStarted}</span>
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </>
  );
};