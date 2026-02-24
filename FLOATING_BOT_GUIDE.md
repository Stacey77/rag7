# Floating Bot Widget - Visual Guide

## 🎨 Appearance

### Closed State (Floating Button)
```
                                    ┌──────────┐
                                    │          │
                                    │    💬    │  ← Gradient purple button
                                    │          │     Hovers in bottom-right
                                    └──────────┘
```

### Open State (Chat Window)
```
┌─────────────────────────────────────┐
│ 🤖 AI Assistant        🗑️ ✕        │  ← Header with gradient
├─────────────────────────────────────┤
│                                     │
│  🤖  Hello! I'm your AI...         │  ← Welcome message
│      Ask me anything!               │
│                                     │
│  👤  What can you do?              │  ← User message
│      2:30 PM                        │
│                                     │
│  🤖  I can help with...            │  ← Assistant message
│      ⚡ slack_send_message ✓       │     with function calls
│      2:30 PM                        │
│                                     │
│  ...                               │  ← Typing indicator
│                                     │
├─────────────────────────────────────┤
│  Type your message...        🚀    │  ← Input area
└─────────────────────────────────────┘
         ↑
    Floating widget
    380px × 600px
```

## ✨ Features

1. **Floating Button**
   - Gradient purple background
   - Chat icon when closed
   - X icon when open
   - Smooth hover animation
   - Bottom-right positioning

2. **Chat Window**
   - Rounded corners (16px)
   - Box shadow for depth
   - Slide-up animation
   - Responsive sizing
   - Mobile-friendly

3. **Header**
   - Gradient background
   - Bot avatar emoji (🤖)
   - Online/Offline status
   - Clear chat button (🗑️)
   - Close button (✕)

4. **Messages**
   - User messages (right, purple gradient)
   - Assistant messages (left, white)
   - Function call badges
   - Timestamps
   - Smooth animations

5. **Input**
   - Rounded input field
   - Send button with icon
   - Disabled state handling
   - Auto-focus on open

## 🎯 Usage

### For Users:
1. Click floating button to open
2. Type message and press Enter or click send
3. See real-time responses
4. View function executions
5. Clear chat with trash icon
6. Close with X or floating button

### For Developers:
- Component: `FloatingBot.js`
- Styles: `FloatingBot.css`
- WebSocket connection for real-time
- Fallback to REST API
- Independent of main app state

## 🌈 Color Scheme

- **Primary Gradient**: #667eea → #764ba2
- **Close Gradient**: #f093fb → #f5576c
- **User Messages**: Purple gradient
- **Assistant Messages**: White with subtle shadow
- **Background**: Light gray (#f9fafb)
- **Hover Effects**: Scale and glow

## 📱 Responsive Behavior

- **Desktop**: 380px × 600px window
- **Mobile**: Full width minus 40px margins
- **Position**: Bottom-right with 20px spacing
- **Button**: 60px × 60px circle
- **Animations**: Slide up, fade in, scale effects
