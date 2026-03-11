#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════
#  SPECTER — The Illusive Security Protocol
#  Standalone installer (no Node.js required for basic init)
#  by Anvin · Illusive Operations
# ══════════════════════════════════════════════════════════════════
set -euo pipefail

VERSION="1.0.0"
SPECTER_REPO="https://github.com/anvin/specter-kit.git"
SPECTER_DIR=".specter"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

banner() {
  echo ""
  echo -e "${CYAN}${BOLD} ┌──────────────────────────────────────────────────┐${RESET}"
  echo -e "${CYAN}${BOLD} │  S P E C T E R ${RESET}${DIM}v${VERSION}${CYAN}${BOLD}                              │${RESET}"
  echo -e "${CYAN}${BOLD} │  The Illusive Security Protocol                  │${RESET}"
  echo -e "${CYAN}${BOLD} │  ${RESET}${DIM}by Anvin · Illusive Operations${CYAN}${BOLD}                   │${RESET}"
  echo -e "${CYAN}${BOLD} └──────────────────────────────────────────────────┘${RESET}"
  echo ""
}

ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
warn() { echo -e "  ${YELLOW}⚠${RESET} $1"; }
fail() { echo -e "  ${RED}✗${RESET} $1"; }
info() { echo -e "  ${DIM}$1${RESET}"; }

# ── Commands ──────────────────────────────────────────────────────

cmd_init() {
  local project_dir="${1:-.}"
  local agent="${2:-auto}"

  banner
  echo "  Initializing SPECTER..."
  echo ""

  # Determine source: if we're running from inside the specter-kit repo
  local src_dir
  src_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  # Check if source has skill files
  if [[ ! -d "${src_dir}/security-governance" ]]; then
    # Try cloning from git
    if command -v git &>/dev/null; then
      info "Downloading SPECTER from repository..."
      local tmp_dir
      tmp_dir=$(mktemp -d)
      git clone --depth 1 --quiet "${SPECTER_REPO}" "${tmp_dir}" 2>/dev/null || {
        fail "Could not clone SPECTER repository"
        fail "Ensure git is installed and ${SPECTER_REPO} is accessible"
        exit 1
      }
      src_dir="${tmp_dir}"
    else
      fail "Cannot find SPECTER source files and git is not available"
      fail "Install via npm: npm install -g specter-kit && specter init"
      exit 1
    fi
  fi

  local specter_dest="${project_dir}/${SPECTER_DIR}"

  # Create .specter directory
  mkdir -p "${specter_dest}/skills"
  mkdir -p "${specter_dest}/references"
  mkdir -p "${specter_dest}/scripts"

  # Copy skills
  local skill_count=0
  local skill_dirs=(
    active-directory-and-identity-audit
    api-security-review
    bug-bounty-triage
    ci-cd-supply-chain-security
    cloud-config-audit
    container-and-runtime-security
    dependency-and-secret-audit
    evidence-and-reporting
    exploit-validation
    indepth-recon-analysis
    mobile-security-assessment
    network-infrastructure-pentest
    secure-code-review
    security-governance
    threat-modeling
    web-misconfig-review
  )

  for skill in "${skill_dirs[@]}"; do
    if [[ -d "${src_dir}/${skill}" ]]; then
      cp -r "${src_dir}/${skill}" "${specter_dest}/skills/"
      ((skill_count++))
    fi
  done
  ok "Installed ${skill_count} security skills"

  # Copy references
  if [[ -d "${src_dir}/references" ]]; then
    cp -r "${src_dir}/references/"* "${specter_dest}/references/" 2>/dev/null || true
    local ref_count
    ref_count=$(find "${specter_dest}/references" -name "*.md" | wc -l)
    ok "Installed ${ref_count} reference documents"
  fi

  # Copy scripts
  if [[ -d "${src_dir}/scripts" ]]; then
    cp -r "${src_dir}/scripts/"* "${specter_dest}/scripts/" 2>/dev/null || true
    local script_count
    script_count=$(find "${specter_dest}/scripts" -name "*.py" | wc -l)
    ok "Installed ${script_count} helper scripts"
  fi

  # Copy master instructions
  if [[ -f "${src_dir}/specter.md" ]]; then
    cp "${src_dir}/specter.md" "${specter_dest}/specter.md"
    ok "Created master instructions"
  fi

  if [[ -f "${src_dir}/specter.instructions.md" ]]; then
    cp "${src_dir}/specter.instructions.md" "${specter_dest}/specter.instructions.md"
    ok "Created auto-load instructions"
  fi

  echo ""

  # Install agent adapters
  install_adapters "${src_dir}" "${project_dir}" "${agent}"

  # Create .specterrc
  cat > "${project_dir}/.specterrc" <<EOF
{
  "version": "${VERSION}",
  "initialized": "$(date -u +%Y-%m-%d)",
  "installer": "setup.sh"
}
EOF
  ok "Created .specterrc"

  # Update .gitignore
  if [[ -f "${project_dir}/.gitignore" ]]; then
    if ! grep -q ".specterrc" "${project_dir}/.gitignore" 2>/dev/null; then
      echo -e "\n# SPECTER\n.specterrc" >> "${project_dir}/.gitignore"
      ok "Updated .gitignore"
    fi
  fi

  echo ""
  echo -e "  ${GREEN}${BOLD}SPECTER is operational.${RESET}"
  echo -e "  ${DIM}Security governance is now enforced for all agents.${RESET}"
  echo ""
}

install_adapters() {
  local src_dir="$1"
  local project_dir="$2"
  local agent="$3"

  install_one_adapter() {
    local src_file="$1"
    local dest_file="$2"
    local agent_name="$3"

    if [[ ! -f "${src_file}" ]]; then
      return
    fi

    if [[ -f "${dest_file}" ]]; then
      warn "${dest_file#${project_dir}/} exists (skipped)"
      return
    fi

    mkdir -p "$(dirname "${dest_file}")"
    cp "${src_file}" "${dest_file}"
    ok "Created ${dest_file#${project_dir}/} ${DIM}(${agent_name})${RESET}"
  }

  case "${agent}" in
    copilot)
      install_one_adapter "${src_dir}/adapters/copilot.instructions.md" "${project_dir}/.github/copilot-instructions.md" "GitHub Copilot"
      ;;
    cursor)
      install_one_adapter "${src_dir}/adapters/cursor-rules.md" "${project_dir}/.cursor/rules/specter.md" "Cursor"
      ;;
    windsurf)
      install_one_adapter "${src_dir}/adapters/windsurf-rules.md" "${project_dir}/.windsurfrules" "Windsurf"
      ;;
    claude)
      install_one_adapter "${src_dir}/adapters/claude.md" "${project_dir}/CLAUDE.md" "Claude Code"
      ;;
    all)
      install_one_adapter "${src_dir}/adapters/copilot.instructions.md" "${project_dir}/.github/copilot-instructions.md" "GitHub Copilot"
      install_one_adapter "${src_dir}/adapters/cursor-rules.md" "${project_dir}/.cursor/rules/specter.md" "Cursor"
      install_one_adapter "${src_dir}/adapters/windsurf-rules.md" "${project_dir}/.windsurfrules" "Windsurf"
      install_one_adapter "${src_dir}/adapters/claude.md" "${project_dir}/CLAUDE.md" "Claude Code"
      install_one_adapter "${src_dir}/adapters/agents.md" "${project_dir}/AGENTS.md" "Generic"
      ;;
    auto|*)
      # Auto-detect: install copilot + generic by default
      install_one_adapter "${src_dir}/adapters/copilot.instructions.md" "${project_dir}/.github/copilot-instructions.md" "GitHub Copilot"
      install_one_adapter "${src_dir}/adapters/agents.md" "${project_dir}/AGENTS.md" "Generic"

      # Detect cursor
      if [[ -d "${project_dir}/.cursor" ]] || [[ -f "${project_dir}/.cursorrules" ]]; then
        install_one_adapter "${src_dir}/adapters/cursor-rules.md" "${project_dir}/.cursor/rules/specter.md" "Cursor"
      fi

      # Detect windsurf
      if [[ -f "${project_dir}/.windsurfrules" ]]; then
        install_one_adapter "${src_dir}/adapters/windsurf-rules.md" "${project_dir}/.windsurfrules" "Windsurf"
      fi
      ;;
  esac
}

# ── Usage ─────────────────────────────────────────────────────────

usage() {
  banner
  echo "  Usage: ./setup.sh [command] [options]"
  echo ""
  echo "  Commands:"
  echo "    init [path]              Initialize SPECTER in project (default: .)"
  echo "    init [path] --agent X    Specify agent: copilot, cursor, windsurf, claude, all"
  echo ""
  echo "  Examples:"
  echo "    ./setup.sh init"
  echo "    ./setup.sh init /path/to/project"
  echo "    ./setup.sh init . --agent all"
  echo "    curl -fsSL <url>/setup.sh | bash -s -- init"
  echo ""
}

# ── Main ──────────────────────────────────────────────────────────

main() {
  local cmd="${1:-help}"
  shift || true

  case "${cmd}" in
    init)
      local target_dir="."
      local agent="auto"

      while [[ $# -gt 0 ]]; do
        case "$1" in
          --agent) agent="${2:-auto}"; shift 2 ;;
          --*) shift ;;
          *) target_dir="$1"; shift ;;
        esac
      done

      cmd_init "${target_dir}" "${agent}"
      ;;
    help|--help|-h)
      usage
      ;;
    *)
      fail "Unknown command: ${cmd}"
      usage
      exit 1
      ;;
  esac
}

main "$@"
