#!/usr/bin/env node
// ══════════════════════════════════════════════════════════════════
//  SPECTER — The Illusive Security Protocol
//  CLI Tool · by Anvin · Illusive Operations
// ══════════════════════════════════════════════════════════════════
'use strict';

const fs = require('fs');
const path = require('path');

const VERSION = '1.0.0';
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
};

const SEP = '━'.repeat(62);

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

const GLITCH_CHARS = '░▒▓█▄▀■□▪▫╬╫╪═║╡╢╖╗╘╙╔╦╠━┃┏┓┗┛';

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
  'mobile-security-assessment',
  'network-infrastructure-pentest',
  'secure-code-review',
  'security-governance',
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
  ],
  'Reporting': [
    ['evidence-and-reporting',   'Report compilation, redaction, statistics'],
  ],
};

// ══════════════════════════════════════════════════════════════════
//  Utilities
// ══════════════════════════════════════════════════════════════════

function copyRecursiveSync(src, dest) {
  if (!fs.existsSync(src)) return 0;
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
  const hide = '\x1b[?25l';
  const show = '\x1b[?25h';
  const clr = '\x1b[2K';

  stdout.write(hide);
  process.on('SIGINT', () => { stdout.write(show); process.exit(0); });

  try {
    stdout.write('\n');

    // Phase 1: Scanning bar
    const barW = 50;
    const steps = 10;
    for (let i = 0; i <= steps; i++) {
      const filled = Math.round((i / steps) * barW);
      const bar = '▓'.repeat(filled) + '░'.repeat(barW - filled);
      const pct = String(Math.round((i / steps) * 100)).padStart(3);
      stdout.write(`${clr}\r  ${c.cyan}${bar}${c.reset} ${c.dim}${pct}%${c.reset}`);
      await sleep(30);
    }
    await sleep(80);
    stdout.write(`${clr}\r`);

    // Phase 2: Logo with glitch reveal
    console.log(`${c.dim}${SEP}${c.reset}`);
    for (const line of LOGO_LINES) {
      const glitched = line.replace(/[^\s]/g, () =>
        GLITCH_CHARS[Math.floor(Math.random() * GLITCH_CHARS.length)]
      );
      stdout.write(`${clr}\r ${c.dim}${glitched}${c.reset}`);
      await sleep(25);
      stdout.write(`${clr}\r ${c.cyan}${c.bold}${line}${c.reset}\n`);
    }
    console.log(`${c.dim}${SEP}${c.reset}`);

    await sleep(60);
    console.log(`  ${c.bold}The Illusive Security Protocol${c.reset}  ${c.dim}v${VERSION}${c.reset}`);
    console.log(`  ${c.dim}by Anvin · Illusive Operations${c.reset}`);
    console.log('');
  } finally {
    stdout.write(show);
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
  } else if (flags.agent) {
    agentKeys = flags.agent.split(',').map(a => a.trim());
    for (const key of agentKeys) {
      if (!ADAPTERS[key]) {
        err(`Unknown agent: ${key}`);
        info(`Available: ${Object.keys(ADAPTERS).join(', ')}, all`);
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

function cmdList() {
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

function cmdHelp() {
  console.log(BANNER);
  console.log(`  ${c.bold}Usage:${c.reset} specter <command> [options]\n`);
  console.log(`  ${c.bold}Commands:${c.reset}`);
  console.log(`    ${c.cyan}init${c.reset}       Initialize SPECTER in current project`);
  console.log(`    ${c.cyan}list${c.reset}       List available security skills`);
  console.log(`    ${c.cyan}doctor${c.reset}     Verify installation health`);
  console.log(`    ${c.cyan}update${c.reset}     Update skills to latest version`);
  console.log(`    ${c.cyan}banner${c.reset}     Replay the animated banner`);
  console.log(`    ${c.cyan}help${c.reset}       Show this help message`);
  console.log('');
  console.log(`  ${c.bold}Init Options:${c.reset}`);
  console.log(`    --agent <name>   Platform: copilot, cursor, windsurf, claude, generic, all`);
  console.log(`    --force          Overwrite existing adapter files`);
  console.log('');
  console.log(`  ${c.bold}Examples:${c.reset}`);
  console.log(`    ${c.dim}$${c.reset} specter init`);
  console.log(`    ${c.dim}$${c.reset} specter init --agent all`);
  console.log(`    ${c.dim}$${c.reset} specter init --agent copilot,cursor`);
  console.log(`    ${c.dim}$${c.reset} specter init --agent cursor --force`);
  console.log(`    ${c.dim}$${c.reset} specter doctor`);
  console.log(`    ${c.dim}$${c.reset} specter update`);
  console.log(`    ${c.dim}$${c.reset} specter banner`);
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
    case 'init':     await cmdInit(flags);   break;
    case 'list':     cmdList();              break;
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
