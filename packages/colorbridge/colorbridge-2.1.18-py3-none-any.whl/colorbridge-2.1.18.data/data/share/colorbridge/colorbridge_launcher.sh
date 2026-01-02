#!/bin/bash
# ColorBridge 启动脚本 - 自动处理串口权限

# 检查用户是否在 dialout 组中
USER_IN_DIALOUT=false

# 方法1: 使用 groups 命令检查
if groups "$USER" | grep -q dialout; then
    USER_IN_DIALOUT=true
fi

# 方法2: 使用 id 命令检查
if ! $USER_IN_DIALOUT; then
    if id -nG "$USER" | grep -q dialout; then
        USER_IN_DIALOUT=true
    fi
fi

# 如果用户不在 dialout 组中，显示提示信息
if ! $USER_IN_DIALOUT; then
    echo "=========================================="
    echo "⚠️  警告: 当前用户不在 dialout 组中"
    echo "=========================================="
    echo "这可能导致无法访问串口设备！"
    echo ""
    echo "请执行以下命令添加用户到 dialout 组:"
    echo "  sudo usermod -a -G dialout $USER"
    echo ""
    echo "然后注销并重新登录以使权限生效"
    echo ""
    echo "按 Enter 键继续启动程序（可能无法访问串口）..."
    echo "=========================================="
    read -r
fi

# 启动 ColorBridge
python3 -m colorbridge "$@"