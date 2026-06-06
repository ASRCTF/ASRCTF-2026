'use strict';

const express = require('express');
const http = require('http');
const { WebSocketServer, WebSocket } = require('ws');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const PORT = process.env.PORT || 3000;
const SECRET_ROOM_ID = process.env.PRIVATE_ROOM_ID || 'stardust-7sigma-9f3a';
const FLAG = process.env.FLAG || 'ASRCTF{w3bs0ck3t_sp4c3_h34st_succ3ssful}';

const BOT_NAME = 'NebulaBidBot';
const BOT_START_BID = 1000;
const BOT_INCREMENT = 500;
const BOT_CAP = 9_999_999;
const BOT_INTERVAL_MS = 3000;
const MAX_BID = 10_000_000;
const STARTING_BALANCE = 1000;
const AUCTION_START_TIME = 15778476000000000;

function createPlayerSession() {
  return {
    currentHighest: 0,
    currentLeader: null,
    clients: new Set(),
    botBid: BOT_START_BID,
    botTimer: null,
  };
}


const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));


app.use('/github', express.static(path.join(__dirname, 'fake-github')));


app.get('/vip', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'vip.html'));
});

// Health check
app.get('/health', (_req, res) => res.json({ status: 'ok' }));

// ─── HTTP → WS Server ─────────────────────────────────────────────────────────
const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/auction' });

// ─── Helpers ─────────────────────────────────────────────────────────────────
function broadcast(room, payload) {
  const msg = JSON.stringify(payload);
  for (const client of room.clients) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(msg);
    }
  }
}

function send(ws, payload) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(payload));
  }
}

function formatCredits(n) {
  return n.toLocaleString('en-US') + ' ₢';
}

// ─── Bot Logic ────────────────────────────────────────────────────────────────
function startBot(session) {
  if (!session || session.botTimer) return;

  session.botTimer = setInterval(() => {
    // Bot only bids if it is not the current leader and its next bid is within cap
    const nextBid = Math.max(session.currentHighest + BOT_INCREMENT, session.botBid);
    if (nextBid > BOT_CAP) {
      // Bot has reached its cap — it gives up
      broadcast(session, {
        type: 'system',
        message: `${BOT_NAME} has reached its maximum budget. The floor is open!`,
      });
      clearInterval(session.botTimer);
      session.botTimer = null;
      return;
    }

    if (session.currentLeader !== BOT_NAME) {
      session.currentHighest = nextBid;
      session.currentLeader = BOT_NAME;
      session.botBid = nextBid + BOT_INCREMENT;

      broadcast(session, {
        type: 'bid',
        bidder: BOT_NAME,
        amount: nextBid,
        formatted: formatCredits(nextBid),
        leader: BOT_NAME,
      });
    }
  }, BOT_INTERVAL_MS);
}

// ─── WebSocket Connection Handler ─────────────────────────────────────────────
wss.on('connection', (ws, req) => {
  const params = new URL(req.url, `http://localhost`).searchParams;
  const roomId = params.get('room');

  // Guard: reject wrong / missing room ID
  if (roomId !== SECRET_ROOM_ID) {
    send(ws, {
      type: 'error',
      message: 'Access denied. This auction room does not exist or you are not invited.',
    });
    ws.close(4001, 'Forbidden');
    return;
  }

  // Parse cookies
  const cookieHeader = req.headers.cookie || '';
  const cookies = Object.fromEntries(cookieHeader.split(';').map(c => c.trim().split('=')));

  // Each connection gets its own isolated game session
  const session = createPlayerSession();
  const clientId = uuidv4().slice(0, 8);
  ws.clientId = clientId;
  ws.bidderName = 'Bidder#' + clientId;
  ws.walletBalance = STARTING_BALANCE;
  ws.isEarly = false;

  // Verify the Base64 time token from cookies
  const tokenB64 = cookies.timeToken;
  if (tokenB64) {
    try {
      const tokenJson = Buffer.from(decodeURIComponent(tokenB64), 'base64').toString('utf-8');
      const token = JSON.parse(tokenJson);
      if (token.clientTime && token.clientTime < AUCTION_START_TIME) {
        ws.isEarly = true;
      }
    } catch (e) {
      ws.isEarly = true; // invalid token means too early
    }
  } else {
    ws.isEarly = true;
  }

  session.clients.add(ws);


  send(ws, {
    type: 'welcome',
    bidder: ws.bidderName,
    message: `Welcome to the private auction for ⭐ Artifact 7-Sigma ⭐ (Lot #7Σ). You are registered as ${ws.bidderName}.`,
    artifact: 'Artifact 7-Sigma — The Stardust Shard',
    description: 'A fragment of the legendary Kepler-442 meteorite. Estimated age: 4.6 billion years. One of only three specimens in existence.',
    currentHighest: session.currentHighest,
    currentLeader: session.currentLeader || 'No bids yet',
    walletBalance: ws.walletBalance,
    maxBid: MAX_BID,
    isEarly: ws.isEarly,
    rules: [
      'Place bids using: { "type": "bid", "amount": <integer> }',
      `Maximum allowed bid: ${formatCredits(MAX_BID)}`,
      'Highest bid when the bot concedes wins the artifact.',
      'Good luck, space cowboy.',
    ],
  });

  if (!ws.isEarly) {
    startBot(session);
  } else {
    send(ws, {
      type: 'system',
      message: '⚠️ AUCTION PENDING. The auction is scheduled to begin in approximately 500,000 years. You are in spectator mode.',
    });
  }
  ws.on('message', (raw) => {
    let data;
    try {
      data = JSON.parse(raw.toString());
    } catch {
      send(ws, { type: 'error', message: 'Invalid JSON payload.' });
      return;
    }

    if (data.type === 'bid') {
      if (ws.isEarly) {
        send(ws, { type: 'error', message: 'The auction has not started yet.' });
        return;
      }

      const amount = parseInt(data.amount, 10);

      if (!Number.isInteger(amount) || amount <= 0) {
        send(ws, { type: 'error', message: 'Bid amount must be a positive integer.' });
        return;
      }

      if (amount > MAX_BID) {
        send(ws, {
          type: 'error',
          message: `Bid exceeds the maximum allowed amount of ${formatCredits(MAX_BID)}.`,
        });
        return;
      }

      if (amount <= session.currentHighest) {
        send(ws, {
          type: 'error',
          message: `Your bid of ${formatCredits(amount)} is too low. Current highest is ${formatCredits(session.currentHighest)}.`,
        });
        return;
      }

      if (amount > ws.walletBalance) {
        send(ws, {
          type: 'error',
          message: `Insufficient funds. Your balance is ${formatCredits(ws.walletBalance)} but you tried to bid ${formatCredits(amount)}.`,
        });
        return;
      }

      // Valid bid
      session.currentHighest = amount;
      session.currentLeader = ws.bidderName;

      broadcast(session, {
        type: 'bid',
        bidder: ws.bidderName,
        amount,
        formatted: formatCredits(amount),
        leader: ws.bidderName,
      });

      // Check for winning bid (exactly MAX_BID)
      if (amount === MAX_BID) {
        // Stop the bot
        if (session.botTimer) {
          clearInterval(session.botTimer);
          session.botTimer = null;
        }

        broadcast(session, {
          type: 'system',
          message: `🔨 SOLD! ${ws.bidderName} wins Artifact 7-Sigma with a maximum bid of ${formatCredits(MAX_BID)}!`,
        });

        // Send flag only to the winner
        send(ws, {
          type: 'flag',
          message: '🚀 Congratulations! You have acquired the legendary Stardust Shard.',
          flag: FLAG,
        });
      }

    } else if (data.type === 'transfer') {
      if (ws.isEarly) {
        send(ws, { type: 'error', message: 'The auction has not started yet.' });
        return;
      }

      const amount = parseInt(data.amount, 10);
      const targetName = data.target;

      if (!Number.isInteger(amount)) {
        send(ws, { type: 'error', message: 'Transfer amount must be an integer.' });
        return;
      }

      if (!targetName || targetName.trim() === '') {
        send(ws, { type: 'error', message: 'Target name is required.' });
        return;
      }

      // VULNERABILITY: Missing check for negative numbers!
      // A negative amount bypasses this check if -amount <= walletBalance.
      // E.g., if balance is 1000 and amount is -10000000, -10000000 > 1000 is FALSE.
      if (amount > ws.walletBalance) {
        send(ws, { type: 'error', message: `Insufficient funds for transfer. Your balance is ${formatCredits(ws.walletBalance)}.` });
        return;
      }

      // VULNERABILITY EXPLOITED: Subtracting a negative number ADDS to the balance!
      ws.walletBalance -= amount;

      send(ws, {
        type: 'system',
        message: `Successfully transferred ${formatCredits(amount)} to ${targetName}.`,
      });
      send(ws, {
        type: 'balance',
        walletBalance: ws.walletBalance,
      });

    } else if (data.type === 'ping') {
      send(ws, { type: 'pong' });
    } else {
      send(ws, { type: 'error', message: `Unknown message type: ${data.type}` });
    }
  });

  ws.on('close', () => {
    session.clients.delete(ws);
    if (session.botTimer) {
      clearInterval(session.botTimer);
      session.botTimer = null;
    }
  });

  ws.on('error', (err) => {
    console.error(`[WS] Client ${ws.bidderName} error:`, err.message);
    session.clients.delete(ws);
  });
});
server.listen(PORT, () => {
  console.log(`[NebulaMart] Server running on http://0.0.0.0:${PORT}`);
  console.log(`[NebulaMart] WebSocket endpoint: ws://0.0.0.0:${PORT}/auction`);
  console.log(`[NebulaMart] Secret room ID: ${SECRET_ROOM_ID}`);
  console.log(`[NebulaMart] Flag: ${FLAG}`);
});
