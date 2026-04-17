from flask import Flask, request, jsonify, render_template
import requests
import subprocess
import re
from datetime import datetime

app = Flask(__name__)

# ========================
# Сканеры безопасности
# ========================

def check_site_availability(url):
    """Проверка доступности сайта"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        r = requests.get(url, timeout=5, headers={'User-Agent': 'CyberScanner/1.0'})
        return r.status_code, url, dict(r.headers)
    except requests.exceptions.Timeout:
        return None, url, None
    except requests.exceptions.ConnectionError:
        return None, url, None
    except Exception as e:
        return None, url, None

def check_security_headers(headers):
    """Проверка security-заголовков"""
    security_checks = {
        'X-Frame-Options': 'Защита от кликджекинга',
        'X-XSS-Protection': 'Защита от XSS',
        'X-Content-Type-Options': 'Защита от MIME-атак',
        'Content-Security-Policy': 'CSP политика безопасности',
        'Strict-Transport-Security': 'HSTS - принудительный HTTPS',
        'Referrer-Policy': 'Контроль реферера'
    }
    
    results = []
    for header, description in security_checks.items():
        if headers and header in headers:
            results.append(f"✅ {description}: {headers[header]}")
        else:
            results.append(f"❌ {description}: отсутствует")
    
    return results

def check_technologies(url):
    """Определение технологий сайта"""
    techs = []
    
    # Проверка сервера
    try:
        r = requests.get(url, timeout=5)
        server = r.headers.get('Server', '')
        if server:
            techs.append(f"Web-сервер: {server}")
        
        # Определение по заголовкам
        if 'X-Powered-By' in r.headers:
            techs.append(f"Технология: {r.headers['X-Powered-By']}")
        
        if 'Set-Cookie' in r.headers:
            if 'PHPSESSID' in str(r.headers):
                techs.append("Язык: PHP")
            elif 'JSESSIONID' in str(r.headers):
                techs.append("Язык: Java (JSP)")
            elif 'ASP.NET' in str(r.headers):
                techs.append("Технология: ASP.NET")
        
        # Поиск в HTML
        if 'wp-content' in r.text or 'wordpress' in r.text.lower():
            techs.append("CMS: WordPress")
        elif 'drupal' in r.text.lower():
            techs.append("CMS: Drupal")
        elif 'joomla' in r.text.lower():
            techs.append("CMS: Joomla")
            
    except:
        pass
    
    return techs if techs else ["Не удалось определить"]

def scan_common_ports(domain):
    """Сканирование популярных портов"""
    domain = re.sub(r'^https?://', '', domain)
    common_ports = {
        21: 'FTP',
        22: 'SSH',
        80: 'HTTP',
        443: 'HTTPS',
        3306: 'MySQL',
        5432: 'PostgreSQL',
        27017: 'MongoDB'
    }
    
    open_ports = []
    for port, service in common_ports.items():
        try:
            # Быстрая проверка порта через subprocess
            result = subprocess.run(
                ['powershell', f"Test-NetConnection {domain} -Port {port} -WarningAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'TcpTestSucceeded : True' in result.stdout:
                open_ports.append(f"🔓 Порт {port} открыт ({service})")
        except:
            pass
    
    return open_ports if open_ports else ["Нет открытых портов"]

def check_ssl_security(url):
    """Базовая проверка SSL/TLS"""
    if url.startswith('https'):
        try:
            import ssl
            import socket
            
            host = re.sub(r'^https://', '', url)
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.connect((host, 443))
                cert = s.getpeercert()
                
                results = []
                # Проверка срока действия
                from datetime import datetime
                expire_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                if expire_date > datetime.now():
                    results.append(f"✅ SSL сертификат действителен до {expire_date.strftime('%Y-%m-%d')}")
                else:
                    results.append("❌ SSL сертификат ПРОСРОЧЕН!")
                
                # Проверка subject
                subject = dict(x[0] for x in cert['subject'])
                results.append(f"🔐 Владелец: {subject.get('commonName', 'Unknown')}")
                
                return results
        except:
            return ["⚠️ Не удалось проверить SSL сертификат"]
    else:
        return ["⚠️ Сайт использует HTTP (незащищённое соединение)"]

def check_info_disclosure(url):
    """Проверка утечки информации"""
    sensitive_paths = [
        '/robots.txt',
        '/.git/config',
        '/.env',
        '/phpinfo.php',
        '/admin',
        '/backup',
        '/config',
        '/wp-config.php.bak'
    ]
    
    found = []
    for path in sensitive_paths:
        try:
            r = requests.get(url + path, timeout=3)
            if r.status_code == 200:
                found.append(f"⚠️ Найден чувствительный путь: {path}")
        except:
            pass
    
    return found if found else ["Нет обнаруженных утечек"]

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cyber Security Scanner</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial;
                margin: 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
            }
            input, button {
                padding: 12px;
                margin: 5px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            input {
                width: 60%;
                font-size: 16px;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: bold;
                padding: 12px 24px;
            }
            button:hover {
                background: #5a67d8;
            }
            .result {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                white-space: pre-wrap;
                font-family: monospace;
                border-left: 4px solid #667eea;
            }
            .scanning {
                text-align: center;
                color: #667eea;
                font-weight: bold;
            }
            .risk-high { color: #e53e3e; font-weight: bold; }
            .risk-medium { color: #ed8936; font-weight: bold; }
            .risk-low { color: #48bb78; font-weight: bold; }
            .section {
                margin-top: 20px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
            .section-title {
                font-weight: bold;
                color: #4a5568;
                margin-bottom: 10px;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Security Scanner</h1>
            <p>Проверка безопасности веб-сайтов</p>
            
            <form id="scanForm">
                <input type="text" id="url" placeholder="https://example.com" required>
                <button type="submit">🚀 Начать сканирование</button>
            </form>
            
            <div id="result" class="result"></div>
        </div>

        <script>
            document.getElementById("scanForm").onsubmit = async (e) => {
                e.preventDefault();
                const url = document.getElementById("url").value;
                const resultDiv = document.getElementById("result");
                resultDiv.innerHTML = '<div class="scanning">🔍 Сканирование... Это может занять до 30 секунд</div>';
                
                try {
                    const res = await fetch("/scan", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ url })
                    });
                    const data = await res.json();
                    
                    if (res.status !== 200) {
                        resultDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                    } else {
                        let riskClass = '';
                        if (data.risk_level.includes('HIGH')) riskClass = 'risk-high';
                        else if (data.risk_level.includes('MEDIUM')) riskClass = 'risk-medium';
                        else riskClass = 'risk-low';
                        
                        resultDiv.innerHTML = `
                            <div class="section">
                                <div class="section-title">📊 ОБЩАЯ ИНФОРМАЦИЯ</div>
                                <strong>🌐 URL:</strong> ${data.url}<br>
                                <strong>📡 HTTP статус:</strong> ${data.status_code}<br>
                                <strong>⚠️ Уровень риска:</strong> <span class="${riskClass}">${data.risk_level}</span>
                            </div>
                            
                            <div class="section">
                                <div class="section-title">🛡️ SECURITY ЗАГОЛОВКИ</div>
                                ${data.security_headers.map(h => h + '<br>').join('')}
                            </div>
                            
                            <div class="section">
                                <div class="section-title">💻 ТЕХНОЛОГИИ САЙТА</div>
                                ${data.technologies.map(t => '🔧 ' + t + '<br>').join('')}
                            </div>
                            
                            <div class="section">
                                <div class="section-title">🔌 ОТКРЫТЫЕ ПОРТЫ</div>
                                ${data.open_ports.map(p => p + '<br>').join('')}
                            </div>
                            
                            <div class="section">
                                <div class="section-title">🔐 SSL/TLS БЕЗОПАСНОСТЬ</div>
                                ${data.ssl_info.map(s => s + '<br>').join('')}
                            </div>
                            
                            <div class="section">
                                <div class="section-title">⚠️ ПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ</div>
                                ${data.info_disclosure.map(i => i + '<br>').join('')}
                            </div>
                        `;
                    }
                } catch (err) {
                    resultDiv.innerHTML = `<div class="error">❌ Ошибка: ${err.message}</div>`;
                }
            };
        </script>
    </body>
    </html>
    '''

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    # Проверка доступности
    status_code, working_url, headers = check_site_availability(url)
    if status_code is None:
        return jsonify({"error": "Сайт недоступен или не отвечает"}), 400
    
    # Сканирование
    print(f"🔍 Scanning {working_url}...")
    
    security_headers = check_security_headers(headers)
    technologies = check_technologies(working_url)
    open_ports = scan_common_ports(working_url)
    ssl_info = check_ssl_security(working_url)
    info_disclosure = check_info_disclosure(working_url)
    
    # Оценка риска
    risk_level = "LOW 🟢"
    risk_score = 0
    
    # Подсчёт проблем
    missing_headers = [h for h in security_headers if h.startswith('❌')]
    risk_score += len(missing_headers)
    
    if len(open_ports) > 1:  # если есть открытые порты кроме HTTP/HTTPS
        risk_score += len(open_ports)
    
    if info_disclosure and info_disclosure[0] != "Нет обнаруженных утечек":
        risk_score += len(info_disclosure)
    
    if ssl_info and "просрочен" in str(ssl_info):
        risk_score += 3
    
    if risk_score >= 5:
        risk_level = "HIGH 🔴"
    elif risk_score >= 2:
        risk_level = "MEDIUM 🟡"
    
    return jsonify({
        "url": working_url,
        "status_code": status_code,
        "security_headers": security_headers,
        "technologies": technologies,
        "open_ports": open_ports,
        "ssl_info": ssl_info,
        "info_disclosure": info_disclosure,
        "risk_level": risk_level,
        "risk_score": risk_score
    })

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    ║   🚀 SECURITY SCANNER ЗАПУЩЕН!       ║
    ║   📱 Открой: http://localhost:5000    ║
    ║   🔍 Сканирует:                      ║
    ║   • Заголовки безопасности          ║
    ║   • Технологии сайта                ║
    ║   • Открытые порты                  ║
    ║   • SSL сертификаты                 ║
    ║   • Утечки информации               ║
    ╚═══════════════════════════════════════╝
    """)
    app.run(debug=True, host='127.0.0.1', port=5000)