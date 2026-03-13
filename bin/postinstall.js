#!/usr/bin/env node
// ══════════════════════════════════════════════════════════════════
//  SPECTER — Post-install Animation  v1.2.0
//  Plays on npm install. Silent in CI / non-TTY environments.
// ══════════════════════════════════════════════════════════════════
'use strict';

const stdout = process.stdout;
const isTTY = stdout.isTTY && !process.env.CI && !process.env.SPECTER_QUIET;

// ── ANSI (zero deps) ───────────────────────────────────────────
const RST     = '\x1b[0m';
const BOLD    = '\x1b[1m';
const DIM     = '\x1b[2m';
const CYAN    = '\x1b[36m';
const BCYAN   = '\x1b[96m';
const GREEN   = '\x1b[32m';
const BGREEN  = '\x1b[92m';
const RED     = '\x1b[31m';
const YELLOW  = '\x1b[33m';
const WHITE   = '\x1b[97m';
const HIDE    = '\x1b[?25l';
const SHOW    = '\x1b[?25h';
const CLR     = '\x1b[2K';
const UP1     = '\x1b[1A';

const V = require('../package.json').version;

const LOGO = [
  '███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗ ',
  '██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗',
  '███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝',
  '╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗',
  '███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║',
  '╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝',
];

const GLITCH    = '░▒▓█▄▀■□▪▫╬╫╪═║╡╢╖╗╘╙╔╦╠━┃┏┓┗┛';
const SEP       = '━'.repeat(62);
const SEP_DIM   = '─'.repeat(62);
const P         = '  ';
const SPINNER   = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'];

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function glitchLine(line) {
  return line.replace(/[^\s]/g, () => GLITCH[Math.floor(Math.random() * GLITCH.length)]);
}

// ── Typewriter ────────────────────────────────────────────────
async function typewrite(text, color = '', delay = 28) {
  for (const ch of text) {
    stdout.write(`${color}${ch}${RST}`);
    await sleep(delay + Math.random() * 10);
  }
}

// ── Static banner (CI / piped output) ──────────────────────────
function staticBanner() {
  console.log('');
  console.log(`${P}${SEP}`);
  for (const l of LOGO) console.log(`${P} ${l}`);
  console.log(`${P}${SEP}`);
  console.log(`${P}  The Illusive Security Protocol  v${V}`);
  console.log(`${P}  by Anvin · Illusive Operations`);
  console.log('');
  console.log(`${P}  18 skills · 11 references · 14 scripts`);
  console.log(`${P}  NEW: specter-delta — continuous post-task audit`);
  console.log(`${P}  Run 'specter init' to activate.`);
  console.log('');
}

// ── Animated banner (interactive terminals) ────────────────────
async function animatedBanner() {
  stdout.write(HIDE);
  process.on('SIGINT', () => { stdout.write(SHOW); process.exit(0); });

  try {
    stdout.write('\n');

    // ── Phase 0: Spinner — "ARMING SPECTER" ──────────────────
    const spinLabel = ' ARMING SPECTER';
    let spinIdx = 0;
    for (let i = 0; i < 22; i++) {
      const frame = SPINNER[spinIdx % SPINNER.length];
      stdout.write(`\r${P}${CYAN}${frame}${RST}${DIM}${spinLabel}${RST}`);
      spinIdx++;
      await sleep(45);
    }
    // Resolve spinner
    stdout.write(`\r${P}${BGREEN}✔${RST}${DIM} ARMED${RST}                \n`);
    await sleep(80);

    // ── Phase 1: Tri-pulse scan bar ───────────────────────────
    const barW = 50;
    const pulses = [
      { label: ' SCANNING ENVIRONMENT ', color: DIM + CYAN },
      { label: ' LOADING  SKILLS      ', color: CYAN       },
      { label: ' SECURITY ONLINE      ', color: BCYAN      },
    ];

    for (const pulse of pulses) {
      for (let i = 0; i <= barW; i += 2) {
        const bar = '█'.repeat(i) + '▒'.repeat(Math.min(3, barW - i)) + '░'.repeat(Math.max(0, barW - i - 3));
        const pct = String(Math.round((i / barW) * 100)).padStart(3);
        stdout.write(`${CLR}\r${P}${pulse.color}${bar}${RST} ${DIM}${pct}%${pulse.label.trim()}${RST}`);
        await sleep(18);
      }
      stdout.write(`${CLR}\r`);
    }

    // ── Phase 2: Logo with multi-pass glitch reveal ───────────
    stdout.write(`\n${P}${DIM}${SEP}${RST}\n`);

    for (const line of LOGO) {
      // Two glitch passes before settling
      for (let pass = 0; pass < 2; pass++) {
        const g = glitchLine(line);
        const col = pass === 0 ? DIM + RED : DIM + YELLOW;
        stdout.write(`${CLR}\r${P} ${col}${g}${RST}`);
        await sleep(22 + pass * 15);
      }
      // Final: real line in full CYAN BOLD
      stdout.write(`${CLR}\r${P} ${CYAN}${BOLD}${line}${RST}\n`);
      await sleep(12);
    }

    stdout.write(`${P}${DIM}${SEP}${RST}\n\n`);
    await sleep(60);

    // ── Phase 3: Typewriter title ─────────────────────────────
    stdout.write(`${P}  `);
    await typewrite('The Illusive Security Protocol', WHITE + BOLD, 22);
    stdout.write(`  ${DIM}v${V}${RST}\n`);
    await sleep(30);

    stdout.write(`${P}  ${DIM}by Anvin · Illusive Operations${RST}\n`);
    stdout.write('\n');
    await sleep(80);

    // ── Phase 4: Stats — staggered with badges ────────────────
    const stats = [
      { icon: '◆', color: CYAN,   text: '18 security skills',   badge: null },
      { icon: '◆', color: CYAN,   text: '11 reference docs',    badge: null },
      { icon: '◆', color: CYAN,   text: '14 helper scripts',    badge: null },
      { icon: '★', color: BGREEN, text: 'specter-delta  continuous post-task audit', badge: 'NEW' },
    ];

    for (const s of stats) {
      const badgeStr = s.badge
        ? `  ${BGREEN}${BOLD}[ ${s.badge} ]${RST}`
        : '';
      stdout.write(`${P}  ${s.color}${s.icon}${RST}  ${DIM}${s.text}${RST}${badgeStr}\n`);
      await sleep(55);
    }
    stdout.write('\n');
    await sleep(60);

    // ── Phase 5: Status panel ────────────────────────────────
    stdout.write(`${P}${DIM}${SEP_DIM}${RST}\n`);
    await sleep(25);

    const rows = [
      [`${BGREEN}ACTIVE${RST}`,  'Security governance enforced'],
      [`${BGREEN}ACTIVE${RST}`,  'Post-task delta audit gate'],
      [`${BCYAN}READY${RST}`,    'Persistent findings store'],
      [`${BCYAN}READY${RST}`,    'CI/CD merge gate (see .github/workflows/)'],
    ];

    for (const [status, desc] of rows) {
      stdout.write(`\r${P}  ${DIM}[${RST} ${status} ${DIM}]${RST}  ${DIM}${desc}${RST}\n`);
      await sleep(40);
    }

    stdout.write(`${P}${DIM}${SEP_DIM}${RST}\n\n`);
    await sleep(40);

    // ── Phase 6: CTA ─────────────────────────────────────────
    stdout.write(`${P}  ${DIM}Run ${RST}${CYAN}${BOLD}specter init${RST}${DIM} to activate in your project.${RST}\n`);
    stdout.write('\n');

  } finally {
    stdout.write(SHOW);
  }
}

// ── Entry ──────────────────────────────────────────────────────
try {
  if (isTTY) {
    animatedBanner().catch(() => {
      stdout.write(SHOW);
      staticBanner();
    });
  } else {
    staticBanner();
  }
} catch {
  // Never break npm install — fail silently
}
