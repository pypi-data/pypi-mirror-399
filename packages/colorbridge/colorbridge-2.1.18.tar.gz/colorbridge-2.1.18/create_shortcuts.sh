#!/bin/bash
# ColorBridge Linux 快捷方式创建脚本
# 用法: ./create_shortcuts.sh

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_info "开始创建ColorBridge桌面快捷方式..."

# 检查.desktop文件
if [ ! -f "colorbridge.desktop" ]; then
    log_warning "未找到colorbridge.desktop文件"
    exit 1
fi

# 创建用户applications目录
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"

# 复制到applications目录
cp "colorbridge.desktop" "$APPS_DIR/"
chmod +x "$APPS_DIR/colorbridge.desktop"
log_success "应用菜单快捷方式创建成功: $APPS_DIR/colorbridge.desktop"

# 创建桌面快捷方式
if [ -d "$HOME/Desktop" ]; then
    cp "colorbridge.desktop" "$HOME/Desktop/ColorBridge.desktop"
    chmod +x "$HOME/Desktop/ColorBridge.desktop"
    log_success "桌面快捷方式创建成功: $HOME/Desktop/ColorBridge.desktop"
else
    log_warning "桌面目录不存在，跳过桌面快捷方式创建"
fi

log_info "✅ 快捷方式创建完成！"
log_info "💡 可以在应用菜单中找到ColorBridge"