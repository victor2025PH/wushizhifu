import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Play, CheckCircle } from 'lucide-react';
import { Language, TRANSLATIONS } from '../types';
import { VideoPlayer } from './VideoPlayer';
import { useVideoUrl } from '../hooks/useVideoUrl';

interface AlipayGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  lang: Language;
}

export const AlipayGuideModal: React.FC<AlipayGuideModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  lang
}) => {
  const [showVideo, setShowVideo] = useState(false);
  const videoUrl = useVideoUrl('alipay');
  const t = TRANSLATIONS[lang];

  const handleConfirm = () => {
    onClose();
    onConfirm();
  };

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
              {/* Header with Close Button */}
              <div className="flex items-center justify-between p-4 border-b border-gray-100">
                <h2 className="text-lg font-bold text-tech-text">{t.alipayGuideTitle}</h2>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  aria-label="Close"
                >
                  <X className="w-5 h-5 text-tech-sub" />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {showVideo ? (
                  <VideoPlayer
                    videoSrc={videoUrl || "/video_20051225.mp4"}
                    onClose={() => setShowVideo(false)}
                  />
                ) : (
                  <>
                    {/* Watch Video Button */}
                    <button
                      onClick={() => setShowVideo(true)}
                      className="w-full mb-6 flex items-center justify-center space-x-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 px-4 rounded-2xl font-semibold shadow-lg hover:shadow-xl transition-all"
                    >
                      <Play className="w-5 h-5" />
                      <span>{t.watchVideo}</span>
                    </button>

                    {/* Guide Content */}
                    <div className="space-y-4 text-sm text-tech-text leading-relaxed">
                      <div>
                        <h3 className="font-bold text-base mb-2 flex items-center">
                          <span className="mr-2">📱</span>
                          {t.alipayGuideStep1}
                        </h3>
                        <p className="text-tech-sub ml-6">{t.alipayGuideStep1Desc}</p>
                      </div>

                      <div>
                        <h3 className="font-bold text-base mb-2 flex items-center">
                          <span className="mr-2">⏳</span>
                          {t.alipayGuideStep2}
                        </h3>
                        <p className="text-tech-sub ml-6">{t.alipayGuideStep2Desc}</p>
                      </div>

                      <div>
                        <h3 className="font-bold text-base mb-2 flex items-center">
                          <span className="mr-2">🔔</span>
                          {t.alipayGuideStep3}
                        </h3>
                        <p className="text-tech-sub ml-6">{t.alipayGuideStep3Desc}</p>
                        <div className="ml-6 mt-2 p-3 bg-blue-50 rounded-xl border border-blue-200">
                          <p className="text-blue-700 font-semibold">{t.alipayGuideStep3Important}</p>
                        </div>
                      </div>

                      <div>
                        <h3 className="font-bold text-base mb-2 flex items-center">
                          <span className="mr-2">💳</span>
                          {t.alipayGuideStep4}
                        </h3>
                        <p className="text-tech-sub ml-6">{t.alipayGuideStep4Desc}</p>
                      </div>

                      <div>
                        <h3 className="font-bold text-base mb-2 flex items-center">
                          <span className="mr-2">✅</span>
                          {t.alipayGuideStep5}
                        </h3>
                        <p className="text-tech-sub ml-6">{t.alipayGuideStep5Desc}</p>
                      </div>

                      {/* Tips */}
                      <div className="mt-6 p-4 bg-amber-50 rounded-xl border border-amber-200">
                        <h4 className="font-bold text-amber-800 mb-2">💡 {t.alipayGuideTips}</h4>
                        <ul className="text-amber-700 text-xs space-y-1 ml-4 list-disc">
                          <li>{t.alipayGuideTip1}</li>
                          <li>{t.alipayGuideTip2}</li>
                        </ul>
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* Footer Buttons */}
              {!showVideo && (
                <div className="p-4 border-t border-gray-100 space-y-2">
                  <button
                    onClick={handleConfirm}
                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-2xl font-semibold shadow-lg hover:bg-blue-700 transition-all flex items-center justify-center space-x-2"
                  >
                    <CheckCircle className="w-5 h-5" />
                    <span>{t.alipayGuideConfirm}</span>
                  </button>
                  <button
                    onClick={onClose}
                    className="w-full text-tech-sub py-2 px-4 rounded-xl font-medium hover:bg-gray-50 transition-colors"
                  >
                    {t.cancel}
                  </button>
                </div>
              )}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

