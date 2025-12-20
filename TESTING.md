# Testing & Verification Guide

This document provides step-by-step instructions to test and verify the Live Interview Copilot implementation.

## Pre-requisites Checklist

- [ ] Python 3.9+ installed
- [ ] Chrome browser (version 96+)
- [ ] Deepgram API key obtained
- [ ] Groq API key obtained

## Backend Testing

### 1. Installation Verification

```bash
cd backend

# Quick setup (recommended)
./setup.sh

# Manual setup (alternative)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration Test

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# DEEPGRAM_API_KEY=your_key_here
# GROQ_API_KEY=your_key_here
```

### 3. Basic Server Start Test

```bash
# With virtual environment activated
python main.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Health Check Test

Open browser and navigate to: `http://localhost:8000`

Expected response:
```json
{
  "status": "running",
  "service": "Live Interview Copilot Backend",
  "deepgram_configured": true,
  "groq_configured": true
}
```

### 5. WebSocket Connection Test

You can test the WebSocket endpoint using a WebSocket client or browser console:

```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/audio');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => console.log('Message:', event.data);
ws.onerror = (error) => console.error('Error:', error);
```

Expected: Connection should open successfully

## Chrome Extension Testing

### 1. Load Extension

1. Open Chrome and navigate to: `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `extension` folder
5. Verify extension appears in list

### 2. Extension Files Verification

Check that all files are present:
```
extension/
├── manifest.json ✓
├── background.js ✓
├── offscreen.html ✓
├── offscreen.js ✓
├── content_script.js ✓
├── popup.html ✓
└── icons/
    ├── icon16.png ✓
    ├── icon48.png ✓
    └── icon128.png ✓
```

### 3. Manifest Validation

In Chrome DevTools for the extension:
```javascript
// Check manifest loads correctly
chrome.runtime.getManifest()
```

Expected: Should return manifest object with no errors

### 4. Permissions Check

Verify permissions are granted:
- `tabCapture` - for capturing audio
- `scripting` - for content scripts
- `activeTab` - for active tab access
- `offscreen` - for offscreen document

### 5. Popup Test

1. Click the extension icon in toolbar
2. Popup should open showing:
   - Title: "🎤 Live Interview Copilot"
   - Status indicator
   - Usage instructions

## End-to-End Testing

### Test Scenario 1: Basic Flow (Without Google Meet)

**Backend Setup:**
1. Start backend: `python main.py`
2. Verify server is running on port 8000

**Extension Test:**
1. Navigate to any webpage (not Meet yet)
2. Open Chrome DevTools (F12)
3. Check console for any errors

Expected: No errors, extension loads cleanly

### Test Scenario 2: Google Meet Integration

**Prerequisites:**
- Backend running
- Extension loaded
- Join a Google Meet call (can be a test call)

**Steps:**

1. **Navigate to Google Meet**
   - Go to: `https://meet.google.com/`
   - Join or start a meeting

2. **Verify Overlay Appears**
   - Look for purple overlay in top-right corner
   - Should show "Interview Copilot" title
   - Status indicator should be gray (inactive)

3. **Test Drag Functionality**
   - Click and hold overlay header
   - Drag to different position
   - Release
   - Overlay should stay in new position

4. **Test Minimize**
   - Click "−" button
   - Content area should hide
   - Click "+" to restore

5. **Start Capture**
   - Click "Start Capture" button
   - Should prompt for permissions (first time)
   - Status indicator turns green
   - "Stop" button becomes active

6. **Test Audio Capture**
   - Speak into microphone or play audio
   - Watch backend console for transcription logs
   - Watch overlay for transcript messages

7. **Verify LLM Responses**
   - Speak a complete question
   - Wait 2-3 seconds
   - AI response should appear in overlay
   - Format: "AI Assistant" label with response text

8. **Stop Capture**
   - Click "Stop" button
   - Status indicator turns gray
   - "Start Capture" button becomes active again

### Test Scenario 3: Error Handling

**Test 1: Backend Not Running**
1. Stop backend server
2. Try to start capture
3. Expected: Error message in overlay

**Test 2: Invalid API Keys**
1. Set invalid keys in .env
2. Restart backend
3. Try to capture audio
4. Expected: Error logged in backend console

**Test 3: Network Interruption**
1. Start capture successfully
2. Stop backend during capture
3. Expected: Reconnection attempts or error message

## Performance Verification

### Latency Measurements

Use browser DevTools Performance tab to measure:

**Target Metrics:**
- Audio capture start: <100ms
- First transcript: <1s after speaking
- LLM response: <3s after question ends
- UI update: <50ms

### Resource Usage

Monitor in Chrome Task Manager (`Shift+Esc`):
- Extension memory: <50MB
- CPU usage: <5% when idle, <15% during capture

Backend:
```bash
# Check CPU and memory usage
top -p $(pgrep -f "python main.py")
```

Expected:
- Memory: <200MB
- CPU: <20% during active transcription

## Debugging Tips

### Backend Debugging

**Enable verbose logging:**
```python
# In main.py, change logging level
logging.basicConfig(level=logging.DEBUG)
```

**Check WebSocket connections:**
```bash
# View active connections
netstat -an | grep 8000
```

### Extension Debugging

**Background Script:**
1. Go to `chrome://extensions/`
2. Find "Live Interview Copilot"
3. Click "service worker" link
4. Opens DevTools for background script

**Content Script:**
1. On Google Meet page, open DevTools (F12)
2. Check Console tab for content script logs
3. Network tab shows WebSocket connections

**Offscreen Document:**
1. Navigate to `chrome://extensions/`
2. Enable Developer mode
3. Find extension and click "Inspect views: offscreen.html"

### Common Issues

**Issue: "Failed to start capture"**
- Check: Backend is running
- Check: On Google Meet page
- Check: Permissions granted

**Issue: No transcriptions**
- Check: Deepgram API key is valid
- Check: Audio is playing in Meet
- Check: WebSocket connection established
- Check: Backend logs for errors

**Issue: No LLM responses**
- Check: Groq API key is valid
- Check: Complete sentences detected
- Check: Backend logs for errors

**Issue: UI not appearing**
- Check: On Google Meet domain
- Check: Content script loaded (DevTools)
- Check: No CSS conflicts

## Security Testing

### Check for Sensitive Data Leaks

1. **Console Logs:**
   - No API keys logged
   - No personal information logged

2. **Network Traffic:**
   - Open DevTools → Network
   - Verify HTTPS for API calls
   - Verify WebSocket uses proper origin

3. **Storage:**
   - Check chrome.storage
   - Should not persist transcripts

## Automated Tests (Future)

Placeholder for future test automation:

```bash
# Backend tests
pytest tests/

# Extension tests
npm test
```

## Reporting Issues

When reporting issues, include:

1. **Environment:**
   - OS version
   - Chrome version
   - Python version

2. **Logs:**
   - Backend console output
   - Browser console errors
   - Extension service worker logs

3. **Steps to reproduce:**
   - Exact sequence of actions
   - Expected vs actual behavior

4. **Configuration:**
   - Manifest version
   - API key status (valid/invalid, don't share keys)

## Success Criteria

✅ Extension loads without errors
✅ Backend starts successfully
✅ WebSocket connection establishes
✅ Audio capture works on Google Meet
✅ Transcriptions appear in real-time
✅ LLM responses generate within 3 seconds
✅ UI is responsive and draggable
✅ No memory leaks during 10-minute session
✅ Clean disconnection and cleanup

---

**Ready for Production?**

Before using in real interviews:
- [ ] Test in mock interview scenarios
- [ ] Verify consistent performance
- [ ] Ensure ethical compliance
- [ ] Have backup plans
- [ ] Practice using the tool
