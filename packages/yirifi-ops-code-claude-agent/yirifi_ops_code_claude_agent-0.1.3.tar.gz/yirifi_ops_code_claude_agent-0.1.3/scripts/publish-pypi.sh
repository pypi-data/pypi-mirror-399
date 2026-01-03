#!/bin/bash
#
# PyPI Publish Manager
# Interactive TUI + CLI for Python package publishing
#
set -e

#######################################
# Colors and Formatting
#######################################
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Unicode symbols
CHECK="✓"
CROSS="✗"
ARROW="▶"
CIRCLE="○"
WARN="⚠"

# Box drawing characters
BOX_TL="╔"
BOX_TR="╗"
BOX_BL="╚"
BOX_BR="╝"
BOX_H="═"
BOX_V="║"
BOX_ML="╠"
BOX_MR="╣"

BOX_TL_S="┌"
BOX_TR_S="┐"
BOX_BL_S="└"
BOX_BR_S="┘"
BOX_H_S="─"
BOX_V_S="│"
BOX_ML_S="├"
BOX_MR_S="┤"

#######################################
# Global State
#######################################
PROJECT_ROOT=""
PROJECT_NAME=""
CURRENT_VERSION=""
GIT_BRANCH=""
GIT_DIRTY=false
GIT_AHEAD=0
PYPI_VERSION=""
PYPI_DATE=""

# CLI/Interactive state
BUMP=""
TEST_PYPI=false
DRY_RUN=false
SKIP_CONFIRM=false
SKIP_CHANGELOG=false
INTERACTIVE_MODE=false

#######################################
# Utility Functions
#######################################
info() { echo -e "${BLUE}==>${NC} $1"; }
success() { echo -e "${GREEN}==>${NC} $1"; }
warn() { echo -e "${YELLOW}WARNING:${NC} $1"; }
error() { echo -e "${RED}ERROR:${NC} $1" >&2; }

clear_screen() {
    printf '\033[2J\033[H'
}

read_single_key() {
    local key
    IFS= read -rsn1 key
    echo "$key"
}

get_terminal_width() {
    tput cols 2>/dev/null || echo 80
}

repeat_char() {
    local char="$1"
    local count="$2"
    printf "%${count}s" | tr ' ' "$char"
}

center_text() {
    local text="$1"
    local width="$2"
    local text_len=${#text}
    local padding=$(( (width - text_len) / 2 ))
    printf "%${padding}s%s%${padding}s" "" "$text" ""
}

#######################################
# Project Discovery
#######################################
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/pyproject.toml" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    if [[ -f "$script_dir/pyproject.toml" ]]; then
        echo "$script_dir"
        return 0
    fi
    return 1
}

get_project_name() {
    python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    print(tomllib.load(f)['project']['name'])
" 2>/dev/null
}

get_project_version() {
    python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    print(tomllib.load(f)['project']['version'])
" 2>/dev/null
}

get_project_description() {
    python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    print(data['project'].get('description', 'No description'))
" 2>/dev/null
}

#######################################
# Git Information
#######################################
refresh_git_status() {
    if command -v git &> /dev/null && [[ -d .git ]]; then
        GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
            GIT_DIRTY=true
        else
            GIT_DIRTY=false
        fi
        GIT_AHEAD=$(git rev-list --count @{upstream}..HEAD 2>/dev/null || echo "0")
    else
        GIT_BRANCH="N/A"
        GIT_DIRTY=false
        GIT_AHEAD=0
    fi
}

get_git_status_display() {
    local status="${GIT_BRANCH}"
    if [[ "$GIT_DIRTY" == true ]]; then
        status="${status} ${DIM}•${NC} ${YELLOW}dirty${NC}"
    else
        status="${status} ${DIM}•${NC} ${GREEN}clean${NC}"
    fi
    if [[ "$GIT_AHEAD" -gt 0 ]]; then
        status="${status} ${DIM}•${NC} ${GIT_AHEAD} ahead"
    fi
    echo -e "$status"
}

#######################################
# PyPI Information
#######################################
refresh_pypi_status() {
    local url="https://pypi.org/pypi/${PROJECT_NAME}/json"
    local response

    # Temporarily disable exit on error for this function
    set +e
    response=$(curl -s --connect-timeout 5 "$url" 2>/dev/null)
    local curl_status=$?
    set -e

    if [[ $curl_status -eq 0 ]] && echo "$response" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        PYPI_VERSION=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])" 2>/dev/null || echo "unknown")
        PYPI_DATE=$(echo "$response" | python3 -c "
import sys,json
from datetime import datetime
try:
    data = json.load(sys.stdin)
    releases = data.get('releases', {})
    version = data['info']['version']
    if version in releases and releases[version]:
        upload_time = releases[version][0].get('upload_time', '')
        if upload_time:
            dt = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
            print(dt.strftime('%Y-%m-%d'))
        else:
            print('')
    else:
        print('')
except:
    print('')
" 2>/dev/null || echo "")
    else
        PYPI_VERSION="not published"
        PYPI_DATE=""
    fi
}

check_pypi_version_exists() {
    local name="$1"
    local version="$2"
    local registry_url="$3"

    local url="${registry_url}/${name}/${version}/json"
    local status
    status=$(curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    [[ "$status" == "200" ]]
}

#######################################
# Version Bumping
#######################################
bump_version() {
    local current="$1"
    local level="$2"

    IFS='.' read -r major minor patch <<< "$current"

    case "$level" in
        major) major=$((major + 1)); minor=0; patch=0 ;;
        minor) minor=$((minor + 1)); patch=0 ;;
        patch) patch=$((patch + 1)) ;;
    esac

    echo "$major.$minor.$patch"
}

apply_version_bump() {
    local new_version="$1"
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "s/^version = \"$CURRENT_VERSION\"/version = \"$new_version\"/" pyproject.toml
    else
        sed -i "s/^version = \"$CURRENT_VERSION\"/version = \"$new_version\"/" pyproject.toml
    fi
}

#######################################
# Interactive Menu - Drawing Functions
#######################################
draw_header() {
    local width=$(get_terminal_width)
    [[ $width -gt 70 ]] && width=70

    echo -e "${CYAN}"
    echo -e "${BOX_TL}$(repeat_char "$BOX_H" $((width-2)))${BOX_TR}"
    printf "${BOX_V}%s${BOX_V}\n" "$(center_text "PyPI Publish Manager" $((width-2)))"
    echo -e "${BOX_ML}$(repeat_char "$BOX_H" $((width-2)))${BOX_MR}"
    echo -e "${NC}"
}

draw_dashboard() {
    local width=$(get_terminal_width)
    [[ $width -gt 70 ]] && width=70

    local git_status=$(get_git_status_display)
    local pypi_display="$PYPI_VERSION"
    [[ -n "$PYPI_DATE" ]] && pypi_display="$PYPI_VERSION ${DIM}($PYPI_DATE)${NC}"

    echo -e "${CYAN}${BOX_V}${NC}  ${BOLD}Package${NC}     $PROJECT_NAME"
    echo -e "${CYAN}${BOX_V}${NC}  ${BOLD}Version${NC}     $CURRENT_VERSION"
    echo -e "${CYAN}${BOX_V}${NC}  ${BOLD}Git${NC}         $git_status"
    echo -e "${CYAN}${BOX_V}${NC}  ${BOLD}PyPI${NC}        $pypi_display"
    echo -e "${CYAN}${BOX_ML}$(repeat_char "$BOX_H" $((width-2)))${BOX_MR}${NC}"
}

draw_main_menu() {
    local width=$(get_terminal_width)
    [[ $width -gt 70 ]] && width=70

    echo -e "${CYAN}${BOX_V}${NC}"
    echo -e "${CYAN}${BOX_V}${NC}  ${BOLD}PUBLISH${NC}                          ${BOLD}INFO${NC}"
    echo -e "${CYAN}${BOX_V}${NC}  ${GREEN}[1]${NC} Publish current ($CURRENT_VERSION)    ${BLUE}[i]${NC} Package info"
    echo -e "${CYAN}${BOX_V}${NC}  ${GREEN}[2]${NC} Bump version & publish       ${BLUE}[l]${NC} View changelog"
    echo -e "${CYAN}${BOX_V}${NC}  ${GREEN}[3]${NC} Publish to TestPyPI          ${BLUE}[p]${NC} Check PyPI versions"
    echo -e "${CYAN}${BOX_V}${NC}  ${GREEN}[4]${NC} Dry run (build only)         ${BLUE}[g]${NC} Git status"
    echo -e "${CYAN}${BOX_V}${NC}"
    echo -e "${CYAN}${BOX_V}${NC}  ${RED}[q]${NC} Quit                          ${DIM}[?] Help${NC}"
    echo -e "${CYAN}${BOX_V}${NC}"
    echo -e "${CYAN}${BOX_BL}$(repeat_char "$BOX_H" $((width-2)))${BOX_BR}${NC}"
    echo ""
    echo -ne "  ${BOLD}Select option:${NC} "
}

draw_bump_menu() {
    local patch_v=$(bump_version "$CURRENT_VERSION" "patch")
    local minor_v=$(bump_version "$CURRENT_VERSION" "minor")
    local major_v=$(bump_version "$CURRENT_VERSION" "major")

    echo ""
    echo -e "  ${BOX_TL_S}$(repeat_char "$BOX_H_S" 40)${BOX_TR_S}"
    echo -e "  ${BOX_V_S}  ${BOLD}Select Version Bump${NC}                  ${BOX_V_S}"
    echo -e "  ${BOX_ML_S}$(repeat_char "$BOX_H_S" 40)${BOX_MR_S}"
    echo -e "  ${BOX_V_S}  Current: ${BOLD}$CURRENT_VERSION${NC}                         ${BOX_V_S}"
    echo -e "  ${BOX_V_S}                                          ${BOX_V_S}"
    echo -e "  ${BOX_V_S}  ${GREEN}[1]${NC} patch ${DIM}→${NC} ${BOLD}$patch_v${NC}  ${DIM}(bug fixes)${NC}       ${BOX_V_S}"
    echo -e "  ${BOX_V_S}  ${GREEN}[2]${NC} minor ${DIM}→${NC} ${BOLD}$minor_v${NC}  ${DIM}(new features)${NC}    ${BOX_V_S}"
    echo -e "  ${BOX_V_S}  ${GREEN}[3]${NC} major ${DIM}→${NC} ${BOLD}$major_v${NC}  ${DIM}(breaking)${NC}        ${BOX_V_S}"
    echo -e "  ${BOX_V_S}                                          ${BOX_V_S}"
    echo -e "  ${BOX_V_S}  ${RED}[b]${NC} Back                                 ${BOX_V_S}"
    echo -e "  ${BOX_BL_S}$(repeat_char "$BOX_H_S" 40)${BOX_BR_S}"
    echo ""
    echo -ne "  ${BOLD}Select:${NC} "
}

draw_preflight() {
    local target_version="$1"
    local registry="$2"
    local all_pass=true

    echo ""
    echo -e "  ${BOX_TL_S}$(repeat_char "$BOX_H_S" 44)${BOX_TR_S}"
    echo -e "  ${BOX_V_S}  ${BOLD}Pre-flight Checklist${NC}                      ${BOX_V_S}"
    echo -e "  ${BOX_ML_S}$(repeat_char "$BOX_H_S" 44)${BOX_MR_S}"

    # Git clean check
    if [[ "$GIT_DIRTY" == true ]]; then
        echo -e "  ${BOX_V_S}  ${YELLOW}${WARN}${NC} Git working tree has changes            ${BOX_V_S}"
        all_pass=false
    else
        echo -e "  ${BOX_V_S}  ${GREEN}${CHECK}${NC} Git working tree clean                  ${BOX_V_S}"
    fi

    # Branch check
    echo -e "  ${BOX_V_S}  ${GREEN}${CHECK}${NC} On branch: ${BOLD}$GIT_BRANCH${NC}                    ${BOX_V_S}"

    # Version exists check
    local pypi_url="https://pypi.org/pypi"
    [[ "$registry" == "testpypi" ]] && pypi_url="https://test.pypi.org/pypi"

    if check_pypi_version_exists "$PROJECT_NAME" "$target_version" "$pypi_url"; then
        echo -e "  ${BOX_V_S}  ${RED}${CROSS}${NC} Version $target_version already on $registry!   ${BOX_V_S}"
        all_pass=false
    else
        echo -e "  ${BOX_V_S}  ${GREEN}${CHECK}${NC} Version $target_version not on $registry        ${BOX_V_S}"
    fi

    # pyproject.toml check
    if python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))" 2>/dev/null; then
        echo -e "  ${BOX_V_S}  ${GREEN}${CHECK}${NC} pyproject.toml valid                    ${BOX_V_S}"
    else
        echo -e "  ${BOX_V_S}  ${RED}${CROSS}${NC} pyproject.toml invalid                  ${BOX_V_S}"
        all_pass=false
    fi

    # Changelog check
    if [[ -f "CHANGELOG.md" ]]; then
        echo -e "  ${BOX_V_S}  ${GREEN}${CHECK}${NC} CHANGELOG.md exists                     ${BOX_V_S}"
    else
        echo -e "  ${BOX_V_S}  ${YELLOW}${WARN}${NC} CHANGELOG.md not found                  ${BOX_V_S}"
    fi

    echo -e "  ${BOX_ML_S}$(repeat_char "$BOX_H_S" 44)${BOX_MR_S}"

    if [[ "$all_pass" == true ]]; then
        echo -e "  ${BOX_V_S}  ${GREEN}[c]${NC} Continue  ${DIM}[e] Edit changelog${NC}  ${RED}[a]${NC} Abort ${BOX_V_S}"
    else
        echo -e "  ${BOX_V_S}  ${YELLOW}[c]${NC} Continue anyway  ${RED}[a]${NC} Abort             ${BOX_V_S}"
    fi
    echo -e "  ${BOX_BL_S}$(repeat_char "$BOX_H_S" 44)${BOX_BR_S}"
    echo ""
    echo -ne "  ${BOLD}Select:${NC} "
}

draw_progress() {
    local step="$1"
    local total_steps=6

    local steps=(
        "Cleaning build artifacts"
        "Installing build tools"
        "Building package"
        "Verifying build"
        "Uploading to registry"
        "Creating git tag"
    )

    echo ""
    echo -e "  ${BOLD}Publishing $PROJECT_NAME $NEW_VERSION → $REGISTRY_NAME${NC}"
    echo ""

    for i in "${!steps[@]}"; do
        local idx=$((i + 1))
        if [[ $idx -lt $step ]]; then
            echo -e "    ${GREEN}${CHECK}${NC} ${steps[$i]}"
        elif [[ $idx -eq $step ]]; then
            echo -e "    ${YELLOW}${ARROW}${NC} ${steps[$i]}..."
        else
            echo -e "    ${DIM}${CIRCLE}${NC} ${DIM}${steps[$i]}${NC}"
        fi
    done
    echo ""
}

#######################################
# Interactive Menu - Info Commands
#######################################
show_package_info() {
    clear_screen
    echo ""
    echo -e "  ${BOLD}Package Information${NC}"
    echo -e "  $(repeat_char "─" 50)"
    echo ""
    echo -e "  Name:        ${BOLD}$PROJECT_NAME${NC}"
    echo -e "  Version:     ${BOLD}$CURRENT_VERSION${NC}"
    echo -e "  Description: $(get_project_description)"
    echo ""
    echo -e "  ${DIM}pyproject.toml location:${NC}"
    echo -e "  ${DIM}$PROJECT_ROOT/pyproject.toml${NC}"
    echo ""
    echo -e "  ${DIM}Press any key to continue...${NC}"
    read_single_key > /dev/null
}

show_changelog() {
    clear_screen
    echo ""
    echo -e "  ${BOLD}Changelog${NC}"
    echo -e "  $(repeat_char "─" 50)"
    echo ""

    if [[ -f "CHANGELOG.md" ]]; then
        head -50 CHANGELOG.md | sed 's/^/  /'
        echo ""
        echo -e "  ${DIM}(showing first 50 lines)${NC}"
    else
        echo -e "  ${YELLOW}No CHANGELOG.md found${NC}"
    fi
    echo ""
    echo -e "  ${DIM}Press any key to continue...${NC}"
    read_single_key > /dev/null
}

show_pypi_versions() {
    clear_screen
    echo ""
    echo -e "  ${BOLD}PyPI Version Status${NC}"
    echo -e "  $(repeat_char "─" 50)"
    echo ""
    echo -e "  Checking PyPI..."

    refresh_pypi_status

    echo -e "\033[1A\033[2K"  # Clear "Checking" line
    echo -e "  ${BOLD}PyPI:${NC}     $PYPI_VERSION ${DIM}${PYPI_DATE}${NC}"
    echo -e "  ${BOLD}Local:${NC}    $CURRENT_VERSION"
    echo ""

    if [[ "$PYPI_VERSION" == "$CURRENT_VERSION" ]]; then
        echo -e "  ${YELLOW}${WARN}${NC} Local version matches PyPI. Bump before publishing."
    elif [[ "$PYPI_VERSION" == "not published" ]]; then
        echo -e "  ${GREEN}${CHECK}${NC} Package not yet on PyPI. Ready to publish!"
    else
        echo -e "  ${GREEN}${CHECK}${NC} Local version differs from PyPI."
    fi
    echo ""
    echo -e "  ${DIM}Press any key to continue...${NC}"
    read_single_key > /dev/null
}

show_git_status() {
    clear_screen
    echo ""
    echo -e "  ${BOLD}Git Status${NC}"
    echo -e "  $(repeat_char "─" 50)"
    echo ""

    refresh_git_status

    echo -e "  Branch:  ${BOLD}$GIT_BRANCH${NC}"
    if [[ "$GIT_DIRTY" == true ]]; then
        echo -e "  Status:  ${YELLOW}Uncommitted changes${NC}"
    else
        echo -e "  Status:  ${GREEN}Clean${NC}"
    fi
    if [[ "$GIT_AHEAD" -gt 0 ]]; then
        echo -e "  Ahead:   ${BOLD}$GIT_AHEAD${NC} commits"
    fi
    echo ""

    if [[ "$GIT_DIRTY" == true ]]; then
        echo -e "  ${DIM}Changed files:${NC}"
        git status --short | head -10 | sed 's/^/  /'
    fi
    echo ""
    echo -e "  ${DIM}Press any key to continue...${NC}"
    read_single_key > /dev/null
}

show_help() {
    clear_screen
    echo ""
    echo -e "  ${BOLD}Help${NC}"
    echo -e "  $(repeat_char "─" 50)"
    echo ""
    echo -e "  ${BOLD}Publish Options:${NC}"
    echo -e "    ${GREEN}1${NC}  Publish current version to PyPI"
    echo -e "    ${GREEN}2${NC}  Select version bump, then publish"
    echo -e "    ${GREEN}3${NC}  Publish to TestPyPI (for testing)"
    echo -e "    ${GREEN}4${NC}  Build and verify without uploading"
    echo ""
    echo -e "  ${BOLD}Info Commands:${NC}"
    echo -e "    ${BLUE}i${NC}  Show package metadata"
    echo -e "    ${BLUE}l${NC}  View changelog"
    echo -e "    ${BLUE}p${NC}  Check PyPI version status"
    echo -e "    ${BLUE}g${NC}  Show git status"
    echo ""
    echo -e "  ${BOLD}CLI Mode:${NC}"
    echo -e "    Run with flags to skip interactive menu:"
    echo -e "    ${DIM}./publish-pypi.sh --bump patch --yes${NC}"
    echo ""
    echo -e "  ${DIM}Press any key to continue...${NC}"
    read_single_key > /dev/null
}

#######################################
# Execute Publish (shared by interactive and CLI)
#######################################
execute_publish() {
    local target_version="${NEW_VERSION:-$CURRENT_VERSION}"
    local registry_name="PyPI"
    local registry_url=""
    local pypi_check_url="https://pypi.org/pypi"

    if [[ "$TEST_PYPI" == true ]]; then
        registry_name="TestPyPI"
        registry_url="https://test.pypi.org/legacy/"
        pypi_check_url="https://test.pypi.org/pypi"
    fi

    REGISTRY_NAME="$registry_name"
    NEW_VERSION="$target_version"

    # Step 1: Clean
    [[ "$INTERACTIVE_MODE" == true ]] && draw_progress 1
    info "Cleaning previous builds..."
    rm -rf dist/ build/ *.egg-info src/*.egg-info

    # Step 2: Install build tools
    [[ "$INTERACTIVE_MODE" == true ]] && draw_progress 2
    info "Installing build tools..."
    if command -v uv &> /dev/null; then
        uv pip install build twine --quiet 2>/dev/null || pip install build twine --quiet
    else
        pip install build twine --quiet
    fi

    # Step 3: Build
    [[ "$INTERACTIVE_MODE" == true ]] && draw_progress 3
    info "Building package..."
    python -m build

    # Step 4: Verify
    [[ "$INTERACTIVE_MODE" == true ]] && draw_progress 4
    info "Verifying build..."
    python -m twine check dist/*

    # Check if version exists
    if check_pypi_version_exists "$PROJECT_NAME" "$target_version" "$pypi_check_url"; then
        error "Version $target_version already exists on $registry_name!"
        return 1
    fi

    # Dry run stops here
    if [[ "$DRY_RUN" == true ]]; then
        echo ""
        echo -e "${BOLD}═══════════════════════════════════════${NC}"
        echo -e "${BOLD}  Dry Run Summary${NC}"
        echo -e "${BOLD}═══════════════════════════════════════${NC}"
        echo -e "  Package:  ${BOLD}$PROJECT_NAME${NC}"
        echo -e "  Version:  ${BOLD}$target_version${NC}"
        echo -e "  Registry: ${BOLD}$registry_name${NC}"
        echo -e "  Files:"
        for f in dist/*; do
            echo -e "    - $(basename "$f")"
        done
        echo -e "${BOLD}═══════════════════════════════════════${NC}"
        echo ""
        success "Dry run complete. No files were uploaded."
        return 0
    fi

    # Confirmation (CLI mode only, interactive already confirmed)
    if [[ "$INTERACTIVE_MODE" == false && "$SKIP_CONFIRM" == false ]]; then
        echo ""
        echo -e "${BOLD}═══════════════════════════════════════${NC}"
        echo -e "${BOLD}  Publish Summary${NC}"
        echo -e "${BOLD}═══════════════════════════════════════${NC}"
        echo -e "  Package:  ${BOLD}$PROJECT_NAME${NC}"
        echo -e "  Version:  ${BOLD}$target_version${NC}"
        echo -e "  Registry: ${BOLD}$registry_name${NC}"
        echo -e "${BOLD}═══════════════════════════════════════${NC}"
        echo ""
        read -p "Publish to $registry_name? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            warn "Aborted."
            return 1
        fi
    fi

    # Step 5: Upload
    [[ "$INTERACTIVE_MODE" == true ]] && draw_progress 5
    info "Uploading to $registry_name..."
    if [[ "$TEST_PYPI" == true ]]; then
        python -m twine upload --repository-url "$registry_url" dist/*
    else
        python -m twine upload dist/*
    fi

    # Step 6: Git tag
    [[ "$INTERACTIVE_MODE" == true ]] && draw_progress 6
    if command -v git &> /dev/null && [[ -d .git ]]; then
        if [[ -n "$BUMP" ]]; then
            if [[ -n "$(git status --porcelain pyproject.toml CHANGELOG.md 2>/dev/null)" ]]; then
                info "Committing version bump..."
                git add pyproject.toml CHANGELOG.md 2>/dev/null || git add pyproject.toml
                git commit -m "chore: release v$target_version"
            fi
        fi

        if ! git tag -l "v$target_version" | grep -q "v$target_version"; then
            info "Creating git tag v$target_version..."
            git tag -a "v$target_version" -m "Release v$target_version"
            success "Created tag v$target_version"
        fi
    fi

    # Success message
    echo ""
    echo -e "${GREEN}${BOLD}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}${BOLD}  Successfully published!${NC}"
    echo -e "${GREEN}${BOLD}═══════════════════════════════════════${NC}"
    echo ""
    if [[ "$TEST_PYPI" == true ]]; then
        echo -e "  Install with:"
        echo -e "  ${BOLD}pip install -i https://test.pypi.org/simple/ $PROJECT_NAME==$target_version${NC}"
        echo ""
        echo -e "  View at:"
        echo -e "  ${BOLD}https://test.pypi.org/project/$PROJECT_NAME/$target_version/${NC}"
    else
        echo -e "  Install with:"
        echo -e "  ${BOLD}pip install $PROJECT_NAME==$target_version${NC}"
        echo ""
        echo -e "  View at:"
        echo -e "  ${BOLD}https://pypi.org/project/$PROJECT_NAME/$target_version/${NC}"
    fi
    echo ""

    if command -v git &> /dev/null && [[ -d .git ]]; then
        warn "Don't forget to push: git push && git push origin v$target_version"
    fi

    return 0
}

#######################################
# Interactive Mode - Main Loop
#######################################
handle_bump_selection() {
    while true; do
        clear_screen
        draw_header
        draw_dashboard
        draw_bump_menu

        local key=$(read_single_key)

        case "$key" in
            1)
                BUMP="patch"
                NEW_VERSION=$(bump_version "$CURRENT_VERSION" "patch")
                return 0
                ;;
            2)
                BUMP="minor"
                NEW_VERSION=$(bump_version "$CURRENT_VERSION" "minor")
                return 0
                ;;
            3)
                BUMP="major"
                NEW_VERSION=$(bump_version "$CURRENT_VERSION" "major")
                return 0
                ;;
            b|B)
                return 1
                ;;
        esac
    done
}

handle_preflight() {
    local target_version="$1"
    local registry="$2"

    while true; do
        clear_screen
        draw_preflight "$target_version" "$registry"

        local key=$(read_single_key)

        case "$key" in
            c|C)
                return 0
                ;;
            e|E)
                if [[ -n "$EDITOR" ]]; then
                    $EDITOR CHANGELOG.md
                else
                    ${VISUAL:-nano} CHANGELOG.md
                fi
                ;;
            a|A)
                return 1
                ;;
        esac
    done
}

do_interactive_publish() {
    local target_version="${NEW_VERSION:-$CURRENT_VERSION}"
    local registry="pypi"
    [[ "$TEST_PYPI" == true ]] && registry="testpypi"

    # Apply version bump if selected
    if [[ -n "$BUMP" ]]; then
        apply_version_bump "$target_version"
        CURRENT_VERSION="$target_version"
    fi

    # Preflight check
    refresh_git_status
    if ! handle_preflight "$target_version" "$registry"; then
        return 1
    fi

    # Execute
    clear_screen
    execute_publish

    echo ""
    echo -e "  ${DIM}Press any key to continue...${NC}"
    read_single_key > /dev/null
}

interactive_main() {
    INTERACTIVE_MODE=true

    # Initial data load
    refresh_git_status
    refresh_pypi_status

    while true; do
        clear_screen
        draw_header
        draw_dashboard
        draw_main_menu

        local key=$(read_single_key)

        case "$key" in
            1)
                # Publish current version
                BUMP=""
                NEW_VERSION="$CURRENT_VERSION"
                TEST_PYPI=false
                DRY_RUN=false
                do_interactive_publish
                refresh_git_status
                refresh_pypi_status
                ;;
            2)
                # Bump and publish
                if [[ "$GIT_DIRTY" == true ]]; then
                    clear_screen
                    echo ""
                    error "Cannot bump version with uncommitted changes."
                    echo -e "  Commit or stash your changes first."
                    echo ""
                    echo -e "  ${DIM}Press any key to continue...${NC}"
                    read_single_key > /dev/null
                else
                    if handle_bump_selection; then
                        TEST_PYPI=false
                        DRY_RUN=false
                        do_interactive_publish
                        refresh_git_status
                        refresh_pypi_status
                        CURRENT_VERSION=$(get_project_version)
                    fi
                fi
                ;;
            3)
                # TestPyPI
                BUMP=""
                NEW_VERSION="$CURRENT_VERSION"
                TEST_PYPI=true
                DRY_RUN=false
                do_interactive_publish
                refresh_git_status
                ;;
            4)
                # Dry run
                BUMP=""
                NEW_VERSION="$CURRENT_VERSION"
                TEST_PYPI=false
                DRY_RUN=true
                clear_screen
                execute_publish
                echo ""
                echo -e "  ${DIM}Press any key to continue...${NC}"
                read_single_key > /dev/null
                ;;
            i|I)
                show_package_info
                ;;
            l|L)
                show_changelog
                ;;
            p|P)
                show_pypi_versions
                ;;
            g|G)
                show_git_status
                ;;
            \?|h|H)
                show_help
                ;;
            q|Q)
                clear_screen
                echo ""
                success "Goodbye!"
                echo ""
                exit 0
                ;;
        esac
    done
}

#######################################
# CLI Mode - Argument Parsing
#######################################
show_cli_help() {
    cat << EOF
${BOLD}PyPI Publish Manager${NC}

Usage: $(basename "$0") [OPTIONS]

Run without options to enter interactive mode.

Options:
  --bump <level>     Bump version before publishing (patch|minor|major)
  --test             Publish to TestPyPI instead of PyPI
  --dry-run          Build and verify but don't upload
  --yes, -y          Skip confirmation prompts
  --no-changelog     Skip changelog prompt
  --help, -h         Show this help message

Examples:
  $(basename "$0")                      # Interactive mode
  $(basename "$0") --bump patch         # Bump 0.1.0 → 0.1.1 and publish
  $(basename "$0") --bump minor --test  # Bump to TestPyPI
  $(basename "$0") --dry-run            # Build only, no upload
  $(basename "$0") --bump major --yes   # Bump, skip confirmation
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --bump)
                BUMP="$2"
                if [[ ! "$BUMP" =~ ^(patch|minor|major)$ ]]; then
                    error "--bump must be: patch, minor, or major"
                    exit 1
                fi
                shift 2
                ;;
            --test)
                TEST_PYPI=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --yes|-y)
                SKIP_CONFIRM=true
                shift
                ;;
            --no-changelog)
                SKIP_CHANGELOG=true
                shift
                ;;
            --help|-h)
                show_cli_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_cli_help
                exit 1
                ;;
        esac
    done
}

cli_main() {
    INTERACTIVE_MODE=false

    info "Project root: $PROJECT_ROOT"
    info "Project: ${BOLD}$PROJECT_NAME${NC}"
    info "Current version: ${BOLD}$CURRENT_VERSION${NC}"

    # Git check
    refresh_git_status
    if [[ "$GIT_DIRTY" == true ]]; then
        if [[ -n "$BUMP" ]]; then
            error "Git working directory is dirty. Commit or stash changes before bumping version."
            git status --short
            exit 1
        else
            warn "Git working directory has uncommitted changes"
            git status --short
            echo ""
        fi
    fi

    # Version bump
    NEW_VERSION="$CURRENT_VERSION"
    if [[ -n "$BUMP" ]]; then
        NEW_VERSION=$(bump_version "$CURRENT_VERSION" "$BUMP")
        info "Bumping version: ${BOLD}$CURRENT_VERSION${NC} → ${BOLD}$NEW_VERSION${NC}"

        if [[ "$DRY_RUN" == false ]]; then
            apply_version_bump "$NEW_VERSION"
            success "Updated pyproject.toml"
        fi
    fi

    # Changelog prompt (CLI mode)
    if [[ "$SKIP_CHANGELOG" == false && "$DRY_RUN" == false && -z "$BUMP" ]]; then
        echo ""
        info "Enter changelog entry for v$NEW_VERSION (press Ctrl+D when done, or Ctrl+C to skip):"
        echo -e "${YELLOW}---${NC}"

        CHANGELOG_ENTRY=""
        if read -r -d '' CHANGELOG_ENTRY; then
            :
        fi

        if [[ -n "$CHANGELOG_ENTRY" ]]; then
            TODAY="$(date +%Y-%m-%d)"
            CHANGELOG_FILE="CHANGELOG.md"

            if [[ -f "$CHANGELOG_FILE" ]]; then
                {
                    echo "## [$NEW_VERSION] - $TODAY"
                    echo ""
                    echo "$CHANGELOG_ENTRY"
                    echo ""
                    cat "$CHANGELOG_FILE"
                } > "${CHANGELOG_FILE}.tmp"
                mv "${CHANGELOG_FILE}.tmp" "$CHANGELOG_FILE"
            else
                {
                    echo "# Changelog"
                    echo ""
                    echo "## [$NEW_VERSION] - $TODAY"
                    echo ""
                    echo "$CHANGELOG_ENTRY"
                    echo ""
                } > "$CHANGELOG_FILE"
            fi
            success "Updated $CHANGELOG_FILE"
        else
            info "No changelog entry provided, skipping"
        fi
    fi

    execute_publish
}

#######################################
# Entry Point
#######################################
main() {
    # Find project root
    PROJECT_ROOT=$(find_project_root) || {
        error "Could not find pyproject.toml"
        exit 1
    }
    cd "$PROJECT_ROOT"

    # Load project info
    PROJECT_NAME=$(get_project_name)
    CURRENT_VERSION=$(get_project_version)

    if [[ -z "$PROJECT_NAME" ]]; then
        error "Could not extract project name from pyproject.toml"
        exit 1
    fi

    if [[ -z "$CURRENT_VERSION" ]]; then
        error "Could not extract version from pyproject.toml"
        exit 1
    fi

    # Decide mode based on arguments
    if [[ $# -eq 0 ]]; then
        interactive_main
    else
        parse_args "$@"
        cli_main
    fi
}

main "$@"
