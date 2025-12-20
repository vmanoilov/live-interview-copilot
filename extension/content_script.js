/**
 * Content Script - UI Layer
 * 
 * Runs in the context of Google Meet pages.
 * Responsibilities:
 * 1. Create Shadow DOM for style isolation
 * 2. Render draggable overlay UI
 * 3. Handle start/stop capture controls
 * 4. Display transcriptions and LLM responses
 * 5. Communicate with background script
 */

// State management
let isCapturing = false;
let shadowRoot = null;
let overlayContainer = null;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeUI);
} else {
  initializeUI();
}

/**
 * Initialize the UI with Shadow DOM
 * Shadow DOM provides style isolation from Google Meet's CSS
 */
function initializeUI() {
  // Create container for shadow root
  const container = document.createElement('div');
  container.id = 'live-interview-copilot-root';
  container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000;';
  document.body.appendChild(container);

  // Attach shadow DOM (mode: 'open' allows external access if needed)
  shadowRoot = container.attachShadow({ mode: 'open' });

  // Create the overlay UI
  createOverlayUI();

  // Make it draggable
  makeDraggable(container);

  console.log('Live Interview Copilot UI initialized');
}

/**
 * Create the overlay UI structure
 */
function createOverlayUI() {
  const styles = `
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    .copilot-overlay {
      width: 400px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      color: white;
      overflow: hidden;
    }

    .copilot-header {
      padding: 16px 20px;
      background: rgba(0, 0, 0, 0.2);
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: move;
      user-select: none;
    }

    .copilot-title {
      font-size: 16px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .copilot-status {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #10b981;
      animation: pulse 2s ease-in-out infinite;
    }

    .copilot-status.inactive {
      background: #6b7280;
      animation: none;
    }

    @keyframes pulse {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }

    .copilot-controls {
      padding: 16px 20px;
      display: flex;
      gap: 10px;
    }

    .copilot-button {
      flex: 1;
      padding: 10px 16px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    .copilot-button.primary {
      background: #10b981;
      color: white;
    }

    .copilot-button.primary:hover {
      background: #059669;
      transform: translateY(-1px);
    }

    .copilot-button.danger {
      background: #ef4444;
      color: white;
    }

    .copilot-button.danger:hover {
      background: #dc2626;
      transform: translateY(-1px);
    }

    .copilot-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }

    .copilot-content {
      padding: 16px 20px;
      max-height: 400px;
      overflow-y: auto;
      background: rgba(255, 255, 255, 0.1);
    }

    .copilot-content::-webkit-scrollbar {
      width: 6px;
    }

    .copilot-content::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.1);
    }

    .copilot-content::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.3);
      border-radius: 3px;
    }

    .copilot-message {
      margin-bottom: 16px;
      padding: 12px;
      background: rgba(0, 0, 0, 0.2);
      border-radius: 8px;
      animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .copilot-message-label {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      opacity: 0.7;
      margin-bottom: 6px;
    }

    .copilot-message-text {
      font-size: 14px;
      line-height: 1.5;
    }

    .copilot-placeholder {
      text-align: center;
      padding: 40px 20px;
      opacity: 0.5;
      font-size: 14px;
    }

    .copilot-minimize {
      background: none;
      border: none;
      color: white;
      font-size: 20px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 4px;
      transition: background 0.2s;
    }

    .copilot-minimize:hover {
      background: rgba(255, 255, 255, 0.1);
    }
  `;

  const html = `
    <style>${styles}</style>
    <div class="copilot-overlay">
      <div class="copilot-header" id="header">
        <div class="copilot-title">
          <span class="copilot-status inactive" id="status"></span>
          <span>Interview Copilot</span>
        </div>
        <button class="copilot-minimize" id="minimize">−</button>
      </div>
      <div class="copilot-controls">
        <button class="copilot-button primary" id="startBtn">Start Capture</button>
        <button class="copilot-button danger" id="stopBtn" disabled>Stop</button>
      </div>
      <div class="copilot-content" id="content">
        <div class="copilot-placeholder">Click "Start Capture" to begin</div>
      </div>
    </div>
  `;

  shadowRoot.innerHTML = html;

  // Get references to elements
  overlayContainer = shadowRoot.querySelector('.copilot-overlay');
  const startBtn = shadowRoot.getElementById('startBtn');
  const stopBtn = shadowRoot.getElementById('stopBtn');
  const minimizeBtn = shadowRoot.getElementById('minimize');

  // Add event listeners
  startBtn.addEventListener('click', handleStartCapture);
  stopBtn.addEventListener('click', handleStopCapture);
  minimizeBtn.addEventListener('click', toggleMinimize);
}

/**
 * Handle start capture button click
 */
function handleStartCapture() {
  const startBtn = shadowRoot.getElementById('startBtn');
  const stopBtn = shadowRoot.getElementById('stopBtn');
  const status = shadowRoot.getElementById('status');

  startBtn.disabled = true;
  startBtn.textContent = 'Starting...';

  // Request background script to start capture
  chrome.runtime.sendMessage({ type: 'START_CAPTURE' }, (response) => {
    if (response && response.success) {
      isCapturing = true;
      startBtn.style.display = 'none';
      stopBtn.disabled = false;
      status.classList.remove('inactive');
      
      clearContent();
      addMessage('System', 'Audio capture started. Listening...', 'system');
      
      console.log('Capture started successfully');
    } else {
      startBtn.disabled = false;
      startBtn.textContent = 'Start Capture';
      
      const error = response?.error || 'Unknown error';
      addMessage('Error', `Failed to start capture: ${error}`, 'error');
      
      console.error('Failed to start capture:', error);
    }
  });
}

/**
 * Handle stop capture button click
 */
function handleStopCapture() {
  const startBtn = shadowRoot.getElementById('startBtn');
  const stopBtn = shadowRoot.getElementById('stopBtn');
  const status = shadowRoot.getElementById('status');

  stopBtn.disabled = true;

  chrome.runtime.sendMessage({ type: 'STOP_CAPTURE' }, (response) => {
    isCapturing = false;
    startBtn.style.display = 'block';
    startBtn.disabled = false;
    startBtn.textContent = 'Start Capture';
    stopBtn.style.display = 'block';
    status.classList.add('inactive');
    
    addMessage('System', 'Audio capture stopped', 'system');
    
    console.log('Capture stopped');
  });
}

/**
 * Toggle minimize/maximize overlay
 */
function toggleMinimize() {
  const content = shadowRoot.querySelector('.copilot-content');
  const controls = shadowRoot.querySelector('.copilot-controls');
  const minimizeBtn = shadowRoot.getElementById('minimize');
  
  if (content.style.display === 'none') {
    content.style.display = 'block';
    controls.style.display = 'flex';
    minimizeBtn.textContent = '−';
  } else {
    content.style.display = 'none';
    controls.style.display = 'none';
    minimizeBtn.textContent = '+';
  }
}

/**
 * Make the overlay draggable
 */
function makeDraggable(element) {
  let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  
  const header = shadowRoot.getElementById('header');
  header.onmousedown = dragMouseDown;

  function dragMouseDown(e) {
    e.preventDefault();
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e.preventDefault();
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    element.style.top = (element.offsetTop - pos2) + 'px';
    element.style.left = (element.offsetLeft - pos1) + 'px';
    element.style.right = 'auto';
  }

  function closeDragElement() {
    document.onmouseup = null;
    document.onmousemove = null;
  }
}

/**
 * Add a message to the content area
 */
function addMessage(label, text, type = 'info') {
  const content = shadowRoot.getElementById('content');
  
  // Remove placeholder if it exists
  const placeholder = content.querySelector('.copilot-placeholder');
  if (placeholder) {
    placeholder.remove();
  }

  const messageEl = document.createElement('div');
  messageEl.className = 'copilot-message';
  messageEl.innerHTML = `
    <div class="copilot-message-label">${label}</div>
    <div class="copilot-message-text">${text}</div>
  `;

  content.appendChild(messageEl);
  content.scrollTop = content.scrollHeight;
}

/**
 * Clear all messages
 */
function clearContent() {
  const content = shadowRoot.getElementById('content');
  content.innerHTML = '';
}

/**
 * Listen for messages from background/offscreen scripts
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.target !== 'content_script') {
    return;
  }

  switch (message.type) {
    case 'transcript':
      addMessage('Transcript', message.text, 'transcript');
      break;
      
    case 'llm_response':
      addMessage('AI Assistant', message.text, 'llm');
      break;
      
    case 'ERROR':
      addMessage('Error', message.message, 'error');
      break;
      
    case 'CAPTURE_STARTED':
      console.log('Capture started notification received');
      break;
      
    case 'CAPTURE_STOPPED':
      console.log('Capture stopped notification received');
      break;
  }
});

console.log('Content script loaded');
