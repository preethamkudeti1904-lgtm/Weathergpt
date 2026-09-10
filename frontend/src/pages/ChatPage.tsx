import React from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { ChatInterface } from '../components/chat/ChatInterface';

export const ChatPage: React.FC = () => {
  const { location } = useWeather();

  return (
    <div className="space-y-4 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">
          WeatherGPT Conversational Assistant
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Ask natural-language questions grounded strictly in verifiable weather observations
        </p>
      </div>

      <ChatInterface />
    </div>
  );
};
