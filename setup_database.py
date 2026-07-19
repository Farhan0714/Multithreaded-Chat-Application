import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_PATH = 'chat_app1.db'

def create_database():

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"✅ Removed old database: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute('PRAGMA journal_mode=WAL')  # Enable Write-Ahead Logging
    c = conn.cursor()

    print(f"📦 Creating new database: {DB_PATH}")
    print("=" * 60)

    c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, 
                      email TEXT UNIQUE, 
                      password_hash TEXT,
                      profile_pic TEXT, 
                      bio TEXT,
                      is_verified INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    print("✅ Created 'users' table (with email field)")

    c.execute('''CREATE TABLE IF NOT EXISTS rooms
                     (room_id TEXT PRIMARY KEY, 
                      room_name TEXT, 
                      room_description TEXT,
                      is_private INTEGER, 
                      private_code TEXT, 
                      creator TEXT, 
                      room_avatar TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    print("✅ Created 'rooms' table")

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
    print("✅ Created 'messages' table")

    c.execute('''CREATE TABLE IF NOT EXISTS message_reactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      message_id INTEGER,
                      username TEXT,
                      reaction TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    print("✅ Created 'message_reactions' table")

    c.execute('''CREATE TABLE IF NOT EXISTS message_reads
                     (message_id INTEGER, 
                      username TEXT, 
                      read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      PRIMARY KEY (message_id, username))''')
    print("✅ Created 'message_reads' table")

    c.execute('''CREATE TABLE IF NOT EXISTS room_members
                     (room_id TEXT,
                      username TEXT,
                      joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      has_joined_before INTEGER DEFAULT 0,
                      PRIMARY KEY (room_id, username))''')
    print("✅ Created 'room_members' table")

    print("✅ Created 'game_scores' table")

    print("\n📊 Creating indexes...")

    c.execute('CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_messages_username ON messages(username)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')  # Changed from phone to email
    c.execute('CREATE INDEX IF NOT EXISTS idx_rooms_creator ON rooms(creator)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_room_members_username ON room_members(username)')
    print("✅ Created all indexes")

    print("\n🌱 Seeding database with sample data...")

    c.execute('''
        INSERT INTO rooms (room_id, room_name, room_description, is_private, creator)
        VALUES ('global', 'Global Chat', 'Welcome to the main chat room!', 0, 'System')
    ''')
    print("✅ Created Global Chat room")

    sample_rooms = [
        ('tech_talk', 'Tech Talk', 'Discuss technology and programming', 0, 'System'),
        ('random', 'Random', 'Talk about anything and everything', 0, 'System'),
        ('gaming', 'Gaming Zone', 'For all the gamers out there', 0, 'System'),
        ('study', 'Study Group', 'Collaborative learning space', 0, 'System'),
    ]

    for room_data in sample_rooms:
        c.execute('''
            INSERT INTO rooms (room_id, room_name, room_description, is_private, creator)
            VALUES (?, ?, ?, ?, ?)
        ''', room_data)
        print(f"✅ Created room: {room_data[1]}")

    demo_users = [
        ('DemoUser1', 'demo1@zetachat.com', 'demo123', '/static/img/default-avatar.png',
         'Hello! I am a demo user. 👋', 1),
        ('DemoUser2', 'demo2@zetachat.com', 'demo123', '/static/img/default-avatar.png',
         'Ready to chat! 💬', 1),
        ('TestUser', 'test@zetachat.com', 'test123', '/static/img/default-avatar.png',
         'Testing ZetaChat Pro 🚀', 1),
        ('AIHelper', 'ai@zetachat.com', 'ai123', '/static/img/default-avatar.png',
         'AI Assistant Bot 🤖', 1),
    ]

    for user in demo_users:
        password_hash = generate_password_hash(user[2])
        c.execute('''
            INSERT INTO users (username, email, password_hash, profile_pic, bio, is_verified)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user[0], user[1], password_hash, user[3], user[4], user[5]))
        print(f"✅ Created demo user: {user[0]}")
        print(f"   📧 Email: {user[1]}")
        print(f"   🔑 Password: {user[2]}")

    welcome_messages = [
        ('global', 'System', 'Welcome to ZetaChat Pro! 🎉', 'system'),
        ('global', 'System', 'Connect with friends, share files, and enjoy real-time chat!', 'system'),
        ('tech_talk', 'System', '💻 Welcome to Tech Talk! Discuss all things technology here.', 'system'),
        ('gaming', 'System', '🎮 Welcome to Gaming Zone! Share your gaming adventures!', 'system'),
    ]

    for msg in welcome_messages:
        c.execute('''
            INSERT INTO messages (room_id, username, message, message_type)
            VALUES (?, ?, ?, ?)
        ''', msg)
    print("\n✅ Added welcome messages to rooms")

    conn.commit()
    print("\n" + "=" * 60)
    print("✅ Database created successfully!")
    print(f"📍 Location: {os.path.abspath(DB_PATH)}")

    print("\n📊 Database Statistics:")
    c.execute("SELECT COUNT(*) FROM users")
    print(f"   👥 Users: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM rooms")
    print(f"   🏠 Rooms: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM messages")
    print(f"   💬 Messages: {c.fetchone()[0]}")

    print("\n📝 Demo Accounts:")
    print("=" * 60)
    c.execute("SELECT username, email FROM users")
    users = c.fetchall()
    for user in users:
        print(f"   Username: {user[0]}")
        print(f"   Email: {user[1]}")
        print(f"   Password: demo123 (for demo users) or test123 (for test user)")
        print("-" * 60)

    conn.close()
    print("\n🎉 Ready to use! Run: python app.py")
    print("=" * 60)


def verify_database():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("\n🔍 Verifying database structure...")

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    print(f"\n📋 Found {len(tables)} tables:")
    for table in tables:
        table_name = table[0]
        c.execute(f"PRAGMA table_info({table_name})")
        columns = c.fetchall()
        print(f"\n   📊 {table_name}:")
        for col in columns:
            nullable = "NULL" if col[3] == 0 else "NOT NULL"
            default = f"DEFAULT {col[4]}" if col[4] else ""
            print(f"      • {col[1]:20s} {col[2]:15s} {nullable:10s} {default}")

    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    has_email = any(col[1] == 'email' for col in columns)

    if has_email:
        print("\n✅ Email field verified in users table")
    else:
        print("\n⚠️  Warning: Email field not found in users table!")

    print("\n🔍 Checking indexes...")
    c.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = c.fetchall()
    print(f"   Found {len(indexes)} indexes:")
    for idx in indexes:
        print(f"      • {idx[0]}")

    conn.close()
    print("\n✅ Database verification complete!")


def migrate_existing_database():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("\n🔄 Migrating database from phone to email...")

    try:
        c.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in c.fetchall()]

        if 'phone' in columns and 'email' not in columns:
            print("📝 Adding email column...")
            c.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")

            c.execute("UPDATE users SET email = phone || '@temp.zetachat.com' WHERE email IS NULL")

            print("✅ Email column added and populated with temporary values")
            print("⚠️  Note: Users will need to update their email addresses")

            print("ℹ️  Phone column retained for backward compatibility")

        elif 'email' in columns:
            print("✅ Email column already exists")
        else:
            print("❌ Unexpected database structure")

        conn.commit()
        print("\n✅ Migration complete!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_menu():
    print("\n" + "=" * 60)
    print("🚀 ZetaChat Pro - Database Setup")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Create new database (WARNING: Deletes existing data)")
    print("  2. Verify existing database")
    print("  3. Migrate existing database (phone → email)")
    print("  4. Exit")
    print("=" * 60)

if __name__ == '__main__':
    show_menu()
    try:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            confirm = input("\n⚠️  This will DELETE all existing data. Continue? (yes/no): ").strip().lower()
            if confirm == 'yes':
                create_database()
                verify_database()
                print("\n✅ Setup complete! Your database is ready to use.")
                print("💡 Start the application with: python app.py")
                print("\n📧 Important: Update SMTP settings in app.py before running!")
                print("   SMTP_EMAIL = 'your_email@gmail.com'")
                print("   SMTP_PASSWORD = 'your_app_password'")
            else:
                print("\n❌ Operation cancelled")

        elif choice == '2':
            verify_database()

        elif choice == '3':
            confirm = input("\n⚠️  This will modify your database. Continue? (yes/no): ").strip().lower()
            if confirm == 'yes':
                migrate_existing_database()
                verify_database()
            else:
                print("\n❌ Operation cancelled")

        elif choice == '4':
            print("\n👋 Goodbye!")

        else:
            print("\n❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print()