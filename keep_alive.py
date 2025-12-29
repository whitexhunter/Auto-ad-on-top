from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Multi-User Auto-Ad Bot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 800px;
                width: 100%;
                text-align: center;
                backdrop-filter: blur(10px);
            }
            
            h1 {
                color: #333;
                margin-bottom: 20px;
                font-size: 2.5em;
            }
            
            .status {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 10px 25px;
                border-radius: 50px;
                font-weight: bold;
                margin: 20px 0;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .info-box {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 15px;
                margin: 25px 0;
                text-align: left;
                border-left: 5px solid #667eea;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 25px 0;
            }
            
            .stat-box {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .stat-box h3 {
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .instructions {
                text-align: left;
                margin: 30px 0;
                line-height: 1.6;
            }
            
            .instructions ol {
                margin-left: 20px;
                margin-top: 10px;
            }
            
            .instructions li {
                margin: 10px 0;
            }
            
            .footer {
                margin-top: 30px;
                color: #666;
                font-size: 0.9em;
            }
            
            .emoji {
                font-size: 1.5em;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1><span class="emoji">🤖</span> Multi-User Auto-Ad Bot</h1>
            
            <div class="status">
                <span class="emoji">✅</span> SYSTEM IS RUNNING
            </div>
            
            <div class="info-box">
                <h2><span class="emoji">📊</span> System Status</h2>
                <p>This bot allows multiple users to run automated Discord advertising campaigns simultaneously.</p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <h3><span class="emoji">👥</span> Users</h3>
                    <p>Unlimited</p>
                </div>
                <div class="stat-box">
                    <h3><span class="emoji">🚀</span> Status</h3>
                    <p>Active</p>
                </div>
                <div class="stat-box">
                    <h3><span class="emoji">⚡</span> Performance</h3>
                    <p>24/7 Uptime</p>
                </div>
                <div class="stat-box">
                    <h3><span class="emoji">🛡️</span> Security</h3>
                    <p>Protected</p>
                </div>
            </div>
            
            <div class="instructions">
                <h2><span class="emoji">📝</span> How to Use</h2>
                <ol>
                    <li>Invite the Discord bot to your server</li>
                    <li>Use <code>!setup</code> command in Discord</li>
                    <li>Add your Discord tokens</li>
                    <li>Add target channel IDs</li>
                    <li>Write your advertisement messages</li>
                    <li>Start your bot with one click!</li>
                </ol>
            </div>
            
            <div class="footer">
                <p><span class="emoji">⚠️</span> Use responsibly and follow Discord's Terms of Service</p>
                <p>System auto-restarts every 24 hours for maintenance</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK", 200

@app.route('/api/status')
def status():
    import json, os
    status = {
        "status": "running",
        "timestamp": time.time(),
        "service": "discord-auto-ad-bot"
    }
    return json.dumps(status)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("✅ Keep-alive server started on port 8080")
    return t
