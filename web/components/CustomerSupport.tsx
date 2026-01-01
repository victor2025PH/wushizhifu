import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Phone, User, Bot, Loader2 } from 'lucide-react';
import { assignCustomerService, openSupportChat } from '../utils/supportService';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  type: 'text' | 'contact_card';
  timestamp: Date;
}

export const CustomerSupport: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showTooltip, setShowTooltip] = useState(true);
  const [isAssigning, setIsAssigning] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome-1',
      text: '您好！我是伍拾支付的智能助手。',
      sender: 'agent',
      type: 'text',
      timestamp: new Date()
    },
    {
      id: 'welcome-card',
      text: '',
      sender: 'agent',
      type: 'contact_card',
      timestamp: new Date()
    }
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen, isTyping]);

  useEffect(() => {
    if (isOpen) {
      setShowTooltip(false);
    }
  }, [isOpen]);

  const handleTelegramClick = async (e: React.MouseEvent<HTMLAnchorElement>) => {
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

  const handleSendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      type: 'text',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    // Simulate agent reply delay
    setTimeout(() => {
      setIsTyping(false);
      const replyMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: '收到您的消息！我们的人工客服 24 小时在线。为确保资金安全与即时响应，请直接点击上方的 Telegram 或 WhatsApp 按钮与我们建立加密对话。',
        sender: 'agent',
        type: 'text',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, replyMsg]);
    }, 1500);
  };

  return (
    <div className="fixed bottom-8 sm:bottom-12 right-6 z-50 flex flex-col items-end font-sans pointer-events-none">
      {/* Chat Window (Enable pointer events) */}
      <div className="pointer-events-auto">
        {isOpen && (
          <div className="mb-4 w-[340px] sm:w-[380px] h-[500px] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-white/10 overflow-hidden flex flex-col transform transition-all duration-300 origin-bottom-right animate-in fade-in slide-in-from-bottom-4">
            
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-brand-blue dark:to-blue-700 p-4 flex justify-between items-center shrink-0 relative overflow-hidden">
               {/* Background Effects */}
              <div className="absolute top-0 right-0 -mt-4 -mr-4 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
              
              <div className="relative z-10 flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center border border-white/30 backdrop-blur-sm">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 border-2 border-blue-600 rounded-full"></div>
                </div>
                <div>
                  <h3 className="text-white font-bold text-lg leading-tight">在线客服支持</h3>
                  <div className="flex items-center gap-1.5 text-blue-100 text-xs mt-0.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
                    <span className="font-medium">7*24小时在线服务</span>
                  </div>
                </div>
              </div>

              <button 
                onClick={() => setIsOpen(false)}
                className="relative z-10 text-white/80 hover:text-white transition-colors p-1.5 rounded-full hover:bg-white/10"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Chat Body */}
            <div className="flex-1 overflow-y-auto p-4 bg-slate-50 dark:bg-slate-950/50 space-y-4 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-700">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex gap-2 max-w-[85%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    
                    {/* Avatar */}
                    <div className="shrink-0 mt-1">
                      {msg.sender === 'agent' ? (
                        <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-slate-800 flex items-center justify-center">
                          <Bot className="w-4 h-4 text-blue-600 dark:text-brand-blue" />
                        </div>
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                          <User className="w-4 h-4 text-slate-500 dark:text-slate-300" />
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div>
                      {msg.type === 'text' && (
                         <div className={`p-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                           msg.sender === 'user' 
                             ? 'bg-blue-600 text-white rounded-tr-none' 
                             : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-tl-none border border-slate-100 dark:border-white/5'
                         }`}>
                           {msg.text}
                         </div>
                      )}

                      {msg.type === 'contact_card' && (
                        <div className="space-y-3 bg-white dark:bg-slate-800 p-3 rounded-2xl rounded-tl-none border border-slate-100 dark:border-white/5 shadow-sm w-full">
                           <p className="text-sm text-slate-600 dark:text-slate-300 mb-2">
                             遇到支付问题或想咨询费率？请选择下方渠道联系人工客服：
                           </p>
                          
                          <a 
                            href="https://t.me/PayShieldSupport" 
                            onClick={handleTelegramClick}
                            className={`flex items-center gap-3 p-3 rounded-xl bg-[#0088cc]/10 hover:bg-[#0088cc]/20 border border-[#0088cc]/20 transition-all group ${isAssigning ? 'opacity-50 cursor-wait' : 'cursor-pointer'}`}
                          >
                            <div className="w-9 h-9 rounded-full bg-[#0088cc] flex items-center justify-center text-white shrink-0 shadow-lg shadow-[#0088cc]/20">
                              {isAssigning ? (
                                <Loader2 className="w-4 h-4 ml-0.5 animate-spin" />
                              ) : (
                                <Send className="w-4 h-4 ml-0.5" />
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-slate-900 dark:text-white text-sm">Telegram</span>
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400 font-bold">推荐</span>
                              </div>
                              <div className="text-xs text-slate-500 dark:text-slate-400 truncate">
                                {isAssigning ? '正在分配客服...' : '点击分配客服'}
                              </div>
                            </div>
                          </a>

                          <a 
                            href="https://wa.me/1234567890" 
                            target="_blank" 
                            rel="noreferrer"
                            className="flex items-center gap-3 p-3 rounded-xl bg-[#25D366]/10 hover:bg-[#25D366]/20 border border-[#25D366]/20 transition-all group"
                          >
                            <div className="w-9 h-9 rounded-full bg-[#25D366] flex items-center justify-center text-white shrink-0 shadow-lg shadow-[#25D366]/20">
                              <Phone className="w-4 h-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="font-bold text-slate-900 dark:text-white text-sm">WhatsApp</div>
                              <div className="text-xs text-slate-500 dark:text-slate-400 truncate">+1 (234) 567-890</div>
                            </div>
                          </a>
                        </div>
                      )}
                      
                      {/* Timestamp */}
                      <div className={`text-[10px] text-slate-400 mt-1 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                         {msg.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
                   <div className="flex gap-2 max-w-[85%]">
                      <div className="shrink-0 mt-1">
                        <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-slate-800 flex items-center justify-center">
                          <Bot className="w-4 h-4 text-blue-600 dark:text-brand-blue" />
                        </div>
                      </div>
                      <div className="bg-white dark:bg-slate-800 p-3 rounded-2xl rounded-tl-none border border-slate-100 dark:border-white/5 flex items-center gap-2">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-blue-500 dark:bg-brand-blue rounded-full animate-bounce"></span>
                          <span className="w-2 h-2 bg-blue-500 dark:bg-brand-blue rounded-full animate-bounce [animation-delay:0.2s]"></span>
                          <span className="w-2 h-2 bg-blue-500 dark:bg-brand-blue rounded-full animate-bounce [animation-delay:0.4s]"></span>
                        </div>
                        <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">正在输入...</span>
                      </div>
                   </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Footer / Input Area */}
            <div className="p-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-white/10">
              <form onSubmit={handleSendMessage} className="relative flex items-center gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="请输入您的问题..."
                  className="w-full bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 text-sm rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                />
                <button 
                  type="submit"
                  disabled={!inputValue.trim() || isTyping}
                  className="absolute right-2 p-1.5 bg-blue-600 dark:bg-brand-blue text-white dark:text-slate-900 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 transition-opacity"
                >
                  {isTyping ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>

      {/* Floating Trigger Container (Enable pointer events) */}
      <div className="relative pointer-events-auto flex items-center justify-end">
        
        {/* Helper Tooltip */}
        {!isOpen && showTooltip && (
           <div className="absolute right-16 top-1/2 -translate-y-1/2 mr-3 whitespace-nowrap origin-right animate-in slide-in-from-right-4 fade-in duration-500 z-50">
              <div 
                className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm text-slate-900 dark:text-white pl-4 pr-5 py-3 rounded-2xl shadow-2xl border border-blue-200 dark:border-brand-blue/30 flex items-center gap-3 cursor-pointer hover:scale-105 transition-all group relative overflow-hidden animate-[float_4s_ease-in-out_infinite]" 
                onClick={() => setIsOpen(true)}
              >
                 {/* Shimmer effect */}
                 <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full animate-[shimmer_3s_infinite] pointer-events-none"></div>

                 <span className="relative flex h-3 w-3 shrink-0">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                 </span>
                 
                 <div className="flex flex-col relative z-10">
                    <span className="text-[10px] uppercase tracking-wider text-slate-500 dark:text-slate-400 font-bold mb-0.5">VIP 通道</span>
                    <span className="text-sm font-black bg-gradient-to-r from-blue-700 via-blue-600 to-purple-600 dark:from-white dark:via-blue-200 dark:to-brand-blue bg-clip-text text-transparent drop-shadow-sm">
                      点击联系客服，立刻免费秒开户
                    </span>
                 </div>

                 {/* Arrow */}
                 <div className="absolute right-[-8px] top-1/2 -translate-y-1/2 w-0 h-0 border-t-[8px] border-t-transparent border-b-[8px] border-b-transparent border-l-[10px] border-l-white dark:border-l-slate-800/95"></div>
              </div>
           </div>
        )}

        {/* Ripple Animation Layers */}
        {!isOpen && (
            <>
              <span className="absolute top-0 left-0 h-full w-full rounded-full bg-blue-400 dark:bg-brand-blue opacity-20 animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite]"></span>
              <span className="absolute top-0 left-0 h-full w-full rounded-full bg-blue-400 dark:bg-brand-blue opacity-10 animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite_delay-300]"></span>
            </>
        )}

        {/* Main Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`relative group flex items-center justify-center w-14 h-14 rounded-full shadow-lg transition-all duration-300 transform hover:scale-110 z-50 ${
            isOpen 
              ? 'bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-300 rotate-90' 
              : 'bg-blue-600 text-white dark:bg-brand-blue dark:text-slate-900 shadow-blue-600/40 dark:shadow-[0_0_25px_rgba(0,240,255,0.5)]'
          }`}
          aria-label="联系客服"
        >
          {isOpen ? (
            <X className="w-6 h-6 transition-transform duration-300" />
          ) : (
            <div className="relative">
              <MessageCircle className="w-7 h-7 animate-[wiggle_3s_ease-in-out_infinite]" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500 border border-white dark:border-slate-900"></span>
              </span>
            </div>
          )}
        </button>
      </div>
      
      {/* Custom Keyframe Styles for Wiggle and Shimmer */}
      <style>{`
        @keyframes wiggle {
          0%, 100% { transform: rotate(0deg); }
          5% { transform: rotate(-10deg); }
          10% { transform: rotate(10deg); }
          15% { transform: rotate(-10deg); }
          20% { transform: rotate(0deg); }
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
};