from flask import Flask, request, jsonify, render_template_string
import requests
import re
import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse
import json
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)

# Хранилище для истории сканов (в реальном приложении используйте БД)
scan_history = {}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Scanner Dashboard</title>
    <style>
        :root {
            --bg: #08111f;
            --bg-soft: rgba(13, 26, 45, 0.78);
            --card: rgba(10, 20, 37, 0.9);
            --line: rgba(160, 199, 255, 0.16);
            --text: #eef4ff;
            --muted: #9eb0ca;
            --accent: #72f2c0;
            --accent-2: #6eb8ff;
            --danger: #ff6f7d;
            --warn: #ffb961;
            --ok: #7af0a2;
            --shadow: 0 30px 70px rgba(0, 0, 0, 0.35);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: "Segoe UI", "Trebuchet MS", sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(110, 184, 255, 0.22), transparent 30%),
                radial-gradient(circle at top right, rgba(114, 242, 192, 0.12), transparent 25%),
                linear-gradient(160deg, #050b14 0%, #08111f 52%, #09182d 100%);
        }

        .shell {
            width: min(1180px, calc(100% - 32px));
            margin: 32px auto;
        }

        .hero {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 24px;
            margin-bottom: 24px;
        }

        .hero-panel,
        .card {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 28px;
            background: var(--bg-soft);
            box-shadow: var(--shadow);
            backdrop-filter: blur(20px);
        }

        .hero-panel {
            padding: 30px;
        }

        .hero-panel::before,
        .card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(114, 242, 192, 0.08), transparent 35%, rgba(110, 184, 255, 0.07));
            pointer-events: none;
        }

        .eyebrow {
            display: inline-flex;
            padding: 8px 12px;
            border-radius: 999px;
            border: 1px solid rgba(114, 242, 192, 0.25);
            color: var(--accent);
            font-size: 12px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            background: rgba(114, 242, 192, 0.08);
        }

        h1, h2, h3, p {
            margin: 0;
        }

        h1 {
            margin-top: 18px;
            font-size: clamp(34px, 5vw, 58px);
            line-height: 0.96;
            letter-spacing: -0.04em;
        }

        .lead {
            margin-top: 18px;
            max-width: 620px;
            color: var(--muted);
            font-size: 17px;
            line-height: 1.6;
        }

        .hero-stats {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 24px;
        }

        .hero-stat,
        .mini-stat {
            padding: 16px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .hero-stat strong,
        .mini-stat strong {
            display: block;
            font-size: 24px;
            margin-top: 8px;
        }

        .hero-side {
            padding: 26px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 16px;
        }

        .hero-side ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            gap: 10px;
            color: var(--muted);
        }

        .hero-side li {
            padding: 12px 14px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .grid {
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 24px;
        }

        .card {
            padding: 22px;
        }

        .scan-form {
            display: grid;
            gap: 14px;
        }

        label {
            color: var(--muted);
            font-size: 14px;
        }

        input {
            width: 100%;
            margin-top: 8px;
            padding: 15px 16px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.03);
            color: var(--text);
            outline: none;
            transition: border-color 0.2s ease, transform 0.2s ease;
        }

        input:focus {
            border-color: rgba(114, 242, 192, 0.45);
            transform: translateY(-1px);
        }

        button {
            margin-top: 6px;
            padding: 15px 18px;
            border: 0;
            border-radius: 18px;
            color: #04101c;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            box-shadow: 0 18px 40px rgba(110, 184, 255, 0.25);
        }

        .status-box {
            margin-top: 14px;
            padding: 14px 16px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.035);
            color: var(--muted);
            min-height: 54px;
        }

        .dashboard {
            display: grid;
            gap: 18px;
        }

        .summary-grid,
        .intel-grid,
        .history-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
        }

        .mini-stat span,
        .chip-list-label,
        .history-date {
            color: var(--muted);
            font-size: 13px;
        }

        .badge-row,
        .chip-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .badge,
        .chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 12px;
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
            color: var(--text);
            font-size: 13px;
        }

        .risk-high { color: var(--danger); }
        .risk-medium { color: var(--warn); }
        .risk-low { color: var(--ok); }

        .panel-title {
            margin-bottom: 14px;
            font-size: 18px;
        }

        .list-block {
            display: grid;
            gap: 10px;
        }

        .list-item,
        .history-item {
            padding: 14px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(255, 255, 255, 0.05);
            word-break: break-word;
        }

        .history-item strong {
            display: block;
            margin-bottom: 6px;
        }

        pre {
            margin: 0;
            padding: 16px;
            border-radius: 18px;
            background: #07111f;
            border: 1px solid rgba(255, 255, 255, 0.06);
            color: #bbdefc;
            white-space: pre-wrap;
            word-break: break-word;
            font-family: Consolas, "Courier New", monospace;
            font-size: 13px;
        }

        .empty-state {
            padding: 22px;
            border-radius: 20px;
            border: 1px dashed rgba(255, 255, 255, 0.1);
            color: var(--muted);
            text-align: center;
        }

        .hidden {
            display: none;
        }

        @media (max-width: 980px) {
            .hero,
            .grid,
            .summary-grid,
            .intel-grid,
            .history-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="shell">
        <section class="hero">
            <div class="hero-panel">
                <span class="eyebrow">Панель мониторинга оперативной разведки</span>
                <h1>Cyber Scanner</h1>
                <h2>Проверь сайт на уязвимости за секунды</h2>
                <p class="lead">
                    Найди слабые места раньше, чем это сделают хакеры. Он показывает, какие данные можно вытащить с сайта уже на первом проходе:
                    заголовки, IP, технологический стек, формы, ссылки, email-адреса и базовые сигналы риска.
                </p>
                <div class="hero-stats">
                    <div class="hero-stat">
                        <span>Что вытаскиваем</span>
                        <strong>Заголовки</strong>
                    </div>
                    <div class="hero-stat">
                        <span>Что считаем</span>
                        <strong>Риск</strong>
                    </div>
                    <div class="hero-stat">
                        <span>Что показываем</span>
                        <strong>Вывод</strong>
                    </div>
                </div>
            </div>

            <aside class="hero-panel hero-side">
                <div>
                    <span class="eyebrow">Предварительный просмотр данных</span>
                    <h2 style="margin-top: 16px; font-size: 28px;">Что мы проверяем</h2>
                </div>
                <ul>
                  <li>🔍 XSS уязвимости</li>
                  <li>💉 SQL-инъекции</li>
                  <li>🌐 Открытые порты</li>
                  <li>🧠 Технологии сайта</li>
                  <li>🛡️ Заголовки безопасности</li>
                </ul>
            </aside>
        </section>

        <section class="grid">
            <div class="card">
                <h2 class="panel-title">Запуск скана</h2>
                <form id="scanForm" class="scan-form">
                    <label>
                        URL сайта
                        <input type="text" id="url" placeholder="example.com или https://testphp.vulnweb.com" required>
                    </label>
                    <label>
                        Email (для истории)
                        <input type="email" id="email" placeholder="your@email.com">
                    </label>
                    <button type="submit">Start Scan</button>
                </form>

                <div id="statusBox" class="status-box">
                    Введите URL и запустите проверку
                </div>
            </div>

            <div class="dashboard">
                <div id="emptyState" class="empty-state">
                    Результаты появятся после первого скана. Я покажу, какие реальные данные удалось достать с целевой страницы.
                </div>

                <div id="results" class="hidden">
                    <div class="card">
                        <h2 class="panel-title">Сводка скана</h2>
                        <div id="summaryGrid" class="summary-grid"></div>
                        <div id="badgeRow" class="badge-row" style="margin-top: 16px;"></div>
                    </div>

                    <div class="card">
                        <h2 class="panel-title">Какие данные удалось вытащить</h2>
                        <div id="intelGrid" class="intel-grid"></div>
                    </div>

                    <div class="card">
                        <h2 class="panel-title">Технологии, заголовки и security headers</h2>
                        <div id="techChips" class="chip-list"></div>
                        <div style="height: 14px;"></div>
                        <div class="chip-list-label">Найденные email</div>
                        <div id="emailChips" class="chip-list" style="margin-top: 10px;"></div>
                        <div style="height: 14px;"></div>
                        <div id="headersList" class="list-block"></div>
                        <div style="height: 14px;"></div>
                        <div id="securityList" class="chip-list"></div>
                    </div>

                    <div class="card">
                        <h2 class="panel-title">Ссылки и порты</h2>
                        <div class="intel-grid">
                            <div>
                                <div class="chip-list-label">Внутренние ссылки</div>
                                <div id="internalLinks" class="list-block" style="margin-top: 10px;"></div>
                            </div>
                            <div>
                                <div class="chip-list-label">Внешние ссылки</div>
                                <div id="externalLinks" class="list-block" style="margin-top: 10px;"></div>
                            </div>
                        </div>
                        <div style="height: 16px;"></div>
                        <pre id="portsPreview">Пока нет данных по портам.</pre>
                    </div>

                    <div class="card">
                        <h2 class="panel-title">История по email</h2>
                        <div id="historyList" class="history-grid"></div>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <script>
        const form = document.getElementById("scanForm");
        const statusBox = document.getElementById("statusBox");
        const emptyState = document.getElementById("emptyState");
        const results = document.getElementById("results");

        const setStatus = (text) => {
            statusBox.textContent = text;
        };

        const renderStats = (items, containerId) => {
            const container = document.getElementById(containerId);
            container.innerHTML = items.map(item => `
                <div class="mini-stat">
                    <span>${item.label}</span>
                    <strong class="${item.className || ""}">${item.value}</strong>
                </div>
            `).join("");
        };

        const renderBadges = (data) => {
            const riskClass = data.risk_level === "HIGH"
                ? "risk-high"
                : data.risk_level === "MEDIUM"
                    ? "risk-medium"
                    : "risk-low";

            document.getElementById("badgeRow").innerHTML = `
                <div class="badge">Scan ID: ${data.scan_id}</div>
                <div class="badge ${riskClass}">Risk: ${data.risk_level}</div>
                <div class="badge">${data.vulnerabilities.xss ? "XSS found" : "XSS not found"}</div>
                <div class="badge">${data.vulnerabilities.sql_injection ? "SQLi found" : "SQLi not found"}</div>
                <div class="badge">Scans left: ${data.scans_left}</div>
            `;
        };

        const renderChipList = (containerId, items, fallback) => {
            const container = document.getElementById(containerId);
            if (!items || !items.length) {
                container.innerHTML = `<div class="chip">${fallback}</div>`;
                return;
            }

            container.innerHTML = items.map(item => `<div class="chip">${escapeHtml(item)}</div>`).join("");
        };

        const renderListBlock = (containerId, items, fallback) => {
            const container = document.getElementById(containerId);
            if (!items || !items.length) {
                container.innerHTML = `<div class="list-item">${fallback}</div>`;
                return;
            }

            container.innerHTML = items.map(item => `<div class="list-item">${escapeHtml(item)}</div>`).join("");
        };

        const renderHeaders = (headers) => {
            const container = document.getElementById("headersList");
            const entries = Object.entries(headers || {});

            if (!entries.length) {
                container.innerHTML = `<div class="list-item">Сервер не отдал полезные заголовки для предпросмотра.</div>`;
                return;
            }

            container.innerHTML = entries.map(([key, value]) => `
                <div class="list-item"><strong>${escapeHtml(key)}:</strong> ${escapeHtml(value)}</div>
            `).join("");
        };

        const renderSecurity = (securityHeaders) => {
            const labels = {
                content_security_policy: "Content-Security-Policy",
                x_frame_options: "X-Frame-Options",
                strict_transport_security: "Strict-Transport-Security",
                x_content_type_options: "X-Content-Type-Options"
            };

            const items = Object.entries(labels).map(([key, label]) => {
                const enabled = Boolean(securityHeaders && securityHeaders[key]);
                return `<div class="chip">${label}: ${enabled ? "present" : "missing"}</div>`;
            });

            document.getElementById("securityList").innerHTML = items.join("");
        };

        const renderHistory = async (email) => {
            const list = document.getElementById("historyList");

            try {
                const res = await fetch(`/history?email=${encodeURIComponent(email)}`);
                const data = await res.json();

                if (!res.ok || !Array.isArray(data) || !data.length) {
                    list.innerHTML = `<div class="history-item">История пока пуста для ${escapeHtml(email)}.</div>`;
                    return;
                }

                list.innerHTML = data.map(item => `
                    <div class="history-item">
                        <strong>${escapeHtml(item.url)}</strong>
                        <div class="history-date">${item.created_at}</div>
                        <div style="margin-top: 10px;">Risk: ${item.risk}</div>
                        <div>XSS: ${item.xss ? "yes" : "no"} | SQLi: ${item.sql_injection ? "yes" : "no"}</div>
                    </div>
                `).join("");
            } catch (error) {
                list.innerHTML = `<div class="history-item">Не удалось загрузить историю: ${error.message}</div>`;
            }
        };

        const escapeHtml = (str) => {
            if (!str) return '';
            return str.replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
        };

        form.onsubmit = async (event) => {
            event.preventDefault();

            const url = document.getElementById("url").value.trim();
            const email = document.getElementById("email").value.trim() || "guest@demo.com";

            setStatus("Сканирование запущено. Делаю запросы к сайту, проверяю уязвимости и собираю page intelligence...");

            try {
                const response = await fetch("/scan", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url, email })
                });

                const data = await response.json();

                if (!response.ok) {
                    if (response.status === 402) {
                        setStatus("Лимит этого email закончился. Оставьте поле email пустым для demo-режима или вызовите POST /reset-quota.");
                    } else {
                        setStatus(data.error || "Скан завершился с ошибкой.");
                    }
                    return;
                }

                emptyState.classList.add("hidden");
                results.classList.remove("hidden");

                renderStats([
                    { label: "HTTP status", value: data.status_code },
                    { label: "Title", value: data.page_intelligence.title || "N/A" },
                    { label: "Response time", value: `${data.page_intelligence.response_time_ms} ms` },
                    { label: "Content size", value: `${data.page_intelligence.content_length} bytes` }
                ], "summaryGrid");

                renderBadges(data);

                renderStats([
                    { label: "IP address", value: data.page_intelligence.ip_address || "Not resolved" },
                    { label: "Server", value: data.page_intelligence.server || "Unknown" },
                    { label: "Forms found", value: data.page_intelligence.forms_count },
                    { label: "Inputs found", value: data.page_intelligence.inputs_count },
                    { label: "Scripts found", value: data.page_intelligence.scripts_count },
                    { label: "Final URL", value: data.page_intelligence.final_url || data.url }
                ], "intelGrid");

                renderChipList(
                    "techChips",
                    data.page_intelligence.technologies,
                    "Технологии явно не определились"
                );

                renderChipList(
                    "emailChips",
                    data.page_intelligence.emails_found,
                    "Email-адреса не найдены"
                );

                renderSecurity(data.page_intelligence.security_headers);
                renderHeaders(data.page_intelligence.headers);

                renderListBlock(
                    "internalLinks",
                    data.page_intelligence.sample_links.internal,
                    "Внутренние ссылки не найдены"
                );

                renderListBlock(
                    "externalLinks",
                    data.page_intelligence.sample_links.external,
                    "Внешние ссылки не найдены"
                );

                document.getElementById("portsPreview").textContent = data.open_ports_preview || "Нет данных по портам.";

                const foundEmails = data.page_intelligence.emails_found?.length
                    ? `Найдены email: ${data.page_intelligence.emails_found.join(", ")}`
                    : "Email-адреса на странице не найдены.";

                setStatus(
                    `Скан завершён. ${foundEmails} ` +
                    `Внутренних ссылок: ${data.page_intelligence.internal_links_count}, ` +
                    `внешних: ${data.page_intelligence.external_links_count}.`
                );

                await renderHistory(email);
            } catch (error) {
                setStatus(`Ошибка: ${error.message}`);
            }
        };
    </script>
</body>
</html>
'''

# Класс для управления квотами
class QuotaManager:
    def __init__(self, daily_limit=10):
        self.daily_limit = daily_limit
        self.usage = {}
    
    def check_quota(self, email):
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"{email}:{today}"
        current = self.usage.get(key, 0)
        if current >= self.daily_limit:
            return False, self.daily_limit - current
        return True, self.daily_limit - current
    
    def increment_usage(self, email):
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"{email}:{today}"
        self.usage[key] = self.usage.get(key, 0) + 1
    
    def reset_quota(self, email):
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"{email}:{today}"
        self.usage[key] = 0

quota_manager = QuotaManager(daily_limit=10)

# Функции сканирования
def check_site_availability(url):
    """Проверка доступности сайта"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    start_time = time.time()
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'CyberScanner/1.0'}, allow_redirects=True)
        response_time = int((time.time() - start_time) * 1000)
        return {
            'status_code': r.status_code,
            'final_url': r.url,
            'headers': dict(r.headers),
            'html': r.text[:10000],
            'content_length': len(r.content),
            'response_time_ms': response_time
        }
    except Exception as e:
        return None

def extract_emails(html):
    """Извлечение email адресов из HTML"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, html)
    return list(set(emails))

def extract_links(html, base_url):
    """Извлечение ссылок из HTML"""
    from urllib.parse import urljoin, urlparse
    
    link_pattern = r'href=["\']([^"\']+)["\']'
    links = re.findall(link_pattern, html)
    
    internal = []
    external = []
    base_domain = urlparse(base_url).netloc
    
    for link in links[:50]:  # Ограничиваем количество
        if link.startswith('#') or link.startswith('javascript:'):
            continue
        
        full_url = urljoin(base_url, link)
        parsed = urlparse(full_url)
        
        if parsed.netloc == base_domain or not parsed.netloc:
            internal.append(full_url)
        else:
            external.append(full_url)
    
    return list(set(internal))[:20], list(set(external))[:20]

def detect_technologies(html, headers):
    """Определение технологий"""
    techs = []
    html_lower = html.lower()
    headers_str = str(headers).lower()
    
    # CMS detection
    if 'wp-content' in html_lower or 'wordpress' in html_lower:
        techs.append('WordPress')
    if 'drupal' in html_lower:
        techs.append('Drupal')
    if 'joomla' in html_lower:
        techs.append('Joomla')
    
    # JS frameworks
    if 'react' in html_lower or 'reactjs' in html_lower:
        techs.append('React')
    if 'vue' in html_lower:
        techs.append('Vue.js')
    if 'angular' in html_lower:
        techs.append('Angular')
    if 'jquery' in html_lower:
        techs.append('jQuery')
    
    # Server detection
    if 'server' in headers:
        techs.append(headers['server'].split('/')[0])
    
    return list(set(techs))[:10]

def check_security_headers(headers):
    """Проверка security заголовков"""
    return {
        'content_security_policy': 'Content-Security-Policy' in headers,
        'x_frame_options': 'X-Frame-Options' in headers,
        'strict_transport_security': 'Strict-Transport-Security' in headers,
        'x_content_type_options': 'X-Content-Type-Options' in headers,
        'x_xss_protection': 'X-XSS-Protection' in headers
    }

def check_vulnerabilities(html):
    """Базовая проверка на уязвимости"""
    vulns = {
        'xss': False,
        'sql_injection': False
    }
    
    html_lower = html.lower()
    
    # Проверка на потенциальные XSS (очень базовая)
    if '<script' in html_lower or 'onerror=' in html_lower or 'onload=' in html_lower:
        vulns['xss'] = True
    
    # Проверка на потенциальные SQL инъекции (по наличию параметров в URL)
    if '?id=' in html_lower or '?page=' in html_lower or '?cat=' in html_lower:
        vulns['sql_injection'] = True
    
    return vulns

def get_ip_address(url):
    """Получение IP адреса"""
    try:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname
        if hostname:
            import socket
            return socket.gethostbyname(hostname)
    except:
        pass
    return None

def scan_ports(domain):
    """Сканирование портов"""
    common_ports = [80, 443, 21, 22, 25, 3306, 5432, 8080, 8443]
    open_ports = []
    
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.split('/')[0]
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((domain, port))
            sock.close()
            if result == 0:
                open_ports.append(port)
        except:
            pass
    
    return open_ports

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    url = data.get('url')
    email = data.get('email', 'guest@demo.com')
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    # Проверка квоты
    allowed, remaining = quota_manager.check_quota(email)
    if not allowed:
        return jsonify({"error": f"Daily limit reached. {remaining} scans left"}), 402
    
    # Проверка доступности
    site_data = check_site_availability(url)
    if not site_data:
        return jsonify({"error": "Site is not accessible"}), 400
    
    # Сбор информации
    html = site_data['html']
    headers = site_data['headers']
    
    emails_found = extract_emails(html)
    internal_links, external_links = extract_links(html, site_data['final_url'])
    technologies = detect_technologies(html, headers)
    security_headers = check_security_headers(headers)
    vulnerabilities = check_vulnerabilities(html)
    
    # Подсчет количества форм и инпутов
    forms_count = len(re.findall(r'<form[^>]*>', html, re.IGNORECASE))
    inputs_count = len(re.findall(r'<input[^>]*>', html, re.IGNORECASE))
    scripts_count = len(re.findall(r'<script[^>]*>', html, re.IGNORECASE))
    
    # Получение title
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    title = title_match.group(1) if title_match else None
    
    ip_address = get_ip_address(url)
    
    # Сканирование портов
    domain = re.sub(r'^https?://', '', url)
    open_ports = scan_ports(domain)
    ports_preview = f"Открытые порты: {', '.join(map(str, open_ports)) if open_ports else 'Не обнаружены открытые порты'}"
    
    # Определение уровня риска
    risk_score = 0
    if vulnerabilities['xss']:
        risk_score += 2
    if vulnerabilities['sql_injection']:
        risk_score += 2
    if not security_headers['content_security_policy']:
        risk_score += 1
    if not security_headers['x_frame_options']:
        risk_score += 1
    if open_ports:
        risk_score += len(open_ports)
    
    if risk_score >= 5:
        risk_level = "HIGH"
    elif risk_score >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Создание результата
    scan_result = {
        "url": site_data['final_url'],
        "scan_id": f"SCAN_{int(time.time())}",
        "status_code": site_data['status_code'],
        "risk_level": risk_level,
        "scans_left": remaining - 1,
        "vulnerabilities": vulnerabilities,
        "page_intelligence": {
            "title": title,
            "ip_address": ip_address,
            "server": headers.get('Server', 'Unknown'),
            "final_url": site_data['final_url'],
            "content_length": site_data['content_length'],
            "response_time_ms": site_data['response_time_ms'],
            "forms_count": forms_count,
            "inputs_count": inputs_count,
            "scripts_count": scripts_count,
            "internal_links_count": len(internal_links),
            "external_links_count": len(external_links),
            "emails_found": emails_found[:10],
            "technologies": technologies,
            "headers": {k: v[:100] for k, v in list(headers.items())[:15]},
            "security_headers": security_headers,
            "sample_links": {
                "internal": internal_links[:10],
                "external": external_links[:10]
            }
        },
        "open_ports_preview": ports_preview
    }
    
    # Сохранение в историю
    if email not in scan_history:
        scan_history[email] = []
    
    scan_history[email].append({
        "url": site_data['final_url'],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk": risk_level,
        "xss": vulnerabilities['xss'],
        "sql_injection": vulnerabilities['sql_injection']
    })
    
    # Ограничиваем историю 50 записями
    if len(scan_history[email]) > 50:
        scan_history[email] = scan_history[email][-50:]
    
    # Увеличиваем счетчик квоты
    quota_manager.increment_usage(email)
    
    return jsonify(scan_result)

@app.route('/history', methods=['GET'])
def get_history():
    email = request.args.get('email', 'guest@demo.com')
    history = scan_history.get(email, [])
    return jsonify(history)

@app.route('/reset-quota', methods=['POST'])
def reset_quota():
    data = request.json
    email = data.get('email')
    if email:
        quota_manager.reset_quota(email)
        return jsonify({"message": f"Quota reset for {email}"})
    return jsonify({"error": "Email required"}), 400

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     🚀 CYBER SCANNER DASHBOARD ЗАПУЩЕН!                     ║
    ║     📱 Открой: http://localhost:5000                        ║
    ║                                                             ║
    ║     🔍 Что анализирует:                                     ║
    ║     • Security заголовки                                    ║
    ║     • Технологии сайта                                      ║
    ║     • Email адреса на странице                              ║
    ║     • Внутренние и внешние ссылки                           ║
    ║     • Открытые порты                                        ║
    ║     • XSS и SQL инъекции                                    ║
    ║                                                             ║
    ║     💡 Каждый email имеет 10 сканов в день                  ║
    ║     📜 История сканов сохраняется                           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='127.0.0.1', port=5000)