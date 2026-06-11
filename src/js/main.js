  (function() {
    const ov = document.createElement('div');
    ov.id = 'err-overlay';
    ov.innerHTML = `
      <div id="err-scanlines"></div>
      <div id="err-inner">
        <div id="err-code">404</div>
        <div id="err-msg">NOT FOUND</div>
        <div id="err-terminal">
          <div id="err-lines"></div>
          <span class="cursor"></span>
        </div>
      </div>`;
    document.body.appendChild(ov);
    const style = document.createElement('style');
    style.textContent = `
      #err-overlay {
        position:fixed;inset:0;z-index:9999;background:#000;
        display:flex;align-items:center;justify-content:center;
        font-family:'JetBrains Mono',monospace;
        animation: err-out 0.3s ease 3.8s forwards;
      }
      @keyframes err-out { to { opacity:0; pointer-events:none; } }
      #err-scanlines {
        position:absolute;inset:0;
        background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,80,0.03) 2px,rgba(0,255,80,0.03) 4px);
        pointer-events:none;
        animation:scan 8s linear infinite;
      }
      @keyframes scan { from{background-position:0 0} to{background-position:0 100%} }
      #err-inner { text-align:center; position:relative; }
      #err-code {
        font-family:'Space Grotesk',sans-serif;
        font-size:clamp(6rem,20vw,14rem);
        font-weight:700;
        color:#00FF41;
        line-height:1;
        letter-spacing:-0.05em;
        text-shadow:0 0 40px #00FF41, 0 0 80px rgba(0,255,65,0.4);
        animation:glitch 0.15s infinite alternate;
      }
      @keyframes glitch {
        0%  { text-shadow:0 0 40px #00FF41, -2px 0 #FF003C, 2px 0 #00D4FF; transform:skew(-0.3deg); }
        100%{ text-shadow:0 0 40px #00FF41,  2px 0 #FF003C,-2px 0 #00D4FF; transform:skew(0.3deg); }
      }
      #err-msg {
        font-size:clamp(0.9rem,3vw,1.4rem);
        color:#00FF41;
        letter-spacing:0.3em;
        margin-top:8px;
        opacity:0.8;
      }
      #err-terminal {
        margin-top:32px;
        text-align:left;
        display:inline-block;
        min-width:340px;
        font-size:0.82rem;
        color:#00FF41;
        line-height:2;
      }
    `;
    document.head.appendChild(style);
    setTimeout(() => { document.body.removeChild(ov); }, 4000);
    const errLines = [
      '> GET /admin HTTP/1.1',
      '< HTTP/1.1 404 Not Found',
      '> Loading portfolio.html ✓',
    ];
    const el = document.getElementById('err-lines');
    let idx = 0;
    function printErrLine() {
      if (idx >= errLines.length) return;
      const d = document.createElement('div');
      el.appendChild(d);
      let i = 0;
      const iv = setInterval(() => {
        d.textContent = errLines[idx].slice(0, i++);
        if (i > errLines[idx].length) { clearInterval(iv); idx++; setTimeout(printErrLine, 220); }
      }, 22);
    }
    setTimeout(printErrLine, 300);
  })();
