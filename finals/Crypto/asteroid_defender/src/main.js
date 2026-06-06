(() => {
  
    const canvas          = document.getElementById('radar-canvas');
    const ctx             = canvas.getContext('2d');
    const trajectoryEl    = document.getElementById('trajectory-display');
    const sectorEl        = document.getElementById('sector-display');
    const streakCountEl   = document.getElementById('streak-count');
    const streakBarEl     = document.getElementById('streak-bar');
    const systemStatusEl  = document.getElementById('system-status');
    const terminalEl      = document.getElementById('terminal-logs');
    const btnObserve      = document.getElementById('btn-observe');
    const compassGrid     = document.getElementById('compass-grid');
    const sectorBtns      = document.querySelectorAll('.sector-btn');
    const defendResult    = document.getElementById('defend-result');
    const flagDisplay     = document.getElementById('flag-display');

    const CX = canvas.width  / 2;   // 150
    const CY = canvas.height / 2;   // 150
    const R  = canvas.width  / 2 - 3; // 147
    const SECTOR_NAMES = ['N','NE','E','SE','S','SW','W','NW'];

    const sectorAngle = (s) => (s * Math.PI / 4) - Math.PI / 2;


    let sweepAngle  = -Math.PI / 2;     // start at North
    const SWEEP_SPEED = (2 * Math.PI) / (4 * 60); // full rotation in 4s @60fps
    let blips = [];           // { x, y, t, color }
    let locked = false;       // prevent double-clicks mid-request
    let lastHitSector = null; // for canvas highlight


    function log(msg, type = '') {
        const el = document.createElement('div');
        el.className = `log-entry ${type}`;
        const ts = new Date().toISOString().split('T')[1].slice(0,12);
        el.textContent = `[${ts}] ${msg}`;
        terminalEl.appendChild(el);
        terminalEl.scrollTop = terminalEl.scrollHeight;
    }


    function setStreak(n) {
        streakCountEl.textContent = n;
        streakBarEl.style.width   = `${n}%`;
    }


    function flashBtn(sectorId, cls, durationMs = 900) {
        const btn = document.getElementById(`sector-${sectorId}`);
        if (!btn) return;
        btn.classList.add(cls);
        setTimeout(() => btn.classList.remove(cls), durationMs);
    }

    function resetBtnClasses() {
        sectorBtns.forEach(b => b.classList.remove('correct','wrong','actual'));
    }

    function addBlip(sectorIdx, r, g, b) {
        const angle  = sectorAngle(sectorIdx);
        const dist   = R * (0.45 + Math.random() * 0.35);
        blips.push({
            x: CX + Math.cos(angle) * dist,
            y: CY + Math.sin(angle) * dist,
            t: Date.now(),
            r, g, b
        });
        blips = blips.filter(b => Date.now() - b.t < 4000);
    }

    function drawRadar() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.save();
        ctx.beginPath();
        ctx.arc(CX, CY, R, 0, Math.PI * 2);
        ctx.clip();

        ctx.fillStyle = '#020e0b';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const bg = ctx.createRadialGradient(CX, CY, 0, CX, CY, R);
        bg.addColorStop(0,   'rgba(0,255,204,0.07)');
        bg.addColorStop(0.6, 'rgba(0,255,204,0.02)');
        bg.addColorStop(1,   'rgba(0,0,0,0)');
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < 8; i++) {
            const a = sectorAngle(i) + Math.PI / 8; // boundary between sectors
            ctx.beginPath();
            ctx.moveTo(CX, CY);
            ctx.lineTo(CX + Math.cos(a) * R, CY + Math.sin(a) * R);
            ctx.strokeStyle = 'rgba(0,255,204,0.12)';
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        [0.33, 0.66, 1.0].forEach(ratio => {
            ctx.beginPath();
            ctx.arc(CX, CY, R * ratio, 0, Math.PI * 2);
            ctx.strokeStyle = ratio === 1.0
                ? 'rgba(0,255,204,0.0)' // outer ring drawn after clip restore
                : 'rgba(0,255,204,0.18)';
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        const TRAIL   = Math.PI / 2.5; // ~72° trail
        const STEPS   = 40;
        for (let i = 0; i < STEPS; i++) {
            const t  = i / STEPS;
            const a0 = sweepAngle - TRAIL * (1 - t);
            const a1 = sweepAngle - TRAIL * (1 - (i + 1) / STEPS);
            ctx.beginPath();
            ctx.moveTo(CX, CY);
            ctx.arc(CX, CY, R - 1, a0, a1);
            ctx.closePath();
            ctx.fillStyle = `rgba(0,255,204,${t * 0.22})`;
            ctx.fill();
        }

        ctx.font = '11px "Share Tech Mono", monospace';
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        for (let i = 0; i < 8; i++) {
            const a = sectorAngle(i);
            const lx = CX + Math.cos(a) * R * 0.78;
            const ly = CY + Math.sin(a) * R * 0.78;

            const isHit = lastHitSector === i;
            ctx.fillStyle = isHit ? 'rgba(255,204,0,0.9)' : 'rgba(0,255,204,0.55)';
            if (isHit) {
                ctx.shadowColor = '#ffcc00';
                ctx.shadowBlur  = 8;
            }
            ctx.fillText(SECTOR_NAMES[i], lx, ly);
            ctx.shadowBlur = 0;
        }

        const now = Date.now();
        blips = blips.filter(b => now - b.t < 3500);
        blips.forEach(b => {
            const age   = now - b.t;
            const alpha = Math.max(0, 1 - age / 3500);
            const radius = 3 + (1 - alpha) * 5;
            ctx.beginPath();
            ctx.arc(b.x, b.y, radius, 0, Math.PI * 2);
            ctx.fillStyle    = `rgba(${b.r},${b.g},${b.b},${alpha.toFixed(2)})`;
            ctx.shadowColor  = `rgb(${b.r},${b.g},${b.b})`;
            ctx.shadowBlur   = 12 * alpha;
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        ctx.restore(); // end clip

        ctx.save();
        ctx.beginPath();
        ctx.arc(CX, CY, R, 0, Math.PI * 2);
        ctx.clip();
        ctx.beginPath();
        ctx.moveTo(CX, CY);
        ctx.lineTo(CX + Math.cos(sweepAngle) * R, CY + Math.sin(sweepAngle) * R);
        ctx.strokeStyle = 'rgba(0,255,204,0.95)';
        ctx.lineWidth   = 2;
        ctx.shadowColor = '#00ffcc';
        ctx.shadowBlur  = 10;
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.restore();

        ctx.beginPath();
        ctx.arc(CX, CY, 4, 0, Math.PI * 2);
        ctx.fillStyle   = '#00ffcc';
        ctx.shadowColor = '#00ffcc';
        ctx.shadowBlur  = 12;
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.beginPath();
        ctx.arc(CX, CY, R, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,255,204,0.85)';
        ctx.lineWidth   = 2;
        ctx.shadowColor = '#00ffcc';
        ctx.shadowBlur  = 18;
        ctx.stroke();
        ctx.shadowBlur = 0;

        sweepAngle = (sweepAngle + SWEEP_SPEED) % (Math.PI * 2);
        if (sweepAngle > Math.PI) sweepAngle -= Math.PI * 2; // keep in [-π, π]

        requestAnimationFrame(drawRadar);
    }

    async function initSession() {
        try {
            const res  = await fetch('/api/session');
            const data = await res.json();
            if (data.status === 'success') {
                systemStatusEl.textContent = 'SYSTEM ONLINE';
                log('Session initialized. Radar online.', 'sys');
            }
            // Restore streak
            const sr = await fetch('/api/status');
            const sd = await sr.json();
            setStreak(sd.streak || 0);
        } catch {
            systemStatusEl.textContent = 'OFFLINE';
            log('Session init failed.', 'err');
        }
    }

    btnObserve.addEventListener('click', async () => {
        if (locked) return;
        locked = true;
        btnObserve.disabled = true;
        btnObserve.querySelector('.btn-text').textContent = '[ SCANNING... ]';

        try {
            const res  = await fetch('/api/observe');
            if (!res.ok) throw new Error(res.status);
            const data = await res.json();

            trajectoryEl.textContent = data.raw;
            sectorEl.textContent     = data.sector_name;
            lastHitSector            = data.sector;

            addBlip(data.sector, 255, 204, 0);
            log(`Impact detected — Signature: ${data.raw}  →  Sector: ${data.sector_name}`, 'warn');

            // Clear hit highlight after 2s
            setTimeout(() => { lastHitSector = null; }, 2000);

        } catch (e) {
            log(`Scan error: ${e.message}`, 'err');
        } finally {
            locked = false;
            btnObserve.disabled = false;
            btnObserve.querySelector('.btn-text').textContent = '[ OBSERVE IMPACT ]';
        }
    });

    sectorBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            if (locked) return;
            locked = true;
            setSectorBtnsDisabled(true);
            resetBtnClasses();
            defendResult.classList.add('hidden');

            const sector = parseInt(btn.dataset.sector, 10);
            let data = null;

            try {
                const res  = await fetch('/api/defend', {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify({ sector })
                });
                data = await res.json();

                setStreak(data.streak);

                if (data.correct) {
                    flashBtn(sector, 'correct');
                    addBlip(sector, 0, 255, 204);

                    defendResult.textContent  = `CORRECT — Sector ${SECTOR_NAMES[sector]} shielded! Streak: ${data.streak}/100`;
                    defendResult.className    = 'defend-result correct';
                    defendResult.classList.remove('hidden');

                    log(`SHIELD HIT  Sector ${SECTOR_NAMES[sector]}  |  Streak: ${data.streak}/100`, 'ok');

                    if (data.flag) {
                        flagDisplay.innerHTML = `FLAG: ${data.flag}`;
                        flagDisplay.classList.remove('hidden');
                        log(`FLAG CAPTURED: ${data.flag}`, 'ok');
                        setSectorBtnsDisabled(true);
                        btnObserve.disabled = true;
                        locked = true;
                        return;
                    }
                } else {
                    flashBtn(sector, 'wrong');
                    flashBtn(data.actual_sector, 'actual');
                    addBlip(data.actual_sector, 255, 0, 85);

                    defendResult.textContent  = `MISS — Asteroid struck ${data.actual_sector_name}. Streak reset.`;
                    defendResult.className    = 'defend-result wrong';
                    defendResult.classList.remove('hidden');

                    log(`SHIELD MISS  Predicted: ${SECTOR_NAMES[sector]}  |  Hit: ${data.actual_sector_name}  |  Streak reset`, 'err');
                }

            } catch (e) {
                log(`Defend error: ${e.message}`, 'err');
            } finally {
                locked = !!(data && data.flag);
                if (!locked) setSectorBtnsDisabled(false);
            }
        });
    });

    function setSectorBtnsDisabled(state) {
        sectorBtns.forEach(b => (b.disabled = state));
    }

    // ── Boot ──────────────────────────────────────────────────────────────────
    initSession();
    requestAnimationFrame(drawRadar);
})();
