/**
 * Background Service Worker (Manifest V3)
 * 
 * CRITICAL: Service workers in Manifest V3 have NO DOM access and limited Web APIs.
 * Cannot directly use AudioContext, MediaRecorder, or process audio streams.
 * 
 * Solution: Offscreen Document Pattern
 * - Creates a hidden HTML document with full Web API access
 * - Passes MediaStream to offscreen document for processing
 * - Manages lifecycle of offscreen document
 */

let offscreenDocumentCreated = false;
let currentStreamId = null;

// Listen for messages from content script to start capture
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'START_CAPTURE') {
    handleStartCapture(sender.tab.id)
      .then(() => sendResponse({ success: true }))
      .catch((error) => {
        console.error('Failed to start capture:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true; // Will respond asynchronously
  }
  
  if (message.type === 'STOP_CAPTURE') {
    handleStopCapture()
      .then(() => sendResponse({ success: true }))
      .catch((error) => {
        console.error('Failed to stop capture:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true;
  }
});

/**
 * Create offscreen document if it doesn't exist
 * Offscreen documents persist until explicitly closed
 */
async function createOffscreenDocument() {
  if (offscreenDocumentCreated) {
    return;
  }

  // Check if offscreen document already exists
  const existingContexts = await chrome.runtime.getContexts({
    contextTypes: ['OFFSCREEN_DOCUMENT']
  });

  if (existingContexts.length > 0) {
    offscreenDocumentCreated = true;
    return;
  }

  // Create new offscreen document
  await chrome.offscreen.createDocument({
    url: 'offscreen.html',
    reasons: ['USER_MEDIA'], // Reason for creating offscreen document
    justification: 'Process audio stream from tab capture for real-time transcription'
  });

  offscreenDocumentCreated = true;
  console.log('Offscreen document created');
}

/**
 * Start audio capture from the active tab
 * Uses chrome.tabCapture API to get MediaStream
 */
async function handleStartCapture(tabId) {
  try {
    // Ensure offscreen document exists before capturing
    await createOffscreenDocument();

    // Capture audio from the tab
    // This returns a MediaStreamId that can be used in the offscreen document
    const streamId = await chrome.tabCapture.getMediaStreamId({
      targetTabId: tabId
    });

    currentStreamId = streamId;
    console.log('Got stream ID:', streamId);

    // Send stream ID to offscreen document for processing
    await chrome.runtime.sendMessage({
      type: 'START_AUDIO_PROCESSING',
      streamId: streamId,
      target: 'offscreen'
    });

    console.log('Audio capture started successfully');
  } catch (error) {
    console.error('Error in handleStartCapture:', error);
    throw error;
  }
}

/**
 * Stop audio capture and cleanup
 */
async function handleStopCapture() {
  try {
    if (currentStreamId) {
      // Notify offscreen document to stop processing
      await chrome.runtime.sendMessage({
        type: 'STOP_AUDIO_PROCESSING',
        target: 'offscreen'
      });

      currentStreamId = null;
    }

    console.log('Audio capture stopped');
  } catch (error) {
    console.error('Error in handleStopCapture:', error);
    throw error;
  }
}

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener(() => {
  console.log('Live Interview Copilot installed');
});

/**
 * Forward messages from offscreen document to content script
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Messages from offscreen document to be forwarded to content script
  if (message.target === 'content_script') {
    // Find the Google Meet tab and send message
    chrome.tabs.query({ url: 'https://meet.google.com/*' }, (tabs) => {
      if (tabs.length > 0) {
        chrome.tabs.sendMessage(tabs[0].id, message);
      }
    });
  }
});

console.log('Background service worker initialized');
