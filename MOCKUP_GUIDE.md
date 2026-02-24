# RAG7 GUI Mockup Guide

## Overview

The `mockup-gui.html` file is a **standalone HTML mockup** that demonstrates the complete RAG7 AI Agent Platform interface without requiring any backend services or build tools. This is perfect for:

- 🎨 **Quick previews** of the UI design
- 👥 **Stakeholder demonstrations** without technical setup
- 📱 **UI/UX testing** across different devices
- 🖼️ **Visual reference** for development
- 🚀 **Fast iteration** on design changes

## Features

### Full GUI Dashboard
- **Sidebar Navigation** - Logo, status badge, navigation menu, quick stats
- **4 Main Views:**
  1. **Chat View** - Conversation interface with message history
  2. **Integrations View** - Cards showing Slack, Gmail, and Notion
  3. **Analytics View** - Statistics cards with metrics
  4. **Settings View** - Configuration options and documentation links

### Floating Bot Widget
- **Toggleable chat** - Bottom-right floating button
- **Independent chat window** - Works alongside main dashboard
- **Animated interactions** - Smooth slide-up animation
- **Fully functional** - Can send/receive mockup messages

### Interactive Elements
- ✅ **View switching** - Click sidebar nav to change views
- ✅ **Chat messaging** - Type and send messages (simulated responses)
- ✅ **Floating bot** - Click to open/close
- ✅ **Settings toggles** - Interactive switches
- ✅ **Responsive design** - Works on mobile and desktop

## How to Use

### Option 1: Open Directly in Browser

```bash
# From repository root
open mockup-gui.html

# Or on Linux
xdg-open mockup-gui.html

# Or on Windows
start mockup-gui.html
```

### Option 2: Serve with Simple HTTP Server

```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx serve .

# Then visit http://localhost:8080/mockup-gui.html
```

### Option 3: Online Hosting

Upload `mockup-gui.html` to any static hosting service:
- GitHub Pages
- Netlify Drop
- Verge
- AWS S3 + CloudFront

## Interface Tour

### Dashboard Sidebar

```
┌────────────────────┐
│  🤖 RAG7          │
│  ● Online         │
├────────────────────┤
│  💬 Chat          │  ← Active
│  🔌 Integrations  │  with badge "3"
│  📊 Analytics     │
│  ⚙️ Settings      │
├────────────────────┤
│  Quick Stats      │
│  Active: 3        │
│  Functions: 9     │
└────────────────────┘
```

### Chat View

**Welcome Card** - Shows available integrations with status pills

**Message Area:**
- User messages (right-aligned, purple gradient)
- Assistant messages (left-aligned, gray)
- Function call badges (yellow/green)
- Timestamps

**Input Area** - Type messages and click send button (🚀)

### Integrations View

**3 Integration Cards:**

1. **Slack** (Connected)
   - Send message
   - List channels
   - Send thread reply

2. **Gmail** (Connected)
   - Send email
   - List messages
   - Read message

3. **Notion** (Connected)
   - Create page
   - Query database
   - Add database entry

### Analytics View

**4 Stat Cards:**
- 💬 Total Messages: 1,247
- 👥 Active Sessions: 89
- ⚡ Functions Executed: 342
- ✅ Success Rate: 98.5%

**Placeholder** for advanced analytics charts

### Settings View

**API Configuration** - OpenAI status indicator

**Interface Options:**
- Enable Floating Bot (toggle)
- Show Function Details (toggle)

**Documentation Links:**
- README
- Quick Start Guide
- Development Guide
- API Documentation

### Floating Bot Widget

**Closed State:**
- Purple gradient circular button (bottom-right)
- Displays 💬 emoji

**Open State:**
- 380×600px chat window
- Header with "AI Assistant" title and close button
- Message area with scrollable history
- Input field with send button

## Visual Design

### Color Palette

```css
Primary Gradient: #667eea → #764ba2
Success Green: #10b981
Background: #f5f7fa
White: #ffffff
Gray Scale: #1f2937 → #9ca3af
```

### Typography

- **Font Family**: System fonts (SF Pro, Segoe UI, Roboto)
- **Headings**: 18px - 28px, bold
- **Body**: 14px, regular
- **Small**: 12px, regular

### Spacing

- **Card Padding**: 24-32px
- **Gap Between Items**: 12-24px
- **Border Radius**: 6-16px
- **Shadows**: Subtle elevation effects

## Customization

### Change Colors

Edit the CSS in `<style>` section:

```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your colors */
background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
```

### Modify Content

All content is in plain HTML - no build process needed:

```html
<!-- Change welcome message -->
<h2>Welcome to RAG7 AI Agent Platform</h2>
<!-- to -->
<h2>Your Custom Message Here</h2>
```

### Add New Messages

Use the JavaScript functions at the bottom:

```javascript
// Add to messages array
const userMsg = document.createElement('div');
userMsg.className = 'message user';
userMsg.innerHTML = `...your HTML...`;
messagesContainer.appendChild(userMsg);
```

### Add New Views

1. Add nav item in sidebar
2. Create new view content div
3. Add to switchView() function

## Interactive Features

### Working Features

✅ **Navigation** - Switch between 4 views
✅ **Chat Input** - Type and send messages
✅ **Floating Bot** - Open/close toggle
✅ **Settings** - Toggle switches
✅ **Responsive** - Mobile-friendly

### Simulated Features

⚠️ **AI Responses** - Static demo responses
⚠️ **Function Calls** - Visual only, no execution
⚠️ **WebSocket** - Not connected
⚠️ **API Calls** - Not made

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Responsive Breakpoints

```css
/* Desktop: Full sidebar + content */
@media (min-width: 769px)

/* Tablet: Narrower sidebar */
@media (min-width: 768px) and (max-width: 1024px)

/* Mobile: Hidden sidebar, full-width content */
@media (max-width: 768px)
```

## Performance

- **Size**: ~40KB (single file)
- **Load Time**: < 100ms
- **No Dependencies**: Pure HTML/CSS/JS
- **Offline Ready**: Works without internet

## Use Cases

### 1. Design Review
Share with designers/stakeholders for UI feedback

### 2. Client Demos
Show interface without revealing implementation

### 3. Documentation
Include in docs as visual reference

### 4. Development Reference
Use as spec for React components

### 5. Testing
Test UI flows and interactions quickly

### 6. Marketing
Showcase product interface on website

## Differences from Real App

| Feature | Mockup | Real App |
|---------|--------|----------|
| **Backend** | None | FastAPI server |
| **AI** | Simulated | OpenAI GPT-4 |
| **WebSocket** | Not connected | Real-time |
| **Integrations** | Visual only | Functional |
| **Authentication** | None | OAuth/API keys |
| **Persistence** | Session only | Database |
| **Build** | None needed | npm build |

## Quick Modifications

### Change Brand Name

Search and replace "RAG7" with your brand name.

### Update Integration Cards

Modify the integrations-grid section:

```html
<div class="integration-card">
    <div class="integration-title">
        <span>YOUR_EMOJI</span>
        <span>Your Service</span>
    </div>
    <!-- ... -->
</div>
```

### Adjust Layout

Change grid columns:

```css
.integrations-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    /* Change 300px to your preferred card width */
}
```

### Add Analytics Charts

Replace placeholder with chart library:

```html
<div id="chartContainer">
    <!-- Add Chart.js, D3.js, or other chart library -->
</div>
```

## Tips

1. **Print to PDF** - Use browser print function for static mockup
2. **Screenshot Tool** - Capture specific views for docs
3. **Browser DevTools** - Test responsive behavior
4. **Edit in Browser** - Use DevTools to experiment with changes
5. **Version Control** - Track changes to mockup in git

## Integration with Real App

The mockup provides:
- ✅ Visual design reference
- ✅ Layout specifications
- ✅ Color palette
- ✅ Component structure
- ✅ Interaction patterns

Developers can:
1. Reference mockup while building React components
2. Extract CSS for production styles
3. Use as acceptance criteria for UI
4. Test responsive behavior
5. Get stakeholder approval before coding

## Troubleshooting

### Styling Issues
- Check browser compatibility
- Clear browser cache
- Verify CSS in <style> tag

### JavaScript Not Working
- Check browser console for errors
- Ensure JavaScript is enabled
- Verify function names match

### Images Not Loading
- Mockup uses emoji, no external images
- All content is self-contained

### Mobile Issues
- Test in actual mobile browser
- Use browser DevTools device emulator
- Check viewport meta tag

## Next Steps

1. **Get Feedback** - Share with team/stakeholders
2. **Iterate Design** - Make changes based on feedback
3. **Reference for Development** - Use as spec for React components
4. **Update Documentation** - Add screenshots to README
5. **Version Control** - Commit changes to repository

## Additional Resources

- **Real App**: Run `docker-compose up` for full platform
- **Documentation**: See README.md, DASHBOARD_GUIDE.md
- **Development**: Check DEVELOPMENT.md for extension guide
- **Troubleshooting**: See TROUBLESHOOTING.md for issues

---

**Perfect for demonstrations, design reviews, and quick previews!** 🎨✨
