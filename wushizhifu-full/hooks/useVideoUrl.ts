/**
 * Hook to get video URL for payment tutorials
 * @param videoType 'wechat' or 'alipay'
 * @returns video URL
 */
export function useVideoUrl(videoType: 'wechat' | 'alipay'): string | null {
  // Fixed video URLs
  const VIDEO_URLS = {
    alipay: 'https://50pay.xingaochengtai.com/video/tut/tut01.mp4',
    wechat: 'https://50pay.xingaochengtai.com/video/tut/tut02.mp4'
  };

  return VIDEO_URLS[videoType] || null;
}

