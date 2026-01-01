import React, { useState } from 'react';
import { Code, ChevronRight, Copy, Check } from 'lucide-react';

export const DeveloperSection: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'python' | 'node' | 'php' | 'go'>('python');
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    const code = codeSnippets[activeTab];
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const codeSnippets = {
    python: `import requests

url = "https://api.payshield.com/v1/create_order"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
payload = {
    "amount": 100.00,
    "currency": "CNY",
    "order_id": "ORD_20240315_001",
    "notify_url": "https://your-site.com/callback"
}

# 发起请求
response = requests.post(url, json=payload, headers=headers)
print(response.json())`,
    node: `const axios = require('axios');

const createOrder = async () => {
  const url = 'https://api.payshield.com/v1/create_order';
  const config = {
    headers: { 
      'Authorization': 'Bearer YOUR_API_KEY',
      'Content-Type': 'application/json'
    }
  };
  const payload = {
    amount: 100.00,
    currency: 'CNY',
    order_id: 'ORD_20240315_001',
    notify_url: 'https://your-site.com/callback'
  };

  try {
    const res = await axios.post(url, payload, config);
    console.log(res.data);
  } catch (err) {
    console.error(err);
  }
};

createOrder();`,
    php: `<?php
$url = "https://api.payshield.com/v1/create_order";
$data = [
    "amount" => 100.00,
    "currency" => "CNY",
    "order_id" => "ORD_20240315_001",
    "notify_url" => "https://your-site.com/callback"
];

$options = [
    "http" => [
        "header" => "Authorization: Bearer YOUR_API_KEY\r\n" .
                    "Content-Type: application/json\r\n",
        "method" => "POST",
        "content" => json_encode($data)
    ]
];

$context = stream_context_create($options);
$result = file_get_contents($url, false, $context);
echo $result;
?>`,
    go: `package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

func main() {
	url := "https://api.payshield.com/v1/create_order"
	payload := map[string]interface{}{
		"amount":     100.00,
		"currency":   "CNY",
		"order_id":   "ORD_20240315_001",
        "notify_url": "https://your-site.com/callback",
	}
	jsonPayload, _ := json.Marshal(payload)

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonPayload))
	req.Header.Set("Authorization", "Bearer YOUR_API_KEY")
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, _ := client.Do(req)
	defer resp.Body.Close()
    
    // Handle response...
    fmt.Println("Order Created")
}`
  };

  return (
    <section id="api" className="py-24 bg-white dark:bg-slate-900/50 border-y border-slate-200 dark:border-white/5 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:grid lg:grid-cols-2 lg:gap-16 items-center">
          
          <div className="mb-12 lg:mb-0">
            <div className="flex items-center gap-2 text-blue-600 dark:text-brand-blue font-bold mb-6">
              <Code className="w-5 h-5" />
              <span>DEVELOPER FIRST</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 dark:text-white mb-6">
              5分钟极速集成 <br />
              <span className="text-slate-500 dark:text-slate-400">标准化 REST API</span>
            </h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg mb-8 leading-relaxed">
              无论您使用 Python, Node.js, PHP 还是 Go，我们都提供简洁清晰的文档。
              支持 Webhook 异步回调，确保订单状态 100% 同步。
            </p>
            
            <ul className="space-y-4 mb-8">
              {['RESTful 架构', 'RSA/MD5 双重签名', '沙箱测试环境', '99.99% API 可用性'].map((item, i) => (
                <li key={i} className="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-brand-purple"></div>
                  {item}
                </li>
              ))}
            </ul>

            <a href="#" className="inline-flex items-center text-blue-600 dark:text-brand-blue font-bold hover:text-blue-800 dark:hover:text-white transition-colors">
              查看完整 API 文档 <ChevronRight className="w-4 h-4 ml-1" />
            </a>
          </div>

          <div className="relative">
            {/* Glow effect - Dark mode only */}
            <div className="hidden dark:block absolute -inset-1 bg-gradient-to-r from-brand-blue to-brand-purple rounded-2xl blur opacity-20"></div>
            
            <div className="relative rounded-2xl bg-slate-900 dark:bg-[#0d1117] border border-slate-200 dark:border-white/10 overflow-hidden shadow-2xl flex flex-col h-[500px]">
              {/* Toolbar */}
              <div className="flex items-center justify-between px-4 py-3 bg-white/5 border-b border-white/5 shrink-0">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <div className="flex gap-4">
                    {(Object.keys(codeSnippets) as Array<keyof typeof codeSnippets>).map((lang) => (
                        <button
                            key={lang}
                            onClick={() => setActiveTab(lang)}
                            className={`text-xs font-bold uppercase transition-colors ${
                                activeTab === lang 
                                ? 'text-blue-400 dark:text-brand-blue' 
                                : 'text-slate-500 hover:text-slate-300'
                            }`}
                        >
                            {lang}
                        </button>
                    ))}
                </div>
              </div>

              {/* Code Area */}
              <div className="relative flex-1 overflow-auto p-6 group">
                 <button 
                    onClick={copyToClipboard}
                    className="absolute top-4 right-4 p-2 rounded-lg bg-white/10 text-slate-400 opacity-0 group-hover:opacity-100 transition-all hover:bg-white/20 hover:text-white"
                 >
                    {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                 </button>
                <pre className="font-mono text-sm leading-relaxed">
                  <code className="text-slate-300 block">
                    {codeSnippets[activeTab]}
                  </code>
                </pre>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};