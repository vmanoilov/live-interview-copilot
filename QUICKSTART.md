# Quick Start Guide

Get up and running with Live Interview Copilot in 5 minutes.

## 🚀 Quick Setup

### 1. Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Quick setup
./setup.sh

# Add API keys to .env
cp .env.example .env
# Edit .env with your keys:
# DEEPGRAM_API_KEY=...
# GROQ_API_KEY=...

# Start server
python main.py
```

✅ Backend should now be running on http://localhost:8000

### 2. Extension (1 minute)

1. Open Chrome: `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder
5. Pin extension to toolbar

✅ Extension is now installed

### 3. Test on Google Meet (2 minutes)

1. Join any Google Meet call
2. Look for purple overlay (top-right)
3. Click "Start Capture"
4. Grant permissions when prompted
5. Speak or play audio
6. Watch for transcripts and AI responses!

## 🔑 Getting API Keys

### Deepgram (Speech-to-Text)

1. Visit: https://console.deepgram.com/
2. Sign up (free tier available)
3. Create a new API key
4. Copy to `.env` as `DEEPGRAM_API_KEY`

### Groq (LLM)

1. Visit: https://console.groq.com/
2. Sign up (free tier available)
3. Create a new API key
4. Copy to `.env` as `GROQ_API_KEY`

## 📝 Customize Resume

Edit `backend/main.py` and update the `RESUME_TEXT` variable:

```python
RESUME_TEXT = """
Your Name - Your Title
- Your experience bullet 1
- Your experience bullet 2
...
"""
```

## 🎯 Usage Tips

**During Interview:**
- Start capture at beginning of interview
- Keep overlay visible but unobtrusive
- Use AI suggestions as conversation starters
- Don't read responses verbatim - be natural
- Stop capture when interview ends

**Best Practices:**
- Test with mock interviews first
- Have backup answers prepared
- Stay engaged with interviewer
- Use AI as assistance, not crutch
- Be ethical and transparent

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check Python version (3.9+) and run `pip install -r requirements.txt` |
| No transcriptions | Verify Deepgram API key is valid in `.env` |
| No AI responses | Verify Groq API key is valid in `.env` |
| Extension not visible | Ensure you're on https://meet.google.com/* |
| Can't start capture | Check backend is running on port 8000 |
| WebSocket errors | Check CORS settings and firewall |

## 📖 More Info

- **Full README**: See `README.md` for complete documentation
- **Testing Guide**: See `TESTING.md` for detailed testing procedures
- **Troubleshooting**: Check backend logs and browser console

## ⚠️ Important Notes

- **Privacy**: All processing happens locally on your machine
- **Ethics**: Use responsibly and follow company/interview guidelines
- **Performance**: Backend requires ~200MB RAM and <20% CPU
- **Latency**: Expect 2-3 seconds for AI responses
- **Free Tier Limits**: Check Deepgram and Groq quotas

## 🎓 Learning Resources

**Chrome Extensions:**
- [Manifest V3 Guide](https://developer.chrome.com/docs/extensions/mv3/intro/)
- [Offscreen Documents](https://developer.chrome.com/docs/extensions/reference/offscreen/)

**APIs:**
- [Deepgram Docs](https://developers.deepgram.com/)
- [Groq Docs](https://console.groq.com/docs)

**FastAPI:**
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)

---

**Ready to go?** Start with step 1 above! 🚀
