import { useState, useEffect } from 'react';

// API base URL - use same as api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://50zf.usdt2026.cc/api';

interface VideoUrlResponse {
  url: string;
  file_id: string;
  file_path: string;
  updated_at?: string;
}

/**
 * Hook to fetch video URL from backend API
 * @param videoType 'wechat' or 'alipay'
 * @returns video URL or null if not available
 */
export function useVideoUrl(videoType: 'wechat' | 'alipay'): string | null {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchVideoUrl() {
      try {
        const endpoint = videoType === 'wechat' ? '/videos/wechat' : '/videos/alipay';
        const response = await fetch(`${API_BASE_URL}${endpoint}`);

        if (!response.ok) {
          console.warn(`Failed to fetch ${videoType} video URL: ${response.statusText}`);
          return;
        }

        const data: VideoUrlResponse = await response.json();
        
        if (!cancelled && data.url) {
          setVideoUrl(data.url);
        }
      } catch (error) {
        console.error(`Error fetching ${videoType} video URL:`, error);
      }
    }

    fetchVideoUrl();

    return () => {
      cancelled = true;
    };
  }, [videoType]);

  return videoUrl;
}

