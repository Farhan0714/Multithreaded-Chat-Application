import threading
import time
import os
import sqlite3
import json
import secrets
import random
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "farhanalam01062004@gmail.com"
SMTP_PASSWORD = "oyebvltvyjpaovcq"

def send_otp_email(email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = email
        msg['Subject'] = "ZetaChat Pro - Email Verification OTP"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #6366f1; text-align: center;">ZetaChat Pro</h2>
                    <h3 style="color: #333;">Email Verification</h3>
                    <p style="color: #666; font-size: 16px;">Your One-Time Password (OTP) for email verification is:</p>
                    <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; color: #6366f1; letter-spacing: 8px;">{otp}</span>
                    </div>
                    <p style="color: #666; font-size: 14px;">This OTP is valid for 5 minutes.</p>
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">If you didn't request this, please ignore this email.</p>
                </div>
            </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"\n{'=' * 50}")
        print(f"📧 OTP SENT TO: {email}")
        print(f"🔑 OTP CODE: {otp}")
        print(f"⏰ Valid for 5 minutes")
        print(f"{'=' * 50}\n")

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def ollama_ai_response(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2:1b",
        "prompt": f"You are a helpful AI assistant in a chat application. Be friendly, concise, and helpful. User question: {prompt}",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if "response" in data:
            return data["response"].strip()
        else:
            return "Hello! I'm your AI assistant. How can I help you today?"
    except requests.exceptions.ConnectionError:
        return "🤖 AI service is not available. Please make sure Ollama is running with: `ollama serve`"
    except requests.exceptions.Timeout:
        return "⏰ AI is thinking too long. Please try a simpler question."
    except Exception as e:
        return f"🤖 AI temporarily unavailable. Error: {str(e)}"

def ollama_translate(text: str, target_lang: str = 'fr') -> str:
    url = "http://localhost:11434/api/generate"

    lang_map = {
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'hi': 'Hindi',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ar': 'Arabic'
    }

    target_language = lang_map.get(target_lang, 'French')

    payload = {
        "model": "llama3.2:1b",
        "prompt": f"Translate the following text to {target_language}. Only provide the translation, nothing else:\n\n{text}",
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        if "response" in data:
            translation = data["response"].strip()
            translation = translation.split('\n')[0].strip()
            return translation
        return text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def simple_sentiment_analysis(text):
    text_lower = text.lower()

    positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'wonderful', 'amazing', 'fantastic', 'best']
    negative_words = ['bad', 'terrible', 'hate', 'awful', 'worst', 'horrible', 'sad', 'angry', 'disappointed']

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=100000000)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'files'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'voice'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)

DB_PATH = 'chat_app1.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

otp_storage = {}

PROFANITY_WORDS = [
    'damn', 'hell', 'stupid', 'idiot', 'fool', 'ass', 'bastard', 'shit',
]

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, 
                  email TEXT UNIQUE, 
                  password_hash TEXT,
                  profile_pic TEXT, 
                  bio TEXT,
                  is_verified INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS rooms
                 (room_id TEXT PRIMARY KEY, 
                  room_name TEXT, 
                  room_description TEXT,
                  is_private INTEGER, 
                  private_code TEXT, 
                  creator TEXT, 
                  room_avatar TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  room_id TEXT, 
                  username TEXT,
                  message TEXT, 
                  message_type TEXT, 
                  file_path TEXT, 
                  file_name TEXT,
                  file_size INTEGER,
                  reply_to INTEGER,
                  is_translated INTEGER DEFAULT 0,
                  original_language TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  status TEXT DEFAULT 'sent',
                  is_blocked INTEGER DEFAULT 0,
                  is_deleted INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS message_reactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  message_id INTEGER,
                  username TEXT,
                  reaction TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS message_reads
                 (message_id INTEGER, 
                  username TEXT, 
                  read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (message_id, username))''')

    c.execute('''CREATE TABLE IF NOT EXISTS room_members
                 (room_id TEXT,
                  username TEXT,
                  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  has_joined_before INTEGER DEFAULT 0,
                  PRIMARY KEY (room_id, username))''')

    c.execute('''CREATE TABLE IF NOT EXISTS game_scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  room_id TEXT,
                  username TEXT,
                  game_type TEXT,
                  score INTEGER,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

init_db()

users = {}
rooms = {}
room_info = {}
typing_users = {}
online_users = set()
active_calls = {}
user_sockets = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def generate_room_code():
    return str(random.randint(100000, 999999))

def verify_otp(email, otp):
    if email in otp_storage:
        stored_data = otp_storage[email]
        if stored_data['otp'] == otp and datetime.now() < stored_data['expiry']:
            del otp_storage[email]
            return True
    return False

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def analyze_sentiment(text):
    text_lower = text.lower()

    for word in PROFANITY_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            return {'is_abusive': True, 'sentiment': 'negative'}

    sentiment = simple_sentiment_analysis(text)
    return {'is_abusive': False, 'sentiment': sentiment, 'polarity': 0}

def format_message(username, message, msg_type='text', file_path=None, message_id=None,
                   status='sent', profile_pic=None, reactions=None, reply_to=None,
                   file_name=None, file_size=None, is_deleted=False):
    return {
        'id': message_id,
        'username': username,
        'message': message,
        'timestamp': datetime.now().strftime('%H:%M'),
        'type': msg_type,
        'file_path': file_path,
        'file_name': file_name,
        'file_size': file_size,
        'status': status,
        'profile_pic': profile_pic,
        'reactions': reactions or {},
        'reply_to': reply_to,
        'is_deleted': is_deleted
    }

def save_message(room_id, username, message, msg_type='text', file_path=None,
                 reply_to=None, is_blocked=False, file_name=None, file_size=None):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO messages (room_id, username, message, message_type, 
                     file_path, file_name, file_size, reply_to, is_blocked)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (room_id, username, message, msg_type, file_path, file_name,
                   file_size, reply_to, 1 if is_blocked else 0))
        message_id = c.lastrowid
        conn.commit()
        return message_id
    except Exception as e:
        print(f"Error saving message: {e}")
        return None
    finally:
        conn.close()

def delete_message(message_id, username):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT username FROM messages WHERE id = ?', (message_id,))
        result = c.fetchone()

        if result and result[0] == username:
            c.execute('UPDATE messages SET is_deleted = 1 WHERE id = ?', (message_id,))
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Error deleting message: {e}")
        return False
    finally:
        conn.close()

def get_messages(room_id, limit=100):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''SELECT m.id, m.username, m.message, m.message_type, m.file_path, 
                     m.timestamp, m.status, m.reply_to, m.is_blocked, u.profile_pic,
                     m.file_name, m.file_size, m.is_deleted
                     FROM messages m
                     LEFT JOIN users u ON m.username = u.username
                     WHERE m.room_id = ? 
                     ORDER BY m.timestamp ASC LIMIT ?''',
                  (room_id, limit))
        messages = c.fetchall()

        result = []
        for msg in messages:
            c.execute('''SELECT username, reaction FROM message_reactions 
                         WHERE message_id = ?''', (msg[0],))
            reactions_data = c.fetchall()
            reactions = {}
            for username, reaction in reactions_data:
                if reaction not in reactions:
                    reactions[reaction] = []
                reactions[reaction].append(username)

            is_deleted = bool(msg[12])
            message_text = "[Message deleted]" if is_deleted else (
                msg[2] if not msg[8] else "[Message blocked due to inappropriate content]")

            result.append({
                'id': msg[0],
                'username': msg[1],
                'message': message_text,
                'type': msg[3],
                'file_path': msg[4] if not is_deleted else None,
                'timestamp': datetime.fromisoformat(msg[5]).strftime('%H:%M') if msg[5] else '',
                'status': msg[6],
                'reply_to': msg[7],
                'is_blocked': bool(msg[8]),
                'profile_pic': msg[9],
                'file_name': msg[10],
                'file_size': msg[11],
                'is_deleted': is_deleted,
                'reactions': reactions
            })

        return result
    except Exception as e:
        print(f"Error getting messages: {e}")
        return []
    finally:
        conn.close()

def update_message_status(message_id, status):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('UPDATE messages SET status = ? WHERE id = ?', (status, message_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating message status: {e}")
    finally:
        conn.close()

def add_reaction(message_id, username, reaction):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id FROM message_reactions 
                 WHERE message_id = ? AND username = ? AND reaction = ?''',
              (message_id, username, reaction))
    existing = c.fetchone()

    if existing:
        c.execute('''DELETE FROM message_reactions 
                     WHERE message_id = ? AND username = ? AND reaction = ?''',
                  (message_id, username, reaction))
        action = 'removed'
    else:
        c.execute('''INSERT INTO message_reactions (message_id, username, reaction)
                     VALUES (?, ?, ?)''', (message_id, username, reaction))
        action = 'added'

    conn.commit()
    conn.close()
    return action

def create_room(room_name, room_description='', is_private=False, creator=None, room_avatar=None):
    room_id = secrets.token_urlsafe(16)
    private_code = generate_room_code() if is_private else None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO rooms (room_id, room_name, room_description, is_private, 
                     private_code, creator, room_avatar)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (room_id, room_name, room_description, 1 if is_private else 0,
                   private_code, creator, room_avatar))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return None, None
    conn.close()

    room_info[room_id] = {
        'name': room_name,
        'description': room_description,
        'is_private': is_private,
        'code': private_code,
        'creator': creator,
        'avatar': room_avatar
    }
    rooms[room_id] = set()
    return room_id, private_code


def get_user_profile(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT username, email, profile_pic, bio, is_verified, last_seen 
                 FROM users WHERE username = ?''', (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return {
            'username': result[0],
            'email': result[1],
            'profile_pic': result[2],
            'bio': result[3],
            'is_verified': bool(result[4]),
            'last_seen': result[5],
            'status': 'online' if result[0] in online_users else 'offline'
        }
    return None

def save_user_profile(username, email=None, profile_pic=None, bio=None, is_verified=False, password=None):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT username FROM users WHERE username = ?', (username,))
        user = c.fetchone()

        if user:
            updates = []
            values = []
            if email is not None:
                updates.append('email = ?')
                values.append(email)
            if profile_pic is not None:
                updates.append('profile_pic = ?')
                values.append(profile_pic)
            if bio is not None:
                updates.append('bio = ?')
                values.append(bio)
            if is_verified:
                updates.append('is_verified = ?')
                values.append(1)
            if password is not None:
                updates.append('password_hash = ?')
                values.append(generate_password_hash(password))
            if updates:
                updates.append('last_seen = ?')
                values.append(datetime.now().isoformat())
                values.append(username)
                c.execute(f'UPDATE users SET {", ".join(updates)} WHERE username = ?', values)
        else:
            password_hash = generate_password_hash(password) if password else ''
            c.execute('''INSERT INTO users (username, email, password_hash, profile_pic, bio, is_verified) 
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (username, email or '', password_hash, profile_pic or '', bio or '', 1 if is_verified else 0))
        conn.commit()
    except Exception as e:
        print(f"Error saving user profile: {e}")
    finally:
        conn.close()


def save_game_score(room_id, username, game_type, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO game_scores (room_id, username, game_type, score)
                 VALUES (?, ?, ?, ?)''', (room_id, username, game_type, score))
    conn.commit()
    conn.close()


def get_game_leaderboard(room_id, game_type, limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT username, MAX(score) as best_score
                 FROM game_scores
                 WHERE room_id = ? AND game_type = ?
                 GROUP BY username
                 ORDER BY best_score DESC
                 LIMIT ?''', (room_id, game_type, limit))
    results = c.fetchall()
    conn.close()
    return [{'username': r[0], 'score': r[1]} for r in results]


def get_all_rooms():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT room_id, room_name, is_private, room_description, room_avatar 
                 FROM rooms ORDER BY created_at DESC''')
    result = c.fetchall()
    conn.close()
    return [{
        'id': r[0],
        'name': r[1],
        'is_private': bool(r[2]),
        'description': r[3],
        'avatar': r[4]
    } for r in result]


def get_user_rooms(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT DISTINCT r.room_id, r.room_name, r.is_private, r.private_code
                 FROM rooms r
                 JOIN room_members rm ON r.room_id = rm.room_id
                 WHERE rm.username = ?''', (username,))
    results = c.fetchall()
    conn.close()
    return {r[0]: {'name': r[1], 'is_private': bool(r[2]), 'code': r[3]} for r in results}


def add_user_to_room(username, room_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''SELECT has_joined_before FROM room_members 
                     WHERE room_id = ? AND username = ?''', (room_id, username))
        result = c.fetchone()

        if result:
            c.execute('''UPDATE room_members SET has_joined_before = 1 
                         WHERE room_id = ? AND username = ?''', (room_id, username))
            has_joined_before = True
        else:
            c.execute('''INSERT INTO room_members (room_id, username, has_joined_before)
                         VALUES (?, ?, 0)''', (room_id, username))
            has_joined_before = False

        conn.commit()
        return has_joined_before
    except Exception as e:
        print(f"Error adding user to room: {e}")
        return True
    finally:
        conn.close()


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


@app.route('/')
def index():
    return render_template('chat.html')


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email', '').strip().lower()

    if not email or not is_valid_email(email):
        return jsonify({'error': 'Invalid email address'}), 400

    otp = generate_otp()
    otp_storage[email] = {
        'otp': otp,
        'expiry': datetime.now() + timedelta(minutes=5)
    }

    if send_otp_email(email, otp):
        return jsonify({'success': True, 'message': 'OTP sent to your email'})
    else:
        return jsonify({'error': 'Failed to send OTP. Please check email configuration.'}), 500


@app.route('/api/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.json
    email = data.get('email', '').strip().lower()
    otp = data.get('otp')

    if verify_otp(email, otp):
        return jsonify({'success': True, 'verified': True})
    return jsonify({'success': False, 'verified': False, 'message': 'Invalid or expired OTP'}), 400


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    username = data.get('username', '').strip()
    profile_pic = data.get('profile_pic')

    if not email or not password or not username:
        return jsonify({'error': 'Missing required fields'}), 400

    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email address'}), 400

    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Check if email already exists
        c.execute('SELECT username FROM users WHERE email = ?', (email,))
        existing = c.fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400

        # Check if username already exists
        c.execute('SELECT email FROM users WHERE username = ?', (username,))
        existing = c.fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Username already taken'}), 400

        password_hash = generate_password_hash(password)
        c.execute('''INSERT INTO users (username, email, password_hash, profile_pic, is_verified)
                     VALUES (?, ?, ?, ?, ?)''',
                  (username, email, password_hash, profile_pic or '', 1))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Registration successful'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT username, password_hash, profile_pic, bio, is_verified FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        username, password_hash, profile_pic, bio, is_verified = user

        if check_password_hash(password_hash, password):
            session.permanent = True
            session['username'] = username
            session['email'] = email
            session['profile_pic'] = profile_pic

            return jsonify({
                'success': True,
                'username': username,
                'profile_pic': profile_pic,
                'bio': bio,
                'is_verified': bool(is_verified),
                'email': email
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email', '').strip().lower()

    if not email or not is_valid_email(email):
        return jsonify({'error': 'Invalid email address'}), 400

    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT username FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'No account found with this email'}), 404

        otp = generate_otp()
        otp_storage[email] = {
            'otp': otp,
            'expiry': datetime.now() + timedelta(minutes=5),
            'type': 'password_reset'
        }

        if send_otp_email(email, otp):
            return jsonify({'success': True, 'message': 'Password reset code sent to your email'})
        else:
            return jsonify({'error': 'Failed to send reset code'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email', '').strip().lower()
    otp = data.get('otp')
    new_password = data.get('new_password')

    if not email or not otp or not new_password:
        return jsonify({'error': 'Missing required fields'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if not verify_otp(email, otp):
        return jsonify({'error': 'Invalid or expired reset code'}), 400

    conn = get_db_connection()
    c = conn.cursor()
    try:
        password_hash = generate_password_hash(new_password)
        c.execute('UPDATE users SET password_hash = ? WHERE email = ?', (password_hash, email))

        if c.rowcount == 0:
            conn.close()
            return jsonify({'error': 'User not found'}), 404

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Password reset successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('username'),
            'email': session.get('email'),
            'profile_pic': session.get('profile_pic')
        })
    return jsonify({'logged_in': False})


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    file_type = request.form.get('type', 'file')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_type == 'voice':
        folder = 'voice'
    elif file_type == 'profile':
        folder = 'profile_pics'
    elif file_type == 'photo' or file.content_type.startswith('image/'):
        folder = 'photos'
    elif file_type == 'video' or file.content_type.startswith('video/'):
        folder = 'videos'
    else:
        folder = 'files'

    filepath = os.path.join(folder, filename)
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filepath)
    file.save(full_path)

    return jsonify({
        'file_path': f'/uploads/{filepath}',
        'filename': filename,
        'file_size': file_size,
        'file_size_formatted': format_file_size(file_size)
    })


@app.route('/api/translate', methods=['POST'])
def translate_message():
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang', 'fr')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    translated = ollama_translate(text, target_lang)
    return jsonify({'translated': translated, 'success': True})


@socketio.on('connect')
def on_connect():
    emit('rooms_list', get_all_rooms())


@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    user = users.pop(sid, None)
    if user:
        username = user['username']
        online_users.discard(username)

        if username in user_sockets:
            del user_sockets[username]

        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('UPDATE users SET last_seen = ? WHERE username = ?',
                      (datetime.now().isoformat(), username))
            conn.commit()
        except Exception as e:
            print(f"Error updating last seen: {e}")
        finally:
            conn.close()

        for room_id in list(typing_users.keys()):
            if username in typing_users[room_id]:
                del typing_users[room_id][username]
                socketio.emit('typing', {'username': username, 'typing': False}, room=room_id)

        for room_name in list(rooms.keys()):
            if sid in rooms[room_name]:
                rooms[room_name].discard(sid)

        socketio.emit('user_status_change', {
            'username': username,
            'status': 'offline',
            'last_seen': datetime.now().strftime('%H:%M')
        })


@socketio.on('join')
def on_join(data):
    sid = request.sid
    username = data.get('username')
    email = data.get('email', '')
    profile_pic = data.get('profile_pic')

    if not username:
        emit('error', {'message': 'Username required'})
        return

    profile = get_user_profile(username)
    if profile:
        profile_pic = profile.get('profile_pic') or profile_pic
        bio = profile.get('bio', '')
        is_verified = profile.get('is_verified', True)
    else:
        bio = ''
        is_verified = True

    users[sid] = {
        'username': username,
        'profile_pic': profile_pic,
        'email': email,
        'bio': bio,
        'is_verified': is_verified
    }

    user_sockets[username] = sid

    was_offline = username not in online_users
    online_users.add(username)

    room = 'global'
    rooms.setdefault(room, set()).add(sid)
    join_room(room)

    has_joined_before = add_user_to_room(username, room)

    if not has_joined_before:
        join_msg = format_message('System', f'{username} joined the chat', 'system')
        save_message(room, 'System', f'{username} joined the chat', 'system')
        emit('message', join_msg, room=room)

    if was_offline:
        socketio.emit('user_online_notification', {
            'username': username,
            'profile_pic': profile_pic
        })

    socketio.emit('user_status_change', {
        'username': username,
        'status': 'online',
        'profile_pic': profile_pic
    })

    online_user_list = []
    for user_sid, user_data in users.items():
        if user_data['username'] != username:
            online_user_list.append({
                'username': user_data['username'],
                'profile_pic': user_data.get('profile_pic'),
                'status': 'online'
            })

    emit('users_update', online_user_list, broadcast=True)

    user_rooms = get_user_rooms(username)
    emit('join_success', {
        'room': room,
        'username': username,
        'profile_pic': profile_pic,
        'email': email,
        'bio': bio,
        'is_verified': is_verified,
        'saved_rooms': user_rooms
    })
    emit('message_history', get_messages(room))


@socketio.on('message')
def handle_message(data):
    sid = request.sid
    current_user = users.get(sid)
    if not current_user:
        return

    username = current_user['username']
    room = data.get('room', 'global')
    msg_text = data.get('message', '')
    msg_type = data.get('type', 'text')
    file_path = data.get('file_path')
    file_name = data.get('file_name')
    file_size = data.get('file_size')
    reply_to = data.get('reply_to')

    if msg_text.strip().lower().startswith('/ai '):
        prompt = msg_text[4:].strip()
        if prompt:
            question_id = save_message(room, username, msg_text, 'text', None, reply_to, False)
            question_obj = format_message(username, msg_text, 'text', None, question_id,
                                          'sent', current_user.get('profile_pic'), {}, reply_to)
            emit('message', question_obj, room=room, include_self=True)

            def get_ai_response():
                socketio.sleep(0.5)
                ai_response = ollama_ai_response(prompt)
                ai_msg_id = save_message(room, 'AI Assistant 🤖', ai_response, 'ai')
                ai_msg_obj = format_message('AI Assistant 🤖', ai_response, 'ai', None, ai_msg_id,
                                            'sent', '/static/img/default-avatar.png', {}, None)
                socketio.emit('message', ai_msg_obj, room=room, namespace='/')

            socketio.start_background_task(get_ai_response)
            return

    is_blocked = False
    if msg_type == 'text' and msg_text:
        analysis = analyze_sentiment(msg_text)
        if analysis['is_abusive']:
            is_blocked = True
            emit('message_blocked', {
                'message': 'Your message contains inappropriate content and has been blocked.'
            })

    message_id = save_message(room, username, msg_text, msg_type, file_path,
                              reply_to, is_blocked, file_name, file_size)

    if not is_blocked:
        msg_obj = format_message(username, msg_text, msg_type, file_path, message_id,
                                 'sent', current_user.get('profile_pic'), {}, reply_to,
                                 file_name, file_size)

        emit('message', msg_obj, room=room, include_self=True)

        def mark_delivered():
            socketio.sleep(0.1)
            update_message_status(message_id, 'delivered')
            socketio.emit('message_status', {
                'message_id': message_id,
                'status': 'delivered'
            }, room=room, namespace='/')

        socketio.start_background_task(mark_delivered)

@socketio.on('delete_message')
def handle_delete_message(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    message_id = data.get('message_id')
    room = data.get('room')

    if delete_message(message_id, user['username']):
        socketio.emit('message_deleted', {
            'message_id': message_id
        }, room=room)

@socketio.on('typing')
def handle_typing(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    room = data.get('room')
    is_typing = data.get('typing', False)

    if room:
        if room not in typing_users:
            typing_users[room] = {}

        if is_typing:
            typing_users[room][user['username']] = time.time()
        elif user['username'] in typing_users[room]:
            del typing_users[room][user['username']]

        emit('typing', {
            'username': user['username'],
            'typing': is_typing,
            'profile_pic': user.get('profile_pic')
        }, room=room, include_self=False)

@socketio.on('add_reaction')
def handle_add_reaction(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    message_id = data.get('message_id')
    reaction = data.get('reaction')
    room = data.get('room')

    if message_id and reaction:
        action = add_reaction(message_id, user['username'], reaction)

        socketio.emit('reaction_update', {
            'message_id': message_id,
            'reaction': reaction,
            'username': user['username'],
            'action': action
        }, room=room)

@socketio.on('game_score')
def handle_game_score(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    room = data.get('room')
    game_type = data.get('game_type')
    score = data.get('score')

    save_game_score(room, user['username'], game_type, score)
    leaderboard = get_game_leaderboard(room, game_type)

    socketio.emit('game_leaderboard', {
        'game_type': game_type,
        'leaderboard': leaderboard
    }, room=room)

@socketio.on('translate_message')
def handle_translate_message(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    message_id = data.get('message_id')
    target_lang = data.get('target_lang', 'fr')
    original_text = data.get('text')

    if original_text:
        translated = ollama_translate(original_text, target_lang)
        emit('message_translated', {
            'message_id': message_id,
            'translated': translated,
            'target_lang': target_lang
        })

@socketio.on('start_call')
def handle_start_call(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    room = data.get('room')
    call_type = data.get('call_type', 'voice')
    target_user = data.get('target_user')

    call_id = secrets.token_urlsafe(16)
    active_calls[call_id] = {
        'caller': user['username'],
        'caller_sid': sid,
        'room': room,
        'type': call_type,
        'started_at': datetime.now().isoformat()
    }

    if target_user and target_user in user_sockets:
        target_sid = user_sockets[target_user]
        socketio.emit('incoming_call', {
            'call_id': call_id,
            'from': user['username'],
            'profile_pic': user.get('profile_pic'),
            'call_type': call_type,
            'caller_sid': sid
        }, room=target_sid)
    else:
        socketio.emit('incoming_call', {
            'call_id': call_id,
            'from': user['username'],
            'profile_pic': user.get('profile_pic'),
            'call_type': call_type,
            'caller_sid': sid
        }, room=room, include_self=False)

@socketio.on('answer_call')
def handle_answer_call(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    call_id = data.get('call_id')
    answer = data.get('answer')

    if call_id in active_calls:
        call_info = active_calls[call_id]
        caller_sid = call_info.get('caller_sid')

        if caller_sid:
            socketio.emit('call_answered', {
                'call_id': call_id,
                'answered_by': user['username'],
                'answer': answer,
                'answerer_sid': sid
            }, room=caller_sid)

        emit('call_answered', {
            'call_id': call_id,
            'answered_by': user['username'],
            'answer': answer,
            'answerer_sid': sid
        })

@socketio.on('end_call')
def handle_end_call(data):
    call_id = data.get('call_id')

    if call_id in active_calls:
        call_info = active_calls[call_id]

        socketio.emit('call_ended', {
            'call_id': call_id
        }, room=call_info['room'])

        del active_calls[call_id]

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    target_sid = data.get('target_sid')
    offer = data.get('offer')
    call_id = data.get('call_id')

    if target_sid:
        socketio.emit('webrtc_offer', {
            'from': user['username'],
            'from_sid': sid,
            'offer': offer,
            'call_id': call_id
        }, room=target_sid)

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    target_sid = data.get('target_sid')
    answer = data.get('answer')
    call_id = data.get('call_id')

    if target_sid:
        socketio.emit('webrtc_answer', {
            'from': user['username'],
            'from_sid': sid,
            'answer': answer,
            'call_id': call_id
        }, room=target_sid)

@socketio.on('webrtc_signal')
def handle_webrtc_signal(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    room = data.get('room')
    signal_data = data.get('signal')
    signal_type = data.get('type')
    target_sid = data.get('target_sid')

    if target_sid:
        socketio.emit('webrtc_signal', {
            'from': user['username'],
            'from_sid': sid,
            'signal': signal_data,
            'type': signal_type
        }, room=target_sid)
    else:
        socketio.emit('webrtc_signal', {
            'from': user['username'],
            'from_sid': sid,
            'signal': signal_data,
            'type': signal_type
        }, room=room, include_self=False)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        return

    target_sid = data.get('target_sid')
    candidate = data.get('candidate')
    call_id = data.get('call_id')

    if target_sid:
        socketio.emit('ice_candidate', {
            'from': user['username'],
            'from_sid': sid,
            'candidate': candidate,
            'call_id': call_id
        }, room=target_sid)

@socketio.on('create_room')
def handle_create_room(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        emit('error', {'message': 'Not authenticated'})
        return

    room_name = data.get('name', 'New Room')
    room_description = data.get('description', '')
    is_private = data.get('is_private', False)
    room_id, code = create_room(room_name, room_description, is_private, user['username'])

    if room_id:
        add_user_to_room(user['username'], room_id)

        emit('room_created', {
            'room_id': room_id,
            'room_name': room_name,
            'code': code,
            'description': room_description,
            'is_private': is_private
        })
        socketio.emit('rooms_list', get_all_rooms())

        print(f"\n{'=' * 50}")
        print(f"🏠 NEW ROOM CREATED")
        print(f"{'=' * 50}")
        print(f"Room Name: {room_name}")
        print(f"Room ID: {room_id}")
        if is_private:
            print(f"🔒 PRIVATE ROOM CODE: {code}")
            print(f"⚠️ Share this code with others to let them join!")
        print(f"{'=' * 50}\n")
    else:
        emit('error', {'message': 'Failed to create room'})

@socketio.on('join_room')
def handle_join_room(data):
    sid = request.sid
    user = users.get(sid)
    if not user:
        emit('error', {'message': 'Not authenticated'})
        return

    room_id = data.get('room_id')
    code = data.get('code')

    for r in list(rooms.keys()):
        if sid in rooms[r]:
            rooms[r].discard(sid)
            leave_room(r)

    room_data = room_info.get(room_id)
    if not room_data:
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('''SELECT room_name, is_private, private_code, room_description, room_avatar 
                         FROM rooms WHERE room_id = ?''', (room_id,))
            result = c.fetchone()
            if result:
                room_data = {
                    'name': result[0],
                    'is_private': bool(result[1]),
                    'code': result[2],
                    'description': result[3],
                    'avatar': result[4]
                }
                room_info[room_id] = room_data
        except Exception as e:
            print(f"Error getting room: {e}")
        finally:
            conn.close()

    if room_data:
        user_rooms = get_user_rooms(user['username'])

        if room_id in user_rooms:
            pass
        elif room_data['is_private']:
            if room_data['code'] != code:
                emit('error', {'message': 'Invalid room code'})
                return

        has_joined_before = add_user_to_room(user['username'], room_id)

        rooms.setdefault(room_id, set()).add(sid)
        join_room(room_id)

        if not has_joined_before:
            join_msg = format_message('System', f"{user['username']} joined", 'system')
            save_message(room_id, 'System', f"{user['username']} joined", 'system')
            emit('message', join_msg, room=room_id)

        emit('room_joined', {
            'room_id': room_id,
            'room_name': room_data['name'],
            'is_private': room_data['is_private'],
            'description': room_data.get('description', ''),
            'avatar': room_data.get('avatar')
        })

        emit('message_history', get_messages(room_id))


@socketio.on('start_private')
def start_private(data):
    sid = request.sid
    target_user = data.get('target')
    current_user = users.get(sid)
    if not target_user or not current_user:
        return

    username = current_user['username']
    room = f"private_{min(username, target_user)}_{max(username, target_user)}"

    if sid in rooms:
        for r in list(rooms.keys()):
            if sid in rooms[r]:
                rooms[r].discard(sid)
                leave_room(r)

    rooms.setdefault(room, set()).add(sid)
    target_sid = None
    for s, u in users.items():
        if u['username'] == target_user:
            target_sid = s
            break

    if target_sid:
        rooms[room].add(target_sid)
        join_room(room, sid=target_sid)
        emit('private_started', {'room': room, 'partner': username}, room=target_sid)

    join_room(room, sid=sid)
    emit('private_started', {'room': room, 'partner': target_user})

    emit('message_history', get_messages(room))

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 ZetaChat Pro Server Starting...")
    print("=" * 70)
    print(f"📱 Access the app at: http://localhost:4000")
    print(f"🌐 Or from other devices: http://YOUR_IP:4000")
    print(f"🤖 AI Features: Type '/ai your question' in chat")
    print(f"📧 Email Configuration: Update SMTP credentials in app.py")
    print("=" * 70)
    socketio.run(app, host='0.0.0.0', port=4000, debug=True, allow_unsafe_werkzeug=True)