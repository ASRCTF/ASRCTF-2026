

document.addEventListener("DOMContentLoaded", async () => {
  console.log("Hyperion V Core Telemetry Systems Online.");
  

  const state = {
    currentTab: "feed",
    archiveSearch: "",
    activeGitTab: "code",
    currentJwt: "",
    jwtStatus: "invalid", 
  };


  const _s = [61,40,63,63,52,56,59,52,49].map(b => String.fromCharCode(b ^ 0x5A)).join("");


  function base64urlEncode(str) {
    const bytes = new TextEncoder().encode(str);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
  }


  function base64urlDecode(base64url) {
    let base64 = base64url.replace(/-/g, "+").replace(/_/g, "/");
    while (base64.length % 4) {
      base64 += "=";
    }
    try {
      const binary = atob(base64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }
      return new TextDecoder().decode(bytes);
    } catch (e) {
      return "Invalid Base64Url encoding";
    }
  }

 
  function arrayBufferToBase64Url(buffer) {
    let binary = "";
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
  }


  async function signHmacSha256(message, secret) {
    const enc = new TextEncoder();
    const keyData = enc.encode(secret);
    const msgData = enc.encode(message);
    
 
    const key = await crypto.subtle.importKey(
      "raw",
      keyData,
      { name: "HMAC", hash: { name: "SHA-256" } },
      false,
      ["sign"]
    );
    
    const signature = await crypto.subtle.sign("HMAC", key, msgData);
    return arrayBufferToBase64Url(signature);
  }


  async function generateDefaultJwt() {
    const header = { alg: "HS256", typ: "JWT" };
    const payload = { username: "cadet_12", role: "cadet" };
    
    const encodedHeader = base64urlEncode(JSON.stringify(header));
    const encodedPayload = base64urlEncode(JSON.stringify(payload));
    const message = `${encodedHeader}.${encodedPayload}`;
    

    const signature = await signHmacSha256(message, _s);
    return `${message}.${signature}`;
  }


  async function verifyAndParseJwt(jwtString) {
    const parts = jwtString.split(".");
    if (parts.length !== 3) {
      return { valid: false, role: "none", username: "none", header: null, payload: null };
    }
    
    const [headerB64, payloadB64, signature] = parts;
    const message = `${headerB64}.${payloadB64}`;
    

    let header, payload;
    try {
      header = JSON.parse(base64urlDecode(headerB64));
      payload = JSON.parse(base64urlDecode(payloadB64));
    } catch (e) {
      return { valid: false, role: "none", username: "none", header: null, payload: null };
    }
    

    const expectedSignature = await signHmacSha256(message, _s);
    
    if (signature === expectedSignature) {
      return {
        valid: true,
        role: payload.role || "none",
        username: payload.username || "none",
        header,
        payload
      };
    } else {
      return {
        valid: false,
        role: payload.role || "none",
        username: payload.username || "none",
        header,
        payload
      };
    }
  }

  const navLinks = document.querySelectorAll(".nav-link");
  const sections = document.querySelectorAll(".content-section");
  
  navLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetSection = link.getAttribute("data-section");
      
 
      document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
      link.parentElement.classList.add("active");
      

      sections.forEach(sec => sec.classList.remove("active"));
      document.getElementById(targetSection).classList.add("active");
      
      state.currentTab = targetSection;
    });
  });


  let storedSession = localStorage.getItem("astro_session");
  if (!storedSession) {
    try {
      const resp = await fetch("/api/session");
      const data = await resp.json();
      storedSession = data.token;
      localStorage.setItem("astro_session", storedSession);
    } catch (e) {
      storedSession = await generateDefaultJwt();
      localStorage.setItem("astro_session", storedSession);
    }
  }
  state.currentJwt = storedSession;

  const jwtTextarea = document.getElementById("jwt-input");
  if (jwtTextarea) {
    jwtTextarea.value = state.currentJwt;
  }


  const archiveInput = document.getElementById("archive-input");
  const archiveBtn = document.getElementById("archive-btn");
  const archiveFrame = document.getElementById("archive-frame");
  
  async function handleArchiveSearch() {
    const query = archiveInput.value.trim();
    if (!query) return;

    let result;
    try {
      const resp = await fetch("/api/archive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      result = await resp.json();
    } catch {
      archiveFrame.innerHTML = `<div class="browser-placeholder"><p>Server unreachable.</p></div>`;
      return;
    }

    if (result.found) {
      archiveFrame.innerHTML = `
        <div class="geocities-blog">
          <div class="retro-header">
            <h1 class="retro-title">★★★ LEOS SPACE CORNER ★★★</h1>
            <p class="retro-tagline">Welcome to my personal archive page! Built with Notepad. Optimized for Netscape 4.0!</p>
          </div>
          
          <div class="retro-marquee">
            📢 BREAKING NEWS: APPOINTED LEAD TELEMETRY ENGINEER FOR HYPERION V MISSION! TO THE STARS AND BEYOND! 🚀
          </div>
          
          <div class="retro-post">
            <h2 class="retro-post-title">MEET COMET! 🐶</h2>
            <div class="retro-post-date">POSTED: AUGUST 18, 2012 | 11:24 PM UTC</div>
            <p class="retro-post-content">
              Just brought home my new Golden Retriever puppy, <b>Comet</b>! He is absolutely tiny, extremely energetic, and loves to chew on literally everything in sight—especially my space mission schematics! I have a feeling he is going to grow up to be an excellent orbital calculations assistant.
            </p>
            <div class="retro-gif-container">
              <span class="retro-badge">Animated Pet GIF Here</span>
              <span class="retro-badge">Under Construction</span>
            </div>
          </div>
          
          <div class="retro-post">
            <h2 class="retro-post-title">DOCUMENT ACCESS & ARCHIVES</h2>
            <div class="retro-post-date">POSTED: JUNE 04, 2012 | 02:15 AM UTC</div>
            <p class="retro-post-content">
              Backing up my notes for the upcoming spacecraft telemetry modules. I've archived the primary reference handbook here for standard flight sequences.
            </p>
            <div class="retro-download-box">
              📂 <a class="retro-download-link" href="assets/handbook.pdf" download="hyperion_handbook.pdf">
                DOWNLOAD: hyperion_handbook.pdf (Classified Reference Handbook)
              </a>
            </div>
          </div>
          
          <div class="retro-visitor-counter">
            YOU ARE VISITOR NUMBER: <span class="counter-digits">004219</span>
          </div>
        </div>
      `;
    } else {
      // 404
      archiveFrame.innerHTML = `
        <div class="browser-placeholder">
          <div class="placeholder-icon">⚠️</div>
          <h3>404 ARCHIVE NOT FOUND</h3>
          <p style="margin-top: 8px;">The requested URL could not be retrieved from the historical index.</p>
          <p style="margin-top: 4px; font-size: 0.8rem; font-family: var(--font-mono); color: var(--text-dim);">Historical snapshots are indexed by their exact intranet server host names (e.g., check Git commit history configurations).</p>
        </div>
      `;
    }
  }

  if (archiveBtn) archiveBtn.addEventListener("click", handleArchiveSearch);
  if (archiveInput) {
    archiveInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") handleArchiveSearch();
    });
  }


  const gitTabs = document.querySelectorAll(".git-tab");
  const gitPanels = document.querySelectorAll(".git-panel");
  
  gitTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetPanel = tab.getAttribute("data-tab");
      
      gitTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      
      gitPanels.forEach(p => p.classList.remove("active"));
      document.getElementById("git-" + targetPanel).classList.add("active");
    });
  });

  const commitItems = document.querySelectorAll(".commit-item");
  const diffViewer = document.getElementById("diff-viewer");
  const diffClose = document.getElementById("diff-close");
  const diffCode = document.getElementById("diff-code");
  
  commitItems.forEach(item => {
    item.addEventListener("click", () => {
      const sha = item.getAttribute("data-sha");
      
      if (sha === "d3b10ea") {

        diffCode.innerHTML = `
<span class="diff-line context">commit d3b10eac9f82d1c045b79a2f7c00e12d1c9ef0d4</span>
<span class="diff-line context">Author: Commander Leo Sterling &lt;lsterling@nebula.net&gt;</span>
<span class="diff-line context">Date:   Wed May 13 14:02:18 2026 -0400</span>
<span class="diff-line context"></span>
<span class="diff-line context">    Remove test endpoint, staging keys, and old archive url</span>
<span class="diff-line context"></span>
<span class="diff-line context">diff --git a/config.py b/config.py</span>
<span class="diff-line context">index 4ea219e..cf6a289 100644</span>
<span class="diff-line context">--- a/config.py</span>
<span class="diff-line context">+++ b/config.py</span>
<span class="diff-line context">@@ -12,5 +12,5 @@</span>
<span class="diff-line deletion">-# TESTING METRICS - DO NOT USE IN PRODUCTION</span>
<span class="diff-line deletion">-ARCHIVE_SERVER = "http://archive.cosmoconnect.net/archive/leosterling.astro.old"</span>
<span class="diff-line deletion">-EXIF_DECRYPTION_KEY = "HYPERION_X"</span>
<span class="diff-line context">+# PRODUCTION TELEMETRY ENDPOINTS</span>
<span class="diff-line addition">+ARCHIVE_SERVER = "https://archive.org"</span>
<span class="diff-line addition">+EXIF_DECRYPTION_KEY = os.environ.get("EXIF_KEY")</span>
        `;
        diffViewer.style.display = "block";
        diffViewer.scrollIntoView({ behavior: "smooth" });
      } else {
        diffCode.innerHTML = `
<span class="diff-line context">commit ${sha}</span>
<span class="diff-line context">Author: Commander Leo Sterling &lt;lsterling@nebula.net&gt;</span>
<span class="diff-line context"></span>
<span class="diff-line context">    System updates. No critical files modified in this diff.</span>
        `;
        diffViewer.style.display = "block";
        diffViewer.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

  if (diffClose) {
    diffClose.addEventListener("click", () => {
      diffViewer.style.display = "none";
    });
  }


  const jwtVisualizer = document.getElementById("jwt-visualizer");
  
  async function updateJwtVisualizer() {
    const tokenVal = jwtTextarea.value.trim();
    if (!tokenVal) {
      jwtVisualizer.innerHTML = `<div style="color: var(--laser-red)">[NO TOKEN DETECTED]</div>`;
      updateJwtStatusIndicator("invalid", null);
      return;
    }
    
    const parsed = await verifyAndParseJwt(tokenVal);
    

    const parts = tokenVal.split(".");
    const headerB64 = parts[0] || "";
    const payloadB64 = parts[1] || "";
    const sigB64 = parts[2] || "";
    
    const formattedHeader = parsed.header ? JSON.stringify(parsed.header, null, 2) : "[Header parsing error]";
    const formattedPayload = parsed.payload ? JSON.stringify(parsed.payload, null, 2) : "[Payload parsing error]";
    
    let statusClass = "invalid";
    let statusText = "INVALID SIGNATURE / RE-SIGN REQUIRED";
    
    if (parsed.valid) {
      if (parsed.role === "commander") {
        statusClass = "valid-commander";
        statusText = "VALID SIGNATURE - ROLE: COMMANDER (ACCESS GRANTED)";
        state.jwtStatus = "commander";
      } else {
        statusClass = "valid-cadet";
        statusText = `VALID SIGNATURE - ROLE: ${parsed.role.toUpperCase()} (UNPRIVILEGED)`;
        state.jwtStatus = "cadet";
      }
    } else {
      state.jwtStatus = "invalid";
    }
    
    jwtVisualizer.innerHTML = `
      <div class="jwt-section-title">Token String Split</div>
      <div class="jwt-token-split">
        <span class="jwt-header-part">${headerB64}</span>.<span class="jwt-payload-part">${payloadB64}</span>.<span class="jwt-sig-part">${sigB64}</span>
      </div>
      
      <div class="jwt-section-title">Decoded Header</div>
      <pre class="jwt-block header">${formattedHeader}</pre>
      
      <div class="jwt-section-title">Decoded Payload</div>
      <pre class="jwt-block payload">${formattedPayload}</pre>
      
      <div class="jwt-status-bar">
        <div class="jwt-status-indicator ${statusClass}"></div>
        <span class="jwt-status-text" style="color: ${statusClass === 'valid-commander' ? 'var(--matrix-green)' : statusClass === 'valid-cadet' ? 'var(--cyber-gold)' : 'var(--laser-red)'}">${statusText}</span>
      </div>
    `;
  }

  function updateJwtStatusIndicator(status, parsed) {
    state.jwtStatus = status;
  }

  if (jwtTextarea) {
    jwtTextarea.addEventListener("input", updateJwtVisualizer);
    // Initial run
    updateJwtVisualizer();
  }


  const consolePanel    = document.getElementById("console-card-panel");
  const unveiledContainer = document.getElementById("unveiled-container");

  function setFeedback(n, msg, type) {
    const el = document.getElementById(`feedback-${n}`);
    if (!el) return;
    el.textContent = msg;
    el.className = `stage-feedback ${type}`;
  }

  function markSolved(n) {
    const block   = document.getElementById(`stage-${n}`);
    const pip     = document.getElementById(`pip-${n}`);
    const verBtn  = document.getElementById(`verify-${n}`);
    const input   = n === 4
      ? document.getElementById("jwt-input")
      : document.getElementById(`key${n}`);

    if (block)  { block.classList.remove("stage-locked"); block.classList.add("stage-solved"); }
    if (pip)    { pip.classList.remove("active"); pip.classList.add("solved"); pip.innerHTML = "✓"; }
    if (verBtn) { verBtn.classList.add("solved"); verBtn.innerHTML = '<i class="fa-solid fa-check"></i> Verified'; verBtn.disabled = true; }
    if (input)  { input.disabled = true; }

    const lines = document.querySelectorAll(".stage-pip-line");
    if (lines[n - 1]) lines[n - 1].classList.add("lit");
  }

  function unlockStage(n, hint) {
    const block   = document.getElementById(`stage-${n}`);
    const pip     = document.getElementById(`pip-${n}`);
    const hintBox = document.getElementById(`hint-${n}`);
    const lockIcon = block ? block.querySelector(".stage-lock-icon") : null;
    const verBtn  = document.getElementById(`verify-${n}`);
    const input   = n === 4
      ? document.getElementById("jwt-input")
      : document.getElementById(`key${n}`);
    const submitBtn = document.getElementById("submit-console");

    if (block)    { block.classList.remove("stage-locked"); }
    if (pip)      { pip.classList.add("active"); }
    if (lockIcon) { lockIcon.style.display = "none"; }

    if (hintBox && hint) {
      hintBox.textContent = hint;
      hintBox.style.display = "block";
      hintBox.classList.add("hint-unlocked");
    }

    if (input)    { input.disabled = false; input.focus(); }
    if (verBtn)   { verBtn.disabled = false; }
    if (n === 4 && submitBtn) { submitBtn.disabled = false; }
  }

  [1, 2, 3].forEach(step => {
    const btn   = document.getElementById(`verify-${step}`);
    const input = document.getElementById(`key${step}`);
    if (!btn || !input) return;

    async function attemptVerify() {
      const value = input.value.trim();
      if (!value) { setFeedback(step, "⚠ Input required.", "error"); return; }

      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
      setFeedback(step, "", "");

      let result;
      try {
        const resp = await fetch("/api/check-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ step, value }),
        });
        result = await resp.json();
      } catch {
        setFeedback(step, "⚠ Server unreachable. Is server.py running?", "error");
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-key"></i> Verify';
        return;
      }

      if (result.correct) {
        setFeedback(step, "✓ Key accepted.", "success");
        markSolved(step);
        // Small delay before sliding in the next stage
        setTimeout(() => unlockStage(step + 1, result.hint), 350);
        // Sync JWT visualizer when stage 4 unlocks
        if (step === 3) {
          setTimeout(() => {
            const jtEl = document.getElementById("jwt-input");
            if (jtEl && jwtTextarea && jtEl !== jwtTextarea) {
            }
            updateJwtVisualizer();
          }, 400);
        }
      } else {
        setFeedback(step, "✗ Incorrect. Try again.", "error");
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-key"></i> Verify';
      }
    }

    btn.addEventListener("click", (e) => { e.preventDefault(); attemptVerify(); });
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); attemptVerify(); } });
  });

  const submitBtn = document.getElementById("submit-console");
  if (submitBtn) {
    submitBtn.addEventListener("click", async (e) => {
      e.preventDefault();

      const key1     = (document.getElementById("key1")     || {}).value || "";
      const key2     = (document.getElementById("key2")     || {}).value || "";
      const key3     = (document.getElementById("key3")     || {}).value || "";
      const tokenVal = (document.getElementById("jwt-input") || {}).value || "";

      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verifying...';
      setFeedback(4, "", "");

      let result;
      try {
        const resp = await fetch("/api/validate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ key1, key2, key3, jwt: tokenVal }),
        });
        result = await resp.json();
      } catch {
        setFeedback(4, "⚠ Server unreachable. Is server.py running?", "error");
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-shield-halved"></i> DECRYPT TELEMETRY & EXECUTE OVERRIDE';
        return;
      }

      if (result.success) {
        const flagEl = document.getElementById("flag-text");
        if (flagEl) flagEl.textContent = result.flag;

        markSolved(4);
        setTimeout(() => {
          consolePanel.style.display = "none";
          unveiledContainer.style.display = "block";
          unveiledContainer.scrollIntoView({ behavior: "smooth" });
        }, 300);

        try {
          const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
          const playNote = (freq, dur, t) => {
            const osc = audioCtx.createOscillator();
            const g   = audioCtx.createGain();
            osc.connect(g); g.connect(audioCtx.destination);
            osc.frequency.value = freq;
            g.gain.setValueAtTime(0.15, t);
            g.gain.exponentialRampToValueAtTime(0.01, t + dur);
            osc.start(t); osc.stop(t + dur);
          };
          const now = audioCtx.currentTime;
          playNote(523.25, 0.15, now);
          playNote(659.25, 0.15, now + 0.12);
          playNote(783.99, 0.15, now + 0.24);
          playNote(1046.50, 0.4, now + 0.36);
        } catch { /* silent */ }

      } else {
        setFeedback(4, result.errors.join(" | ") + (result.hint ? " — " + result.hint : ""), "error");
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-shield-halved"></i> DECRYPT TELEMETRY & EXECUTE OVERRIDE';
      }
    });
  }



  const spectrogramCanvas = document.getElementById("spectrogram-canvas");
  const playAudioBtn = document.getElementById("play-audio-btn");
  const stopAudioBtn = document.getElementById("stop-audio-btn");
  const specStatus = document.getElementById("spectrogram-status");

  if (spectrogramCanvas && playAudioBtn && stopAudioBtn) {
    const specCtx = spectrogramCanvas.getContext("2d");
    

    specCtx.fillStyle = "#07080b";
    specCtx.fillRect(0, 0, spectrogramCanvas.width, spectrogramCanvas.height);
    
    specCtx.strokeStyle = "rgba(6, 182, 212, 0.05)";
    specCtx.lineWidth = 1;
    for (let i = 40; i < spectrogramCanvas.width; i += 40) {
      specCtx.beginPath();
      specCtx.moveTo(i, 0);
      specCtx.lineTo(i, spectrogramCanvas.height);
      specCtx.stroke();
    }
    for (let i = 20; i < spectrogramCanvas.height; i += 20) {
      specCtx.beginPath();
      specCtx.moveTo(0, i);
      specCtx.lineTo(spectrogramCanvas.width, i);
      specCtx.stroke();
    }

    let audioContext = null;
    let audioSource = null;
    let analyserNode = null;
    let audioObj = null;
    let specAnimId = null;

    async function startSpectrogram() {
      try {
        if (!audioContext) {
          audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }


        if (audioContext.state === "suspended") {
          await audioContext.resume();
        }

        audioObj = new Audio("assets/telemetry_signal.wav");
        audioObj.crossOrigin = "anonymous";


        analyserNode = audioContext.createAnalyser();
        analyserNode.fftSize = 2048; // Large FFT size for sharp text definition

        audioSource = audioContext.createMediaElementSource(audioObj);
        audioSource.connect(analyserNode);
        analyserNode.connect(audioContext.destination);


        playAudioBtn.disabled = true;
        playAudioBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Scanning...`;
        stopAudioBtn.disabled = false;
        specStatus.textContent = "STATUS: ACTIVE DECRYPTION";
        specStatus.style.color = "var(--matrix-green)";


        audioObj.play();


        audioObj.onended = () => {
          stopSpectrogram();
        };


        const bufferLength = analyserNode.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        function drawFrame() {
          if (!audioObj || audioObj.paused) return;
          
          specAnimId = requestAnimationFrame(drawFrame);
          analyserNode.getByteFrequencyData(dataArray);


          const tempCanvas = document.createElement("canvas");
          tempCanvas.width = spectrogramCanvas.width;
          tempCanvas.height = spectrogramCanvas.height;
          const tempCtx = tempCanvas.getContext("2d");
          tempCtx.drawImage(spectrogramCanvas, 0, 0);

          specCtx.clearRect(0, 0, spectrogramCanvas.width, spectrogramCanvas.height);
          specCtx.drawImage(tempCanvas, -2, 0);

 
          const minBin = 20;
          const maxBin = 200;
          const binRange = maxBin - minBin;

          for (let y = 0; y < spectrogramCanvas.height; y++) {

            const percent = 1 - (y / spectrogramCanvas.height);
            const binIndex = Math.floor(minBin + (percent * binRange));
            const value = dataArray[binIndex] || 0;


            let color = "#07080b";
            
            if (value > 25) {
              const intensity = value / 255;
              
    
              let r = 0, g = 0, b = 0;
              if (intensity < 0.3) {
                r = Math.floor(100 * intensity);
                g = Math.floor(50 * intensity);
                b = Math.floor(150 + 105 * (intensity / 0.3));
              } else if (intensity < 0.7) {

                const localIntensity = (intensity - 0.3) / 0.4;
                r = Math.floor(6 * (1 - localIntensity) + 16 * localIntensity);
                g = Math.floor(182 * (1 - localIntensity) + 215 * localIntensity);
                b = Math.floor(212 * (1 - localIntensity) + 129 * localIntensity);
              } else {

                const localIntensity = (intensity - 0.7) / 0.3;
                r = Math.floor(16 + 239 * localIntensity);
                g = Math.floor(215 + 40 * localIntensity);
                b = Math.floor(129 + 126 * localIntensity);
              }
              color = `rgba(${r}, ${g}, ${b}, ${0.3 + intensity * 0.7})`;
            }

            specCtx.fillStyle = color;
            specCtx.fillRect(spectrogramCanvas.width - 2, y, 2, 1);
          }
        }
        
        drawFrame();

      } catch (err) {
        console.error("Spectrogram Init Error:", err);
        specStatus.textContent = "STATUS: ERROR";
        specStatus.style.color = "var(--laser-red)";
        alert("Web Audio API blocked or unsupported. Use 'Open Tab' or direct download to analyze manually.");
        stopSpectrogram();
      }
    }

    function stopSpectrogram() {

      if (specAnimId) {
        cancelAnimationFrame(specAnimId);
        specAnimId = null;
      }

  
      if (audioObj) {
        audioObj.pause();
        audioObj.src = "";
        audioObj = null;
      }


      playAudioBtn.disabled = false;
      playAudioBtn.innerHTML = `<i class="fa-solid fa-play"></i> Play & Scan Signal`;
      stopAudioBtn.disabled = true;
      specStatus.textContent = "STATUS: READY";
      specStatus.style.color = "var(--text-dim)";
    }

    playAudioBtn.addEventListener("click", startSpectrogram);
    stopAudioBtn.addEventListener("click", stopSpectrogram);
  }
});
