import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from functools import wraps
import sqlite3
import threading

app = Flask(__name__, static_folder='.')
CORS(app)

# Database setup
DB_PATH = 'analytics.db'

def init_database():
    """Initialize the analytics database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            session_id TEXT,
            user_message TEXT,
            response_text TEXT,
            api_provider TEXT,
            model_name TEXT,
            tokens_prompt INTEGER,
            tokens_completion INTEGER,
            tokens_total INTEGER,
            response_time REAL,
            success BOOLEAN,
            error_message TEXT
        )
    ''')
    
    # Create hourly stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hourly_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hour_timestamp TEXT,
            total_requests INTEGER,
            successful_requests INTEGER,
            failed_requests INTEGER,
            total_tokens INTEGER,
            avg_response_time REAL,
            groq_requests INTEGER,
            gemini_requests INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Rate limiting
last_request_time = {}
REQUEST_COOLDOWN = 1

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        if client_ip in last_request_time:
            time_since_last = current_time - last_request_time[client_ip]
            if time_since_last < REQUEST_COOLDOWN:
                return jsonify({'error': 'Too many requests. Please wait.'}), 429
        
        last_request_time[client_ip] = current_time
        return f(*args, **kwargs)
    return decorated_function

conversations = {}

def estimate_tokens(text):
    """Rough token estimation (1 token ≈ 4 characters for English)"""
    return len(text) // 4

def log_request(session_id, user_message, response_text, api_provider, model_name, 
                response_time, success=True, error_message=None):
    """Log request details to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        tokens_prompt = estimate_tokens(user_message)
        tokens_completion = estimate_tokens(response_text) if response_text else 0
        tokens_total = tokens_prompt + tokens_completion
        
        cursor.execute('''
            INSERT INTO requests 
            (timestamp, session_id, user_message, response_text, api_provider, 
             model_name, tokens_prompt, tokens_completion, tokens_total, 
             response_time, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            time.time(),
            session_id,
            user_message,
            response_text,
            api_provider,
            model_name,
            tokens_prompt,
            tokens_completion,
            tokens_total,
            response_time,
            success,
            error_message
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging request: {str(e)}")

@app.route('/')
def index():
    return send_from_directory('.', 'chatbot_interface.html')

@app.route('/analytics')
def analytics():
    return send_from_directory('.', 'analytics_dashboard.html')

@app.route('/api/chat', methods=['POST'])
@rate_limit
def chat():
    start_time = time.time()
    api_provider = None
    model_name = None
    response_text = None
    error_message = None
    success = False
    
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        if session_id not in conversations:
            conversations[session_id] = []
        
        conversations[session_id].append({
            'role': 'user',
            'content': user_message
        })
        
        # Try Groq first (faster and more quota)
        response_text, api_provider, model_name = try_groq_api(conversations[session_id])
        
        # If Groq fails, try Google Gemini
        if response_text is None:
            print("Groq failed, trying Google Gemini...")
            response_text, api_provider, model_name = try_gemini_api(conversations[session_id])
        
        if response_text is None:
            error_message = 'All AI services are currently unavailable'
            response_time = time.time() - start_time
            log_request(session_id, user_message, "", api_provider or "none", 
                       model_name or "none", response_time, False, error_message)
            return jsonify({'error': error_message}), 500
        
        conversations[session_id].append({
            'role': 'assistant',
            'content': response_text
        })
        
        success = True
        response_time = time.time() - start_time
        
        # Log successful request
        log_request(session_id, user_message, response_text, api_provider, 
                   model_name, response_time, True, None)
        
        return jsonify({
            'response': response_text,
            'session_id': session_id,
            'api_provider': api_provider,
            'model': model_name,
            'response_time': round(response_time, 2),
            'tokens': {
                'prompt': estimate_tokens(user_message),
                'completion': estimate_tokens(response_text),
                'total': estimate_tokens(user_message) + estimate_tokens(response_text)
            }
        })
        
    except Exception as e:
        error_message = str(e)
        response_time = time.time() - start_time
        log_request(session_id, user_message, "", api_provider or "error", 
                   model_name or "error", response_time, False, error_message)
        print(f"Error: {error_message}")
        return jsonify({'error': f'An error occurred: {error_message}'}), 500

def try_groq_api(conversation_history):
    """Try using Groq API"""
    try:
        import requests
        
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            print("No Groq API key found")
            return None, None, None
        
        messages = [
            {
                "role": "system",
                "content": get_system_instruction()
            }
        ]
        
        for msg in conversation_history:
            messages.append({
                "role": msg['role'] if msg['role'] == 'user' else 'assistant',
                "content": msg['content']
            })
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response from Groq (Llama 3.3)")
            return result['choices'][0]['message']['content'], "Groq", "llama-3.3-70b-versatile"
        else:
            print(f"Groq API error: {response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"Groq error: {str(e)}")
        return None, None, None

def try_gemini_api(conversation_history):
    """Try using Google Gemini API"""
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        
        contents = []
        for msg in conversation_history:
            role = "user" if msg['role'] == 'user' else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg['content'])],
                )
            )
        
        generate_content_config = types.GenerateContentConfig(
            system_instruction=[
                types.Part.from_text(text=get_system_instruction()),
            ],
        )
        
        response_text = ""
        model = "gemini-1.5-flash-8b"
        
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                response_text += chunk.text
        
        print("✅ Response from Google Gemini 1.5 Flash-8B")
        return response_text, "Google Gemini", "gemini-1.5-flash-8b"
        
    except Exception as e:
        print(f"Gemini error: {str(e)}")
        return None, None, None

@app.route('/api/analytics/overview', methods=['GET'])
def analytics_overview():
    """Get overview statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total requests
        cursor.execute('SELECT COUNT(*) FROM requests')
        total_requests = cursor.fetchone()[0]
        
        # Successful requests
        cursor.execute('SELECT COUNT(*) FROM requests WHERE success = 1')
        successful_requests = cursor.fetchone()[0]
        
        # Total tokens
        cursor.execute('SELECT SUM(tokens_total) FROM requests')
        total_tokens = cursor.fetchone()[0] or 0
        
        # Average response time
        cursor.execute('SELECT AVG(response_time) FROM requests WHERE success = 1')
        avg_response_time = cursor.fetchone()[0] or 0
        
        # API provider breakdown
        cursor.execute('''
            SELECT api_provider, COUNT(*) 
            FROM requests 
            GROUP BY api_provider
        ''')
        provider_stats = dict(cursor.fetchall())
        
        # Recent requests (last 24 hours)
        twenty_four_hours_ago = time.time() - (24 * 60 * 60)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM requests 
            WHERE timestamp > ?
        ''', (twenty_four_hours_ago,))
        requests_24h = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': total_requests - successful_requests,
            'total_tokens': total_tokens,
            'avg_response_time': round(avg_response_time, 2),
            'provider_stats': provider_stats,
            'requests_24h': requests_24h,
            'success_rate': round((successful_requests / total_requests * 100) if total_requests > 0 else 0, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/timeline', methods=['GET'])
def analytics_timeline():
    """Get timeline data for graphs"""
    try:
        hours = int(request.args.get('hours', 24))
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cutoff_time = time.time() - (hours * 60 * 60)
        
        cursor.execute('''
            SELECT 
                datetime(timestamp, 'unixepoch') as time,
                COUNT(*) as count,
                SUM(tokens_total) as tokens,
                AVG(response_time) as avg_time,
                api_provider
            FROM requests
            WHERE timestamp > ?
            GROUP BY strftime('%Y-%m-%d %H', datetime(timestamp, 'unixepoch')), api_provider
            ORDER BY timestamp
        ''', (cutoff_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        timeline_data = []
        for row in results:
            timeline_data.append({
                'time': row[0],
                'count': row[1],
                'tokens': row[2] or 0,
                'avg_time': round(row[3], 2) if row[3] else 0,
                'provider': row[4]
            })
        
        return jsonify(timeline_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/recent', methods=['GET'])
def analytics_recent():
    """Get recent requests"""
    try:
        limit = int(request.args.get('limit', 50))
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                datetime(timestamp, 'unixepoch') as time,
                session_id,
                user_message,
                response_text,
                api_provider,
                model_name,
                tokens_prompt,
                tokens_completion,
                tokens_total,
                response_time,
                success,
                error_message
            FROM requests
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        recent_requests = []
        for row in results:
            recent_requests.append({
                'time': row[0],
                'session_id': row[1],
                'user_message': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
                'response_length': len(row[3]) if row[3] else 0,
                'api_provider': row[4],
                'model': row[5],
                'tokens_prompt': row[6],
                'tokens_completion': row[7],
                'tokens_total': row[8],
                'response_time': round(row[9], 2),
                'success': bool(row[10]),
                'error': row[11]
            })
        
        return jsonify(recent_requests)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in conversations:
            conversations[session_id] = []
        
        return jsonify({'message': 'Conversation cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_system_instruction():
    """Return the system instruction for the chatbot"""
    return """You are the Infoins V4 Assistant, a professional and helpful chatbot for the Infoins V4 insurance management system.

Your role:
- Provide clear, step-by-step guidance on system features
- Be professional but friendly
- Use emojis occasionally (📂 🔐 👤 etc.)
- Format responses with proper spacing and bullet points
- Focus on Admin Module features: User Management, Group Management, Staff Management, Role Permissions, Branch Management, System Settings

Always:
- Use clear paragraphs with line breaks
- Number steps when giving instructions
- Highlight important terms
- Be concise but complete
- Assume users may not be technical experts"""

if __name__ == '__main__':
    if not os.environ.get("GROQ_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: No API keys found!")
        print("Please set GROQ_API_KEY and/or GEMINI_API_KEY")
    else:
        if os.environ.get("GROQ_API_KEY"):
            print("✅ Groq API key found!")
        if os.environ.get("GEMINI_API_KEY"):
            print("✅ Gemini API key found!")
    
    print("\n🚀 Starting Infoins V4 Chatbot Server with Analytics...")
    print("📱 Chatbot: http://localhost:5000")
    print("📊 Analytics Dashboard: http://localhost:5000/analytics")
    print("🌐 Access from other devices: http://YOUR_IP_ADDRESS:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
