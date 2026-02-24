# GUI Testing Guide

Complete guide for testing the RAG7 Conversational AI Agent Platform GUI.

## Table of Contents
1. [Automated Testing](#automated-testing)
2. [Manual Testing](#manual-testing)
3. [Setup Validation](#setup-validation)
4. [Component-Specific Testing](#component-specific-testing)
5. [Browser Testing](#browser-testing)
6. [Troubleshooting](#troubleshooting)

---

## Automated Testing

### Backend Tests

**Run all backend tests:**
```bash
cd /home/runner/work/rag7/rag7
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_web_api.py -v
pytest tests/test_integrations.py -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=src --cov-report=html
```

**Expected Results:**
- ✅ 15 tests should pass
- ✅ All integrations (Slack, Gmail, Notion) discoverable
- ✅ API endpoints return 200 status
- ✅ Health checks pass

### Frontend Tests

**Install test dependencies:**
```bash
cd frontend
npm install
```

**Run all frontend tests:**
```bash
npm test
```

**Run tests with coverage:**
```bash
npm run test:coverage
```

**Run tests in CI mode (non-interactive):**
```bash
CI=true npm test
```

**Expected Results:**
- ✅ Dashboard component renders
- ✅ Navigation works between views
- ✅ FloatingBot opens/closes correctly
- ✅ ChatInterface sends messages
- ✅ API calls are made properly
- ✅ Error handling works

### Test Files Created
- `frontend/src/Dashboard.test.js` - Dashboard navigation and view tests
- `frontend/src/FloatingBot.test.js` - Floating bot widget tests
- `frontend/src/ChatInterface.test.js` - Chat interface interaction tests
- `frontend/src/setupTests.js` - Jest testing configuration

---

## Manual Testing

### Quick Start Testing

**Option 1: HTML Mockup (No Setup Required)**
```bash
# Simply open in browser
open mockup-gui.html
# OR
python -m http.server 8080
# Visit http://localhost:8080/mockup-gui.html
```

**Test Checklist for HTML Mockup:**
- [ ] Page loads without errors
- [ ] Sidebar navigation is visible
- [ ] All 4 views accessible (Chat, Integrations, Analytics, Settings)
- [ ] Floating bot button appears in bottom-right
- [ ] Clicking floating bot opens chat window
- [ ] Navigation switches between views
- [ ] Chat input accepts text
- [ ] Responsive design works on mobile (resize browser)

**Option 2: Full Platform (React + Backend)**
```bash
# Automated setup
chmod +x setup.sh
./setup.sh

# OR Docker
docker-compose up --build

# OR Manual
# Terminal 1 - Backend
pip install -r requirements.txt
uvicorn src.interfaces.web_api:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm start
```

### Dashboard Testing Checklist

**Access:** http://localhost:3000

#### Sidebar Navigation
- [ ] Logo displays "RAG7"
- [ ] Status indicator shows (Online/Offline)
- [ ] 4 navigation items visible:
  - [ ] 💬 Chat
  - [ ] 🔌 Integrations  
  - [ ] 📊 Analytics
  - [ ] ⚙️ Settings
- [ ] Badge indicators show counts
- [ ] Quick stats display at bottom

#### Chat View
- [ ] Welcome screen displays on first visit
- [ ] Input field accepts text
- [ ] Send button is clickable
- [ ] Messages appear in chat history
- [ ] Timestamps show for each message
- [ ] Function calls are visualized
- [ ] Typing indicator appears (if implemented)
- [ ] Can send message with Enter key
- [ ] Can send message with Send button

#### Integrations View
- [ ] Cards for each integration (Slack, Gmail, Notion)
- [ ] Health status indicators show
  - [ ] Connected (green) or Not Connected (red/gray)
- [ ] Function listings per integration
- [ ] Connection stats display
- [ ] Cards are responsive

#### Analytics View
- [ ] 4 stat cards display:
  - [ ] Messages count
  - [ ] Sessions count
  - [ ] Functions Executed count
  - [ ] Success Rate percentage
- [ ] Numbers update (if real-time)
- [ ] Cards are visually consistent

#### Settings View
- [ ] API configuration section visible
- [ ] Interface toggles work
- [ ] Documentation links present:
  - [ ] README
  - [ ] Quick Start
  - [ ] Dev Guide
  - [ ] API Docs
- [ ] Links navigate correctly

### Floating Bot Testing Checklist

#### Initial State
- [ ] Floating button visible in bottom-right corner
- [ ] Button has gradient purple design
- [ ] Button animates on hover

#### Opening/Closing
- [ ] Click button opens chat window
- [ ] Window slides up with animation
- [ ] Window size is appropriate (380×600px)
- [ ] Close button (×) is visible
- [ ] Clicking close button closes window
- [ ] Clicking floating button again closes window

#### Chat Functionality
- [ ] Chat input field is visible
- [ ] Can type message in input
- [ ] Send button works
- [ ] Enter key sends message
- [ ] Messages appear in chat history
- [ ] User messages aligned right
- [ ] Bot messages aligned left
- [ ] Function calls are visualized
- [ ] Success/error indicators show

#### Additional Features
- [ ] Clear chat button works
- [ ] Chat history persists during session
- [ ] WebSocket connection established (check console)
- [ ] Falls back to REST API if WebSocket fails
- [ ] Works independently of dashboard
- [ ] Mobile responsive (resize browser)

### API Testing Checklist

**Access:** http://localhost:8000/docs

- [ ] `/health` - Returns healthy status
- [ ] `/chat` - Accepts POST with message
- [ ] `/integrations` - Lists all integrations
- [ ] `/functions` - Lists available functions
- [ ] `/ws/chat` - WebSocket endpoint accessible
- [ ] Interactive API docs work
- [ ] All endpoints return proper responses

---

## Setup Validation

### Run Validation Script

Create and run this validation script:

```bash
#!/bin/bash
# save as validate-setup.sh

echo "=== RAG7 Platform Setup Validation ==="
echo ""

# Check backend
echo "1. Checking Backend..."
if python -c "import fastapi, openai, chromadb" 2>/dev/null; then
    echo "   ✅ Backend dependencies installed"
else
    echo "   ❌ Backend dependencies missing"
fi

# Check frontend
echo "2. Checking Frontend..."
if [ -d "frontend/node_modules" ]; then
    echo "   ✅ Frontend dependencies installed"
else
    echo "   ❌ Frontend dependencies missing - run 'cd frontend && npm install'"
fi

# Check environment
echo "3. Checking Environment..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    if grep -q "OPENAI_API_KEY" .env; then
        echo "   ✅ OPENAI_API_KEY configured"
    else
        echo "   ⚠️  OPENAI_API_KEY not set in .env"
    fi
else
    echo "   ⚠️  .env file not found - copy from .env.example"
fi

# Check ports
echo "4. Checking Ports..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ Backend running on port 8000"
else
    echo "   ⚠️  Backend not running on port 8000"
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ Frontend running on port 3000"
else
    echo "   ⚠️  Frontend not running on port 3000"
fi

# Run tests
echo "5. Running Tests..."
if pytest tests/ -q 2>/dev/null; then
    echo "   ✅ Backend tests passing"
else
    echo "   ⚠️  Backend tests failed or pytest not available"
fi

echo ""
echo "=== Validation Complete ==="
```

**Run validation:**
```bash
chmod +x validate-setup.sh
./validate-setup.sh
```

---

## Component-Specific Testing

### Dashboard Component

**Test Navigation:**
1. Open http://localhost:3000
2. Click each navigation item
3. Verify view changes
4. Check browser console for errors
5. Verify no memory leaks (check dev tools)

**Test API Integration:**
1. Open Network tab in dev tools
2. Navigate between views
3. Verify API calls are made:
   - `/health` on mount
   - `/integrations` for integrations view
   - `/functions` for functions list
4. Check response status codes (should be 200)

### FloatingBot Component

**Test Isolation:**
1. Open dashboard
2. Open floating bot
3. Send message in floating bot
4. Navigate dashboard views
5. Verify both work independently
6. Check for state interference

**Test WebSocket:**
1. Open browser console
2. Open floating bot
3. Look for WebSocket connection message
4. Send a message
5. Verify WebSocket sends/receives
6. Close and reopen - verify reconnection

### ChatInterface Component

**Test Message Flow:**
1. Type message
2. Click send
3. Verify message appears in history
4. Verify response appears
5. Check function visualization
6. Verify timestamps

**Test Error Handling:**
1. Stop backend server
2. Try sending message
3. Verify error handling
4. Start backend
5. Verify recovery

---

## Browser Testing

### Desktop Browsers

Test on multiple browsers:
- [ ] **Chrome** (latest)
- [ ] **Firefox** (latest)
- [ ] **Safari** (if on Mac)
- [ ] **Edge** (latest)

**Test in each browser:**
- [ ] Dashboard loads
- [ ] Navigation works
- [ ] Floating bot works
- [ ] Chat sends messages
- [ ] Styles display correctly
- [ ] No console errors

### Mobile/Responsive

**Test responsive design:**
1. Open http://localhost:3000
2. Open dev tools (F12)
3. Toggle device toolbar (Ctrl+Shift+M)
4. Test different sizes:
   - [ ] iPhone SE (375×667)
   - [ ] iPhone 12 Pro (390×844)
   - [ ] iPad (768×1024)
   - [ ] Desktop (1920×1080)

**Verify for each size:**
- [ ] Sidebar adapts/collapses
- [ ] Floating bot remains accessible
- [ ] Chat input visible
- [ ] Buttons are tappable
- [ ] Text is readable
- [ ] No horizontal scroll

### Performance Testing

**Check Performance:**
```bash
# Build for production
cd frontend
npm run build

# Serve production build
npx serve -s build -p 3000
```

**Test:**
- [ ] Page load time < 3 seconds
- [ ] No console warnings
- [ ] Lighthouse score > 90
- [ ] Memory usage reasonable

---

## Troubleshooting

### Frontend Tests Fail

**Issue:** Tests fail with module errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm test
```

**Issue:** Tests timeout
- Increase jest timeout in setupTests.js
- Check if API endpoints are mocked correctly

### GUI Not Loading

**Issue:** Blank page or 404
1. Check frontend is running: http://localhost:3000
2. Check backend is running: http://localhost:8000/health
3. Check browser console for errors
4. Clear browser cache
5. Check TROUBLESHOOTING.md

**Issue:** API calls fail
1. Verify backend is running
2. Check proxy in package.json
3. Verify CORS settings
4. Check network tab in dev tools

### Floating Bot Not Working

**Issue:** Button not visible
- Check z-index in FloatingBot.css
- Verify component is imported in Dashboard.js
- Check browser console for errors

**Issue:** WebSocket fails
- Verify backend WebSocket endpoint
- Check browser WebSocket support
- Should fallback to REST API

### Performance Issues

**Issue:** Slow loading
- Build for production
- Check network tab for large assets
- Verify API response times
- Check for memory leaks

---

## Test Summary

After completing all tests, you should have:

✅ **Backend:**
- 15 passing tests
- All endpoints working
- Integrations discoverable

✅ **Frontend:**
- All component tests passing
- Dashboard navigation working
- FloatingBot functional
- ChatInterface sending messages

✅ **Manual:**
- HTML mockup working
- All views accessible
- Both UI modes independent
- Responsive design verified

✅ **Integration:**
- API calls successful
- WebSocket connected
- Error handling works
- Cross-browser compatible

---

## Quick Reference Commands

```bash
# Backend tests
pytest tests/ -v

# Frontend tests
cd frontend && npm test

# Run full platform
./setup.sh

# Docker
docker-compose up --build

# Validation
./validate-setup.sh

# View mockup
open mockup-gui.html
```

---

## Next Steps

After successful testing:
1. Review test coverage reports
2. Add integration tokens to .env
3. Test with real API keys
4. Deploy to production
5. Set up monitoring
6. Add more tests as needed

For issues, see `TROUBLESHOOTING.md`
