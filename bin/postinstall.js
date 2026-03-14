#!/usr/bin/env node
// ══════════════════════════════════════════════════════════════════
//  SPECTER — Post-install Animation  v1.4.0
//  Plays on npm install. Silent in CI / non-TTY environments.
// ══════════════════════════════════════════════════════════════════
'use strict';

const stdout = process.stdout;
const isTTY = stdout.isTTY && !process.env.CI && !process.env.SPECTER_QUIET;

// ── ANSI (zero deps) ───────────────────────────────────────────
const RST    = '\x1b[0m';
const BOLD   = '\x1b[1m';
const DIM    = '\x1b[2m';
const CYAN   = '\x1b[36m';
const BCYAN  = '\x1b[96m';
const GREEN  = '\x1b[32m';    // eslint-disable-line no-unused-vars
const BGREEN = '\x1b[92m';
const RED    = '\x1b[31m';
const YELLOW = '\x1b[33m';
const WHITE  = '\x1b[97m';
const HIDE   = '\x1b[?25l';
const SHOW   = '\x1b[?25h';
const CLR    = '\x1b[2K';

const pkg = require('../package.json');
const V    = pkg.version;

// ── Counts (single source of truth — update here when skills/refs/scripts change) ──
const COUNTS = { skills: 18, refs: 14, scripts: 15 };

const LOGO = [
  '███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗ ',
  '██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗',
  '███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝',
  '╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗',
  '███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║',
  '╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝',
];

// Per-line gradient: dim → bright → bold-white → bright → dim → dim
const LOGO_COLORS = [
  CYAN,
  BCYAN,
  WHITE + BOLD,
  BCYAN,
  CYAN,
  DIM + CYAN,
];

const GLITCH  = '░▒▓█▄▀■□▪▫╬╫╪═║╡╢╖╗╘╙╔╦╠━┃┏┓┗┛';
const MATRIX  = 'アイウエオカキクケコサシスセソタチツテトナニヌネノ░▒▓│┤╡╢╗╘╙╚╛╜╝╞╟╠═╬╧╨╤╥╫╪┘┐┌└┼';
const SEP     = '━'.repeat(62);
const SEP_DIM = '─'.repeat(62);
const P       = '  ';
const SPINNER = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'];

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function glitchLine(line) {
  return line.replace(/[^\s]/g, () => GLITCH[Math.floor(Math.random() * GLITCH.length)]);
}

function matrixLine(width) {
  return Array.from({ length: width }, () =>
    MATRIX[Math.floor(Math.random() * MATRIX.length)]
  ).join('');
}

// ── Typewriter ────────────────────────────────────────────────
async function typewrite(text, color = '', delay = 28) {
  for (const ch of text) {
    stdout.write(`${color}${ch}${RST}`);
    await sleep(delay + Math.random() * 8);
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
  console.log(`${P}  ${COUNTS.skills} skills · ${COUNTS.refs} references · ${COUNTS.scripts} scripts`);
  console.log(`${P}  NEW: specter-delta — continuous post-task audit`);
  console.log(`${P}  Run 'specter init' to activate.`);
  console.log('');
}

// ── Animated banner (interactive terminals) ────────────────────
async function animatedBanner() {
  stdout.write(HIDE);
  process.on('SIGINT', () => {
    stdout.write(`${CLR}\r${SHOW}`);
    process.exit(0);
  });

  const termW = stdout.columns || 80;
  const barW  = Math.min(50, termW - 20);

  try {
    stdout.write('\n');

    // ── Phase 0: Boot sequence typewriter ─────────────────────
    const bootLines = [
      `  SPECTER CORE v${V}`,
      '  LOADING SECURITY MODULES',
      '  AGENT INTERFACE ONLINE',
    ];

    for (const line of bootLines) {
      const padLen = Math.max(4, 38 - line.length);
      stdout.write(`${DIM}${CYAN}`);
      for (const ch of line) {
        stdout.write(ch);
        await sleep(8 + Math.random() * 5);
      }
      stdout.write(`${RST}${DIM}`);
      for (let d = 0; d < padLen; d++) {
        stdout.write('.');
        await sleep(12);
      }
      stdout.write(`${RST}${BGREEN}[OK]${RST}\n`);
      await sleep(60);
    }

    await sleep(120);

    // ── Phase 1: Matrix burst ─────────────────────────────────
    const matW = Math.min(58, termW - 4);

    // Reserve 3 lines for the matrix
    stdout.write('\n\n\n');

    for (let frame = 0; frame < 15; frame++) {
      stdout.write('\x1b[3A');  // cursor up 3
      for (let row = 0; row < 3; row++) {
        if (frame < 14) {
          stdout.write(`${CLR}\r${P}${DIM}${CYAN}${matrixLine(matW)}${RST}\n`);
        } else {
          stdout.write(`${CLR}\r\n`);  // last frame: erase
        }
      }
      await sleep(12);
    }

    // Cursor is 3 lines below where matrix started — go back up
    stdout.write('\x1b[3A');
    await sleep(80);

    // ── Phase 2: Tri-pulse scan bar ───────────────────────────
    const pulses = [
      { label: 'SCANNING ENVIRONMENT', color: DIM + CYAN },
      { label: 'LOADING THREAT DB',    color: CYAN       },
      { label: 'SECURITY ARMED',       color: BCYAN      },
    ];

    for (const pulse of pulses) {
      for (let i = 0; i <= barW; i += 2) {
        const bar = '█'.repeat(i) + '▒'.repeat(Math.min(3, barW - i)) + '░'.repeat(Math.max(0, barW - i - 3));
        const pct = String(Math.round((i / barW) * 100)).padStart(3);
        stdout.write(`${CLR}\r${P}${pulse.color}${bar}${RST} ${DIM}${pct}% ${pulse.label}${RST}`);
        await sleep(18);
      }
      stdout.write(`${CLR}\r`);
    }

    // ── Phase 3: Logo with 3-pass glitch + gradient ───────────
    stdout.write(`\n${P}${DIM}${SEP}${RST}\n`);

    for (let li = 0; li < LOGO.length; li++) {
      const line = LOGO[li];
      // 3 glitch passes
      const passes = [
        { col: DIM + RED,    ms: 18 },
        { col: DIM + YELLOW, ms: 12 },
        { col: DIM + BCYAN,  ms:  8 },
      ];
      for (const { col, ms } of passes) {
        stdout.write(`${CLR}\r${P} ${col}${glitchLine(line)}${RST}`);
        await sleep(ms);
      }
      // Final: gradient color per line
      const lineColor = LOGO_COLORS[li] || CYAN;
      stdout.write(`${CLR}\r${P} ${lineColor}${line}${RST}\n`);
      await sleep(12);
    }

    stdout.write(`${P}${DIM}${SEP}${RST}\n\n`);
    await sleep(60);

    // ── Phase 4: Typewriter title + author ────────────────────
    stdout.write(`${P}  `);
    await typewrite('The Illusive Security Protocol', WHITE + BOLD, 18);
    stdout.write(`  ${DIM}v${V}${RST}\n`);
    await sleep(30);

    stdout.write(`${P}  `);
    await typewrite('by Anvin · Illusive Operations', DIM, 14);
    stdout.write(`${RST}\n\n`);
    await sleep(80);

    // ── Phase 5: Count-up stats ───────────────────────────────
    const numStats = [
      { icon: '◆', color: CYAN,  label: 'security skills', target: COUNTS.skills  },
      { icon: '◆', color: CYAN,  label: 'reference docs',  target: COUNTS.refs    },
      { icon: '◆', color: CYAN,  label: 'helper scripts',  target: COUNTS.scripts },
    ];

    const TICKS   = 18;
    const TICK_MS = 16;

    for (const s of numStats) {
      for (let tick = 0; tick <= TICKS; tick++) {
        const cur    = Math.round((tick / TICKS) * s.target);
        const done   = tick === TICKS;
        const numStr = String(cur).padStart(2);
        const suffix = done ? `  ${BGREEN}✓${RST}` : '   ';
        stdout.write(`${CLR}\r${P}  ${s.color}${s.icon}${RST}  ${numStr} ${DIM}${s.label}${RST}${suffix}`);
        if (!done) await sleep(TICK_MS);
      }
      stdout.write('\n');
      await sleep(30);
    }

    // specter-delta: static (no count-up)
    stdout.write(`${P}  ${BGREEN}★${RST}  ${DIM}specter-delta  continuous post-task audit${RST}  ${BGREEN}${BOLD}[ NEW ]${RST}\n`);
    stdout.write('\n');
    await sleep(60);

    // ── Phase 6: Status panel ─────────────────────────────────
    stdout.write(`${P}${DIM}${SEP_DIM}${RST}\n`);
    await sleep(25);

    const rows = [
      [`${BGREEN}ACTIVE${RST}`, 'Security governance enforced'],
      [`${BGREEN}ACTIVE${RST}`, 'Post-task delta audit gate'],
      [`${BCYAN}READY${RST}`,   'Persistent findings store'],
      [`${BCYAN}READY${RST}`,   'CI/CD merge gate (see .github/workflows/)'],
      [`${BCYAN}READY${RST}`,   `${COUNTS.skills} skills · ${COUNTS.refs} references · ${COUNTS.scripts} scripts`],
    ];

    for (const [status, desc] of rows) {
      stdout.write(`\r${P}  ${DIM}[${RST} ${status} ${DIM}]${RST}  ${DIM}${desc}${RST}\n`);
      await sleep(40);
    }

    stdout.write(`${P}${DIM}${SEP_DIM}${RST}\n\n`);
    await sleep(40);

    // ── Phase 7: CTA with blinking cursor ─────────────────────
    stdout.write(`${P}  ${DIM}Run ${RST}${CYAN}${BOLD}specter init${RST}${DIM} to activate in your project.${RST} `);
    for (let b = 0; b < 3; b++) {
      stdout.write(`${CYAN}▌${RST}`);
      await sleep(200);
      stdout.write('\b \b');
      await sleep(200);
    }
    stdout.write('\n\n');

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
