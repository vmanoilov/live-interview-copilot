/**
 * Offscreen Document - Audio Processing Context
 * 
 * This script runs in a hidden document with full Web API access.
 * Handles audio stream processing that cannot be done in the service worker.
 * 
 * Key responsibilities:
 * 1. Receive MediaStream from background script
 * 2. Convert audio to 16kHz sample rate for Deepgram
 * 3. Use MediaRecorder to chunk audio data
 * 4. Stream audio via WebSocket to backend
 * 5. Receive transcriptions and LLM responses
 */

const BACKEND_WS_URL = 'ws://localhost:8000/ws/audio';
let mediaStream = null;
let mediaRecorder = null;
let websocket = null;
let audioContext = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 2000; // 2 seconds

/**
 * Listen for messages from background script
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.target !== 'offscreen') {
    return;
  }

  if (message.type === 'START_AUDIO_PROCESSING') {
    handleStartAudioProcessing(message.streamId)
      .then(() => sendResponse({ success: true }))
      .catch((error) => {
        console.error('Failed to start audio processing:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true;
  }

  if (message.type === 'STOP_AUDIO_PROCESSING') {
    handleStopAudioProcessing();
    sendResponse({ success: true });
  }
});

/**
 * Initialize WebSocket connection to backend
 */
function initWebSocket() {
  return new Promise((resolve, reject) => {
    try {
      websocket = new WebSocket(BACKEND_WS_URL);

      websocket.onopen = () => {
        console.log('WebSocket connected to backend');
        reconnectAttempts = 0;
        resolve();
      };

      websocket.onmessage = (event) => {
        handleWebSocketMessage(event.data);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      websocket.onclose = () => {
        console.log('WebSocket closed');
        attemptReconnect();
      };
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Attempt to reconnect WebSocket with exponential backoff
 */
function attemptReconnect() {
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    console.error('Max reconnection attempts reached');
    notifyContentScript({
      type: 'ERROR',
      message: 'Lost connection to backend'
    });
    return;
  }

  reconnectAttempts++;
  const delay = RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1);
  
  console.log(`Attempting reconnect ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS} in ${delay}ms`);
  
  setTimeout(() => {
    initWebSocket().catch(() => {
      // Will retry through onclose handler
    });
  }, delay);
}

/**
 * Handle messages received from backend
 */
function handleWebSocketMessage(data) {
  try {
    const message = JSON.parse(data);
    
    // Forward transcriptions and LLM responses to content script
    if (message.type === 'transcript' || message.type === 'llm_response') {
      notifyContentScript(message);
    }
    
    console.log('Received from backend:', message.type);
  } catch (error) {
    console.error('Error parsing WebSocket message:', error);
  }
}

/**
 * Send message to content script via background script
 */
function notifyContentScript(message) {
  chrome.runtime.sendMessage({
    ...message,
    target: 'content_script'
  });
}

/**
 * Start audio processing
 * 1. Get MediaStream from streamId
 * 2. Initialize AudioContext for resampling
 * 3. Set up MediaRecorder
 * 4. Connect to WebSocket
 */
async function handleStartAudioProcessing(streamId) {
  try {
    // Initialize WebSocket first
    await initWebSocket();

    // Get the media stream using the streamId
    // Note: In Manifest V3, we need to use navigator.mediaDevices.getUserMedia
    // with the constraint that includes the chromeMediaSourceId
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        mandatory: {
          chromeMediaSource: 'tab',
          chromeMediaSourceId: streamId
        }
      }
    });

    console.log('Got media stream');

    // Initialize AudioContext for potential resampling
    // Deepgram works best with 16kHz audio
    audioContext = new AudioContext({ sampleRate: 16000 });

    // Create MediaRecorder with appropriate settings
    // Using webm/opus codec which is widely supported
    const options = {
      mimeType: 'audio/webm;codecs=opus',
      audioBitsPerSecond: 128000
    };

    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      console.warn('Preferred MIME type not supported, using default');
      mediaRecorder = new MediaRecorder(mediaStream);
    } else {
      mediaRecorder = new MediaRecorder(mediaStream, options);
    }

    // Handle audio data chunks
    // Using timeslice of 250ms for real-time responsiveness
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0 && websocket && websocket.readyState === WebSocket.OPEN) {
        // Convert blob to array buffer and send to backend
        event.data.arrayBuffer().then((buffer) => {
          // Send audio chunk with metadata
          const message = JSON.stringify({
            type: 'audio',
            timestamp: Date.now()
          });
          
          // Send metadata first
          websocket.send(message);
          // Then send audio data
          websocket.send(buffer);
        });
      }
    };

    mediaRecorder.onerror = (error) => {
      console.error('MediaRecorder error:', error);
    };

    // Start recording with 250ms chunks
    mediaRecorder.start(250);
    console.log('MediaRecorder started');

    // Notify content script that capture has started
    notifyContentScript({
      type: 'CAPTURE_STARTED'
    });

  } catch (error) {
    console.error('Error in handleStartAudioProcessing:', error);
    throw error;
  }
}

/**
 * Stop audio processing and cleanup resources
 */
function handleStopAudioProcessing() {
  try {
    // Stop media recorder
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }

    // Stop all tracks in the media stream
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
    }

    // Close WebSocket connection
    if (websocket) {
      websocket.close();
    }

    // Close audio context
    if (audioContext) {
      audioContext.close();
    }

    // Reset state
    mediaRecorder = null;
    mediaStream = null;
    websocket = null;
    audioContext = null;
    reconnectAttempts = 0;

    console.log('Audio processing stopped and cleaned up');

    // Notify content script
    notifyContentScript({
      type: 'CAPTURE_STOPPED'
    });

  } catch (error) {
    console.error('Error in handleStopAudioProcessing:', error);
  }
}

console.log('Offscreen document initialized');
