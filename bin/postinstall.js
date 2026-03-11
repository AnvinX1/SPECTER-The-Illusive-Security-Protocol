#!/usr/bin/env node
// ══════════════════════════════════════════════════════════════════
//  SPECTER — Post-install Animation
//  Plays on npm install. Silent in CI / non-TTY environments.
// ══════════════════════════════════════════════════════════════════
'use strict';

const stdout = process.stdout;
const isTTY = stdout.isTTY && !process.env.CI && !process.env.SPECTER_QUIET;

// ── ANSI (zero deps) ───────────────────────────────────────────
const RST  = '\x1b[0m';
const BOLD = '\x1b[1m';
const DIM  = '\x1b[2m';
const CYAN = '\x1b[36m';
const GREEN = '\x1b[32m';
const WHITE = '\x1b[97m';
const HIDE = '\x1b[?25l';
const SHOW = '\x1b[?25h';
const CLR  = '\x1b[2K';

const V = '1.0.0';

const LOGO = [
  '███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗ ',
  '██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗',
  '███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝',
  '╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗',
  '███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║',
  '╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝',
];

const GLITCH = '░▒▓█▄▀■□▪▫╬╫╪═║╡╢╖╗╘╙╔╦╠━┃┏┓┗┛';
const SEP = '━'.repeat(62);
const P = '  ';

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Static banner (CI / piped output) ──────────────────────────
function staticBanner() {
  console.log('');
  console.log(`${P}${SEP}`);
  for (const l of LOGO) console.log(`${P} ${l}`);
  console.log(`${P}${SEP}`);
  console.log(`${P}  The Illusive Security Protocol  v${V}`);
  console.log(`${P}  by Anvin · Illusive Operations`);
  console.log('');
  console.log(`${P}  16 skills · 11 references · 8 scripts`);
  console.log(`${P}  Run 'specter init' to activate.`);
  console.log('');
}

// ── Animated banner (interactive terminals) ────────────────────
async function animatedBanner() {
  stdout.write(HIDE);
  process.on('SIGINT', () => { stdout.write(SHOW); process.exit(0); });

  try {
    stdout.write('\n');

    // ▸ Phase 1: Scanning bar
    const barW = 50;
    const steps = 12;
    for (let i = 0; i <= steps; i++) {
      const filled = Math.round((i / steps) * barW);
      const bar = '▓'.repeat(filled) + '░'.repeat(barW - filled);
      const pct = String(Math.round((i / steps) * 100)).padStart(3);
      stdout.write(`${CLR}\r${P}${CYAN}${bar}${RST} ${DIM}${pct}%${RST}`);
      await sleep(30);
    }
    await sleep(100);
    stdout.write(`${CLR}\r`);

    // ▸ Phase 2: Logo with glitch reveal
    console.log(`${P}${DIM}${SEP}${RST}`);
    for (const line of LOGO) {
      // Glitch frame — random chars where letters should be
      const glitched = line.replace(/[^\s]/g, () =>
        GLITCH[Math.floor(Math.random() * GLITCH.length)]
      );
      stdout.write(`${CLR}\r${P} ${DIM}${glitched}${RST}`);
      await sleep(25);
      // Resolve to real line
      stdout.write(`${CLR}\r${P} ${CYAN}${BOLD}${line}${RST}\n`);
    }
    console.log(`${P}${DIM}${SEP}${RST}`);

    await sleep(80);

    // ▸ Phase 3: Info
    console.log(`${P}  ${WHITE}${BOLD}The Illusive Security Protocol${RST}  ${DIM}v${V}${RST}`);
    await sleep(40);
    console.log(`${P}  ${DIM}by Anvin · Illusive Operations${RST}`);
    console.log('');
    await sleep(60);

    // ▸ Phase 4: Stats
    console.log(`${P}  ${GREEN}◆${RST} 16 security skills   ${GREEN}◆${RST} 11 reference docs   ${GREEN}◆${RST} 8 helper scripts`);
    console.log('');
    await sleep(40);

    // ▸ Phase 5: CTA
    console.log(`${P}  ${DIM}Run ${RST}${CYAN}specter init${RST}${DIM} to activate in your project.${RST}`);
    console.log('');
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
