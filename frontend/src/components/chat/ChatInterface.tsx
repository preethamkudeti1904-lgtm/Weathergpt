import React, { useState, useEffect, useRef } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';
import { ChatMessageItem, ConversationSummary } from '../../types';
import {
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Trash2,
  Bot,
  User,
  Sparkles,
  MapPin,
  Clock,
  ShieldAlert,
  MessageSquare,
  Plus,
  Search,
  MoreVertical,
  Edit2,
  Menu,
  X,
  History,
  Check,
  AlertTriangle
} from 'lucide-react';

const SUGGESTED_QUESTIONS_BY_LANG: Record<string, (loc: string) => string[]> = {
  en: (loc) => [
    `Have you ate?`,
    `How are you?`,
    `What is the temperature now in ${loc}?`,
    `Will it rain today in ${loc}?`,
    `Are there any active disaster warnings?`,
    `Has this place experienced floods before?`,
    `How do I change the language or use GPS?`
  ],
  te: (loc) => [
    `ఎలా ఉన్నావు?`,
    `${loc} లో ఇప్పుడు ఉష్ణోగ్రత ఎంత?`,
    `ఈరోజు ${loc} లో వర్షం పడుతుందా?`,
    `ఏవైనా అధికారిక విపత్తు హెచ్చరికలు ఉన్నాయా?`,
    `గతంలో ఇక్కడ వరదలు లేదా తుఫానులు వచ్చాయా?`,
    `ఈ వెబ్‌సైట్‌ను ఎలా ఉపయోగించాలి?`
  ],
  hi: (loc) => [
    `आप कैसे हैं?`,
    `${loc} में वर्तमान तापमान कितना है?`,
    `क्या आज ${loc} में बारिश होगी?`,
    `क्या कोई आधिकारिक आपदा चेतावनी सक्रिय है?`,
    `क्या यहाँ पहले कभी बाढ़ या चक्रवात आया था?`,
    `इस वेबसाइट का उपयोग कैसे करें?`
  ],
  ta: (loc) => [
    `நீங்கள் எப்படி இருக்கிறீர்கள்?`,
    `${loc} இல் தற்போதைய வெப்பநிலை என்ன?`,
    `இன்று ${loc} இல் மழை பெய்யுமா?`,
    `ஏதேனும் பேரிடர் எச்சரிக்கைகள் செயலில் உள்ளதா?`,
    `இந்த இணையதளத்தை எவ்வாறு பயன்படுத்துவது?`
  ],
  kn: (loc) => [
    `ನೀವು ಹೇಗಿದ್ದೀರಿ?`,
    `${loc} ನಲ್ಲಿ ಪ್ರಸ್ತುತ ತಾಪಮಾನ ಎಷ್ಟು?`,
    `ಇಂದು ${loc} ನಲ್ಲಿ ಮಳೆ ಬರುತ್ತದೆಯೇ?`,
    `ಯಾವುದಾದರೂ ಅಧಿಕೃತ ವಿపತ್ತು ಎಚ್ಚರಿಕೆಗಳಿವೆಯೇ?`,
    `ಈ ವೆಬ್‌ಸೈಟ್ ಅನ್ನು ಹೇಗೆ ಬಳಸುವುದು?`
  ],
  ml: (loc) => [
    `സുഖമാണോ?`,
    `${loc} ലെ ഇപ്പോഴത്തെ താപനില എത്രയാണ്?`,
    `ഇന്ന് ${loc} ൽ മഴ പെയ്യുമോ?`,
    `എന്തെങ്കിലും ഔദ്യോഗിക മുന്നറിയിപ്പുകൾ ഉണ്ടോ?`,
    `ഈ വെബ്സൈറ്റ് എങ്ങനെ ഉപയോഗിക്കാം?`
  ],
  mr: (loc) => [
    `तुम्ही कसे आहात?`,
    `${loc} मधील सध्याचे तापमान किती आहे?`,
    `आज ${loc} मध्ये पाऊस पडेल का?`,
    `काही अधिकृत आपत्कालीन इशारे सक्रिय आहेत का?`,
    `ही वेबसाइट कशी वापरावी?`
  ],
  bn: (loc) => [
    `আপনি কেমন আছেন?`,
    `${loc}-এ বর্তমান তাপমাত্রা কত?`,
    `আজ ${loc}-এ কি বৃষ্টি হবে?`,
    `কোনো সরকারি দুর্যোগ সতর্কতা জারি আছে কি?`,
    `এই ওয়েবসাইট কীভাবে ব্যবহার করবেন?`
  ]
};

const WELCOME_MESSAGES_BY_LANG: Record<string, (loc: string, lat: number, lon: number) => string> = {
  en: (loc, lat, lon) =>
    `Hello! I am WeatherGPT, your conversational weather and website assistant for ${loc} (${lat.toFixed(3)}°, ${lon.toFixed(3)}°).\n\nFeel free to chat casually, ask about current temperatures, rain projections, official warnings (SACHET/NDMA), historical disaster records, or how to use this platform.`,
  te: (loc, lat, lon) =>
    `నమస్కారం! నేను WeatherGPT, ${loc} (${lat.toFixed(3)}°, ${lon.toFixed(3)}°) కోసం మీ సంభాషణాత్మక వాతావరణ మరియు వెబ్‌సైట్ సహాయకుడిని.\n\nమీరు సహజంగా మాట్లాడవచ్చు లేదా తాజా ఉష్ణోగ్రత, వర్ష సూచన, అధికారిక హెచ్చరికలు, చారిత్రక రికార్డులు లేదా వెబ్‌సైట్ గురించి నన్ను అడగవచ్చు.`,
  hi: (loc, lat, lon) =>
    `नमस्ते! मैं WeatherGPT हूँ, ${loc} (${lat.toFixed(3)}°, ${lon.toFixed(3)}°) के लिए आपका संवादात्मक मौसम और वेबसाइट सहायक।\n\nआप सामान्य बातचीत कर सकते हैं या ताज़ा तापमान, बारिश, आधिकारिक चेतावनियाँ, आपदा इतिहास या वेबसाइट सहायता मांग सकते हैं।`,
  ta: (loc, lat, lon) =>
    `வணக்கம்! நான் WeatherGPT, ${loc} (${lat.toFixed(3)}°, ${lon.toFixed(3)}°) பகுதிக்கான உங்கள் வானிலை மற்றும் இணையதள உதவியாளர்.\n\nஇயல்பாக பேசலாம் அல்லது தற்போதைய வெப்பநிலை, மழை, எச்சரிக்கைகள் பற்றி கேட்கலாம்.`,
  kn: (loc, lat, lon) =>
    `ನಮಸ್ಕಾರ! ನಾನು WeatherGPT, ${loc} ಗಾಗಿ ನಿಮ್ಮ ಹವಾಮಾನ ಮತ್ತು ವೆಬ್‌ಸೈಟ್ ಸಹಾಯಕ. ನೀವು ಸಾಮಾನ್ಯವಾಗಿ ಮಾತನಾಡಬಹುದು ಅಥವಾ ಹವಾಮಾನ, ಮಳೆ, ಎಚ್ಚರಿಕೆಗಳ ಬಗ್ಗೆ ಕೇಳಬಹುದು.`,
  ml: (loc, lat, lon) =>
    `നമസ്കാരം! ഞാൻ WeatherGPT, ${loc} ലേക്കുള്ള നിങ്ങളുടെ കാലാവസ്ഥാ സഹായ അസിസ്റ്റന്റ്. സാധാരണ സംഭാഷണങ്ങൾ നടത്താം അല്ലെങ്കിൽ കാലാവസ്ഥയെക്കുറിച്ച് ചോദിക്കാം.`,
  mr: (loc, lat, lon) =>
    `नमस्कार! मी WeatherGPT आहे, ${loc} साठी आपला हवामान व वेबसाइट सहाय्यक. आपण सहज संवाद साधू शकता किंवा हवामानाविषयी विचारू शकता.`,
  bn: (loc, lat, lon) =>
    `নমস্কার! আমি WeatherGPT, ${loc}-এর জন্য আপনার আবহাওয়া এবং ওয়েবসাইট সহকারী। আপনি স্বাভাবিকভাবে কথা বলতে পারেন বা আবহাওয়া সম্পর্কে জানতে পারেন।`
};

export const ChatInterface: React.FC = () => {
  const { currentLocation, location, latitude, longitude, accuracy, locationSource, timezone, localTimeStr, language, t } = useWeather();
  const { user } = useAuth();

  const cityShort = currentLocation.name || location.split(',')[0].trim();

  // Dynamic welcome message generator
  const getWelcomeMessage = (): ChatMessageItem => {
    const welcomeGen = WELCOME_MESSAGES_BY_LANG[language] || WELCOME_MESSAGES_BY_LANG['en'];
    const suggestGen = SUGGESTED_QUESTIONS_BY_LANG[language] || SUGGESTED_QUESTIONS_BY_LANG['en'];
    return {
      id: 'welcome',
      role: 'assistant',
      content: welcomeGen(cityShort, latitude, longitude),
      source_attribution: 'WeatherGPT Conversational Assistant',
      updated_at: localTimeStr || new Date().toLocaleTimeString(),
      timestamp: new Date().toISOString(),
      suggested_questions: suggestGen(cityShort)
    };
  };

  const [messages, setMessages] = useState<ChatMessageItem[]>([getWelcomeMessage()]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sessionId, setSessionId] = useState<number | undefined>(undefined);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState<string | number | null>(null);

  // Chat History Sidebar State
  const [isHistoryOpen, setIsHistoryOpen] = useState(true);
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [searchHistory, setSearchHistory] = useState('');
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [activeMenuId, setActiveMenuId] = useState<number | null>(null);
  const [renamingId, setRenamingId] = useState<number | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);

  // Intent-specific loading status (Section 32)
  const [loadingText, setLoadingText] = useState('Thinking...');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Load conversations list
  const loadConversations = async (searchQuery?: string) => {
    try {
      setIsLoadingHistory(true);
      const list = await api.getConversations(searchQuery);
      setConversations(list);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [user]);

  // Debounced search for chat history (Section 31)
  useEffect(() => {
    const handler = setTimeout(() => {
      loadConversations(searchHistory);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchHistory]);

  // Update initial welcome message when location or language changes on fresh chat
  useEffect(() => {
    if (messages.length === 1 && messages[0].id === 'welcome') {
      setMessages([getWelcomeMessage()]);
    }
  }, [language, location]);

  // Auto-scroll on message update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  // Speech Recognition Setup
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;

      const langMap: Record<string, string> = {
        en: 'en-IN',
        hi: 'hi-IN',
        te: 'te-IN',
        ta: 'ta-IN',
        kn: 'kn-IN',
        ml: 'ml-IN',
        mr: 'mr-IN',
        bn: 'bn-IN'
      };
      recognition.lang = langMap[language] || 'en-IN';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };

      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);
      recognitionRef.current = recognition;
    }
  }, [language]);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert(t('voice_unsupported') || 'Speech recognition is not supported in this browser.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleSpeak = (text: string, msgId: string | number) => {
    if ('speechSynthesis' in window) {
      if (isSpeaking === msgId) {
        window.speechSynthesis.cancel();
        setIsSpeaking(null);
        return;
      }

      window.speechSynthesis.cancel();
      const cleanText = text.replace(/[*#•`🌡️🌤️💧💨⚠️🔴✅📅🏛️🛡️🌐]/g, '').trim();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.0;

      const voiceLangMap: Record<string, string> = {
        en: 'en-IN',
        hi: 'hi-IN',
        te: 'te-IN',
        ta: 'ta-IN',
        kn: 'kn-IN',
        ml: 'ml-IN',
        mr: 'mr-IN',
        bn: 'bn-IN'
      };
      utterance.lang = voiceLangMap[language] || 'en-IN';

      utterance.onend = () => setIsSpeaking(null);
      utterance.onerror = () => setIsSpeaking(null);
      setIsSpeaking(msgId);
      window.speechSynthesis.speak(utterance);
    }
  };

  // Determine intent-based loading state (Section 32)
  const determineLoadingState = (msg: string) => {
    const q = msg.toLowerCase();
    if (
      q.includes('alert') ||
      q.includes('warning') ||
      q.includes('cyclone') ||
      q.includes('disaster') ||
      q.includes('హెచ్చరిక') ||
      q.includes('चेतावनी') ||
      q.includes('ఎచ్చరిక')
    ) {
      return language === 'te'
        ? 'అధికారిక హెచ్చరికలను (SACHET/NDMA) తనిఖీ చేస్తోంది...'
        : language === 'hi'
        ? 'आधिकारिक चेतावनियों (SACHET/NDMA) की जांच की जा रही है...'
        : 'Checking official alerts...';
    }
    if (
      q.includes('past') ||
      q.includes('history') ||
      q.includes('flood') ||
      q.includes('record') ||
      q.includes('చరిత్ర') ||
      q.includes('గతం') ||
      q.includes('इतिहास')
    ) {
      return language === 'te'
        ? 'చారిత్రక విపత్తు రికార్డులను శోధిస్తోంది...'
        : language === 'hi'
        ? 'ऐतिहासिक आपदा अभिलेखों की जांच हो रही है...'
        : 'Checking historical records...';
    }
    if (
      q.includes('tomorrow') ||
      q.includes('forecast') ||
      q.includes('next week') ||
      q.includes('రేపు') ||
      q.includes('సూచన') ||
      q.includes('कल') ||
      q.includes('पूर्वानुमान')
    ) {
      return language === 'te'
        ? 'రాబోయే వాతావరణ సూచనను అంచనా వేస్తోంది...'
        : language === 'hi'
        ? 'मौसम पूर्वानुमान की गणना की जा रही है...'
        : 'Checking forecast data...';
    }
    if (
      q.includes('temp') ||
      q.includes('weather') ||
      q.includes('rain') ||
      q.includes('wind') ||
      q.includes('humid') ||
      q.includes('hot') ||
      q.includes('cold') ||
      q.includes('ఉష్ణోగ్రత') ||
      q.includes('వాతావరణం') ||
      q.includes('వర్షం') ||
      q.includes('तापमान') ||
      q.includes('मौसम') ||
      q.includes('बारिश')
    ) {
      return language === 'te'
        ? 'తాజా ప్రత్యక్ష వాతావరణ సమాచారాన్ని పొందుతోంది...'
        : language === 'hi'
        ? 'वर्तमान मौसम प्रेक्षणों की जांच की जा रही है...'
        : 'Checking current weather...';
    }
    return language === 'te' ? 'ఆలోచిస్తోంది...' : language === 'hi' ? 'सोच रहा हूँ...' : 'Thinking...';
  };

  // Send Message
  const handleSend = async (messageText?: string) => {
    const textToSend = (messageText || inputMessage).trim();
    if (!textToSend || isSending) return;

    const userMsg: ChatMessageItem = {
      id: Date.now(),
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsSending(true);
    setLoadingText(determineLoadingState(textToSend));

    try {
      const response = await api.sendChatMessage({
        message: textToSend,
        location: {
          latitude: currentLocation.latitude,
          longitude: currentLocation.longitude,
          accuracy: currentLocation.accuracy,
          name: currentLocation.name,
          city: currentLocation.city,
          district: currentLocation.district,
          state: currentLocation.state,
          country: currentLocation.country,
          timezone: currentLocation.timezone,
          source: currentLocation.source,
          timestamp: currentLocation.timestamp
        },
        location_name: currentLocation.name || location,
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        timezone: currentLocation.timezone || timezone,
        local_time: localTimeStr,
        language,
        user_type: user?.user_type || 'General User',
        session_id: sessionId
      });

      setSessionId(response.session_id);

      const assistantMsg: ChatMessageItem = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message || response.answer || '',
        intent: response.intent,
        advisory: response.advisory,
        source_attribution: response.source_attribution,
        updated_at: response.updated_at || response.data_timestamp,
        suggested_questions: response.suggested_questions,
        timestamp: new Date().toISOString()
      };

      setMessages((prev) => [...prev, assistantMsg]);
      // Refresh history list so new chat shows up immediately
      loadConversations();
    } catch (err: any) {
      const errorMsg: ChatMessageItem = {
        id: Date.now() + 1,
        role: 'assistant',
        content:
          language === 'te'
            ? 'సందేశాన్ని ప్రస్తుతం ప్రాసెస్ చేయలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి.'
            : language === 'hi'
            ? 'संदेश को अभी प्रोसेस नहीं किया जा सका। कृपया पुनः प्रयास करें।'
            : 'I could not process your message right now. Please try again shortly.',
        source_attribution: 'WeatherGPT System',
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  // Section 11: New Chat (+ New Chat)
  const handleNewChat = () => {
    setSessionId(undefined);
    setMessages([getWelcomeMessage()]);
    setIsMobileDrawerOpen(false);
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  };

  // Section 12: Open Old Chat (Loads complete conversation)
  const handleOpenConversation = async (convId: number) => {
    try {
      setIsSending(true);
      setLoadingText('Loading conversation history...');
      const details = await api.getConversationDetails(convId);
      setSessionId(details.id);

      if (details.messages && details.messages.length > 0) {
        const loadedMsgs: ChatMessageItem[] = details.messages.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          intent: m.intent,
          source_attribution: m.source_attribution || 'WeatherGPT Assistant',
          timestamp: m.timestamp || m.created_at || new Date().toISOString()
        }));
        setMessages(loadedMsgs);
      } else {
        setMessages([getWelcomeMessage()]);
      }
      setIsMobileDrawerOpen(false);
    } catch (err) {
      console.error('Failed to load conversation:', err);
    } finally {
      setIsSending(false);
    }
  };

  // Section 13: Rename Chat
  const handleStartRename = (conv: ConversationSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setRenamingId(conv.id);
    setRenameValue(conv.title);
    setActiveMenuId(null);
  };

  const handleSaveRename = async (convId: number, e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!renameValue.trim()) {
      setRenamingId(null);
      return;
    }
    try {
      await api.updateConversationTitle(convId, renameValue.trim());
      setConversations((prev) =>
        prev.map((c) => (c.id === convId ? { ...c, title: renameValue.trim() } : c))
      );
    } catch (err) {
      console.error('Failed to rename conversation:', err);
    } finally {
      setRenamingId(null);
    }
  };

  // Section 13: Delete Chat with Confirmation
  const handleDeleteConversation = async (convId: number) => {
    try {
      await api.deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (sessionId === convId) {
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    } finally {
      setDeleteConfirmId(null);
      setActiveMenuId(null);
    }
  };

  // Group conversations into Today, Yesterday, and Previous (Sections 9 & 30)
  const groupConversations = (list: ConversationSummary[]) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const groups: {
      today: ConversationSummary[];
      yesterday: ConversationSummary[];
      previous: ConversationSummary[];
    } = { today: [], yesterday: [], previous: [] };

    list.forEach((c) => {
      const itemDate = new Date(c.updated_at || c.created_at);
      itemDate.setHours(0, 0, 0, 0);

      if (itemDate.getTime() >= today.getTime()) {
        groups.today.push(c);
      } else if (itemDate.getTime() >= yesterday.getTime()) {
        groups.yesterday.push(c);
      } else {
        groups.previous.push(c);
      }
    });

    return groups;
  };

  const grouped = groupConversations(conversations);

  // Helper to render formatted assistant content
  const renderMessageContent = (content: string) => {
    return (
      <div className="whitespace-pre-line leading-relaxed space-y-1">
        {content.split('\n').map((line, lIdx) => {
          if (line.includes('OFFICIAL GOVERNMENT WARNING')) {
            return (
              <div key={lIdx} className="font-bold text-red-600 dark:text-red-400 flex items-center gap-1.5 py-0.5 text-xs sm:text-sm">
                <ShieldAlert className="w-4 h-4 flex-shrink-0 animate-pulse" />
                <span>{line}</span>
              </div>
            );
          }
          if (line.includes('AI Risk Monitoring') || line.includes('AI Threat Level')) {
            return (
              <div key={lIdx} className="font-semibold text-primary-600 dark:text-primary-400 flex items-center gap-1 py-0.5">
                <Sparkles className="w-3.5 h-3.5" />
                <span>{line}</span>
              </div>
            );
          }
          if (line.startsWith('• **') || line.startsWith('**')) {
            return (
              <p key={lIdx} className="font-semibold text-slate-900 dark:text-white pt-1">
                {line.replace(/\*\*/g, '')}
              </p>
            );
          }
          return <span key={lIdx} className="block">{line}</span>;
        })}
      </div>
    );
  };

  // Render a conversation item in sidebar
  const renderConversationItem = (conv: ConversationSummary) => {
    const isSelected = sessionId === conv.id;
    const isRenaming = renamingId === conv.id;

    if (isRenaming) {
      return (
        <form
          key={conv.id}
          onSubmit={(e) => handleSaveRename(conv.id, e)}
          className="flex items-center gap-1 px-2 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800"
        >
          <input
            type="text"
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            autoFocus
            className="flex-1 text-xs bg-transparent border-none outline-none text-slate-900 dark:text-white"
          />
          <button
            type="submit"
            className="p-1 text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 cursor-pointer"
          >
            <Check className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => setRenamingId(null)}
            className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </form>
      );
    }

    return (
      <div
        key={conv.id}
        onClick={() => handleOpenConversation(conv.id)}
        className={`group relative flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition ${
          isSelected
            ? 'bg-primary-50 dark:bg-primary-950/60 text-primary-700 dark:text-primary-300 font-medium'
            : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/70'
        }`}
      >
        <div className="flex items-center gap-2 truncate pr-2">
          <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${isSelected ? 'text-primary-600 dark:text-primary-400' : 'text-slate-400'}`} />
          <span className="truncate">{conv.title || 'New Conversation'}</span>
        </div>

        {/* Action ⋮ menu */}
        <div className="relative flex-shrink-0" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => setActiveMenuId(activeMenuId === conv.id ? null : conv.id)}
            className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded opacity-70 group-hover:opacity-100 transition"
            title="Options"
          >
            <MoreVertical className="w-3.5 h-3.5" />
          </button>

          {activeMenuId === conv.id && (
            <div className="absolute right-0 mt-1 w-28 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 z-50 text-xs">
              <button
                onClick={(e) => handleStartRename(conv, e)}
                className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200"
              >
                <Edit2 className="w-3 h-3 text-slate-400" />
                <span>Rename</span>
              </button>
              <button
                onClick={() => {
                  setDeleteConfirmId(conv.id);
                  setActiveMenuId(null);
                }}
                className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-red-50 dark:hover:bg-red-950/50 text-red-600 dark:text-red-400"
              >
                <Trash2 className="w-3 h-3" />
                <span>Delete</span>
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Sidebar Component JSX
  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800">
      {/* Sidebar Header & New Chat */}
      <div className="p-3 border-b border-slate-200 dark:border-slate-800 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
            <History className="w-4 h-4 text-primary-500" />
            <span>Chat History</span>
          </div>
          {/* Close drawer on mobile */}
          <button
            onClick={() => setIsMobileDrawerOpen(false)}
            className="sm:hidden p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Section 11: + New Chat Button */}
        <button
          onClick={handleNewChat}
          className="w-full py-2 px-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition shadow-xs cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>+ New Chat</span>
        </button>

        {/* Section 31: Search Field */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchHistory}
            onChange={(e) => setSearchHistory(e.target.value)}
            placeholder="Search conversations"
            className="w-full pl-8 pr-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          {searchHistory && (
            <button
              onClick={() => setSearchHistory('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* History List Grouped by Date */}
      <div className="flex-1 overflow-y-auto p-2.5 space-y-4">
        {isLoadingHistory && conversations.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-400">Loading history...</div>
        ) : conversations.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-400">
            {searchHistory ? 'No chats found' : 'No previous chats'}
          </div>
        ) : (
          <>
            {/* Today */}
            {grouped.today.length > 0 && (
              <div className="space-y-1">
                <div className="px-2 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                  Today
                </div>
                {grouped.today.map(renderConversationItem)}
              </div>
            )}

            {/* Yesterday */}
            {grouped.yesterday.length > 0 && (
              <div className="space-y-1">
                <div className="px-2 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                  Yesterday
                </div>
                {grouped.yesterday.map(renderConversationItem)}
              </div>
            )}

            {/* Previous */}
            {grouped.previous.length > 0 && (
              <div className="space-y-1">
                <div className="px-2 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                  Previous
                </div>
                {grouped.previous.map(renderConversationItem)}
              </div>
            )}
          </>
        )}
      </div>

      {/* User Status Bar */}
      <div className="p-2.5 border-t border-slate-200 dark:border-slate-800 text-[11px] text-slate-500 dark:text-slate-400 flex items-center justify-between">
        <span className="truncate">{user ? user.name || user.email : 'Guest Session'}</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono">
          {conversations.length} {conversations.length === 1 ? 'chat' : 'chats'}
        </span>
      </div>
    </div>
  );

  return (
    <div className="relative bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex h-[700px] overflow-hidden">
      {/* Desktop History Sidebar (Collapsible) */}
      {isHistoryOpen && (
        <aside className="hidden md:block w-64 flex-shrink-0 h-full">
          {sidebarContent}
        </aside>
      )}

      {/* Mobile Drawer (Section 30) */}
      {isMobileDrawerOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div
            className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs"
            onClick={() => setIsMobileDrawerOpen(false)}
          />
          <div className="relative w-72 max-w-[80%] h-full bg-white dark:bg-slate-900 shadow-2xl z-10">
            {sidebarContent}
          </div>
        </div>
      )}

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col min-w-0 h-full bg-white dark:bg-slate-900">
        {/* Chat Header */}
        <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-850/70">
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Toggle History Button (Sections 30 & 10) */}
            <button
              onClick={() => {
                if (window.innerWidth < 768) {
                  setIsMobileDrawerOpen(true);
                } else {
                  setIsHistoryOpen(!isHistoryOpen);
                }
              }}
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-800 transition cursor-pointer"
              title="Toggle Chat History [☰]"
            >
              <Menu className="w-4 h-4" />
            </button>

            <div className="w-8 h-8 rounded-lg bg-primary-600 text-white flex items-center justify-center shadow-sm flex-shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                  {t('weathergpt_assistant') || 'WeatherGPT AI'}
                </h3>
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  {t('grounded_reasoning') || 'Two-Stage AI'}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 hidden sm:block">
                {t('verified_met_observations') || 'Conversational assistant & live meteorological intelligence'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="hidden lg:flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300 px-2.5 py-1 rounded-md bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-2xs">
              <div className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-primary-500" />
                <span className="font-semibold truncate max-w-[130px]">{cityShort}</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">
                {latitude.toFixed(3)}°, {longitude.toFixed(3)}°
              </span>
              {locationSource === 'gps' && accuracy && (
                <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">
                  ±{Math.round(accuracy)}m
                </span>
              )}
            </div>

            {/* Clear / New Chat Header Icon */}
            <button
              onClick={handleNewChat}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
              title="New Chat"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Message List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[88%] sm:max-w-[80%] ${
                  isUser ? 'ml-auto flex-row-reverse' : ''
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                    isUser
                      ? 'bg-slate-700 text-white'
                      : 'bg-primary-600 text-white shadow-sm'
                  }`}
                >
                  {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                </div>

                <div className="space-y-1.5 flex-1 min-w-0">
                  <div
                    className={`p-3.5 rounded-2xl text-xs sm:text-sm ${
                      isUser
                        ? 'bg-primary-600 text-white rounded-tr-none'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-tl-none border border-slate-200/60 dark:border-slate-700/60'
                    }`}
                  >
                    {renderMessageContent(msg.content)}

                    {/* AI Advisory Callout */}
                    {msg.advisory && (
                      <div className="mt-2.5 p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50 text-amber-900 dark:text-amber-200 text-xs">
                        {msg.advisory}
                      </div>
                    )}

                    {/* Source & Timestamp Footer */}
                    {!isUser && (
                      <div className="mt-2.5 pt-2 border-t border-slate-200/80 dark:border-slate-700/80 flex items-center justify-between text-[10px] text-slate-400">
                        <div className="flex items-center gap-1.5 truncate mr-2">
                          <span>{msg.source_attribution || 'WeatherGPT Assistant'}</span>
                          {msg.updated_at && (
                            <>
                              <span>•</span>
                              <span className="flex items-center gap-0.5">
                                <Clock className="w-2.5 h-2.5" />
                                {msg.updated_at}
                              </span>
                            </>
                          )}
                        </div>
                        <button
                          onClick={() => handleSpeak(msg.content, msg.id)}
                          className="hover:text-primary-500 p-1 flex-shrink-0 cursor-pointer"
                          title="Voice playback"
                        >
                          {isSpeaking === msg.id ? (
                            <VolumeX className="w-3.5 h-3.5 text-primary-500" />
                          ) : (
                            <Volume2 className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Suggested Follow-up Prompts */}
                  {msg.suggested_questions && msg.suggested_questions.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {msg.suggested_questions.map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(q)}
                          className="text-[11px] px-2.5 py-1 rounded-full bg-slate-50 dark:bg-slate-850 hover:bg-primary-50 dark:hover:bg-primary-950/60 text-slate-600 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Section 32: Dynamic Intent-Specific Loading State */}
          {isSending && (
            <div className="flex gap-3 max-w-[85%]">
              <div className="w-7 h-7 rounded-full bg-primary-600 text-white flex items-center justify-center flex-shrink-0">
                <Bot className="w-3.5 h-3.5" />
              </div>
              <div className="p-3.5 rounded-2xl rounded-tl-none bg-slate-100 dark:bg-slate-800 text-xs text-slate-600 dark:text-slate-300 flex items-center gap-2 border border-slate-200/60 dark:border-slate-700/60 shadow-xs">
                <span className="w-2 h-2 rounded-full bg-primary-500 animate-ping"></span>
                <span className="font-medium">{loadingText}</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Box */}
        <div className="p-3 sm:p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            {/* Voice Input Microphone Button */}
            <button
              type="button"
              onClick={toggleVoiceInput}
              className={`p-2.5 rounded-lg border transition cursor-pointer ${
                isListening
                  ? 'bg-red-500 text-white border-red-600 animate-pulse'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
              title={isListening ? t('voice_listening') : t('chat_voice')}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            {/* Text Input */}
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={isListening ? t('voice_listening') : (t('chat_placeholder') || 'Ask about weather, alerts, forecasts, or website help...')}
              className="flex-1 py-2 px-3.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={!inputMessage.trim() || isSending}
              className="px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-xs sm:text-sm flex items-center gap-1.5 transition shadow-sm cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{t('chat_send') || 'Send'}</span>
            </button>
          </form>
        </div>
      </div>

      {/* Section 13: Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/50 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-xl max-w-sm w-full p-5 border border-slate-200 dark:border-slate-700 space-y-4">
            <div className="flex items-center gap-3 text-amber-600 dark:text-amber-400">
              <AlertTriangle className="w-6 h-6 flex-shrink-0" />
              <h4 className="font-bold text-slate-900 dark:text-white text-sm">Delete this conversation?</h4>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              This will permanently delete this conversation from your history. This action cannot be undone.
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setDeleteConfirmId(null)}
                className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleDeleteConversation(deleteConfirmId)}
                className="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-medium cursor-pointer"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
