import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, AlertCircle, User } from 'lucide-react';
import { Language, TRANSLATIONS } from '../types';

interface CustomerServiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  serviceAccount: string | null;
  assignmentMethod?: string;
  error?: string;
  onContact: () => void;
  onContactAdmin?: () => void;
  lang: Language;
}

export const CustomerServiceModal: React.FC<CustomerServiceModalProps> = ({
  isOpen,
  onClose,
  serviceAccount,
  assignmentMethod,
  error,
  onContact,
  onContactAdmin,
  lang
}) => {
  const t = TRANSLATIONS[lang];

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative"
        >
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          {error ? (
            // Error State
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="bg-red-100 p-3 rounded-full">
                  <AlertCircle className="w-8 h-8 text-red-600" />
                </div>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                {lang === 'zh' ? '客服分配失败' : 'Service Assignment Failed'}
              </h3>
              <p className="text-sm text-gray-600 mb-6">
                {error}
              </p>
              {onContactAdmin && (
                <button
                  onClick={() => {
                    onContactAdmin();
                    onClose();
                  }}
                  className="w-full bg-gradient-to-r from-champagne-500 to-champagne-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
                >
                  {lang === 'zh' ? '联系管理员' : 'Contact Admin'}
                </button>
              )}
            </div>
          ) : serviceAccount ? (
            // Success State
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="bg-champagne-100 p-3 rounded-full">
                  <MessageCircle className="w-8 h-8 text-champagne-600" />
                </div>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                {lang === 'zh' ? '已为您分配客服' : 'Customer Service Assigned'}
              </h3>
              <div className="bg-gray-50 rounded-xl p-4 mb-4">
                <div className="flex items-center justify-center space-x-2">
                  <User className="w-5 h-5 text-gray-600" />
                  <span className="text-lg font-semibold text-gray-900">
                    @{serviceAccount}
                  </span>
                </div>
                {assignmentMethod && (
                  <p className="text-xs text-gray-500 mt-2">
                    {lang === 'zh' 
                      ? `分配方式：${assignmentMethod === 'smart' ? '智能分配' : assignmentMethod === 'round_robin' ? '轮询分配' : assignmentMethod}`
                      : `Method: ${assignmentMethod}`
                    }
                  </p>
                )}
              </div>
              <p className="text-sm text-gray-600 mb-6">
                {lang === 'zh' 
                  ? '点击下方按钮立即联系客服'
                  : 'Click the button below to contact customer service'
                }
              </p>
              <button
                onClick={() => {
                  onContact();
                  onClose();
                }}
                className="w-full bg-gradient-to-r from-champagne-500 to-champagne-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center space-x-2"
              >
                <MessageCircle className="w-5 h-5" />
                <span>
                  {lang === 'zh' ? `联系客服 @${serviceAccount}` : `Contact @${serviceAccount}`}
                </span>
              </button>
            </div>
          ) : (
            // Loading State (should not appear, but just in case)
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-champagne-600"></div>
              </div>
              <p className="text-sm text-gray-600">
                {lang === 'zh' ? '正在分配客服...' : 'Assigning customer service...'}
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
