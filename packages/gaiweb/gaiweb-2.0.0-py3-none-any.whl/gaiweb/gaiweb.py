# -*- coding: UTF-8 -*-
# python_xueba/2026/1/1
import logging
from datetime import datetime
from typing import List, Dict
import requests
import json
import re
import time
import argparse
from flask import Flask, Response, request, render_template_string
from flask_cors import CORS
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

default_api_key = "AIzaSyCLNcqW65Kyn3yLZC0w04Hj1vR5Qy_3axA"

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent"

MODEL_MAP = {
    "gemini-2.0-flash-lite": "gemini-2.0-flash-lite",
    "gemini-2.0-flash": "gemini-2.0-flash",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
    "gemini-2.5-flash-image": "gemini-2.5-flash-image",
    "gemini-2.5-flash-preview-09-2025": "gemini-2.5-flash-preview-09-2025",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-3-pro-image-preview": "gemini-3-pro-image-preview",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "gemini-3-pro-preview": "gemini-3-pro-preview",
}

SYSTEM_INSTRUCTION_TEXT = (
    "你是GAI,使用模型 {}。当前时间约 {}。\n"
    "请使用标准 Markdown 格式回复，支持表格、代码块、LaTeX 公式（使用 $...$ 行内，$$...$$ 块级）。\n"
)

GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1048576
}

def fetch_url_content(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text(separator=' ', strip=True)[:65536]
    except Exception as e:
        return f"链接获取失败: {str(e)}"

def extract_urls(text: str) -> List[str]:
    pattern = re.compile(r'(https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+)')
    urls = pattern.findall(text)
    normalized = []
    for url in urls:
        if url.startswith('www.'):
            url = 'https://' + url
        if url not in normalized:
            normalized.append(url)
    return normalized

def normalize_context(context: List[Dict]) -> List[Dict]:
    normalized = []
    for item in context:
        if item.get("role") == "system":
            continue
        role = "model" if item.get("role") in ("assistant", "model") else "user"
        parts = []
        for p in item.get("parts", []):
            if p.get("text"):
                parts.append({"text": p["text"]})
            elif p.get("inline_data"):
                parts.append({"inline_data": p["inline_data"]})
        if parts:
            normalized.append({"role": role, "parts": parts})
    return normalized

def generate_gemini_stream(prompt: str, history: List[Dict], images: List[str], model_name: str, api_key: str):
    model = MODEL_MAP.get(model_name, "gemini-2.5-flash")
    url = GEMINI_BASE_URL.format(model=model)
    key = api_key if api_key else default_api_key
    if not key or key == "placeholder":
        return Response("data: " + json.dumps({'error': '请提供有效的 API Key'}) + "\n\n", mimetype="text/event-stream")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_instruction = {"parts": [{"text": SYSTEM_INSTRUCTION_TEXT.format(model, current_time)}]}

    urls = extract_urls(prompt)
    url_parts = [{"text": f"\n--- 引用内容 ({u}) ---\n{fetch_url_content(u)}\n-------------------------\n"} for u in urls]

    contents = normalize_context(history)

    user_parts = url_parts[:]
    for chunk in [prompt[i:i+4096] for i in range(0, len(prompt), 4096)]:
        user_parts.append({"text": f"用户的请求：{chunk}"})
    if images:
        user_parts.extend([{"inline_data": {"mime_type": "image/jpeg", "data": img}} for img in images])
    if not user_parts:
        user_parts.append({"text": "（无具体请求）"})

    contents.append({"role": "user", "parts": user_parts})

    payload = {
        "contents": contents,
        "generationConfig": GENERATION_CONFIG,
        "systemInstruction": system_instruction
    }

    if len(json.dumps(payload).encode()) > 2 * 1024 * 1024:
        return Response("data: " + json.dumps({'error': '请求负载过大'}) + "\n\n", mimetype="text/event-stream")

    def stream():
        for attempt in range(3):
            try:
                with requests.post(url, params={"key": key, "alt": "sse"}, json=payload, stream=True, timeout=120) as r:
                    if r.status_code != 200:
                        full_error = r.text.strip()
                        safe_error = re.sub(r'[A-Za-z0-9_-]{30,}', '[隐藏]', full_error)
                        yield f"data: {json.dumps({'error': f'服务器错误 {r.status_code}: {safe_error}'})}\n\n"
                        return
                    for line in r.iter_lines():
                        if line and line.startswith(b"data: "):
                            data = json.loads(line[6:])
                            text = "".join(p.get("text", "") for c in data.get("candidates", []) for p in c.get("content", {}).get("parts", []))
                            if text:
                                yield f"data: {json.dumps({'text': text})}\n\n"
                            if data.get("candidates") and data["candidates"][0].get("finishReason"):
                                yield f"data: {json.dumps({'done': True})}\n\n"
                                return
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    return
            except Exception as e:
                safe_msg = re.sub(r'[A-Za-z0-9_-]{30,}', '[隐藏]', str(e))
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                yield f"data: {json.dumps({'error': f'请求异常: {safe_msg}'})}\n\n"

    return app.response_class(stream(), mimetype="text/event-stream")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)
    if not data:
        return Response("data: " + json.dumps({'error': '无效请求'}) + "\n\n", mimetype="text/event-stream")
    images = data.get('images', [])
    return generate_gemini_stream(
        data.get('message', ''),
        data.get('context', []),
        images,
        data.get('model_name', 'gemini-2.5-flash'),
        data.get('api_key', '')
    )

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GAIWeb</title>
     <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/base16/tomorrow-night.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked@4.3.0/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify@2.4.0/dist/purify.min.js"></script>
    <style>
        :root {
            --bg: #ffffff;
            --text: #000000;
            --border: #e0e0e0;
            --shadow: rgba(0,0,0,0.08);
            --hover: #f5f5f5;
            --code-bg: #282c34;
            --code-text: #abb2bf;
            --inline-code-bg: #000000;
            --inline-code-text: #ffffff;
            --ai-bg: #f7f9fc;
            --user-bg: #000000;
            --input-bg: #ffffff;
            --scrollbar-track: #f1f1f1;
            --scrollbar-thumb: #c0c0c0;
            --scrollbar-thumb-hover: #a8a8a8;
            --marker: #666666;
            --primary: #000000;
            --table-border: #d4dbe3;
            --table-header: #f8f9fb;
        }
        [data-theme="dark"] {
            --bg: #000000;
            --text: #ffffff;
            --border: #333333;
            --shadow: rgba(0,0,0,0.4);
            --hover: #1e1e1e;
            --code-bg: #1e1e1e;
            --code-text: #d4d4d4;
            --inline-code-bg: #2d2d2d;
            --inline-code-text: #d4a76a;
            --ai-bg: #111111;
            --user-bg: #ffffff;
            --input-bg: #000000;
            --scrollbar-track: #111111;
            --scrollbar-thumb: #444444;
            --scrollbar-thumb-hover: #666666;
            --marker: #bbbbbb;
            --primary: #ffffff;
            --table-border: #3a3a3a;
            --table-header: #1e1e1e;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 96px 20px 0;
        }
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-track { background: var(--scrollbar-track); border-radius: 10px; }
        ::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 10px; border: 2px solid var(--scrollbar-track); }
        ::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-thumb-hover); }
        .container {
            width: 100%;
            max-width: 1400px;
            height: calc(100vh - 96px);
            background: var(--bg);
            box-shadow: 0 8px 32px var(--shadow);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .menu-toggle {
            position: fixed;
            top: 32px;
            left: 32px;
            background: #000000;
            border: 1px solid var(--border);
            border-radius: 50%;
            width: 48px;
            height: 48px;
            cursor: pointer;
            z-index: 1001;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px var(--shadow);
        }
        .menu-toggle.hidden { opacity: 0; pointer-events: none; }
        .new-chat-btn {
            position: fixed;
            top: 32px;
            right: 32px;
            background: var(--primary);
            color: var(--bg);
            border: none;
            border-radius: 50%;
            width: 48px;
            height: 48px;
            cursor: pointer;
            z-index: 1001;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px var(--shadow);
            font-size: 26px;
        }
        .sidebar {
            width: 300px;
            background: var(--bg);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            position: fixed;
            left: -300px;
            top: 0;
            height: 100%;
            transition: left 0.3s ease;
            z-index: 1000;
            box-shadow: 8px 0 32px var(--shadow);
        }
        .sidebar.active { left: 0; }
        .settings-panel { padding: 24px; border-bottom: 1px solid var(--border); }
        .settings-summary { font-weight: 600; cursor: pointer; padding: 12px 0; display: flex; justify-content: space-between; align-items: center; font-size: 18px; }
        .settings-summary .arrow { transition: transform 0.2s; font-size: 20px; }
        details[open] > summary .arrow { transform: rotate(180deg); }
        .settings-content { padding-top: 12px; display: flex; flex-direction: column; gap: 16px; }
        .settings-content label { font-size: 14px; color: var(--text); opacity: 0.8; }
        .settings-content select, .settings-content input { width: 100%; padding: 12px; border: 1px solid var(--border); border-radius: 12px; background: var(--input-bg); color: var(--text); font-size: 16px; }
        .theme-toggle { width: 100%; padding: 14px; background: var(--hover); border: none; border-radius: 12px; cursor: pointer; margin-top: 8px; font-size: 16px; color: var(--text); }
        .history-search { margin: 20px 24px; padding: 12px; border: 1px solid var(--border); border-radius: 12px; background: var(--input-bg); color: var(--text); font-size: 16px; }
        .chat-history { flex: 1; overflow-y: auto; padding: 0 24px 24px; }
        .history-item { padding: 16px; border-radius: 12px; cursor: pointer; margin-bottom: 12px; transition: background 0.2s; }
        .history-item:hover, .history-item.active { background: var(--hover); }
        .history-item-title { font-weight: 600; font-size: 16px; margin-bottom: 8px; word-break: break-word; }
        .history-item-preview { font-size: 14px; color: var(--text); opacity: 0.7; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 8px; }
        .history-item-time { font-size: 13px; color: var(--text); opacity: 0.6; }
        .clear-history { padding: 16px 24px; text-align: center; cursor: pointer; font-weight: 500; font-size: 16px; }
        .clear-history:hover { background: var(--hover); }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 32px 32px 120px 32px;
            display: flex;
            flex-direction: column;
            gap: 28px;
        }
        .message {
            max-width: 95%;
            border-radius: 24px;
            padding: 18px 24px;
            box-shadow: 0 4px 16px var(--shadow);
            align-self: flex-start;
        }
        .message.user {
            align-self: flex-end;
            background: var(--user-bg);
            color: var(--bg);
            border-bottom-right-radius: 6px;
        }
        .message.ai {
            background: var(--ai-bg);
            border-bottom-left-radius: 6px;
        }
        .message-content {
            line-height: 1.8;
            font-size: 17px;
            font-weight: 500;
        }
        .message-content code:not(pre code) {
            background: var(--inline-code-bg);
            color: var(--inline-code-text);
            padding: 3px 8px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 900;
            font-size: 15px;
        }
        .message-content h1 { font-size: 26px; font-weight: 700; margin: 28px 0 16px; }
        .message-content h2 { font-size: 22px; font-weight: 700; margin: 24px 0 14px; }
        .message-content h3 { font-size: 19px; font-weight: 700; margin: 20px 0 12px; }
        .message-content p { margin: 14px 0; }
        .message-content strong { font-weight: 700; }
        .message-content em { font-style: italic; }
        .message-content blockquote {
            border-left: 4px solid var(--primary);
            padding-left: 20px;
            margin: 20px 0;
            opacity: 0.9;
            font-style: italic;
            background: var(--hover);
            border-radius: 0 8px 8px 0;
        }
        .message-content ul, .message-content ol {
            padding-left: 28px;
            margin: 16px 0;
        }
        .message-content li { margin: 10px 0; }
        .message-content li::marker { color: var(--marker); font-weight: bold; }
        .message-content table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            margin: 24px 0;
            font-size: 16px;
            background: var(--bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 16px var(--shadow);
        }
        .message-content table th,
        .message-content table td {
            border: 1px solid var(--table-border);
            padding: 14px 18px;
            text-align: left;
        }
        .message-content table th {
            background: var(--table-header);
            font-weight: 700;
        }
        .message-content table tr:hover td {
            background: var(--hover);
            transition: background 0.2s;
        }
        .message-content hr {
            border: none;
            border-top: 2px solid var(--border);
            margin: 40px 0;
        }
        .message-content pre {
            background: #000000;
            color: var(--code-text);
            padding: 15px;
            border-radius: 16px;
            margin: 24px 0;
            position: relative;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 900;
            font-size: 15.5px;
            line-height: 1.6;
            box-shadow: 0 6px 20px var(--shadow);
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .message-content pre::-webkit-scrollbar {
            height: 10px;
        }
        .message-content pre::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.08);
            border-radius: 5px;
        }
        .message-content pre::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.25);
            border-radius: 5px;
        }
        .message-content pre::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.4);
        }
        [data-theme="dark"] .message-content pre::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.3);
        }
        [data-theme="dark"] .message-content pre::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.3);
        }.menu-toggle {
    background:#ffffff;
}
        [data-theme="dark"] .message-content pre::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.15);
        }
        [data-theme="dark"] .message-content pre::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.3);
        }
        .message-content pre code {
            background: none;
            padding: 0;
            white-space: pre;
            overflow-x: auto;
            display: block;
        }
        .code-actions {
            position: absolute;
            bottom: 12px;
            right: 12px;
            opacity: 0;
            transition: opacity 0.3s;
            display: flex;
            gap: 10px;
        }
        pre:hover .code-actions { opacity: 1; }
        .code-actions button {
            background: rgba(255, 255, 255, 0.15);
            color: #fff;
            border: none;
            padding: 9px 18px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 900;
            backdrop-filter: blur(10px);
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .code-actions button:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }
        [data-theme="dark"] .code-actions button {
            background: rgba(0, 0, 0, 0.5);
        }
        [data-theme="dark"] .code-actions button:hover {
            background: rgba(0, 0, 0, 0.7);
        }
        .input-area {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 16px 32px 32px;
            background: var(--bg);
            border-top: 1px solid var(--border);
            max-width: 1400px;
            margin: 0 auto;
            box-shadow: 0 -8px 32px var(--shadow);
            z-index: 100;
        }
        .image-preview-container {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 12px;
        }
        .image-preview-container:empty { margin-bottom: 0; }
        .image-preview-item {
            position: relative;
            width: 100px;
            height: 100px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px var(--shadow);
        }
        .remove-image {
            position: absolute;
            top: 6px;
            right: 6px;
            background: rgba(0,0,0,0.7);
            color: white;
            border: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 14px;
        }
        .input-wrapper {
            display: flex;
            background: var(--input-bg);
            border: 1px solid var(--border);
            border-radius: 32px;
            padding: 12px 20px;
            gap: 16px;
            align-items: center;
            box-shadow: 0 4px 12px var(--shadow);
        }
        #message-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text);
            font-size: 17px;
            font-weight: 500;
            resize: none;
            min-height: 24px;
            max-height: 160px;
            overflow-y: auto;
            line-height: 1.6;
        }
        .upload-button, #send-button, #stop-button {
            background: none;
            border: none;
            color: var(--text);
            font-size: 24px;
            cursor: pointer;
            opacity: 0.8;
            transition: all 0.2s;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }
        .upload-button:hover, #send-button:hover, #stop-button:hover {
            opacity: 1;
            background: var(--hover);
        }
        #stop-button { display: none; }
        .loading-dots {
            display: flex;
            gap: 8px;
            padding: 16px 0;
        }
        .loading-dots span {
            width: 10px;
            height: 10px;
            background: var(--text);
            border-radius: 50%;
            animation: pulse 1.4s infinite ease-in-out both;
            opacity: 0.6;
        }
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }
        #html-modal {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.85);
            z-index: 2000;
            justify-content: center;
            align-items: center;
        }
        .modal-content {
            background: var(--bg);
            width: 95%;
            max-width: 1200px;
            height: 95%;
            border-radius: 16px;
            overflow: hidden;
            position: relative;
            box-shadow: 0 16px 64px var(--shadow);
        }
        .modal-close {
            position: absolute;
            top: 16px;
            right: 16px;
            background: rgba(0,0,0,0.3);
            color: var(--text);
            border: none;
            font-size: 32px;
            cursor: pointer;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        [data-theme="dark"] .modal-close { background: rgba(255,255,255,0.2); }
        .modal-close:hover { background: rgba(255,255,255,0.3); }
        [data-theme="dark"] .modal-close:hover { background: rgba(255,255,255,0.4); }
        #html-frame { width: 100%; height: 100%; border: none; }
        @media (max-width: 768px) {
            body { padding: 88px 12px 0; }
            .container { border-radius: 0; height: calc(100vh - 88px); }
            .chat-messages { padding: 20px 20px 140px 20px; }
            .input-area { padding: 16px 20px 32px; }
            .input-wrapper { padding: 12px 16px; }
            .menu-toggle, .new-chat-btn { width: 44px; height: 44px; font-size: 22px; }
        }
    </style>
</head>
<body>
    <button class="menu-toggle" id="menu-toggle">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
    </button>
    <button class="new-chat-btn" onclick="startNewChat()">
        <svg width="20" height="20" viewBox="0 0 16 16" fill="none">
            <path d="M8 3.33337V12.6667M3.33333 8H12.6667" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
    </button>
    <div class="container">
        <div class="sidebar" id="sidebar">
            <details class="settings-panel">
                <summary class="settings-summary">设置 <span class="arrow">▼</span></summary>
                <div class="settings-content">
                    <label>模型</label>
                    <select id="model-select">
                        <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite</option>
                        <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                        <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                        <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
                        <option value="gemini-2.5-flash-image">Gemini 2.5 Flash Image</option>
                        <option value="gemini-2.5-flash-preview-09-2025">Gemini 2.5 Flash Preview (09-2025)</option>
                        <option value="gemini-2.5-flash" selected>Gemini 2.5 Flash</option>
                        <option value="gemini-3-pro-image-preview">Gemini 3 Pro Image Preview</option>
                        <option value="gemini-3-flash-preview">Gemini 3 Flash Preview</option>
                        <option value="gemini-3-pro-preview">Gemini 3 Pro Preview</option>
                    </select>
                    <label>API Key (本地保存)</label>
                    <input type="password" id="api-key-input" placeholder="可选，留空使用启动时提供的">
                    <button class="theme-toggle" onclick="toggleTheme()">夜间模式</button>
                </div>
            </details>
            <input type="text" class="history-search" placeholder="搜索历史" oninput="updateChatHistory(this.value.trim())">
            <div class="chat-history" id="chat-history"></div>
            <div class="clear-history" onclick="clearHistory()">清空历史</div>
        </div>
        <div class="chat-messages" id="chat-messages"></div>
        <div class="input-area">
            <div class="image-preview-container" id="image-preview"></div>
            <div class="input-wrapper">
                <button class="upload-button" id="upload-button">
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="none">
                        <path d="M14 10V12H2V10H0V14H16V10H14ZM8 2L12 6H9V10H7V6H4L8 2Z" fill="currentColor"/>
                    </svg>
                </button>
                <textarea id="message-input" placeholder="输入消息或Ctrl+V粘贴图片..." rows="1"></textarea>
                <button id="send-button">
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="none">
                        <path d="M14.6667 1.33337L7.33333 8.66671M14.6667 1.33337L10 14.6667L7.33333 8.66671L1.33333 6.00004L14.6667 1.33337Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
                <button id="stop-button">
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="none">
                        <path d="M4 4H12V12H4V4Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>
    <div id="html-modal">
        <div class="modal-content">
            <button class="modal-close">×</button>
            <iframe id="html-frame"></iframe>
        </div>
    </div>
    <script>
        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, {language: lang}).value;
                    } catch (e) {}
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
            gfm: true
        });

        const Config = { MAX_IMAGE_UPLOADS: 5 };
        let conversations = JSON.parse(localStorage.getItem('conversations') || '[]');
        let currentConversationId = localStorage.getItem('currentConversationId') || Date.now().toString();
        localStorage.setItem('currentConversationId', currentConversationId);
        let currentContext = [];
        let uploadedImages = [];
        let isGenerating = false;
        let currentAiMessageDiv = null;
        let currentContentDiv = null;
        let loadingElement = null;

        const messagesDiv = document.getElementById('chat-messages');
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-button');
        const stopBtn = document.getElementById('stop-button');
        const preview = document.getElementById('image-preview');
        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.getElementById('menu-toggle');
        const chatHistory = document.getElementById('chat-history');
        const modelSelect = document.getElementById('model-select');
        const apiKeyInput = document.getElementById('api-key-input');
        const htmlModal = document.getElementById('html-modal');

        function toggleTheme() {
            const root = document.documentElement;
            const isDark = root.hasAttribute('data-theme');
            if (isDark) root.removeAttribute('data-theme');
            else root.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', isDark ? 'light' : 'dark');
            closeSidebar();
        }

        function closeSidebar() {
            sidebar.classList.remove('active');
            menuToggle.classList.remove('hidden');
        }

        function openSidebar() {
            sidebar.classList.add('active');
            menuToggle.classList.add('hidden');
        }

        function scrollToBottom() {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // 安全局部渲染函数（关键修复）
        function renderMessageContent(contentDiv) {
            if (!contentDiv) return;
            setTimeout(() => {
                try {
                    renderMathInElement(contentDiv, {
                        delimiters: [
                            {left: "$$", right: "$$", display: true},
                            {left: "$", right: "$", display: false},
                            {left: "\\[", right: "\\]", display: true},
                            {left: "\\(", right: "\\)", display: false}
                        ],
                        throwOnError: false
                    });
                } catch (e) {}
                contentDiv.querySelectorAll('pre code').forEach(block => {
                    try { hljs.highlightElement(block); } catch (e) {}
                });
                contentDiv.querySelectorAll('pre').forEach(pre => {
                    if (pre.querySelector('.code-actions')) return;
                    const actions = document.createElement('div');
                    actions.className = 'code-actions';
                    actions.innerHTML = `
                        <button onclick="navigator.clipboard.writeText(this.closest('pre').querySelector('code').textContent).then(()=>{this.textContent='已复制';setTimeout(()=>this.textContent='复制',2000)})">复制</button>
                        <button onclick="previewHTML(this.closest('pre').querySelector('code').textContent)">预览</button>
                    `;
                    pre.appendChild(actions);
                });
            }, 0);
        }

        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
            const savedKey = localStorage.getItem('geminiApiKey');
            if (savedKey) apiKeyInput.value = savedKey;
            const savedModel = localStorage.getItem('selectedModel');
            if (savedModel) modelSelect.value = savedModel;
            apiKeyInput.addEventListener('input', () => localStorage.setItem('geminiApiKey', apiKeyInput.value));
            modelSelect.addEventListener('change', () => localStorage.setItem('selectedModel', modelSelect.value));
            loadConversation(currentConversationId);
            updateChatHistory();
            setupEvents();
        });

        htmlModal.addEventListener('click', e => {
            if (e.target === htmlModal || e.target.classList.contains('modal-close')) {
                htmlModal.style.display = 'none';
            }
        });

        function setupEvents() {
            menuToggle.addEventListener('click', e => {
                e.stopPropagation();
                if (sidebar.classList.contains('active')) closeSidebar();
                else openSidebar();
            });
            document.addEventListener('click', e => {
                if (sidebar.classList.contains('active') && !sidebar.contains(e.target) && e.target !== menuToggle) {
                    closeSidebar();
                }
            });
            sendBtn.onclick = sendMessage;
            stopBtn.onclick = stopGeneration;
            input.onkeydown = e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            };
            input.oninput = () => {
                input.style.height = 'auto';
                input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
            };
            document.getElementById('upload-button').onclick = () => {
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = 'image/*';
                fileInput.multiple = true;
                fileInput.onchange = e => handleImageUpload(e.target.files);
                fileInput.click();
            };
            input.onpaste = e => {
                for (const item of e.clipboardData.items) {
                    if (item.type.indexOf('image') !== -1) {
                        const file = item.getAsFile();
                        const reader = new FileReader();
                        reader.onload = ev => addImagePreview(ev.target.result);
                        reader.readAsDataURL(file);
                    }
                }
            };
        }

        function handleImageUpload(files) {
            const remaining = Config.MAX_IMAGE_UPLOADS - uploadedImages.length;
            Array.from(files).slice(0, remaining).forEach(file => {
                const reader = new FileReader();
                reader.onload = e => addImagePreview(e.target.result);
                reader.readAsDataURL(file);
            });
        }

        function addImagePreview(dataUrl) {
            if (uploadedImages.length >= Config.MAX_IMAGE_UPLOADS) return;
            const base64 = dataUrl.split(',')[1];
            const id = Date.now() + Math.random();
            uploadedImages.push({id, data: base64});
            const div = document.createElement('div');
            div.className = 'image-preview-item';
            div.dataset.id = id;
            div.innerHTML = `<img src="${dataUrl}">
                             <button class="remove-image" onclick="this.parentElement.remove(); uploadedImages = uploadedImages.filter(i=>i.id!=${id})">×</button>`;
            preview.appendChild(div);
        }

        function updateChatHistory(filter = '') {
            chatHistory.innerHTML = '';
            [...conversations].reverse().filter(c => c.messages?.length && (!filter || JSON.stringify(c.messages).toLowerCase().includes(filter))).forEach(c => {
                const div = document.createElement('div');
                div.className = `history-item ${c.id === currentConversationId ? 'active' : ''}`;
                const userMsg = c.messages.find(m => m.role === 'user');
                const title = userMsg?.parts?.find(p => p.text)?.text?.trim().slice(0,50) || '[图片]';
                const aiMsg = c.messages.find(m => m.role === 'model');
                const previewText = aiMsg?.parts?.find(p => p.text)?.text?.trim().slice(0,180) || '';
                const time = new Date(c.messages[c.messages.length-1].timestamp).toLocaleString();
                div.innerHTML = `
                    <div class="history-item-title">${title}${title.length > 50 ? '...' : ''}</div>
                    <div class="history-item-preview">${previewText}${previewText.length > 180 ? '...' : ''}</div>
                    <div class="history-item-time">${time}</div>
                `;
                div.onclick = () => loadConversation(c.id);
                chatHistory.appendChild(div);
            });
        }

        function loadConversation(id) {
            if (isGenerating) return;
            currentConversationId = id;
            localStorage.setItem('currentConversationId', id);
            const conv = conversations.find(c => c.id === id) || {id, messages: []};
            messagesDiv.innerHTML = '';
            conv.messages.forEach((m, index) => {
                const text = m.parts.find(p => p.text)?.text || '';
                const imgs = m.parts.filter(p => p.inline_data).map(p => p.inline_data);
                const {div, content} = addMessage(text, m.role === 'user' ? 'user' : 'ai', imgs);
                if (m.role !== 'user') {
                    // 分批延迟渲染，避免一次性渲染大量内容导致卡顿
                    setTimeout(() => renderMessageContent(content), index * 10);
                }
            });
            currentContext = conv.messages.slice(-60);
            updateChatHistory();
            closeSidebar();
            scrollToBottom();
        }

        function addMessage(text, type, images = []) {
            const div = document.createElement('div');
            div.className = `message ${type}`;
            const content = document.createElement('div');
            content.className = 'message-content';
            div.appendChild(content);

            if (images.length) {
                const container = document.createElement('div');
                container.className = 'image-preview-container';
                images.forEach(i => {
                    const item = document.createElement('div');
                    item.className = 'image-preview-item';
                    item.innerHTML = `<img src="data:image/jpeg;base64,${i.data}">`;
                    container.appendChild(item);
                });
                div.appendChild(container);
            }

            if (type === 'user') {
                content.textContent = text || '[图片]';
            } else {
                const clean = DOMPurify.sanitize(marked.parse(text || ''), {FORBID_TAGS:['style','script']});
                content.innerHTML = clean;
            }

            messagesDiv.appendChild(div);
            scrollToBottom();
            return {div, content};
        }

        function previewHTML(code) {
            document.getElementById('html-frame').srcdoc = code;
            htmlModal.style.display = 'flex';
        }

        async function sendMessage() {
            const text = input.value.trim();
            if ((!text && uploadedImages.length === 0) || isGenerating) return;

            isGenerating = true;
            sendBtn.style.display = 'none';
            stopBtn.style.display = 'block';

            const imagesToSend = uploadedImages.map(i => i.data);
            uploadedImages = [];
            preview.innerHTML = '';

            addMessage(text || '[图片]', 'user', imagesToSend.map(d => ({data: d})));

            input.value = '';
            input.style.height = 'auto';

            loadingElement = document.createElement('div');
            loadingElement.className = 'message ai';
            loadingElement.innerHTML = '<div class="message-content"><div class="loading-dots"><span></span><span></span><span></span></div></div>';
            messagesDiv.appendChild(loadingElement);
            scrollToBottom();

            const {div: aiDiv, content: contentDiv} = addMessage('', 'ai');
            currentAiMessageDiv = aiDiv;
            currentContentDiv = contentDiv;

            const payload = {
                message: text,
                context: currentContext,
                images: imagesToSend,
                model_name: modelSelect.value,
                api_key: apiKeyInput.value
            };

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });

                if (!res.ok) throw new Error('请求失败');

                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let fullText = '';

                while (true) {
                    const {done, value} = await reader.read();
                    if (done) {
                        finalize(text, fullText, imagesToSend);
                        break;
                    }

                    buffer += decoder.decode(value, {stream: true});
                    let pos;
                    while ((pos = buffer.indexOf('\n\n')) > -1) {
                        const line = buffer.slice(0, pos).trim();
                        buffer = buffer.slice(pos + 2);
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.slice(6));
                            if (data.text) {
                                fullText += data.text;
                                const clean = DOMPurify.sanitize(marked.parse(fullText), {FORBID_TAGS:['style','script']});
                                currentContentDiv.innerHTML = clean;
                                renderMessageContent(currentContentDiv);
                                scrollToBottom();
                            }
                            if (data.error) {
                                currentContentDiv.innerHTML = `<span style="color:#ff4444">${data.error}</span>`;
                                finalize(text, '', imagesToSend);
                            }
                        }
                    }
                }
            } catch (e) {
                if (loadingElement && loadingElement.parentNode) loadingElement.remove();
                if (currentAiMessageDiv && currentAiMessageDiv.parentNode) currentAiMessageDiv.remove();
                addMessage('网络错误，请检查连接', 'ai');
                finalize(text, '', imagesToSend);
            }
        }

        function stopGeneration() {
            isGenerating = false;
            sendBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            if (loadingElement && loadingElement.parentNode) loadingElement.remove();
            loadingElement = null;
            currentAiMessageDiv = null;
            currentContentDiv = null;
        }

        function finalize(userText, aiText, images) {
            if (loadingElement && loadingElement.parentNode) loadingElement.remove();
            loadingElement = null;

            currentContext.push({role:'user', parts:[{text:userText||'[图片]'}].concat(images.map(d=>({inline_data:{mime_type:'image/jpeg',data:d}})))});
            currentContext.push({role:'model', parts:[{text:aiText}]});
            currentContext = currentContext.slice(-60);

            let conv = conversations.find(c => c.id === currentConversationId);
            if (!conv) { conv = {id:currentConversationId, messages:[]}; conversations.push(conv); }

            conv.messages.push(
                {role:'user', parts:[{text:userText||'[图片]'}].concat(images.map(d=>({inline_data:{mime_type:'image/jpeg',data:d}}))), timestamp:new Date().toISOString()},
                {role:'model', parts:[{text:aiText}], timestamp:new Date().toISOString()}
            );

            localStorage.setItem('conversations', JSON.stringify(conversations));
            updateChatHistory();
            isGenerating = false;
            sendBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            currentAiMessageDiv = null;
            currentContentDiv = null;
            input.focus();
        }

        function startNewChat() {
            if (isGenerating) return;
            currentConversationId = Date.now().toString();
            localStorage.setItem('currentConversationId', currentConversationId);
            messagesDiv.innerHTML = '';
            currentContext = [];
            if (!conversations.find(c => c.id === currentConversationId)) conversations.push({id:currentConversationId, messages:[]});
            localStorage.setItem('conversations', JSON.stringify(conversations));
            updateChatHistory();
            closeSidebar();
        }

        function clearHistory() {
            if (confirm('确定要清空所有历史记录吗？')) {
                conversations = [];
                localStorage.removeItem('conversations');
                startNewChat();
                updateChatHistory();
                closeSidebar();
            }
        }
    </script>
</body>
</html>'''

def main():
    parser = argparse.ArgumentParser(description='GAIWeb - Gemini 聊天界面')
    parser.add_argument('--apikey', '-k', type=str, default=None, help='Gemini API Key')
    parser.add_argument('--port', '-p', type=int, default=5000, help='端口号')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='监听地址')
    args = parser.parse_args()

    if args.apikey:
        global default_api_key
        default_api_key = args.apikey.strip()
        logger.info("已使用启动时提供的 API Key")

    logger.info(f"GAIWeb 已启动 → http://localhost:{args.port}")
    app.run(host=args.host, port=args.port, threaded=True)

if __name__ == '__main__':
    main()