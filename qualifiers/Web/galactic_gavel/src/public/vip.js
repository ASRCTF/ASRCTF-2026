/**
 * NebulaMart Auction WebSocket Client
 * ─────────────────────────────────────
 * Connects to the private auction room over WebSocket and handles
 * bid submission, real-time feed updates, and auction state display.
 *
 * WebSocket endpoint: ws://<host>/auction
 * Required query parameter: ?room=<ROOM_ID>
 *
 * Message format (client → server):
 *   Place a bid:  { "type": "bid", "amount": <integer> }
 *   Ping:         { "type": "ping" }
 *
 * Message format (server → client):
 *   welcome  — initial state + rules
 *   state    — current highest bid update
 *   bid      — a new bid was placed (by you or another bidder)
 *   system   — system announcement
 *   error    — error with your last action
 *   flag     — 🏆 you won! flag is in this message
 *   pong     — ping reply
 */

(function () {
  'use strict';

  // ── DOM refs ──────────────────────────────────────────────────────────────
  const auctionRoom     = document.getElementById('auction-room');
  const accessDenied    = document.getElementById('access-denied-msg');
  const wsStatus        = document.getElementById('ws-status');
  const wsStatusText    = document.getElementById('ws-status-text');
  const roomBadge       = document.getElementById('room-badge');
  const currentBidDisp  = document.getElementById('current-bid-display');
  const currentLeader   = document.getElementById('current-leader-name');
  const feedList        = document.getElementById('feed-list');
  const walletDisplay   = document.getElementById('wallet-balance-display');
  const myIdentityBadge = document.getElementById('my-identity-badge');
  const bidForm         = document.getElementById('bid-form');
  const bidInput        = document.getElementById('bid-amount-input');
  const placeBidBtn     = document.getElementById('place-bid-btn');
  const bidHint         = document.getElementById('bid-hint-text');
  const transferForm    = document.getElementById('transfer-form');
  const transferTarget  = document.getElementById('transfer-target-input');
  const transferAmount  = document.getElementById('transfer-amount-input');
  const transferBtn     = document.getElementById('transfer-btn');
  const flagReveal      = document.getElementById('flag-reveal');
  const flagDisplay     = document.getElementById('flag-display');
  const artifactDesc    = document.getElementById('artifact-desc');
  const soldBanner      = document.getElementById('sold-banner');
  const lockOverlay     = document.getElementById('lock-overlay');
  const lockTimer       = document.getElementById('lock-timer');

  // ── Read room ID from URL ─────────────────────────────────────────────────
  const params = new URLSearchParams(window.location.search);
  const roomId = params.get('room');

  if (!roomId) {
    accessDenied.style.display = 'block';
    return;
  }

  auctionRoom.style.display = 'grid';

  // ── WebSocket connection ──────────────────────────────────────────────────
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${wsProtocol}//${window.location.host}/auction?room=${encodeURIComponent(roomId)}`;

  let ws = null;
  let reconnectTimer = null;
  let myBidderName = null;
  let auctionEnded = false;
  let currentHighestAmount = 0;

  function formatCredits(n) {
    return '₢ ' + Number(n).toLocaleString('en-US');
  }

  function now() {
    const d = new Date();
    return d.toTimeString().slice(0, 8);
  }

  function setStatus(state, text) {
    wsStatus.className = `ws-status ${state}`;
    wsStatusText.textContent = text;
    roomBadge.textContent = state.toUpperCase();
  }

  // ── Feed helpers ──────────────────────────────────────────────────────────
  function addFeedItem(iconHtml, textHtml) {
    const item = document.createElement('div');
    item.className = 'feed-item';
    item.innerHTML = `
      <div class="feed-icon">${iconHtml}</div>
      <div class="feed-body">
        <div class="feed-text">${textHtml}</div>
        <div class="feed-time">${now()}</div>
      </div>`;
    feedList.prepend(item);

    // Cap feed at 50 items
    while (feedList.children.length > 50) {
      feedList.removeChild(feedList.lastChild);
    }
  }

  // ── UI Updates ────────────────────────────────────────────────────────────
  function updateBidDisplay(amount, leader) {
    currentHighestAmount = amount;
    currentBidDisp.textContent = formatCredits(amount);
    currentBidDisp.classList.add('updated');
    setTimeout(() => currentBidDisp.classList.remove('updated'), 400);
    if (leader) currentLeader.textContent = leader;
  }

  function updateWallet(amount) {
    walletDisplay.textContent = formatCredits(amount);
    walletDisplay.classList.add('updated');
    setTimeout(() => walletDisplay.classList.remove('updated'), 400);
  }

  // ── Fake Timer Logic ──────────────────────────────────────────────────────
  let lockTimerInterval = null;
  function startLockTimer() {
    if (lockTimerInterval) return;
    lockOverlay.classList.add('visible');
    
    // Starting values for visual effect
    let y = 500000;
    let mo = 11;
    let d = 29;
    let h = 23;
    let m = 59;
    let s = 59;
    
    lockTimerInterval = setInterval(() => {
      s--;
      if (s < 0) { s = 59; m--; }
      if (m < 0) { m = 59; h--; }
      
      const pad = (n) => String(n).padStart(2, '0');
      lockTimer.innerHTML = `${y.toLocaleString()} <span>YRS</span> : ${pad(mo)} <span>MO</span> : ${pad(d)} <span>D</span> : ${pad(h)} <span>H</span> : ${pad(m)} <span>M</span> : ${pad(s)} <span>S</span>`;
    }, 1000);
  }

  function hideLockTimer() {
    if (lockTimerInterval) {
      clearInterval(lockTimerInterval);
      lockTimerInterval = null;
    }
    lockOverlay.classList.remove('visible');
  }

  // ── Message handler ───────────────────────────────────────────────────────
  function handleMessage(data) {
    switch (data.type) {

      case 'welcome':
        myBidderName = data.bidder || myBidderName;
        if (myIdentityBadge) {
          myIdentityBadge.textContent = myBidderName;
          myIdentityBadge.style.display = 'inline-block';
        }
        artifactDesc.textContent = data.description || '';
        if (data.walletBalance !== undefined) updateWallet(data.walletBalance);
        if (data.currentHighest > 0) {
          updateBidDisplay(data.currentHighest, data.currentLeader);
        }
        addFeedItem('🎙️', `<span class="system">${data.message}</span>`);
        if (data.rules) {
          data.rules.forEach(r => addFeedItem('📋', `<span class="system">${r}</span>`));
        }

        if (data.isEarly) {
          startLockTimer();
        } else {
          hideLockTimer();
          placeBidBtn.disabled = false;
          bidInput.disabled = false;
          transferBtn.disabled = false;
        }
        break;

      case 'state':
        updateBidDisplay(data.currentHighest, data.currentLeader);
        addFeedItem('📊', `Current bid: <span class="amount">${data.formatted}</span> by <span class="bidder">${data.currentLeader}</span>`);
        break;

      case 'bid':
        updateBidDisplay(data.amount, data.leader);
        const isMe = data.bidder === myBidderName;
        const icon = data.bidder === 'NebulaBidBot' ? '🤖' : (isMe ? '✅' : '👤');
        addFeedItem(icon, `<span class="bidder">${data.bidder}</span> bid <span class="amount">${data.formatted}</span>`);
        break;

      case 'system':
        addFeedItem('📢', `<span class="system">${data.message}</span>`);
        break;

      case 'error':
        addFeedItem('❌', `<span style="color:var(--danger)">${data.message}</span>`);
        break;

      case 'flag':
        auctionEnded = true;
        addFeedItem('🏆', `<span class="system">${data.message}</span>`);
        addFeedItem('🚩', `<span class="flag-text">${data.flag}</span>`);

        // Show flag reveal panel
        flagDisplay.textContent = data.flag;
        flagReveal.classList.add('visible');

        // Show sold banner
        soldBanner.style.display = 'flex';

        // Disable inputs
        placeBidBtn.disabled = true;
        bidInput.disabled = true;
        transferBtn.disabled = true;
        transferAmount.disabled = true;
        transferTarget.disabled = true;
        bidHint.textContent = '🔨 Auction closed. You won!';
        break;

      case 'balance':
        updateWallet(data.walletBalance);
        break;

      case 'pong':
        // ignore
        break;

      default:
        console.warn('[WS] Unknown message type:', data.type, data);
    }
  }

  // ── Connection ────────────────────────────────────────────────────────────
  function connect() {
    if (ws) return;


    // Generate time token and set it as a cookie
    const tokenPayload = JSON.stringify({ clientTime: Date.now() });
    const token = btoa(tokenPayload);
    document.cookie = "timeToken=" + encodeURIComponent(token) + "; path=/";

    const wsUrl = `ws://${window.location.host}/auction?room=${encodeURIComponent(roomId)}`;

    setStatus('connecting', 'Connecting to auction room…');
    placeBidBtn.disabled = true;
    bidInput.disabled = true;
    transferBtn.disabled = true;

    ws = new WebSocket(wsUrl);
    window.ws = ws; // Expose to global scope for DevTools console (challenge mechanic)

    ws.addEventListener('open', () => {
      setStatus('connected', `Connected — Room: ${roomId}`);
      addFeedItem('🔗', '<span class="system">Connected to private auction room.</span>');
      if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    });

    ws.addEventListener('message', (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch (e) {
        console.error('[WS] Failed to parse message:', event.data);
        return;
      }
      handleMessage(data);
    });

    ws.addEventListener('close', (event) => {
      setStatus('error', `Disconnected (${event.code})`);
      placeBidBtn.disabled = true;
      bidInput.disabled = true;
      transferBtn.disabled = true;
      addFeedItem('🔌', `<span class="system">Connection closed. ${event.reason || ''}</span>`);

      if (!auctionEnded && event.code !== 4001) {
        // Reconnect after 3s (unless access denied)
        reconnectTimer = setTimeout(connect, 3000);
      }
    });

    ws.addEventListener('error', () => {
      setStatus('error', 'Connection error');
    });
  }

  connect();

  // ── Bid submission ────────────────────────────────────────────────────────
  bidForm.addEventListener('submit', (e) => {
    e.preventDefault();

    if (!ws || ws.readyState !== WebSocket.OPEN) {
      addFeedItem('⚠️', '<span style="color:var(--warning)">Not connected. Please wait…</span>');
      return;
    }

    const amount = parseInt(bidInput.value, 10);
    if (!amount || amount <= 0) {
      addFeedItem('⚠️', '<span style="color:var(--warning)">Please enter a valid bid amount.</span>');
      return;
    }

    // Send bid message to server
    ws.send(JSON.stringify({ type: 'bid', amount }));
    bidInput.value = '';
  });

  // ── Transfer submission ───────────────────────────────────────────────────
  transferForm.addEventListener('submit', (e) => {
    e.preventDefault();

    if (!ws || ws.readyState !== WebSocket.OPEN) {
      addFeedItem('⚠️', '<span style="color:var(--warning)">Not connected. Please wait…</span>');
      return;
    }

    const amount = parseInt(transferAmount.value, 10);
    const target = transferTarget.value.trim();

    if (!amount || amount <= 0) {
      addFeedItem('⚠️', '<span style="color:var(--warning)">Please enter a valid transfer amount.</span>');
      return;
    }
    if (!target) return;

    // Send transfer message to server
    ws.send(JSON.stringify({ type: 'transfer', target, amount }));
    transferAmount.value = '';
    transferTarget.value = '';
  });

  // ── Keep-alive ping ───────────────────────────────────────────────────────
  setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
    }
  }, 25000);

})();
