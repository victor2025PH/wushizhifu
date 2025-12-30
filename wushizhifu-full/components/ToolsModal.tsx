import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calculator, Clock } from 'lucide-react';
import { HistoryView } from './HistoryView';
import { Language, TRANSLATIONS } from '../types';

interface ToolsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenCalculator: () => void;
  onOpenHistory: () => void;
  lang: Language;
}

export const ToolsModal: React.FC<ToolsModalProps> = ({
  isOpen,
  onClose,
  onOpenCalculator,
  onOpenHistory,
  lang
}) => {
  const [activeTab, setActiveTab] = useState<'calculator' | 'history'>('calculator');
  const t = TRANSLATIONS[lang];

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden pointer-events-auto flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-100">
                <h2 className="text-lg font-bold text-tech-text">{t.toolsAndRecords}</h2>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  aria-label="Close"
                >
                  <X className="w-5 h-5 text-tech-sub" />
                </button>
              </div>

              {/* Tabs */}
              <div className="flex border-b border-gray-200">
                <button
                  onClick={() => setActiveTab('calculator')}
                  className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
                    activeTab === 'calculator'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Calculator className="w-5 h-5 inline-block mr-2" />
                  {t.calculator}
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
                    activeTab === 'history'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Clock className="w-5 h-5 inline-block mr-2" />
                  {t.history}
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-4">
                {activeTab === 'calculator' ? (
                  <div className="space-y-4">
                    <div className="text-center text-sm text-tech-sub mb-4">
                      {t.calculator}
                    </div>
                    <button
                      onClick={() => {
                        onClose();
                        onOpenCalculator();
                      }}
                      className="w-full py-4 bg-gradient-to-r from-champagne-500 to-champagne-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
                    >
                      {t.calculator}
                    </button>
                  </div>
                ) : (
                  <HistoryView
                    lang={lang}
                    onBack={onClose}
                    isTab={true}
                  />
                )}
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

