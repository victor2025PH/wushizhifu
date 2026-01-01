import React from 'react';

export interface TickerItem {
  id: string;
  text: string;
  type: 'withdrawal' | 'defense' | 'new_user';
  timestamp: string;
}

export interface FeatureProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}