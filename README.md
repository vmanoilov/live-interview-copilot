# 🎤 Live Interview Copilot

A Chrome Extension that provides real-time AI-powered assistance during Google Meet interviews. Captures audio, transcribes it using Deepgram, and generates helpful response suggestions using Groq's Llama 3.

## 🌟 Features

- **Real-Time Audio Capture**: Captures tab audio from Google Meet using Chrome's `tabCapture` API
- **Live Transcription**: Streams audio to Deepgram for accurate speech-to-text conversion
- **AI-Powered Assistance**: Sends transcribed questions to Groq's Llama 3 with resume context
- **Elegant UI**: Draggable overlay with Shadow DOM for style isolation
- **Low Latency**: Optimized for real-time performance (<2-3 seconds end-to-end)
- **Manifest V3**: Uses the modern Offscreen Document pattern for audio processing

## 🏗️ Architecture

### Chrome Extension (Manifest V3)

```
extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker (manages offscreen document)
├── offscreen.html         # Hidden document for audio processing
├── offscreen.js           # Audio capture and WebSocket streaming
├── content_script.js      # UI overlay with Shadow DOM
├── popup.html             # Extension popup
└── icons/                 # Extension icons
```

**Key Architectural Decisions:**

1. **Offscreen Document Pattern**: Manifest V3 service workers cannot access Web APIs like `AudioContext` and `MediaRecorder`. Solution: Create a hidden offscreen document that has full API access.

2. **Shadow DOM**: Isolates UI styles from Google Meet's CSS to prevent conflicts.

3. **WebSocket Architecture**: Bidirectional communication between extension and backend for audio streaming and response delivery.

### Backend (Python/FastAPI)

```
backend/
├── main.py               # FastAPI app with WebSocket endpoint
├── deepgram_client.py    # Deepgram SDK integration
├── groq_client.py        # Groq LLM integration
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variable template
```

## 📋 Prerequisites

- **Chrome Browser**: Version 96+ (for Manifest V3 support)
- **Python**: 3.9 or higher
- **API Keys**:
  - [Deepgram API Key](https://console.deepgram.com/) - for speech-to-text
  - [Groq API Key](https://console.groq.com/) - for LLM responses

## 🚀 Setup Instructions

### Backend Setup

#### Option 1: Automated Setup (Recommended)

The backend now features **automated setup** that runs when you start the server for the first time:

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Start the backend server**:
   ```bash
   python main.py
   ```

   On first run, the server will automatically:
   - Check Python version (requires 3.9+)
   - Install all required dependencies from `requirements.txt`
   - Create a `.env` file from `.env.example`
   - Validate the configuration

3. **Configure API keys**:
   After the automated setup completes, edit the `.env` file and add your API keys:
   ```env
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Restart the server**:
   ```bash
   python main.py
   ```

   The server will start on `http://localhost:8000`

#### Option 2: Manual Setup (Alternative)

If you prefer manual control or the automated setup doesn't work:

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Run setup script** (Linux/Mac):
   ```bash
   ./setup.sh
   ```

   Or manually create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env` file** and add your API keys:
   ```env
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

6. **Update resume context** in `main.py`:
   - Edit the `RESUME_TEXT` variable with your actual resume
   - Or set `RESUME_PATH` in `.env` to load from file

7. **Start the backend server**:
   ```bash
   python main.py
   ```

   The server will start on `http://localhost:8000`

#### Setup Behavior

- **First Run**: Automated setup runs automatically when dependencies are missing
- **Subsequent Runs**: Setup is skipped if already complete (tracked via `.setup_complete` flag)
- **Manual Re-setup**: Delete `backend/.setup_complete` to trigger setup again
- **Configuration Check**: API keys are validated on every startup

### Chrome Extension Setup

1. **Open Chrome Extensions page**:
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right)

2. **Load the extension**:
   - Click "Load unpacked"
   - Select the `extension` folder from this project

3. **Verify installation**:
   - You should see "Live Interview Copilot" in your extensions list
   - Pin it to your toolbar for easy access

## 📖 Usage

### During an Interview

1. **Start Backend**: Ensure the Python backend is running (`python main.py`)

2. **Join Google Meet**: Navigate to a Google Meet call

3. **Activate Extension**: 
   - Look for the purple overlay in the top-right corner
   - Or click the extension icon in your toolbar

4. **Start Capture**:
   - Click "Start Capture" button in the overlay
   - Grant audio capture permissions if prompted

5. **View AI Assistance**:
   - Transcriptions appear in real-time
   - AI-generated response suggestions appear below transcripts
   - Use suggestions naturally in your conversation

6. **Stop Capture**: Click "Stop" when interview ends

### UI Features

- **Draggable**: Click and drag the header to reposition
- **Minimizable**: Click the "−" button to minimize
- **Auto-scroll**: Automatically scrolls to show latest responses

## 🔧 Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# Required
DEEPGRAM_API_KEY=your_key
GROQ_API_KEY=your_key

# Optional
HOST=0.0.0.0
PORT=8000
LLM_MODEL=llama3-70b-8192
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=150
```

### Resume Context

**Method 1: Inline** (in `main.py`):
```python
RESUME_TEXT = """
Your resume text here...
"""
```

**Method 2: File** (in `.env`):
```env
RESUME_PATH=/path/to/your/resume.txt
```

### Audio Settings

In `backend/config.py`:
- `AUDIO_SAMPLE_RATE`: 16000 (16kHz, optimal for Deepgram)
- `AUDIO_CHUNK_SIZE`: 250 (250ms chunks)
- `SENTENCE_END_PAUSE_MS`: 3000 (3 seconds pause detection)

## 🐛 Troubleshooting

### Extension Issues

**Problem**: "Failed to start capture"
- **Solution**: Ensure you're on a Google Meet page
- **Solution**: Check that backend is running on `localhost:8000`
- **Solution**: Verify manifest.json permissions

**Problem**: No audio is captured
- **Solution**: Check browser permissions for the extension
- **Solution**: Ensure Google Meet has audio enabled
- **Solution**: Try refreshing the Meet page

**Problem**: Overlay doesn't appear
- **Solution**: Check browser console for errors (F12)
- **Solution**: Verify content_script.js is loading
- **Solution**: Try disabling and re-enabling the extension

### Backend Issues

**Problem**: "Module not found" errors
- **Solution**: Ensure virtual environment is activated
- **Solution**: Run `pip install -r requirements.txt` again

**Problem**: "API key not configured"
- **Solution**: Check `.env` file exists and contains valid keys
- **Solution**: Verify no extra spaces in API keys

**Problem**: WebSocket connection fails
- **Solution**: Ensure backend is running on port 8000
- **Solution**: Check firewall settings
- **Solution**: Verify CORS configuration in main.py

**Problem**: Poor transcription quality
- **Solution**: Check audio input device quality
- **Solution**: Ensure stable internet connection
- **Solution**: Verify Deepgram API key is valid

### CORS Issues

If you see CORS errors in the browser console:

1. Verify `allow_origins` in `main.py` includes `chrome-extension://*`
2. Check Content Security Policy in `manifest.json`
3. Ensure WebSocket URL uses `ws://` not `wss://` for localhost

## 🔒 Security & Privacy

- **Local Processing**: Backend runs locally on your machine
- **No Data Storage**: Transcripts and responses are not stored
- **API Keys**: Keep your API keys secure and never commit them
- **Permissions**: Only requests necessary Chrome permissions
- **Open Source**: Code is transparent and auditable

## 🎯 Performance Metrics

Expected latency targets:

- **Audio Capture**: <50ms
- **Transcription**: 500-1000ms
- **LLM Response**: 1-2 seconds
- **Total End-to-End**: <3 seconds

## 🛠️ Development

### Testing Locally

1. **Test Backend**:
   ```bash
   cd backend
   python main.py
   ```
   Visit `http://localhost:8000` to see health check

2. **Test WebSocket**:
   Use a WebSocket client to connect to `ws://localhost:8000/ws/audio`

3. **Test Extension**:
   - Load unpacked extension
   - Open developer tools (F12)
   - Check console for logs

### Adding Features

- **Custom Models**: Modify `groq_client.py` to use different LLM models
- **UI Themes**: Edit styles in `content_script.js`
- **Additional Providers**: Add new clients similar to `deepgram_client.py`

## 📚 Technical Deep Dive

### Manifest V3 Challenges

**Problem**: Service workers have no DOM access
**Solution**: Offscreen Document pattern

```javascript
// background.js creates offscreen document
await chrome.offscreen.createDocument({
  url: 'offscreen.html',
  reasons: ['USER_MEDIA'],
  justification: 'Process audio stream'
});

// offscreen.js has full Web API access
const audioContext = new AudioContext();
const mediaRecorder = new MediaRecorder(stream);
```

### Audio Processing Pipeline

1. **Capture**: `chrome.tabCapture.getMediaStreamId()`
2. **Stream**: Pass to offscreen document
3. **Record**: `MediaRecorder` with webm/opus codec
4. **Chunk**: 250ms slices for real-time processing
5. **Stream**: Send via WebSocket to backend
6. **Transcribe**: Deepgram processes audio
7. **Respond**: Groq generates assistance
8. **Display**: Show in Shadow DOM overlay

### WebSocket Message Protocol

**Client → Server**:
```json
{
  "type": "audio",
  "timestamp": 1234567890
}
```
(followed by binary audio data)

**Server → Client**:
```json
{
  "type": "transcript",
  "text": "What is your experience with Python?"
}
```

```json
{
  "type": "llm_response",
  "text": "I have 5 years of Python experience...",
  "question": "What is your experience with Python?"
}
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Response streaming for lower perceived latency
- [ ] Multi-language support
- [ ] Resume parsing from PDF/DOCX
- [ ] Conversation history tracking
- [ ] Custom prompt templates
- [ ] Analytics dashboard

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- [Deepgram](https://deepgram.com/) for excellent speech-to-text API
- [Groq](https://groq.com/) for fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) for the async Python framework

## 📞 Support

Having issues? 

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review browser console logs (F12)
3. Check backend logs in terminal
4. Open an issue on GitHub

---

**⚠️ Disclaimer**: This tool is for educational and personal use. Be aware of company policies and interview guidelines before using any AI assistance during professional interviews. Always ensure transparency and ethical use.
