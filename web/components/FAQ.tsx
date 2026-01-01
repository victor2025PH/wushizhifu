import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface FAQItemProps {
  question: string;
  answer: string;
}

const FAQItem: React.FC<FAQItemProps> = ({ question, answer }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-slate-200 dark:border-white/10 last:border-0">
      <button
        className="flex justify-between items-center w-full py-6 text-left focus:outline-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="text-lg font-medium text-slate-900 dark:text-white pr-4">{question}</span>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-blue-600 dark:text-brand-blue flex-shrink-0" />
        ) : (
          <ChevronDown className="w-5 h-5 text-slate-400 flex-shrink-0" />
        )}
      </button>
      {isOpen && (
        <div className="pb-6 pr-4">
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
            {answer}
          </p>
        </div>
      )}
    </div>
  );
};

export const FAQ: React.FC = () => {
  const faqs = [
    {
      question: "资金是如何结算的？支持哪些币种？",
      answer: "我们采用 D0 实时结算系统。用户的法币（人民币）支付成功后，系统会自动将其兑换为 USDT (TRC20)，并实时划转到您在 Telegram 机器人绑定的钱包地址中。全程自动化，无人工干预。"
    },
    {
      question: "如何防止我的收款码被风控冻结？",
      answer: "伍拾支付独创的『熔断防御机制』会实时监控订单投诉率。一旦监测到恶意投诉或异常高频交易，系统会自动触发退款或轮询切换收款码，将风险扼杀在摇篮中，最大程度保护您的原生收款账号。"
    },
    {
      question: "接入需要提供营业执照或实名信息吗？",
      answer: "不需要。我们主打隐私保护与极速接入。您只需要一个 Telegram 账号即可开始使用。没有繁琐的 KYC 流程，保护您的商业隐私。"
    },
    {
      question: "手续费是多少？有开户费吗？",
      answer: "目前公测期间，免收开户费和年费。我们仅在每笔交易成功时收取少量手续费（具体费率请在机器人内查看）。不成功不收费。"
    }
  ];

  return (
    <section className="py-24 bg-white dark:bg-slate-950 transition-colors duration-300">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">常见问题解答</h2>
          <p className="text-slate-600 dark:text-slate-400">
            如果您有更多疑问，欢迎加入我们的 Telegram 官方群组咨询。
          </p>
        </div>
        <div className="bg-slate-50 dark:bg-slate-900 rounded-2xl p-6 sm:p-8 border border-slate-200 dark:border-white/5">
          {faqs.map((faq, index) => (
            <FAQItem key={index} question={faq.question} answer={faq.answer} />
          ))}
        </div>
      </div>
    </section>
  );
};