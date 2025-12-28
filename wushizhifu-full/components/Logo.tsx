import React from 'react';

interface LogoProps {
  className?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

/**
 * Logo component that displays the WuShiPay logo image
 * Supports responsive sizing and maintains aspect ratio
 */
export const Logo: React.FC<LogoProps> = ({ className = '', size = 'md' }) => {
  const sizeClasses = {
    xs: 'w-[18px] h-[18px]',  // 18px
    sm: 'w-8 h-8',            // 32px
    md: 'w-9 h-9',            // 36px (default)
    lg: 'w-12 h-12',          // 48px
    xl: 'w-16 h-16',          // 64px
  };

  return (
    <img
      src="/logo_300.png"
      alt="WuShiPay Logo"
      className={`${sizeClasses[size]} object-contain ${className}`}
      style={{
        width: 'auto',
        height: 'auto',
        maxWidth: '100%',
        maxHeight: '100%',
      }}
      onError={(e) => {
        // Fallback if image fails to load
        console.error('Failed to load logo image');
        e.currentTarget.style.display = 'none';
      }}
    />
  );
};

