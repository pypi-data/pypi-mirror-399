#!/bin/bash
# Nexus CLI Installation Script
# Usage: ./install.sh [--plugin] [--dev]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
INSTALL_PLUGIN=false
DEV_MODE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --plugin)
            INSTALL_PLUGIN=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        --help|-h)
            echo "Nexus CLI Installation Script"
            echo ""
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --plugin    Also install Claude Code plugin"
            echo "  --dev       Install in development mode (editable)"
            echo "  --help      Show this help message"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}"
echo "    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗"
echo "    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝"
echo "    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗"
echo "    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║"
echo "    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║"
echo "    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
echo -e "${NC}"
echo "    Knowledge workflow CLI for research, teaching, and writing"
echo ""

# Check Python version
echo -e "${YELLOW}Checking dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}Error: Python 3.10+ is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is required but not installed.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3${NC}"

# Check optional dependencies
echo ""
echo -e "${YELLOW}Checking optional dependencies...${NC}"

if command -v rg &> /dev/null; then
    echo -e "${GREEN}✓ ripgrep (rg)${NC}"
else
    echo -e "${YELLOW}○ ripgrep not found - vault search will use fallback${NC}"
fi

if command -v quarto &> /dev/null; then
    echo -e "${GREEN}✓ quarto${NC}"
else
    echo -e "${YELLOW}○ quarto not found - teaching features limited${NC}"
fi

if [ -f ~/Zotero/zotero.sqlite ]; then
    echo -e "${GREEN}✓ Zotero database${NC}"
else
    echo -e "${YELLOW}○ Zotero database not found - research features limited${NC}"
fi

# Install nexus
echo ""
echo -e "${YELLOW}Installing Nexus CLI...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ "$DEV_MODE" = true ]; then
    echo "Installing in development mode..."
    pip3 install -e . --quiet
else
    pip3 install . --quiet
fi

echo -e "${GREEN}✓ Nexus CLI installed${NC}"

# Create config directory
CONFIG_DIR="$HOME/.config/nexus"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

if [ ! -d "$CONFIG_DIR" ]; then
    echo ""
    echo -e "${YELLOW}Creating configuration...${NC}"
    mkdir -p "$CONFIG_DIR"

    cat > "$CONFIG_FILE" << 'EOF'
# Nexus CLI Configuration
# Edit paths to match your system

vault:
  # Path to your Obsidian vault
  path: ~/Documents/Obsidian
  # Path to templates folder (optional)
  templates: ~/Documents/Obsidian/_SYSTEM/templates

zotero:
  # Path to Zotero database
  database: ~/Zotero/zotero.sqlite
  # Path to Zotero storage
  storage: ~/Zotero/storage

teaching:
  # Directory containing course folders
  courses_dir: ~/projects/teaching

writing:
  # Directory containing manuscript folders
  manuscripts_dir: ~/projects/manuscripts
EOF

    echo -e "${GREEN}✓ Created $CONFIG_FILE${NC}"
    echo -e "${YELLOW}  Please edit this file with your actual paths${NC}"
else
    echo -e "${GREEN}✓ Config directory exists${NC}"
fi

# Install Claude Code plugin
if [ "$INSTALL_PLUGIN" = true ]; then
    echo ""
    echo -e "${YELLOW}Installing Claude Code plugin...${NC}"

    PLUGIN_DIR="$HOME/.claude/plugins/nexus-cli"

    # Create plugins directory if it doesn't exist
    mkdir -p "$HOME/.claude/plugins"

    # Remove existing symlink/directory
    if [ -L "$PLUGIN_DIR" ] || [ -d "$PLUGIN_DIR" ]; then
        rm -rf "$PLUGIN_DIR"
    fi

    # Create symlink
    ln -sf "$SCRIPT_DIR/plugin" "$PLUGIN_DIR"

    echo -e "${GREEN}✓ Plugin installed at $PLUGIN_DIR${NC}"
fi

# Verify installation
echo ""
echo -e "${YELLOW}Verifying installation...${NC}"

if command -v nexus &> /dev/null; then
    VERSION=$(nexus --version 2>/dev/null | head -1)
    echo -e "${GREEN}✓ nexus command available ($VERSION)${NC}"
else
    echo -e "${YELLOW}○ 'nexus' not in PATH - you may need to restart your shell${NC}"
fi

# Done
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit your config: ${BLUE}nexus config --edit${NC}"
echo "  2. Check your setup: ${BLUE}nexus doctor${NC}"
echo "  3. Try a search:     ${BLUE}nexus knowledge vault search \"test\"${NC}"
echo ""

if [ "$INSTALL_PLUGIN" = false ]; then
    echo "To install the Claude Code plugin, run:"
    echo "  ${BLUE}./install.sh --plugin${NC}"
    echo ""
fi
