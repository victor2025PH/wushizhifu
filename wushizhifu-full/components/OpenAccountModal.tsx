import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, UserPlus, Phone, Lock, CheckCircle, AlertCircle } from 'lucide-react';
import { Language, TRANSLATIONS } from '../types';

interface OpenAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  lang: Language;
}

export const OpenAccountModal: React.FC<OpenAccountModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  lang
}) => {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [phone, setPhone] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [codeSent, setCodeSent] = useState(false);
  const [countdown, setCountdown] = useState(0);

  const t = TRANSLATIONS[lang];

  const handleClose = () => {
    setStep(1);
    setPhone('');
    setVerificationCode('');
    setPassword('');
    setConfirmPassword('');
    setAgreed(false);
    setError('');
    setCodeSent(false);
    setCountdown(0);
    onClose();
  };

  const handleSendCode = async () => {
    if (!phone || phone.length < 11) {
      setError('请输入正确的手机号码');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // TODO: 调用发送验证码 API
      // await apiClient.sendVerificationCode(phone);
      
      // 模拟 API 调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setCodeSent(true);
      setCountdown(60);
      
      // 倒计时
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
    } catch (err: any) {
      setError(err.message || '发送验证码失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    setError('');

    // 验证
    if (!phone || phone.length < 11) {
      setError('请输入正确的手机号码');
      return;
    }

    if (!verificationCode || verificationCode.length !== 6) {
      setError('请输入6位验证码');
      return;
    }

    if (!password || password.length < 6) {
      setError('支付密码至少6位');
      return;
    }

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (!agreed) {
      setError('请阅读并同意《用户协议》');
      return;
    }

    setLoading(true);

    try {
      // TODO: 调用开户 API
      // const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://50zf.usdt2026.cc/api';
      // const response = await fetch(`${API_BASE_URL}/account/open`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'X-Telegram-Init-Data': window.Telegram?.WebApp?.initData || ''
      //   },
      //   body: JSON.stringify({
      //     phone,
      //     verification_code: verificationCode,
      //     payment_password: password
      //   })
      // });

      // if (!response.ok) {
      //   const error = await response.json();
      //   throw new Error(error.detail || '开户失败');
      // }

      // 模拟 API 调用
      await new Promise(resolve => setTimeout(resolve, 1500));

      // 开户成功
      setStep(3);
      setTimeout(() => {
        onSuccess();
        handleClose();
      }, 2000);

    } catch (err: any) {
      setError(err.message || '开户失败，请重试');
    } finally {
      setLoading(false);
    }
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
            onClick={handleClose}
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
                <h2 className="text-lg font-bold text-tech-text flex items-center space-x-2">
                  <UserPlus className="w-5 h-5 text-champagne-600" />
                  <span>{t.openAccount}</span>
                </h2>
                <button
                  onClick={handleClose}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  aria-label="Close"
                >
                  <X className="w-5 h-5 text-tech-sub" />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {step === 1 && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-tech-text mb-2">
                        手机号码
                      </label>
                      <div className="flex space-x-2">
                        <input
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                          placeholder="请输入手机号码"
                          maxLength={11}
                          className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:border-champagne-400 focus:ring-2 focus:ring-champagne-200 outline-none transition-all"
                        />
                        <button
                          onClick={handleSendCode}
                          disabled={loading || countdown > 0 || !phone}
                          className="px-4 py-3 bg-champagne-500 text-white rounded-xl font-semibold hover:bg-champagne-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
                        >
                          {countdown > 0 ? `${countdown}秒` : codeSent ? '重新发送' : '获取验证码'}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-tech-text mb-2">
                        验证码
                      </label>
                      <input
                        type="text"
                        value={verificationCode}
                        onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                        placeholder="请输入6位验证码"
                        maxLength={6}
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-champagne-400 focus:ring-2 focus:ring-champagne-200 outline-none transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-tech-text mb-2">
                        设置支付密码
                      </label>
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="至少6位数字或字母"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-champagne-400 focus:ring-2 focus:ring-champagne-200 outline-none transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-tech-text mb-2">
                        确认支付密码
                      </label>
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="请再次输入支付密码"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-champagne-400 focus:ring-2 focus:ring-champagne-200 outline-none transition-all"
                      />
                    </div>

                    <div className="flex items-start space-x-2">
                      <input
                        type="checkbox"
                        id="agree"
                        checked={agreed}
                        onChange={(e) => setAgreed(e.target.checked)}
                        className="mt-1 w-4 h-4 text-champagne-600 border-gray-300 rounded focus:ring-champagne-500"
                      />
                      <label htmlFor="agree" className="text-sm text-tech-sub">
                        我已阅读并同意
                        <a href="#" className="text-champagne-600 hover:underline ml-1">《用户协议》</a>
                        和
                        <a href="#" className="text-champagne-600 hover:underline ml-1">《隐私政策》</a>
                      </label>
                    </div>

                    {error && (
                      <div className="flex items-center space-x-2 text-red-500 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        <span>{error}</span>
                      </div>
                    )}

                    <button
                      onClick={handleSubmit}
                      disabled={loading || !agreed}
                      className="w-full py-3 bg-gradient-to-r from-champagne-500 to-champagne-600 text-white rounded-xl font-semibold hover:shadow-lg disabled:bg-gray-300 disabled:cursor-not-allowed transition-all"
                    >
                      {loading ? '提交中...' : '提交开户'}
                    </button>
                  </div>
                )}

                {step === 3 && (
                  <div className="flex flex-col items-center justify-center py-8 space-y-4">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-10 h-10 text-green-600" />
                    </div>
                    <h3 className="text-xl font-bold text-tech-text">开户成功！</h3>
                    <p className="text-sm text-tech-sub text-center">
                      您的账户已成功开通，现在可以开始使用所有功能了
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

