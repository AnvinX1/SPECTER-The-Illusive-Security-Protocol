#!/usr/bin/env node
// ══════════════════════════════════════════════════════════════════
//  SPECTER — The Illusive Security Protocol
//  CLI Tool · by Anvin · Illusive Operations
// ══════════════════════════════════════════════════════════════════
'use strict';

const fs = require('fs');
const path = require('path');

const VERSION = require(path.resolve(__dirname, '..', 'package.json')).version;
const SPECTER_DIR = '.specter';

// ── ANSI Colors (zero dependencies) ────────────────────────────
const c = {
  reset:   '\x1b[0m',
  bold:    '\x1b[1m',
  dim:     '\x1b[2m',
  red:     '\x1b[31m',
  green:   '\x1b[32m',
  yellow:  '\x1b[33m',
  cyan:    '\x1b[36m',
  magenta: '\x1b[35m',
  bcyan:   '\x1b[96m',
  white:   '\x1b[97m',
  bgreen:  '\x1b[92m',
};

const SEP      = '━'.repeat(62);
const SEP_DIM  = '─'.repeat(62);
const HIDE     = '\x1b[?25l';
const SHOW     = '\x1b[?25h';
const CLR      = '\x1b[2K';
const SPINNER  = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'];
const GLITCH_CHARS = '░▒▓█▄▀■□▪▫╬╫╪═║╡╢╖╗╘╙╔╦╠━┃┏┓┗┛';
const MATRIX_CHARS = 'アイウエオカキクケコサシスセソタチツテトナニヌネノ░▒▓│┤╡╢╗╘╙╚╛╜╝╞╟╠═╬╧╨╤╥╫╪┘┐┌└┼';
const LOGO_COLORS  = [c.cyan, c.bcyan, c.white + c.bold, c.bcyan, c.cyan, c.dim + c.cyan];
const COUNTS       = { skills: 18, refs: 14, scripts: 15 };
const P            = '  ';

const BANNER = `
${c.dim}${SEP}${c.reset}
 ${c.cyan}${c.bold}███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗ ${c.reset}
 ${c.cyan}${c.bold}██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗${c.reset}
 ${c.cyan}${c.bold}███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝${c.reset}
 ${c.cyan}${c.bold}╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗${c.reset}
 ${c.cyan}${c.bold}███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║${c.reset}
 ${c.cyan}${c.bold}╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝${c.reset}
${c.dim}${SEP}${c.reset}
  ${c.bold}The Illusive Security Protocol${c.reset}  ${c.dim}v${VERSION}${c.reset}
  ${c.dim}by Anvin · Illusive Operations${c.reset}
`;

const LOGO_LINES = [
  '███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗ ',
  '██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗',
  '███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝',
  '╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗',
  '███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║',
  '╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝',
];

// ── Package root (where npm installed us) ──────────────────────
const PKG_ROOT = path.resolve(__dirname, '..');

// ── Skill directories ──────────────────────────────────────────
const SKILL_DIRS = [
  'active-directory-and-identity-audit',
  'api-security-review',
  'bug-bounty-triage',
  'ci-cd-supply-chain-security',
  'cloud-config-audit',
  'container-and-runtime-security',
  'dependency-and-secret-audit',
  'evidence-and-reporting',
  'exploit-validation',
  'indepth-recon-analysis',
  'llm-and-ai-security',
  'mobile-security-assessment',
  'network-infrastructure-pentest',
  'secure-code-review',
  'security-governance',
  'specter-delta',
  'threat-modeling',
  'web-misconfig-review',
];

// ── Agent adapter definitions ──────────────────────────────────
const ADAPTERS = {
  copilot: {
    name: 'GitHub Copilot',
    src: 'adapters/copilot.instructions.md',
    dest: '.github/copilot-instructions.md',
  },
  cursor: {
    name: 'Cursor',
    src: 'adapters/cursor-rules.md',
    dest: '.cursor/rules/specter.md',
  },
  windsurf: {
    name: 'Windsurf',
    src: 'adapters/windsurf-rules.md',
    dest: '.windsurfrules',
  },
  claude: {
    name: 'Claude Code',
    src: 'adapters/claude.md',
    dest: 'CLAUDE.md',
  },
  zed: {
    name: 'Zed Editor',
    src: 'adapters/zed-rules.md',
    dest: '.zed/specter.md',
  },
  continue: {
    name: 'Continue.dev',
    src: 'adapters/continue-rules.md',
    dest: '.continue/specter.md',
  },
  cline: {
    name: 'Cline',
    src: 'adapters/cline-rules.md',
    dest: '.clinerules',
  },
  generic: {
    name: 'Generic Agents',
    src: 'adapters/agents.md',
    dest: 'AGENTS.md',
  },
};

// ── Skill metadata (for list command) ──────────────────────────
const SKILL_META = {
  'Governance & Triage': [
    ['security-governance',      'Authorization, scope, 22 cascading guardrails'],
    ['bug-bounty-triage',        'Intake, dedup, severity, routing matrix'],
  ],
  'Reconnaissance & Design': [
    ['indepth-recon-analysis',   'Attack surface mapping, tech fingerprinting'],
    ['threat-modeling',          'STRIDE, PASTA, attack trees, risk prioritization'],
  ],
  'Code & Application': [
    ['secure-code-review',       'Source code vulnerability hunting'],
    ['api-security-review',      'OWASP API Top 10, GraphQL, WebSocket'],
    ['web-misconfig-review',     'Headers, TLS, CORS, server config audit'],
  ],
  'Infrastructure & Cloud': [
    ['cloud-config-audit',       'IAM, storage, network, CIS benchmarks'],
    ['container-and-runtime-security', 'Container escape, K8s runtime, service mesh'],
    ['network-infrastructure-pentest', 'Segmentation, firewall, protocol testing'],
  ],
  'Supply Chain & Identity': [
    ['dependency-and-secret-audit',    'CVE lookup, secret detection, license risk'],
    ['ci-cd-supply-chain-security',    'Pipeline config, SLSA, artifact integrity'],
    ['active-directory-and-identity-audit', 'Kerberos, AD CS, BloodHound, Azure AD'],
  ],
  'Specialized': [
    ['exploit-validation',       'PoC development, exploitation, confirmation'],
    ['mobile-security-assessment', 'OWASP Mobile Top 10, Frida, Objection'],
    ['llm-and-ai-security',      'OWASP LLM Top 10, prompt injection, AI red teaming'],
  ],
  'Reporting & Audit': [
    ['evidence-and-reporting',   'Report compilation, redaction, statistics'],
    ['specter-delta',            'Fast-path post-task audit, findings store, CI gate'],
  ],
};

// ══════════════════════════════════════════════════════════════════
//  Utilities
// ══════════════════════════════════════════════════════════════════

function copyRecursiveSync(src, dest) {
  if (!fs.existsSync(src)) {
    console.warn(`  [specter] warning: source not found, skipping: ${src}`);
    return 0;
  }
  let count = 0;
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const child of fs.readdirSync(src)) {
      count += copyRecursiveSync(path.join(src, child), path.join(dest, child));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
    count = 1;
  }
  return count;
}

function countFiles(dir, ext) {
  if (!fs.existsSync(dir)) return 0;
  return fs.readdirSync(dir).filter(f => f.endsWith(ext)).length;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

const ok   = (msg) => console.log(`  ${c.green}✓${c.reset} ${msg}`);
const warn = (msg) => console.log(`  ${c.yellow}⚠${c.reset} ${msg}`);
const err  = (msg) => console.log(`  ${c.red}✗${c.reset} ${msg}`);
const info = (msg) => console.log(`  ${c.dim}${msg}${c.reset}`);

function parseArgs(argv) {
  const cmd = argv[0] || 'help';
  const flags = {};
  for (let i = 1; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        flags[key] = next;
        i++;
      } else {
        flags[key] = true;
      }
    }
  }
  return { cmd, flags };
}

// ══════════════════════════════════════════════════════════════════
//  Agent Detection
// ══════════════════════════════════════════════════════════════════

function detectAgents(projectDir) {
  const detected = [];

  if (fs.existsSync(path.join(projectDir, '.github')) ||
      fs.existsSync(path.join(projectDir, '.vscode'))) {
    detected.push('copilot');
  }
  if (fs.existsSync(path.join(projectDir, '.cursorrules')) ||
      fs.existsSync(path.join(projectDir, '.cursor'))) {
    detected.push('cursor');
  }
  if (fs.existsSync(path.join(projectDir, '.windsurfrules'))) {
    detected.push('windsurf');
  }
  if (fs.existsSync(path.join(projectDir, '.zed'))) {
    detected.push('zed');
  }
  if (fs.existsSync(path.join(projectDir, '.continue'))) {
    detected.push('continue');
  }
  if (fs.existsSync(path.join(projectDir, '.clinerules'))) {
    detected.push('cline');
  }

  // Default: copilot + generic if nothing else detected
  if (detected.length === 0) {
    detected.push('copilot');
  }
  if (!detected.includes('generic')) {
    detected.push('generic');
  }

  return detected;
}

// ══════════════════════════════════════════════════════════════════
//  Commands
// ══════════════════════════════════════════════════════════════════

async function animatedBanner() {
  const stdout = process.stdout;
  stdout.write(HIDE);
  process.on('SIGINT', () => {
    stdout.write(`${CLR}\r${SHOW}`);
    process.exit(0);
  });

  const termW = stdout.columns || 80;
  const barW  = Math.min(50, termW - 20);

  const glitch = (line) =>
    line.replace(/[^\s]/g, () => GLITCH_CHARS[Math.floor(Math.random() * GLITCH_CHARS.length)]);
  const matrix = (width) =>
    Array.from({ length: width }, () =>
      MATRIX_CHARS[Math.floor(Math.random() * MATRIX_CHARS.length)]
    ).join('');
  const typewrite = async (text, color, delay) => {
    for (const ch of text) {
      stdout.write(`${color}${ch}${c.reset}`);
      await sleep(delay + Math.random() * 8);
    }
  };

  try {
    stdout.write('\n');

    // ── Phase 0: Boot sequence ────────────────────────────────
    const bootLines = [
      `  SPECTER CORE v${VERSION}`,
      '  LOADING SECURITY MODULES',
      '  AGENT INTERFACE ONLINE',
    ];
    for (const line of bootLines) {
      const padLen = Math.max(4, 38 - line.length);
      stdout.write(`${c.dim}${c.cyan}`);
      for (const ch of line) { stdout.write(ch); await sleep(8 + Math.random() * 5); }
      stdout.write(`${c.reset}${c.dim}`);
      for (let d = 0; d < padLen; d++) { stdout.write('.'); await sleep(12); }
      stdout.write(`${c.reset}${c.bgreen}[OK]${c.reset}\n`);
      await sleep(60);
    }
    await sleep(120);

    // ── Phase 1: Matrix burst ─────────────────────────────────
    const matW = Math.min(58, termW - 4);
    stdout.write('\n\n\n');
    for (let frame = 0; frame < 15; frame++) {
      stdout.write('\x1b[3A');
      for (let row = 0; row < 3; row++) {
        if (frame < 14) {
          stdout.write(`${CLR}\r${P}${c.dim}${c.cyan}${matrix(matW)}${c.reset}\n`);
        } else {
          stdout.write(`${CLR}\r\n`);
        }
      }
      await sleep(12);
    }
    stdout.write('\x1b[3A');
    await sleep(80);

    // ── Phase 2: Tri-pulse scan bar ───────────────────────────
    const pulses = [
      { label: 'SCANNING ENVIRONMENT', color: c.dim + c.cyan  },
      { label: 'LOADING THREAT DB',    color: c.cyan           },
      { label: 'SECURITY ARMED',       color: c.bcyan          },
    ];
    for (const pulse of pulses) {
      for (let i = 0; i <= barW; i += 2) {
        const bar = '█'.repeat(i) + '▒'.repeat(Math.min(3, barW - i)) + '░'.repeat(Math.max(0, barW - i - 3));
        const pct = String(Math.round((i / barW) * 100)).padStart(3);
        stdout.write(`${CLR}\r${P}${pulse.color}${bar}${c.reset} ${c.dim}${pct}% ${pulse.label}${c.reset}`);
        await sleep(18);
      }
      stdout.write(`${CLR}\r`);
    }

    // ── Phase 3: Logo with 3-pass glitch + gradient ───────────
    stdout.write(`\n${P}${c.dim}${SEP}${c.reset}\n`);
    for (let li = 0; li < LOGO_LINES.length; li++) {
      const line = LOGO_LINES[li];
      const passes = [
        { col: c.dim + c.red,    ms: 18 },
        { col: c.dim + c.yellow, ms: 12 },
        { col: c.dim + c.bcyan,  ms:  8 },
      ];
      for (const { col, ms } of passes) {
        stdout.write(`${CLR}\r${P} ${col}${glitch(line)}${c.reset}`);
        await sleep(ms);
      }
      const lineColor = LOGO_COLORS[li] || c.cyan;
      stdout.write(`${CLR}\r${P} ${lineColor}${line}${c.reset}\n`);
      await sleep(12);
    }
    stdout.write(`${P}${c.dim}${SEP}${c.reset}\n\n`);
    await sleep(60);

    // ── Phase 4: Typewriter title + author ────────────────────
    stdout.write(`${P}  `);
    await typewrite('The Illusive Security Protocol', c.white + c.bold, 18);
    stdout.write(`  ${c.dim}v${VERSION}${c.reset}\n`);
    await sleep(30);
    stdout.write(`${P}  `);
    await typewrite('by Anvin · Illusive Operations', c.dim, 14);
    stdout.write(`${c.reset}\n\n`);
    await sleep(80);

    // ── Phase 5: Count-up stats ───────────────────────────────
    const numStats = [
      { icon: '◆', color: c.cyan,  label: 'security skills', target: COUNTS.skills  },
      { icon: '◆', color: c.cyan,  label: 'reference docs',  target: COUNTS.refs    },
      { icon: '◆', color: c.cyan,  label: 'helper scripts',  target: COUNTS.scripts },
    ];
    const TICKS = 18, TICK_MS = 16;
    for (const s of numStats) {
      for (let tick = 0; tick <= TICKS; tick++) {
        const cur    = Math.round((tick / TICKS) * s.target);
        const done   = tick === TICKS;
        const numStr = String(cur).padStart(2);
        const suffix = done ? `  ${c.bgreen}✓${c.reset}` : '   ';
        stdout.write(`${CLR}\r${P}  ${s.color}${s.icon}${c.reset}  ${numStr} ${c.dim}${s.label}${c.reset}${suffix}`);
        if (!done) await sleep(TICK_MS);
      }
      stdout.write('\n');
      await sleep(30);
    }
    stdout.write(`${P}  ${c.bgreen}★${c.reset}  ${c.dim}specter-delta  continuous post-task audit${c.reset}  ${c.bgreen}${c.bold}[ NEW ]${c.reset}\n\n`);
    await sleep(60);

    // ── Phase 6: Status panel ─────────────────────────────────
    stdout.write(`${P}${c.dim}${SEP_DIM}${c.reset}\n`);
    await sleep(25);
    const rows = [
      [`${c.bgreen}ACTIVE${c.reset}`, 'Security governance enforced'],
      [`${c.bgreen}ACTIVE${c.reset}`, 'Post-task delta audit gate'],
      [`${c.bcyan}READY${c.reset}`,   'Persistent findings store'],
      [`${c.bcyan}READY${c.reset}`,   'CI/CD merge gate (see .github/workflows/)'],
      [`${c.bcyan}READY${c.reset}`,   `${COUNTS.skills} skills · ${COUNTS.refs} references · ${COUNTS.scripts} scripts`],
    ];
    for (const [status, desc] of rows) {
      stdout.write(`\r${P}  ${c.dim}[${c.reset} ${status} ${c.dim}]${c.reset}  ${c.dim}${desc}${c.reset}\n`);
      await sleep(40);
    }
    stdout.write(`${P}${c.dim}${SEP_DIM}${c.reset}\n\n`);
    await sleep(40);

    // ── Phase 7: CTA with blinking cursor ─────────────────────
    stdout.write(`${P}  ${c.dim}Run ${c.reset}${c.cyan}${c.bold}specter init${c.reset}${c.dim} to activate in your project.${c.reset} `);
    for (let b = 0; b < 3; b++) {
      stdout.write(`${c.cyan}▌${c.reset}`);
      await sleep(200);
      stdout.write('\b \b');
      await sleep(200);
    }
    stdout.write('\n\n');

  } finally {
    stdout.write(SHOW);
  }
}

async function cmdInit(flags) {
  if (process.stdout.isTTY && !process.env.CI) {
    await animatedBanner();
  } else {
    console.log(BANNER);
  }

  const projectDir = process.cwd();
  const specterDir = path.join(projectDir, SPECTER_DIR);
  const force = !!flags.force;

  // Determine target agents
  let agentKeys;
  if (flags.agent === 'all') {
    agentKeys = Object.keys(ADAPTERS);
  } else if (flags.agent === 'custom') {
    // Custom agent: copy --src file to --dest path
    if (!flags.src || !flags.dest) {
      err('--agent custom requires --src <file> and --dest <path>');
      info('Usage: specter init --agent custom --src ./my-adapter.md --dest ./.myagent/specter.md');
      process.exit(1);
    }
    const srcFile  = path.resolve(flags.src);
    const destFile = path.resolve(flags.dest);
    if (!fs.existsSync(srcFile)) {
      err(`Custom adapter source not found: ${flags.src}`);
      process.exit(1);
    }
    fs.mkdirSync(path.dirname(destFile), { recursive: true });
    fs.copyFileSync(srcFile, destFile);
    ok(`Custom agent adapter installed: ${flags.dest}`);
    agentKeys = [];
  } else if (flags.agent) {
    agentKeys = flags.agent.split(',').map(a => a.trim());
    for (const key of agentKeys) {
      if (!ADAPTERS[key]) {
        err(`Unknown agent: ${key}`);
        info(`Available: ${Object.keys(ADAPTERS).join(', ')}, all, custom`);
        process.exit(1);
      }
    }
  } else {
    agentKeys = detectAgents(projectDir);
  }

  console.log('  Initializing SPECTER...\n');

  // ── 1. Create .specter directory ────────────────────────────
  fs.mkdirSync(specterDir, { recursive: true });

  // ── 2. Copy skills ─────────────────────────────────────────
  const skillsDest = path.join(specterDir, 'skills');
  let skillCount = 0;
  for (const dir of SKILL_DIRS) {
    const src = path.join(PKG_ROOT, dir);
    if (fs.existsSync(src)) {
      copyRecursiveSync(src, path.join(skillsDest, dir));
      skillCount++;
    }
  }
  ok(`Installed ${c.bold}${skillCount}${c.reset} security skills`);

  // ── 3. Copy references ─────────────────────────────────────
  const refsCount = copyRecursiveSync(
    path.join(PKG_ROOT, 'references'),
    path.join(specterDir, 'references')
  );
  ok(`Installed ${c.bold}${refsCount}${c.reset} reference documents`);

  // ── 4. Copy scripts ────────────────────────────────────────
  const scriptsCount = copyRecursiveSync(
    path.join(PKG_ROOT, 'scripts'),
    path.join(specterDir, 'scripts')
  );
  ok(`Installed ${c.bold}${scriptsCount}${c.reset} helper scripts`);

  // ── 5. Copy master instructions ────────────────────────────
  for (const docFile of ['specter.md', 'specter.instructions.md']) {
    const src = path.join(PKG_ROOT, docFile);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, path.join(specterDir, docFile));
    }
  }
  ok('Created master instructions');

  console.log('');

  // ── 6. Install agent adapters ──────────────────────────────
  for (const key of agentKeys) {
    const adapter = ADAPTERS[key];
    if (!adapter) continue;

    const srcFile = path.join(PKG_ROOT, adapter.src);
    const destFile = path.join(projectDir, adapter.dest);

    if (!fs.existsSync(srcFile)) {
      warn(`Adapter source missing: ${adapter.src}`);
      continue;
    }

    if (fs.existsSync(destFile) && !force) {
      warn(`${adapter.dest} exists ${c.dim}(use --force to overwrite)${c.reset}`);
      continue;
    }

    fs.mkdirSync(path.dirname(destFile), { recursive: true });
    fs.copyFileSync(srcFile, destFile);
    ok(`Created ${adapter.dest} ${c.dim}(${adapter.name})${c.reset}`);
  }

  // ── 7. Write .specterrc ────────────────────────────────────
  const rc = {
    version: VERSION,
    initialized: new Date().toISOString().split('T')[0],
    agents: agentKeys,
    skills: SKILL_DIRS.length,
    createdBy: 'Anvin (Illusive Operations)',
  };
  fs.writeFileSync(
    path.join(projectDir, '.specterrc'),
    JSON.stringify(rc, null, 2) + '\n'
  );
  ok('Created .specterrc');

  // ── 8. Update .gitignore ───────────────────────────────────
  const gitignorePath = path.join(projectDir, '.gitignore');
  if (fs.existsSync(gitignorePath)) {
    const content = fs.readFileSync(gitignorePath, 'utf8');
    if (!content.includes('.specterrc')) {
      fs.appendFileSync(gitignorePath, '\n# SPECTER\n.specterrc\n');
      ok('Updated .gitignore');
    }
  }

  // ── Done ───────────────────────────────────────────────────
  console.log(`\n${c.green}${c.bold}  SPECTER is operational.${c.reset}`);
  console.log(`${c.dim}  Security governance is now enforced for all agents.`);
  console.log(`  Run 'specter list' to see installed skills.`);
  console.log(`  Run 'specter doctor' to verify installation.${c.reset}\n`);
}

function cmdList(flags = {}) {
  if (flags.agents) {
    console.log(BANNER);
    console.log(`  ${c.bold}Supported Agents:${c.reset}\n`);
    for (const [key, adapter] of Object.entries(ADAPTERS)) {
      const check = `${c.green}✓${c.reset}`;
      const pad = ' '.repeat(Math.max(1, 12 - key.length));
      console.log(`    ${check} ${c.cyan}${key}${c.reset}${pad}${c.dim}→ ${adapter.dest}${c.reset}`);
    }
    console.log(`      ${c.dim}custom      → --src <file> --dest <path>  (any agent)${c.reset}`);
    console.log('');
    return;
  }

  console.log(BANNER);
  console.log(`  ${c.bold}Security Skills (${SKILL_DIRS.length}):${c.reset}\n`);

  for (const [category, skills] of Object.entries(SKILL_META)) {
    console.log(`  ${c.cyan}${c.bold}${category}${c.reset}`);
    for (const [name, desc] of skills) {
      const exists = fs.existsSync(path.join(PKG_ROOT, name, 'SKILL.md'));
      const mark = exists ? `${c.green}✓${c.reset}` : `${c.red}✗${c.reset}`;
      const pad = ' '.repeat(Math.max(1, 42 - name.length));
      console.log(`    ${mark} ${name}${pad}${c.dim}${desc}${c.reset}`);
    }
    console.log('');
  }

  console.log(`  ${c.dim}References: ${countFiles(path.join(PKG_ROOT, 'references'), '.md')}`);
  console.log(`  Scripts:    ${countFiles(path.join(PKG_ROOT, 'scripts'), '.py')}${c.reset}\n`);
}

function cmdDoctor() {
  console.log(BANNER);
  console.log(`  ${c.bold}Health Check:${c.reset}\n`);

  const projectDir = process.cwd();
  const specterDir = path.join(projectDir, SPECTER_DIR);
  let healthy = true;
  let warnings = 0;

  // Check .specter/
  if (fs.existsSync(specterDir)) {
    ok(`${SPECTER_DIR}/ directory exists`);
  } else {
    err(`${SPECTER_DIR}/ not found — run 'specter init'`);
    healthy = false;
  }

  // Check skills
  const skillsDir = path.join(specterDir, 'skills');
  if (fs.existsSync(skillsDir)) {
    const installed = fs.readdirSync(skillsDir)
      .filter(d => fs.existsSync(path.join(skillsDir, d, 'SKILL.md'))).length;
    if (installed === SKILL_DIRS.length) {
      ok(`${installed}/${SKILL_DIRS.length} skills installed`);
    } else {
      warn(`${installed}/${SKILL_DIRS.length} skills installed (${SKILL_DIRS.length - installed} missing)`);
      warnings++;
    }
  } else if (healthy) {
    err('skills/ directory missing');
    healthy = false;
  }

  // Check references
  const refsDir = path.join(specterDir, 'references');
  if (fs.existsSync(refsDir)) {
    const count = countFiles(refsDir, '.md');
    ok(`${count} reference documents`);
  } else if (healthy) {
    err('references/ directory missing');
    healthy = false;
  }

  // Check scripts
  const scriptsDir = path.join(specterDir, 'scripts');
  if (fs.existsSync(scriptsDir)) {
    const count = countFiles(scriptsDir, '.py');
    ok(`${count} helper scripts`);
  } else if (healthy) {
    err('scripts/ directory missing');
    healthy = false;
  }

  // Check master instructions
  if (fs.existsSync(path.join(specterDir, 'specter.md'))) {
    ok('Master instructions present');
  } else {
    warn('Master instructions missing');
    warnings++;
  }

  if (fs.existsSync(path.join(specterDir, 'specter.instructions.md'))) {
    ok('Auto-load instructions present');
  } else {
    warn('Auto-load instructions missing');
    warnings++;
  }

  // Check adapters
  console.log('');
  console.log(`  ${c.bold}Agent Adapters:${c.reset}`);
  for (const [, adapter] of Object.entries(ADAPTERS)) {
    const destFile = path.join(projectDir, adapter.dest);
    if (fs.existsSync(destFile)) {
      ok(`${adapter.name}: ${c.dim}${adapter.dest}${c.reset}`);
    } else {
      info(`${adapter.name}: not installed`);
    }
  }

  // Check .specterrc
  const rcPath = path.join(projectDir, '.specterrc');
  if (fs.existsSync(rcPath)) {
    try {
      const rc = JSON.parse(fs.readFileSync(rcPath, 'utf8'));
      console.log('');
      info(`Version: ${rc.version} | Initialized: ${rc.initialized} | Agents: ${(rc.agents || []).join(', ')}`);
    } catch { /* ignore parse errors */ }
  }

  // Summary
  if (healthy && warnings === 0) {
    console.log(`\n  ${c.green}${c.bold}Status: Healthy ✓${c.reset}\n`);
  } else if (healthy) {
    console.log(`\n  ${c.yellow}${c.bold}Status: OK with ${warnings} warning(s)${c.reset}\n`);
  } else {
    console.log(`\n  ${c.red}${c.bold}Status: Issues found — run 'specter init'${c.reset}\n`);
    process.exit(1);
  }
}

function cmdUpdate() {
  console.log(BANNER);

  const projectDir = process.cwd();
  const specterDir = path.join(projectDir, SPECTER_DIR);

  if (!fs.existsSync(specterDir)) {
    err(`SPECTER not initialized. Run 'specter init' first.`);
    process.exit(1);
  }

  console.log('  Updating SPECTER...\n');

  // Re-copy skills
  const skillsDest = path.join(specterDir, 'skills');
  let updated = 0;
  for (const dir of SKILL_DIRS) {
    const src = path.join(PKG_ROOT, dir);
    if (fs.existsSync(src)) {
      copyRecursiveSync(src, path.join(skillsDest, dir));
      updated++;
    }
  }
  ok(`Updated ${updated} skills`);

  // Re-copy references
  copyRecursiveSync(
    path.join(PKG_ROOT, 'references'),
    path.join(specterDir, 'references')
  );
  ok('Updated references');

  // Re-copy scripts
  copyRecursiveSync(
    path.join(PKG_ROOT, 'scripts'),
    path.join(specterDir, 'scripts')
  );
  ok('Updated scripts');

  // Re-copy master instructions
  for (const docFile of ['specter.md', 'specter.instructions.md']) {
    const src = path.join(PKG_ROOT, docFile);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, path.join(specterDir, docFile));
    }
  }
  ok('Updated master instructions');

  console.log(`\n${c.green}${c.bold}  SPECTER updated to v${VERSION}.${c.reset}\n`);
}

function cmdRun(runArgs) {
  // runArgs = everything after 'run' on the argv (raw, un-parsed)
  const CHECK_MAP = {
    'http-headers': 'http_headers_check.py',
    'tls':          'tls_check.py',
    'ports':        'port_probe.py',
    'secrets':      'secret_grep.py',
    'tool':         'cmd_runner.py',
  };

  const check = runArgs[0];

  if (!check || check === '--help' || check === '-h') {
    console.log('');
    console.log(`  ${c.bold}Usage:${c.reset} specter run <check> <target> [options]\n`);
    console.log(`  ${c.bold}Checks:${c.reset}`);
    console.log(`    ${c.cyan}http-headers${c.reset}  <url>                  Check HTTP security headers`);
    console.log(`    ${c.cyan}tls${c.reset}           <host> [--port N]      Check TLS/SSL configuration`);
    console.log(`    ${c.cyan}ports${c.reset}         <host> [--ports spec]  TCP port probe with banners`);
    console.log(`    ${c.cyan}secrets${c.reset}       [dir]                  Scan directory for secrets`);
    console.log(`    ${c.cyan}tool${c.reset}          <toolname> [args...]   Run an allowlisted tool`);
    console.log('');
    console.log(`  ${c.bold}Examples:${c.reset}`);
    console.log(`    ${c.dim}$${c.reset} specter run http-headers https://example.com`);
    console.log(`    ${c.dim}$${c.reset} specter run tls example.com --port 8443`);
    console.log(`    ${c.dim}$${c.reset} specter run ports 10.0.0.1 --ports top1000 --threads 100`);
    console.log(`    ${c.dim}$${c.reset} specter run secrets ./src --include '.env,.py'`);
    console.log(`    ${c.dim}$${c.reset} specter run tool nmap -sV -p 80,443 example.com`);
    console.log(`    ${c.dim}$${c.reset} specter run tool --list`);
    console.log('');
    return;
  }

  const scriptName = CHECK_MAP[check];
  if (!scriptName) {
    err(`Unknown check: ${check}`);
    err(`Valid checks: ${Object.keys(CHECK_MAP).join(', ')}`);
    process.exit(1);
  }

  // Require a target for checks that need one
  const needsTarget = check !== 'secrets' && check !== 'tool';
  if (needsTarget && !runArgs[1]) {
    err(`specter run ${check} requires a target.`);
    err(`Example: specter run ${check} <target>`);
    process.exit(1);
  }

  // Resolve script: prefer installed .specter/scripts/ over package root
  const projectDir = process.cwd();
  const installedScript = path.join(projectDir, SPECTER_DIR, 'scripts', scriptName);
  const pkgScript = path.join(PKG_ROOT, 'scripts', scriptName);
  const scriptPath = fs.existsSync(installedScript) ? installedScript : pkgScript;

  if (!fs.existsSync(scriptPath)) {
    err(`Script not found: ${scriptName}`);
    err(`Run 'specter init' to install SPECTER scripts, or check your SPECTER_DIR.`);
    process.exit(1);
  }

  // Args to pass to the Python script: everything after the check name
  const scriptArgs = runArgs.slice(1);

  const { spawnSync } = require('child_process');
  const python = process.platform === 'win32' ? 'python' : 'python3';

  const result = spawnSync(python, [scriptPath, ...scriptArgs], {
    stdio: 'inherit',
    shell: false,  // never true — prevents injection even if scriptArgs contains metacharacters
  });

  if (result.error) {
    err(`Failed to start Python: ${result.error.message}`);
    err('Ensure python3 is installed and in PATH.');
    process.exit(1);
  }

  process.exit(result.status ?? 0);
}

function cmdScan(scanArgs) {
  const { spawnSync } = require('child_process');

  const mode = scanArgs[0];

  if (!mode || mode === '--help' || mode === '-h') {
    console.log('');
    console.log(`  ${c.bold}Usage:${c.reset} specter scan <mode> <target> [options]\n`);
    console.log(`  ${c.bold}Modes:${c.reset}`);
    console.log(`    ${c.cyan}web${c.reset}   <url>            Run TLS + HTTP headers checks`);
    console.log(`    ${c.cyan}host${c.reset}  <hostname>       Run TLS + port probe`);
    console.log(`    ${c.cyan}dir${c.reset}   [path]           Run secret scanner on directory`);
    console.log(`    ${c.cyan}all${c.reset}   <url> [path]     Run all applicable checks`);
    console.log('');
    console.log(`  ${c.bold}Options:${c.reset}`);
    console.log(`    --output <file>    Write combined markdown report to file`);
    console.log('');
    console.log(`  ${c.bold}Examples:${c.reset}`);
    console.log(`    ${c.dim}$${c.reset} specter scan web https://example.com`);
    console.log(`    ${c.dim}$${c.reset} specter scan host example.com`);
    console.log(`    ${c.dim}$${c.reset} specter scan dir ./src`);
    console.log(`    ${c.dim}$${c.reset} specter scan all https://example.com ./src --output report.md`);
    console.log('');
    return;
  }

  // Parse --output flag and collect positional args
  let outputFile = null;
  const positionalArgs = [];
  for (let i = 1; i < scanArgs.length; i++) {
    if (scanArgs[i] === '--output' && scanArgs[i + 1]) {
      outputFile = scanArgs[++i];
    } else if (!scanArgs[i].startsWith('--')) {
      positionalArgs.push(scanArgs[i]);
    }
  }

  // Resolve a Python script path (prefer installed .specter/scripts/ over pkg root)
  const projectDir = process.cwd();
  function scriptPath(name) {
    const candidates = [
      path.join(projectDir, SPECTER_DIR, 'scripts', name),
      path.join(PKG_ROOT, 'scripts', name),
    ];
    for (const p of candidates) {
      if (fs.existsSync(p)) return p;
    }
    return null;
  }

  // Normalise URL → ensure it has a scheme so URL() parses correctly
  function normaliseUrl(raw) {
    return raw.startsWith('http://') || raw.startsWith('https://') ? raw : `https://${raw}`;
  }

  // Build task list based on mode
  let tasks = [];
  switch (mode) {
    case 'web': {
      const rawUrl = positionalArgs[0];
      if (!rawUrl) { err('specter scan web requires a <url>'); process.exit(1); }
      const url = normaliseUrl(rawUrl);
      let hostname = rawUrl;
      try { hostname = new URL(url).hostname; } catch { /* keep rawUrl */ }
      tasks = [
        { label: 'TLS Check',      script: 'tls_check.py',          args: [hostname] },
        { label: 'HTTP Headers',   script: 'http_headers_check.py',  args: [url] },
      ];
      break;
    }
    case 'host': {
      const host = positionalArgs[0];
      if (!host) { err('specter scan host requires a <hostname>'); process.exit(1); }
      tasks = [
        { label: 'TLS Check',  script: 'tls_check.py',  args: [host] },
        { label: 'Port Probe', script: 'port_probe.py', args: [host, '--ports', 'top100'] },
      ];
      break;
    }
    case 'dir': {
      const dir = positionalArgs[0] || '.';
      tasks = [
        { label: 'Secret Scan', script: 'secret_grep.py', args: [dir] },
      ];
      break;
    }
    case 'all': {
      const rawUrl = positionalArgs[0];
      if (!rawUrl) { err('specter scan all requires a <url>'); process.exit(1); }
      const url = normaliseUrl(rawUrl);
      let hostname = rawUrl;
      try { hostname = new URL(url).hostname; } catch { /* keep rawUrl */ }
      const dir = positionalArgs[1] || '.';
      tasks = [
        { label: 'TLS Check',    script: 'tls_check.py',          args: [hostname] },
        { label: 'HTTP Headers', script: 'http_headers_check.py',  args: [url] },
        { label: 'Port Probe',   script: 'port_probe.py',          args: [hostname, '--ports', 'top100'] },
        { label: 'Secret Scan',  script: 'secret_grep.py',         args: [dir] },
      ];
      break;
    }
    default:
      err(`Unknown scan mode: ${mode}`);
      info('Valid modes: web, host, dir, all');
      process.exit(1);
  }

  const python = process.platform === 'win32' ? 'python' : 'python3';
  console.log(`\n${c.bold}SPECTER Scan${c.reset}  ${c.dim}mode=${mode}${c.reset}\n`);

  const capuredOutputs = [];
  let anyS1 = false;
  let anyError = false;

  for (const task of tasks) {
    const sp = scriptPath(task.script);
    if (!sp) {
      warn(`Script not found, skipping: ${task.script}`);
      continue;
    }

    console.log(`${c.cyan}▶ ${task.label}${c.reset}`);
    const result = spawnSync(python, [sp, ...task.args], { encoding: 'utf8', shell: false });

    if (result.error) {
      err(`${task.label} failed to start: ${result.error.message}`);
      anyError = true;
      continue;
    }

    const stdout = result.stdout || '';
    const stderr = result.stderr || '';
    if (stderr.trim()) process.stderr.write(stderr);
    if (stdout.trim()) {
      process.stdout.write(stdout);
      capuredOutputs.push(stdout);
    }

    // S1 exit code from scripts signals critical findings
    if (result.status === 1 && /\|\s*S1\s*\|/.test(stdout)) anyS1 = true;
    if (result.status !== 0) anyError = true;
  }

  // Write combined output to file
  if (outputFile && capuredOutputs.length > 0) {
    const targetDesc = positionalArgs.join(' ');
    const date = new Date().toISOString().split('T')[0];
    const combined =
      `# SPECTER Scan Report\n\n` +
      `**Mode:** ${mode}  \n**Target:** \`${targetDesc}\`  \n**Date:** ${date}\n\n` +
      capuredOutputs.join('\n\n---\n\n');
    try {
      fs.writeFileSync(outputFile, combined, 'utf8');
      ok(`Report → ${outputFile}`);
    } catch (e) {
      err(`Could not write report: ${e.message}`);
    }
  }

  console.log('');
  if (anyS1) {
    console.log(`${c.red}${c.bold}  ⚠  Critical (S1) findings detected.${c.reset}\n`);
    process.exit(1);
  } else if (anyError) {
    process.exit(1);
  }
}

function cmdHelp() {
  console.log(BANNER);
  console.log(`  ${c.bold}Usage:${c.reset} specter <command> [options]\n`);
  console.log(`  ${c.bold}Commands:${c.reset}`);
  console.log(`    ${c.cyan}init${c.reset}       Initialize SPECTER in current project`);
  console.log(`    ${c.cyan}scan${c.reset}       Multi-check scan (TLS, headers, ports, secrets)`);
  console.log(`    ${c.cyan}run${c.reset}        Run a single security check or tool`);
  console.log(`    ${c.cyan}list${c.reset}       List available security skills`);
  console.log(`    ${c.cyan}doctor${c.reset}     Verify installation health`);
  console.log(`    ${c.cyan}update${c.reset}     Update skills to latest version`);
  console.log(`    ${c.cyan}banner${c.reset}     Replay the animated banner`);
  console.log(`    ${c.cyan}help${c.reset}       Show this help message`);
  console.log('');
  console.log(`  ${c.bold}Init Options:${c.reset}`);
  console.log(`    --agent <name>   Platform: copilot, cursor, windsurf, claude, zed, continue, cline, generic, all`);
  console.log(`                     OR: custom --src <file> --dest <path>  (any agent)`);
  console.log(`    --force          Overwrite existing adapter files`);
  console.log('');
  console.log(`  ${c.bold}List Options:${c.reset}`);
  console.log(`    --agents         Show all supported agent platforms`);
  console.log('');
  console.log(`  ${c.bold}Examples:${c.reset}`);
  console.log(`    ${c.dim}$${c.reset} specter init`);
  console.log(`    ${c.dim}$${c.reset} specter init --agent all`);
  console.log(`    ${c.dim}$${c.reset} specter init --agent zed`);
  console.log(`    ${c.dim}$${c.reset} specter init --agent cline`);
  console.log(`    ${c.dim}$${c.reset} specter init --agent custom --src ./my-adapter.md --dest ./.myagent/specter.md`);
  console.log(`    ${c.dim}$${c.reset} specter list --agents`);
  console.log(`    ${c.dim}$${c.reset} specter scan web https://example.com`);
  console.log(`    ${c.dim}$${c.reset} specter scan host example.com --output report.md`);
  console.log(`    ${c.dim}$${c.reset} specter scan dir ./src`);
  console.log(`    ${c.dim}$${c.reset} specter scan all https://example.com ./src`);
  console.log(`    ${c.dim}$${c.reset} specter run http-headers https://example.com`);
  console.log(`    ${c.dim}$${c.reset} specter run tls example.com`);
  console.log(`    ${c.dim}$${c.reset} specter run ports 10.0.0.1 --ports top1000`);
  console.log(`    ${c.dim}$${c.reset} specter run secrets ./src`);
  console.log(`    ${c.dim}$${c.reset} specter run tool nmap -sV -p 80,443 example.com`);
  console.log(`    ${c.dim}$${c.reset} specter doctor`);
  console.log(`    ${c.dim}$${c.reset} specter update`);
  console.log('');
}

async function cmdBanner() {
  if (process.stdout.isTTY && !process.env.CI) {
    await animatedBanner();
  } else {
    console.log(BANNER);
  }
}

// ══════════════════════════════════════════════════════════════════
//  Main
// ══════════════════════════════════════════════════════════════════

async function main() {
  const { cmd, flags } = parseArgs(process.argv.slice(2));

  switch (cmd) {
    case 'init':     await cmdInit(flags);                  break;
    case 'scan':     cmdScan(process.argv.slice(3));         break;
    case 'run':      cmdRun(process.argv.slice(3));          break;
    case 'list':     cmdList(flags);                              break;
    case 'doctor':   cmdDoctor();            break;
    case 'update':   cmdUpdate();            break;
    case 'banner':   await cmdBanner();      break;
    case 'help':
    case '--help':
    case '-h':       cmdHelp();              break;
    case '--version':
    case '-v':       console.log(`specter v${VERSION}`); break;
    default:
      err(`Unknown command: ${cmd}`);
      cmdHelp();
      process.exit(1);
  }
}

main().catch(() => process.exit(1));
