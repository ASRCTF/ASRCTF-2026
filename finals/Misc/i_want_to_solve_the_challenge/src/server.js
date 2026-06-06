const express = require("express");
const crypto = require("crypto");
const app = express();
app.use(express.json());

const FLAG = "ASRCTF{th3_ch4ll3ng3_w3r3_th3_fr13nd5_w3_m4d3_4l0ng_th3_w4y}";
const KNOCK_SEQUENCE = [4, 8, 15, 16, 23, 42];
const unlockedIPs = new Set();

function xorBuffer(data, key) {
  const keyBuf = Buffer.from(key, "hex");
  return Buffer.from(data).map((b, i) => b ^ keyBuf[i % keyBuf.length]);
}

app.get("/", (req, res) => {
  res.set("X-Hint", "There is more here than meets the eye. Crawlers know where to start.");
  res.set("X-Version", "i-want-to-solve-the-challenge/1.0");
  res.status(200).send("");
});

app.get("/robots.txt", (req, res) => {
  res.type("text/plain").send(
    "User-agent: *\n" +
    "Disallow: /the-map-was-here-all-along\n"
  );
});

app.get("/the-map-was-here-all-along", (req, res) => {
  const hint = Buffer.from("knock: 4,8,15,16,23,42").toString("base64");
  res.set("Content-Type", "text/plain");
  res.set("X-Encoding", "base64");
  res.send(hint);
});

app.post("/knock", (req, res) => {
  const { sequence } = req.body || {};
  const ip = req.ip;

  if (!Array.isArray(sequence)) {
    return res.status(400).json({ error: "Expected JSON body: { \"sequence\": [...] }" });
  }

  const correct =
    sequence.length === KNOCK_SEQUENCE.length &&
    sequence.every((v, i) => v === KNOCK_SEQUENCE[i]);

  if (!correct) {
    return res.status(403).json({ error: "Wrong sequence. Keep trying." });
  }

  unlockedIPs.add(ip);
  return res.status(200).json({
    message: "The door is open. But only briefly, and only for you.",
    next: "/finally",
  });
});

app.get("/finally", (req, res) => {
  const ip = req.ip;

  if (!unlockedIPs.has(ip)) {
    return res.status(403).json({ error: "You haven't knocked." });
  }

  unlockedIPs.delete(ip);

  const key = crypto.randomBytes(8).toString("hex");
  const encoded = xorBuffer(Buffer.from(FLAG, "utf8"), key);

  res.set("X-Key", key);
  res.set("X-Encoding", "xor: flag XOR key, result as hex");
  res.set("Content-Type", "text/plain");
  res.send(encoded.toString("hex"));
});

const PORT = process.env.PORT || <port>;
app.listen(PORT);
