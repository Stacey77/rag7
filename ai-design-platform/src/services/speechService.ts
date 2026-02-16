/**
 * Speech Service - Voice interaction system using Web Speech API
 * Provides speech recognition and text-to-speech synthesis
 */

export type SpeechLanguage = 'en-US' | 'es-ES' | 'fr-FR' | 'de-DE' | 'zh-CN' | 'ja-JP' | 'hi-IN' | 'ar-SA' | 'pt-BR' | 'ru-RU';

export interface VoiceSettings {
  rate: number;
  pitch: number;
  volume: number;
}

export interface SpeechRecognitionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionAlternative[];
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => ISpeechRecognition;
    webkitSpeechRecognition: new () => ISpeechRecognition;
  }
}

class SpeechService {
  private recognition: ISpeechRecognition | null = null;
  private synthesis: SpeechSynthesis | null = null;
  private currentLanguage: SpeechLanguage = 'en-US';
  private voiceSettings: VoiceSettings = {
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0
  };
  private isListening = false;
  private silenceTimer: number | null = null;
  private silenceTimeout = 3000;
  private onResultCallback: ((result: SpeechRecognitionResult) => void) | null = null;
  private onSilenceCallback: (() => void) | null = null;

  constructor() {
    this.initializeSpeechRecognition();
    this.initializeSpeechSynthesis();
  }

  /**
   * Initialize speech recognition
   */
  private initializeSpeechRecognition(): void {
    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
      console.warn('Speech recognition not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    
    if (this.recognition) {
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = this.currentLanguage;
      this.recognition.maxAlternatives = 1;

      this.recognition.addEventListener('result', this.handleSpeechResult.bind(this));
      this.recognition.addEventListener('error', this.handleSpeechError.bind(this));
      this.recognition.addEventListener('end', this.handleSpeechEnd.bind(this));
    }
  }

  /**
   * Initialize speech synthesis
   */
  private initializeSpeechSynthesis(): void {
    if ('speechSynthesis' in window) {
      this.synthesis = window.speechSynthesis;
    } else {
      console.warn('Speech synthesis not supported in this browser');
    }
  }

  /**
   * Handle speech recognition results
   */
  private handleSpeechResult(event: Event): void {
    const speechEvent = event as SpeechRecognitionEvent;
    this.resetSilenceTimer();

    for (let i = speechEvent.resultIndex; i < speechEvent.results.length; i++) {
      const result = speechEvent.results[i];
      const transcript = result[0].transcript;
      const confidence = result[0].confidence;
      const isFinal = result.isFinal;

      if (this.onResultCallback) {
        this.onResultCallback({
          transcript,
          confidence,
          isFinal
        });
      }
    }
  }

  /**
   * Handle speech recognition errors
   */
  private handleSpeechError(event: Event): void {
    const errorEvent = event as SpeechRecognitionErrorEvent;
    console.error('Speech recognition error:', errorEvent.error);
    
    if (errorEvent.error === 'no-speech') {
      this.triggerSilenceDetection();
    }
  }

  /**
   * Handle speech recognition end
   */
  private handleSpeechEnd(): void {
    if (this.isListening && this.recognition) {
      try {
        this.recognition.start();
      } catch (error) {
        console.error('Error restarting recognition:', error);
        this.isListening = false;
      }
    }
  }

  /**
   * Reset silence detection timer
   */
  private resetSilenceTimer(): void {
    if (this.silenceTimer) {
      window.clearTimeout(this.silenceTimer);
    }
    
    this.silenceTimer = window.setTimeout(() => {
      this.triggerSilenceDetection();
    }, this.silenceTimeout);
  }

  /**
   * Trigger silence detection callback
   */
  private triggerSilenceDetection(): void {
    if (this.onSilenceCallback) {
      this.onSilenceCallback();
    }
  }

  /**
   * Start listening for speech
   */
  public startListening(
    onResult: (result: SpeechRecognitionResult) => void,
    onSilence?: () => void
  ): boolean {
    if (!this.recognition) {
      console.error('Speech recognition not available');
      return false;
    }

    if (this.isListening) {
      console.warn('Already listening');
      return false;
    }

    this.onResultCallback = onResult;
    this.onSilenceCallback = onSilence || null;
    
    try {
      this.recognition.start();
      this.isListening = true;
      this.resetSilenceTimer();
      return true;
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      return false;
    }
  }

  /**
   * Stop listening for speech
   */
  public stopListening(): void {
    if (!this.recognition || !this.isListening) {
      return;
    }

    if (this.silenceTimer) {
      window.clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }

    try {
      this.recognition.stop();
      this.isListening = false;
      this.onResultCallback = null;
      this.onSilenceCallback = null;
    } catch (error) {
      console.error('Error stopping speech recognition:', error);
    }
  }

  /**
   * Speak text using speech synthesis
   */
  public speak(text: string, options?: Partial<VoiceSettings>): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.synthesis) {
        reject(new Error('Speech synthesis not available'));
        return;
      }

      if (!text.trim()) {
        resolve();
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      const settings = { ...this.voiceSettings, ...options };

      utterance.lang = this.currentLanguage;
      utterance.rate = settings.rate;
      utterance.pitch = settings.pitch;
      utterance.volume = settings.volume;

      const voices = this.synthesis.getVoices();
      const preferredVoice = voices.find(voice => voice.lang.startsWith(this.currentLanguage.split('-')[0]));
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }

      utterance.onend = () => resolve();
      utterance.onerror = (event) => reject(event);

      this.synthesis.cancel();
      this.synthesis.speak(utterance);
    });
  }

  /**
   * Set speech language
   */
  public setSpeechLanguage(language: SpeechLanguage): void {
    this.currentLanguage = language;
    
    if (this.recognition) {
      const wasListening = this.isListening;
      if (wasListening) {
        this.stopListening();
      }
      
      this.recognition.lang = language;
      
      if (wasListening && this.onResultCallback) {
        this.startListening(this.onResultCallback, this.onSilenceCallback || undefined);
      }
    }
  }

  /**
   * Set voice settings
   */
  public setVoiceSettings(settings: Partial<VoiceSettings>): void {
    this.voiceSettings = { ...this.voiceSettings, ...settings };
  }

  /**
   * Get current language
   */
  public getCurrentLanguage(): SpeechLanguage {
    return this.currentLanguage;
  }

  /**
   * Get listening status
   */
  public getIsListening(): boolean {
    return this.isListening;
  }

  /**
   * Set silence timeout
   */
  public setSilenceTimeout(timeout: number): void {
    this.silenceTimeout = timeout;
  }
}

const speechService = new SpeechService();

export const startListening = (
  onResult: (result: SpeechRecognitionResult) => void,
  onSilence?: () => void
): boolean => speechService.startListening(onResult, onSilence);

export const stopListening = (): void => speechService.stopListening();

export const speak = (text: string, options?: Partial<VoiceSettings>): Promise<void> => 
  speechService.speak(text, options);

export const setSpeechLanguage = (language: SpeechLanguage): void => 
  speechService.setSpeechLanguage(language);

export const setVoiceSettings = (settings: Partial<VoiceSettings>): void =>
  speechService.setVoiceSettings(settings);

export const getCurrentLanguage = (): SpeechLanguage =>
  speechService.getCurrentLanguage();

export const getIsListening = (): boolean =>
  speechService.getIsListening();

export const setSilenceTimeout = (timeout: number): void =>
  speechService.setSilenceTimeout(timeout);

export default speechService;
