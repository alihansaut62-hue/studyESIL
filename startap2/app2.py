from flask import Flask, request, jsonify, render_template_string  # ← добавил render_template_string
import requests
import subprocess
import re
import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)

# ========================
# Расширенный сканер безопасности
# ========================

def check_site_availability(url):
    """Проверка доступности сайта"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        r = requests.get(url, timeout=5, headers={'User-Agent': 'CyberScanner/1.0'}, allow_redirects=True)
        return r.status_code, url, dict(r.headers), r.text[:5000]  # сохраняем часть HTML
    except Exception as e:
        return None, url, None, None

def analyze_security_headers(headers):
    """Анализ security-заголовков с рекомендациями"""
    results = []
    
    checks = {
        'X-Frame-Options': {
            'name': 'Защита от кликджекинга',
            'risk': 'Злоумышленник может встроить ваш сайт в iframe и обманом заставить пользователя кликнуть на скрытые элементы',
            'exploit': 'Атака Clickjacking - подмена кнопок, кража данных при клике',
            'fix': 'Добавьте заголовок: X-Frame-Options: DENY или SAMEORIGIN',
            'critical': True
        },
        'X-XSS-Protection': {
            'name': 'Защита от XSS атак',
            'risk': 'Возможны межсайтовые скриптовые атаки, кража cookies, сессий',
            'exploit': 'Злоумышленник может внедрить свой скрипт на страницу и украсть данные пользователя',
            'fix': 'Добавьте заголовок: X-XSS-Protection: 1; mode=block',
            'critical': True
        },
        'X-Content-Type-Options': {
            'name': 'Защита от MIME-атак',
            'risk': 'Браузер может неправильно интерпретировать файлы, возможна XSS',
            'exploit': 'Загрузка вредоносных файлов под видом изображений',
            'fix': 'Добавьте заголовок: X-Content-Type-Options: nosniff',
            'critical': True
        },
        'Content-Security-Policy': {
            'name': 'CSP политика',
            'risk': 'Нет контроля над загружаемыми ресурсами, возможна XSS',
            'exploit': 'Атакующий может загрузить любой скрипт с любого домена',
            'fix': 'Добавьте: Content-Security-Policy: default-src "self"',
            'critical': False
        },
        'Strict-Transport-Security': {
            'name': 'HSTS принудительный HTTPS',
            'risk': 'Возможна атака man-in-the-middle, перехват трафика',
            'exploit': 'Злоумышленник может понизить соединение до HTTP и перехватить данные',
            'fix': 'Добавьте: Strict-Transport-Security: max-age=31536000; includeSubDomains',
            'critical': True
        },
        'Referrer-Policy': {
            'name': 'Контроль реферера',
            'risk': 'Утечка URL и параметров на сторонние сайты',
            'exploit': 'Передача токенов, ключей API в Referer заголовке',
            'fix': 'Добавьте: Referrer-Policy: strict-origin-when-cross-origin',
            'critical': False
        }
    }
    
    for header, info in checks.items():
        if headers and header in headers:
            results.append({
                'status': '✅',
                'name': info['name'],
                'value': headers[header],
                'message': f'Защита активна: {headers[header]}'
            })
        else:
            results.append({
                'status': '❌',
                'name': info['name'],
                'risk': info['risk'],
                'exploit': info['exploit'],
                'fix': info['fix'],
                'critical': info['critical']
            })
    
    return results

def analyze_technologies(url, html):
    """Анализ технологий с уязвимостями"""
    results = []
    
    # Определяем технологии
    techs = {}
    
    try:
        r = requests.get(url, timeout=5)
        headers = r.headers
        
        # Сервер
        server = headers.get('Server', '')
        if server:
            techs['web_server'] = server
            if 'nginx/1.0' in server.lower() or 'apache/2.2' in server.lower():
                results.append({
                    'type': '⚠️ УСТАРЕВШАЯ ВЕРСИЯ',
                    'name': f'Веб-сервер: {server}',
                    'risk': 'Известные уязвимости в старой версии',
                    'exploit': 'Атакующий может использовать публичные эксплойты',
                    'fix': f'Обновите {server} до последней версии'
                })
        
        # Язык программирования
        if 'PHPSESSID' in str(headers):
            techs['language'] = 'PHP'
            results.append({
                'type': '📝 ИНФОРМАЦИЯ',
                'name': 'Язык программирования: PHP',
                'risk': 'Может быть уязвим к типичным PHP атакам',
                'exploit': 'SQL инъекции, LFI, RFI, загрузка файлов',
                'fix': 'Используйте подготовленные запросы, валидацию ввода'
            })
        elif 'JSESSIONID' in str(headers):
            techs['language'] = 'Java'
            results.append({
                'type': '📝 ИНФОРМАЦИЯ',
                'name': 'Язык программирования: Java',
                'risk': 'Возможны уязвимости в фреймворках',
                'exploit': 'Deserialization атаки, EL инъекции',
                'fix': 'Обновляйте зависимости, используйте безопасные настройки'
            })
        
        # CMS определение
        if html:
            html_lower = html.lower()
            if 'wp-content' in html_lower or 'wordpress' in html_lower:
                techs['cms'] = 'WordPress'
                results.append({
                    'type': '⚠️ CMS: WordPress',
                    'name': 'WordPress обнаружен',
                    'risk': 'Плагины, темы, ядро могут иметь уязвимости',
                    'exploit': 'Атаки на плагины, брутфорс wp-admin, утечки данных',
                    'fix': 'Обновляйте WP, плагины, темы. Используйте WAF'
                })
            elif 'drupal' in html_lower:
                techs['cms'] = 'Drupal'
                results.append({
                    'type': '⚠️ CMS: Drupal',
                    'name': 'Drupal обнаружен',
                    'risk': 'Критические уязвимости (Drupalgeddon)',
                    'exploit': 'RCE (Remote Code Execution) через уязвимости',
                    'fix': 'Срочно обновитесь до последней версии'
                })
        
    except:
        pass
    
    if not results:
        results.append({
            'type': 'ℹ️ ИНФОРМАЦИЯ',
            'name': 'Технологии не определены',
            'risk': 'Неизвестно',
            'exploit': 'Требуется более глубокий анализ',
            'fix': 'Используйте специализированные инструменты'
        })
    
    return results

def scan_ports_with_analysis(domain):
    """Сканирование портов с анализом рисков"""
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.split('/')[0]
    
    ports_to_scan = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        80: 'HTTP',
        443: 'HTTPS',
        3306: 'MySQL',
        5432: 'PostgreSQL',
        27017: 'MongoDB',
        6379: 'Redis',
        9200: 'Elasticsearch',
        8080: 'HTTP-Proxy',
        8443: 'HTTPS-Alt'
    }
    
    results = []
    
    for port, service in ports_to_scan.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((domain, port))
            sock.close()
            
            if result == 0:
                risk_info = {
                    '21': 'Незащищённый FTP - перехват паролей, загрузка вредоносных файлов',
                    '22': 'SSH доступ - возможен брутфорс, старая версия может быть уязвима',
                    '23': 'Telnet - ПЕРЕДАЧА ПАРОЛЕЙ В ОТКРЫТОМ ВИДЕ!',
                    '3306': 'MySQL - доступ к БД, кража данных, изменение записей',
                    '5432': 'PostgreSQL - утечка данных, выполнение запросов',
                    '27017': 'MongoDB - доступ ко всем коллекциям без аутентификации',
                    '6379': 'Redis - кража кэша, выполнение команд',
                    '9200': 'Elasticsearch - утечка данных, возможно выполнение запросов'
                }
                
                exploit_info = {
                    '21': 'Атакующий может подключиться к FTP и загрузить веб-шелл',
                    '22': 'Брутфорс SSH паролей, использование уязвимостей версии',
                    '23': 'Сниффинг трафика - полный контроль над сервером',
                    '3306': 'Подключение к БД через mysql клиент, дамп всех таблиц',
                    '5432': 'Дамп данных, изменение записей, выполнение команд через CVE',
                    '27017': 'NoSQL инъекции, дамп всех документов',
                    '6379': 'Выполнение Lua скриптов, кража сессий',
                    '9200': 'Чтение всех индексов, удаление данных через REST API'
                }
                
                results.append({
                    'port': port,
                    'service': service,
                    'status': '🔓 ОТКРЫТ',
                    'risk': risk_info.get(str(port), 'Открытый порт - потенциальная угроза'),
                    'exploit': exploit_info.get(str(port), 'Дополнительное исследование необходимо'),
                    'fix': f'Закройте порт {port} через firewall, используйте VPN/SSH туннели'
                })
        except:
            pass
    
    if not results:
        results.append({
            'port': None,
            'service': None,
            'status': '✅ БЕЗОПАСНО',
            'risk': 'Критические порты закрыты',
            'exploit': 'Внешние атаки через сеть затруднены',
            'fix': 'Продолжайте поддерживать безопасную конфигурацию'
        })
    
    return results

def analyze_ssl_security(url):
    """Расширенный анализ SSL/TLS"""
    results = []
    
    if not url.startswith('https'):
        results.append({
            'status': '❌ КРИТИЧНО',
            'name': 'HTTPS не используется',
            'risk': 'Все данные передаются в открытом виде',
            'exploit': 'Атака Man-in-the-Middle - перехват паролей, cookies, личных данных',
            'fix': 'Установите SSL сертификат, настройте редирект с HTTP на HTTPS'
        })
        return results
    
    host = re.sub(r'^https://', '', url)
    host = host.split('/')[0]
    
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(5)
            s.connect((host, 443))
            cert = s.getpeercert()
            
            # Проверка срока действия
            expire_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_left = (expire_date - datetime.now()).days
            
            if days_left < 0:
                results.append({
                    'status': '❌ КРИТИЧНО',
                    'name': 'SSL сертификат ПРОСРОЧЕН',
                    'risk': 'Браузер показывает ошибку, соединение небезопасно',
                    'exploit': 'Атака MITM возможна, данные не шифруются',
                    'fix': 'Обновите SSL сертификат немедленно'
                })
            elif days_left < 30:
                results.append({
                    'status': '⚠️ ВНИМАНИЕ',
                    'name': f'SSL сертификат истекает через {days_left} дней',
                    'risk': 'Скоро станет недействительным',
                    'exploit': 'После истечения - перехват трафика',
                    'fix': 'Запланируйте обновление сертификата'
                })
            else:
                results.append({
                    'status': '✅ ХОРОШО',
                    'name': f'SSL сертификат действителен до {expire_date.strftime("%Y-%m-%d")}',
                    'risk': 'Низкий',
                    'exploit': 'Требуются другие векторы атак',
                    'fix': 'Продолжайте своевременное обновление'
                })
            
            # Информация о владельце
            subject = dict(x[0] for x in cert['subject'])
            results.append({
                'status': 'ℹ️ ИНФО',
                'name': f'Владелец: {subject.get("commonName", "Unknown")}',
                'risk': 'Проверьте, что сайт действительно принадлежит этой организации',
                'exploit': 'Фишинговые сайты могут иметь поддельные сертификаты',
                'fix': 'Проверяйте информацию о сертификате в браузере'
            })
            
    except Exception as e:
        results.append({
            'status': '❌ ОШИБКА',
            'name': 'Не удалось проверить SSL',
            'risk': 'Возможно, порт 443 закрыт или проблемы с сертификатом',
            'exploit': 'Соединение может быть небезопасным',
            'fix': 'Проверьте настройки SSL/TLS на сервере'
        })
    
    return results

def analyze_info_disclosure(url):
    """Поиск утечек информации с анализом"""
    sensitive_paths = {
        '/robots.txt': 'Скрытые директории, запрещённые для индексации',
        '/.git/config': 'Исходный код, пароли, токены в Git репозитории',
        '/.env': 'Переменные окружения, пароли БД, API ключи',
        '/phpinfo.php': 'Полная информация о PHP, сервере, расширениях',
        '/backup.zip': 'Резервные копии с исходным кодом и данными',
        '/admin': 'Панель администратора - цель для брутфорса',
        '/wp-config.php.bak': 'Пароли от БД, соли WordPress',
        '/config.json': 'Конфигурационные файлы с секретами',
        '/.htaccess': 'Конфигурация Apache - обход ограничений',
        '/database.sql': 'Дамп базы данных со всеми записями'
    }
    
    results = []
    
    for path, risk_desc in sensitive_paths.items():
        try:
            test_url = url.rstrip('/') + path
            r = requests.get(test_url, timeout=3, allow_redirects=False)
            
            if r.status_code == 200:
                results.append({
                    'path': path,
                    'status': '⚠️ УТЕЧКА',
                    'risk': risk_desc,
                    'exploit': f'Атакующий может скачать файл {path} и получить конфиденциальную информацию',
                    'fix': f'Удалите {path} или ограничьте доступ через .htaccess/WAF'
                })
            elif r.status_code == 403:
                results.append({
                    'path': path,
                    'status': '🔒 ЗАЩИЩЕН',
                    'risk': 'Доступ запрещён, но директория существует',
                    'exploit': 'Может быть обойдено при определённых условиях',
                    'fix': 'Проверьте, что доступ действительно ограничен правильно'
                })
        except:
            pass
    
    if not results:
        results.append({
            'path': None,
            'status': '✅ ХОРОШО',
            'risk': 'Чувствительные пути не обнаружены',
            'exploit': 'Требуются другие методы разведки',
            'fix': 'Продолжайте мониторить появление новых файлов'
        })
    
    return results

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    # Проверка доступности
    status_code, working_url, headers, html = check_site_availability(url)
    if status_code is None:
        return jsonify({"error": "Сайт недоступен или не отвечает"}), 400
    
    print(f"🔍 Сканирование {working_url}...")
    
    # Все проверки
    security_headers = analyze_security_headers(headers)
    technologies = analyze_technologies(working_url, html)
    
    domain = re.sub(r'^https?://', '', working_url)
    ports = scan_ports_with_analysis(domain)
    ssl_security = analyze_ssl_security(working_url)
    info_disclosure = analyze_info_disclosure(working_url)
    
    # Подсчёт критических проблем
    critical_count = sum(1 for h in security_headers if h.get('critical') and h.get('status') == '❌')
    critical_count += sum(1 for s in ssl_security if 'КРИТИЧНО' in s.get('status', ''))
    critical_count += sum(1 for p in ports if p.get('port') not in [80, 443])
    critical_count += sum(1 for i in info_disclosure if i.get('status') == '⚠️ УТЕЧКА')
    
    if critical_count >= 3:
        risk_level = "КРИТИЧЕСКИЙ 🔴"
    elif critical_count >= 1:
        risk_level = "ВЫСОКИЙ 🟠"
    elif len([h for h in security_headers if h.get('status') == '❌']) > 3:
        risk_level = "СРЕДНИЙ 🟡"
    else:
        risk_level = "НИЗКИЙ 🟢"
    
    return jsonify({
        "url": working_url,
        "status_code": status_code,
        "risk_level": risk_level,
        "critical_count": critical_count,
        "security_headers": security_headers,
        "technologies": technologies,
        "ports": ports,
        "ssl_security": ssl_security,
        "info_disclosure": info_disclosure
    })

# HTML шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Advanced Security Scanner</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        h1 { color: #00d9ff; margin-bottom: 10px; }
        .subtitle { color: #ccc; }
        .scan-box {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        input {
            width: 70%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .result {
            background: white;
            border-radius: 15px;
            padding: 20px;
            display: none;
        }
        .risk-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 10px 0;
        }
        .section {
            margin-bottom: 25px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }
        .section-title {
            background: #f5f5f5;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 18px;
            cursor: pointer;
        }
        .section-content { padding: 20px; display: block; }
        .vuln-item {
            background: #fafafa;
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        .vuln-critical { border-left-color: #e74c3c; background: #fee; }
        .vuln-high { border-left-color: #e67e22; background: #fff3e0; }
        .vuln-medium { border-left-color: #f39c12; background: #fff8e1; }
        .vuln-low { border-left-color: #27ae60; background: #e8f8f5; }
        .vuln-good { border-left-color: #3498db; background: #e8f4fd; }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }
        .badge-critical { background: #e74c3c; color: white; }
        .badge-high { background: #e67e22; color: white; }
        .badge-medium { background: #f39c12; color: white; }
        .badge-low { background: #27ae60; color: white; }
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 18px;
            color: #667eea;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🛡️ Advanced Security Scanner</h1>
        <p class="subtitle">Анализ безопасности с эксплойт-векторами и рекомендациями</p>
    </div>
    
    <div class="scan-box">
        <form id="scanForm">
            <input type="text" id="url" placeholder="https://example.com" required>
            <button type="submit">🚀 Начать сканирование</button>
        </form>
    </div>
    
    <div id="result" class="result"></div>
</div>

<script>
document.getElementById("scanForm").onsubmit = async (e) => {
    e.preventDefault();
    const url = document.getElementById("url").value;
    const resultDiv = document.getElementById("result");
    resultDiv.style.display = "block";
    resultDiv.innerHTML = '<div class="loading">🔍 Сканирование... анализ безопасности может занять до 30 секунд</div>';
    
    try {
        const res = await fetch("/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });
        const data = await res.json();
        
        if (res.status !== 200) {
            resultDiv.innerHTML = `<div class="loading" style="color: red;">❌ ${data.error}</div>`;
            return;
        }
        
        let riskClass = '';
        if (data.risk_level.includes('КРИТИЧЕСКИЙ')) riskClass = 'badge-critical';
        else if (data.risk_level.includes('ВЫСОКИЙ')) riskClass = 'badge-high';
        else if (data.risk_level.includes('СРЕДНИЙ')) riskClass = 'badge-medium';
        else riskClass = 'badge-low';
        
        let html = `
            <div style="margin-bottom: 20px;">
                <h2>📊 Результаты сканирования: ${data.url}</h2>
                <p>HTTP статус: ${data.status_code}</p>
                <p><span class="badge ${riskClass}">${data.risk_level}</span> Уровень риска (${data.critical_count} критических проблем)</p>
            </div>
        `;
        
        // Security Headers
        html += `<div class="section"><div class="section-title">🛡️ Security Заголовки</div><div class="section-content">`;
        for (const h of data.security_headers) {
            const vulnClass = h.status === '❌' ? 'vuln-critical' : 'vuln-good';
            html += `<div class="vuln-item ${vulnClass}">
                        <strong>${h.status} ${h.name}</strong><br>`;
            if (h.value) {
                html += `<span style="color: #666;">Значение: ${h.value}</span><br>`;
            }
            if (h.risk) {
                html += `<span style="color: #e74c3c;">🎯 Риск: ${h.risk}</span><br>
                         <span style="color: #e67e22;">💀 Эксплойт: ${h.exploit}</span><br>
                         <span style="color: #27ae60;">🔧 Исправление: ${h.fix}</span>`;
            } else {
                html += `<span style="color: #27ae60;">✅ ${h.message}</span>`;
            }
            html += `</div>`;
        }
        html += `</div></div>`;
        
        // Technologies
        html += `<div class="section"><div class="section-title">💻 Технологии и уязвимости</div><div class="section-content">`;
        for (const t of data.technologies) {
            const vulnClass = t.type.includes('УСТАРЕВШАЯ') ? 'vuln-high' : 'vuln-good';
            html += `<div class="vuln-item ${vulnClass}">
                        <strong>${t.type || 'ℹ️'} ${t.name}</strong><br>
                        <span style="color: #e74c3c;">🎯 Риск: ${t.risk}</span><br>
                        <span style="color: #e67e22;">💀 Эксплойт: ${t.exploit}</span><br>
                        <span style="color: #27ae60;">🔧 Исправление: ${t.fix}</span>
                    </div>`;
        }
        html += `</div></div>`;
        
        // Ports
        html += `<div class="section"><div class="section-title">🔌 Открытые порты</div><div class="section-content">`;
        for (const p of data.ports) {
            const vulnClass = p.status === '🔓 ОТКРЫТ' ? 'vuln-critical' : 'vuln-good';
            html += `<div class="vuln-item ${vulnClass}">
                        <strong>${p.status} ${p.port ? `Порт ${p.port} (${p.service})` : p.service || 'Порты'}</strong><br>`;
            if (p.risk) {
                html += `<span style="color: #e74c3c;">🎯 Риск: ${p.risk}</span><br>
                         <span style="color: #e67e22;">💀 Эксплойт: ${p.exploit}</span><br>
                         <span style="color: #27ae60;">🔧 Исправление: ${p.fix}</span>`;
            } else {
                html += `<span style="color: #27ae60;">✅ ${p.risk || 'Безопасно'}</span>`;
            }
            html += `</div>`;
        }
        html += `</div></div>`;
        
        // SSL
        html += `<div class="section"><div class="section-title">🔐 SSL/TLS Безопасность</div><div class="section-content">`;
        for (const s of data.ssl_security) {
            const vulnClass = s.status.includes('КРИТИЧНО') ? 'vuln-critical' : (s.status.includes('ВНИМАНИЕ') ? 'vuln-medium' : 'vuln-good');
            html += `<div class="vuln-item ${vulnClass}">
                        <strong>${s.status} ${s.name}</strong><br>
                        <span style="color: #e74c3c;">🎯 Риск: ${s.risk}</span><br>
                        <span style="color: #e67e22;">💀 Эксплойт: ${s.exploit}</span><br>
                        <span style="color: #27ae60;">🔧 Исправление: ${s.fix}</span>
                    </div>`;
        }
        html += `</div></div>`;
        
        // Info Disclosure
        html += `<div class="section"><div class="section-title">⚠️ Утечки информации</div><div class="section-content">`;
        for (const i of data.info_disclosure) {
            const vulnClass = i.status === '⚠️ УТЕЧКА' ? 'vuln-critical' : 'vuln-good';
            html += `<div class="vuln-item ${vulnClass}">
                        <strong>${i.status} ${i.path || 'Проверка'}</strong><br>
                        <span style="color: #e74c3c;">🎯 Риск: ${i.risk}</span><br>
                        <span style="color: #e67e22;">💀 Эксплойт: ${i.exploit}</span><br>
                        <span style="color: #27ae60;">🔧 Исправление: ${i.fix}</span>
                    </div>`;
        }
        html += `</div></div>`;
        
        resultDiv.innerHTML = html;
        
        // Add toggle functionality for sections
        document.querySelectorAll('.section-title').forEach(title => {
            title.style.cursor = 'pointer';
            title.onclick = () => {
                const content = title.nextElementSibling;
                content.style.display = content.style.display === 'none' ? 'block' : 'none';
            };
        });
        
    } catch (err) {
        resultDiv.innerHTML = `<div class="loading" style="color: red;">❌ Ошибка: ${err.message}</div>`;
    }
};
</script>
</body>
</html>
'''

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     🚀 ADVANCED SECURITY SCANNER ЗАПУЩЕН!          ║
    ║     📱 Открой: http://localhost:5000               ║
    ║                                                    ║
    ║     🔍 Что анализирует:                           ║
    ║     • Security заголовки с векторами атак         ║
    ║     • Технологии и их уязвимости                  ║
    ║     • Открытые порты и что через них можно сделать║
    ║     • SSL/TLS с эксплойтами                       ║
    ║     • Утечки информации                           ║
    ║                                                    ║
    ║     💀 Показывает РИСК и ЭКСПЛОЙТ для каждой      ║
    ║     🔧 Даёт рекомендации по ИСПРАВЛЕНИЮ           ║
    ╚══════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='127.0.0.1', port=5000)