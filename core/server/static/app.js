/* ========================================================
   J.A.R.V.I.S. TACTICAL HUD JAVASCRIPT CONTROLLER
   WebSockets, Canvas Waveform Visualizer & Telemetry Bridge
   ======================================================== */

// DOM Elements
const timeDisplay = document.getElementById('timeDisplay');
const batteryDisplay = document.getElementById('batteryDisplay');
const weatherDisplay = document.getElementById('weatherDisplay');
const connStatus = document.getElementById('connStatus');
const volumeSlider = document.getElementById('volumeSlider');
const volumeVal = document.getElementById('volumeVal');
const starkBtn = document.getElementById('starkBtn');
const trackName = document.getElementById('trackName');
const trackArtist = document.getElementById('trackArtist');
const playPauseBtn = document.getElementById('playPauseBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const arcReactor = document.getElementById('arcReactor');
const promptText = document.getElementById('promptText');
const transcriptFeed = document.getElementById('transcriptFeed');
const commandForm = document.getElementById('commandForm');
const commandInput = document.getElementById('commandInput');
const canvas = document.getElementById('waveformCanvas');
const ctx = canvas.getContext('2d');

let ws = null;
let isSpeaking = false;
let audioActivityLevel = 0.2; // 0.2 idle, 1.0 active

// 1. Clock Updates
function updateClock() {
  const now = new Date();
  timeDisplay.innerText = now.toLocaleTimeString('en-US', { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();

// 2. WebSocket Telemetry Bridge
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    connStatus.innerText = 'ONLINE // TELEMETRY LINKED';
    connStatus.style.color = '#38ef7d';
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'telemetry') {
      updateTelemetryUI(data.data);
    } else if (data.type === 'conversation') {
      appendTranscript(data.user, data.jarvis);
      triggerSpeechAnimation();
    } else if (data.type === 'stark_protocol') {
      appendTranscript('System Protocol', `Tony Stark Protocol: ${data.song || 'Highway to Hell'} Active.`);
      triggerSpeechAnimation(3000);
    }
  };

  ws.onclose = () => {
    connStatus.innerText = 'STANDBY // RECONNECTING...';
    connStatus.style.color = '#f59e0b';
    setTimeout(connectWebSocket, 2000);
  };
}

// 3. UI Updates
function updateTelemetryUI(data) {
  if (!data) return;

  // Battery
  if (data.battery && data.battery.percentage !== null) {
    const icon = data.battery.is_charging ? '⚡ ' : '🔋 ';
    batteryDisplay.innerText = `${icon}${data.battery.percentage}%`;
  }

  // Volume
  if (data.volume !== null && data.volume !== undefined) {
    volumeSlider.value = data.volume;
    volumeVal.innerText = `${data.volume}%`;
  }

  // Weather
  if (data.weather && data.weather.temp_c) {
    weatherDisplay.innerText = `${data.weather.temp_c}°C ${data.weather.condition || ''}`;
  }

  // Spotify Track
  if (data.spotify && data.spotify.track && data.spotify.track.name) {
    trackName.innerText = data.spotify.track.name;
    trackArtist.innerText = data.spotify.track.artist;
  }
}

function appendTranscript(userText, jarvisText) {
  const now = new Date().toLocaleTimeString();

  if (userText) {
    const userDiv = document.createElement('div');
    userDiv.className = 'feed-entry user-entry';
    userDiv.innerHTML = `<span class="entry-time">[USER // ${now}]</span><p>${userText}</p>`;
    transcriptFeed.appendChild(userDiv);
  }

  if (jarvisText) {
    const jarvisDiv = document.createElement('div');
    jarvisDiv.className = 'feed-entry jarvis-entry';
    jarvisDiv.innerHTML = `<span class="entry-time">[JARVIS // ${now}]</span><p>${jarvisText}</p>`;
    transcriptFeed.appendChild(jarvisDiv);
  }

  transcriptFeed.scrollTop = transcriptFeed.scrollHeight;
}

function triggerSpeechAnimation(durationMs = 4000) {
  isSpeaking = true;
  audioActivityLevel = 1.0;
  promptText.innerText = '⚡ J.A.R.V.I.S. VOCAL ENGINE TRANSMITTING...';
  promptText.style.color = '#00f2fe';

  setTimeout(() => {
    isSpeaking = false;
    audioActivityLevel = 0.2;
    promptText.innerText = 'CLICK ARC REACTOR OR PRESS [SPACEBAR] TO TALK';
    promptText.style.color = '#7dd3fc';
  }, durationMs);
}

// 4. Command Input Form
commandForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = commandInput.value.trim();
  if (!text) return;

  commandInput.value = '';
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'command', text: text }));
  } else {
    fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: text })
    });
  }
});

// Quick Command Chips
document.querySelectorAll('.quick-chip').forEach(btn => {
  btn.addEventListener('click', () => {
    const cmd = btn.getAttribute('data-cmd');
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: 'command', text: cmd }));
    }
  });
});

// 5. Tony Stark Protocol Button
starkBtn.addEventListener('click', () => {
  fetch('/api/stark', { method: 'POST' });
});

// 6. Media Controls
playPauseBtn.addEventListener('click', () => fetch('/api/spotify/toggle', { method: 'POST' }));
prevBtn.addEventListener('click', () => fetch('/api/spotify/previous', { method: 'POST' }));
nextBtn.addEventListener('click', () => fetch('/api/spotify/next', { method: 'POST' }));

volumeSlider.addEventListener('input', (e) => {
  const val = e.target.value;
  volumeVal.innerText = `${val}%`;
  fetch(`/api/volume/${val}`, { method: 'POST' });
});

// 7. Arc Reactor Click to Talk
arcReactor.addEventListener('click', () => {
  promptText.innerText = '🎤 LISTENING TO VOICE COMMAND...';
  promptText.style.color = '#f6d365';
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'voice_input' }));
  }
});

// Spacebar push to talk
window.addEventListener('keydown', (e) => {
  if (e.code === 'Space' && document.activeElement !== commandInput) {
    e.preventDefault();
    arcReactor.click();
  }
});

// 8. Animated Waveform Canvas
let wavePhase = 0;
function drawWaveform() {
  requestAnimationFrame(drawWaveform);

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const width = canvas.width;
  const height = canvas.height;
  const centerY = height / 2;

  // Wave 1: Cyan primary sine
  ctx.beginPath();
  ctx.lineWidth = isSpeaking ? 3 : 1.5;
  ctx.strokeStyle = isSpeaking ? '#00f2fe' : 'rgba(0, 242, 254, 0.4)';

  for (let x = 0; x < width; x++) {
    const freq = isSpeaking ? 0.04 : 0.02;
    const amp = isSpeaking ? 28 : 8;
    const y = centerY + Math.sin(x * freq + wavePhase) * amp * Math.sin(x / width * Math.PI);
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // Wave 2: Outer Secondary Wave
  ctx.beginPath();
  ctx.lineWidth = 1;
  ctx.strokeStyle = isSpeaking ? 'rgba(246, 211, 101, 0.7)' : 'rgba(0, 242, 254, 0.2)';

  for (let x = 0; x < width; x++) {
    const freq = isSpeaking ? 0.06 : 0.03;
    const amp = isSpeaking ? 16 : 4;
    const y = centerY + Math.cos(x * freq - wavePhase * 1.5) * amp * Math.sin(x / width * Math.PI);
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  wavePhase += isSpeaking ? 0.12 : 0.04;
}

drawWaveform();
connectWebSocket();
