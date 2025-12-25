import React from 'react';
import { motion } from 'framer-motion';
import { Language, TRANSLATIONS } from '../types';
import { Logo } from './Logo';

interface LoadingScreenProps {
  lang: Language;
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ lang }) => {
  const t = TRANSLATIONS[lang];

  return (
    <motion.div 
      className="flex flex-col items-center justify-center h-[80vh] w-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.5 }}
    >
      <div className="relative mb-10">
        {/* Outer Ripple - Tech Blue */}
        <motion.div
          className="absolute inset-[-20px] rounded-full border border-tech-primary/20"
          animate={{ scale: [0.8, 1.3, 0.8], opacity: [0, 1, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
        {/* Inner Ripple - Champagne Gold */}
        <motion.div
          className="absolute inset-[-10px] rounded-full border border-champagne-400/40"
          animate={{ scale: [0.9, 1.1, 0.9], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut", delay: 0.2 }}
        />
        
        {/* Logo Container */}
        <div className="bg-white p-6 rounded-3xl shadow-soft relative z-10 flex items-center justify-center border border-champagne-100">
           <motion.div
             animate={{ rotate: 360 }}
             transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
             className="absolute inset-0 rounded-3xl bg-gradient-to-tr from-tech-primary/5 to-champagne-300/20"
           />
          <div className="relative z-10">
            <Logo size="lg" className="drop-shadow-lg" />
          </div>
        </div>
      </div>
      
      <motion.div 
        className="flex flex-col items-center space-y-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <div className="flex space-x-1">
          <motion.div className="w-2 h-2 rounded-full bg-champagne-500" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} />
          <motion.div className="w-2 h-2 rounded-full bg-tech-primary" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }} />
          <motion.div className="w-2 h-2 rounded-full bg-champagne-400" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }} />
        </div>
        <span className="text-tech-sub text-xs font-medium tracking-wide uppercase mt-2">{t.loading}</span>
      </motion.div>
    </motion.div>
  );
};