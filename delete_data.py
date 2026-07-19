import sqlite3
import os

DB_PATH = 'chat_app1.db'


def delete_all_messages():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM messages")
        count = c.fetchone()[0]

        c.execute("DELETE FROM messages")

        c.execute("DELETE FROM message_reactions")
        c.execute("DELETE FROM message_reads")

        conn.commit()
        conn.close()

        print(f"✅ Deleted {count} messages from the database")
        print("✅ Deleted all message reactions")
        print("✅ Deleted all message read records")

    except Exception as e:
        print(f"❌ Error deleting messages: {e}")


def delete_all_rooms():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM rooms WHERE room_id != 'global'")
        count = c.fetchone()[0]

        c.execute("DELETE FROM rooms WHERE room_id != 'global'")

        c.execute("DELETE FROM room_members WHERE room_id != 'global'")

        c.execute("DELETE FROM messages WHERE room_id != 'global'")

        c.execute("DELETE FROM game_scores WHERE room_id != 'global'")

        conn.commit()
        conn.close()

        print(f"✅ Deleted {count} rooms (kept 'global' room)")
        print("✅ Deleted related room members")
        print("✅ Deleted messages from deleted rooms")
        print("✅ Deleted game scores from deleted rooms")

    except Exception as e:
        print(f"❌ Error deleting rooms: {e}")


def delete_specific_room(room_id):
    if room_id == 'global':
        print("❌ Cannot delete the global room!")
        return

    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        c.execute("SELECT room_name FROM rooms WHERE room_id = ?", (room_id,))
        result = c.fetchone()

        if not result:
            print(f"❌ Room '{room_id}' not found!")
            conn.close()
            return

        room_name = result[0]

        c.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
        c.execute("DELETE FROM room_members WHERE room_id = ?", (room_id,))
        c.execute("DELETE FROM messages WHERE room_id = ?", (room_id,))
        c.execute("DELETE FROM game_scores WHERE room_id = ?", (room_id,))

        conn.commit()
        conn.close()

        print(f"✅ Deleted room: {room_name} ({room_id})")
        print("✅ Deleted all related data")

    except Exception as e:
        print(f"❌ Error deleting room: {e}")


def delete_messages_from_room(room_id):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        c.execute("SELECT room_name FROM rooms WHERE room_id = ?", (room_id,))
        result = c.fetchone()

        if not result:
            print(f"❌ Room '{room_id}' not found!")
            conn.close()
            return

        room_name = result[0]

        c.execute("SELECT COUNT(*) FROM messages WHERE room_id = ?", (room_id,))
        count = c.fetchone()[0]

        c.execute("DELETE FROM messages WHERE room_id = ?", (room_id,))

        conn.commit()
        conn.close()

        print(f"✅ Deleted {count} messages from room: {room_name} ({room_id})")

    except Exception as e:
        print(f"❌ Error deleting messages: {e}")


def list_all_users():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        c.execute("""SELECT username, email, is_verified, created_at 
                     FROM users ORDER BY created_at DESC""")
        users = c.fetchall()

        print("\n👥 Registered Users:")
        print("=" * 80)
        if not users:
            print("   No users found!")
        else:
            for user in users:
                verified = "✅ Verified" if user[2] else "❌ Not Verified"
                print(f"   {verified} - {user[0]} ({user[1]}) - Created: {user[3]}")
        print("=" * 80)

        conn.close()

    except Exception as e:
        print(f"❌ Error listing users: {e}")


def delete_specific_user(username):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        # Check if user exists
        c.execute("SELECT username, email FROM users WHERE username = ?", (username,))
        result = c.fetchone()

        if not result:
            print(f"❌ User '{username}' not found!")
            conn.close()
            return

        email = result[1]

        # Get statistics before deletion
        c.execute("SELECT COUNT(*) FROM messages WHERE username = ?", (username,))
        message_count = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM room_members WHERE username = ?", (username,))
        room_count = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM game_scores WHERE username = ?", (username,))
        game_count = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM message_reactions WHERE username = ?", (username,))
        reaction_count = c.fetchone()[0]

        # Delete user and all related data
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        c.execute("DELETE FROM messages WHERE username = ?", (username,))
        c.execute("DELETE FROM room_members WHERE username = ?", (username,))
        c.execute("DELETE FROM game_scores WHERE username = ?", (username,))
        c.execute("DELETE FROM message_reactions WHERE username = ?", (username,))
        c.execute("DELETE FROM message_reads WHERE username = ?", (username,))

        # Delete rooms created by this user (except global)
        c.execute("DELETE FROM rooms WHERE creator = ? AND room_id != 'global'", (username,))

        conn.commit()
        conn.close()

        print(f"\n✅ Deleted user: {username} ({email})")
        print(f"   📧 Messages deleted: {message_count}")
        print(f"   🏠 Room memberships deleted: {room_count}")
        print(f"   🎮 Game scores deleted: {game_count}")
        print(f"   😊 Reactions deleted: {reaction_count}")
        print(f"   🗑️  All associated data removed")

    except Exception as e:
        print(f"❌ Error deleting user: {e}")


def delete_all_users():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]

        if count == 0:
            print("ℹ️  No users to delete!")
            conn.close()
            return

        # Delete all users and their data
        c.execute("DELETE FROM users")
        c.execute("DELETE FROM messages")
        c.execute("DELETE FROM room_members")
        c.execute("DELETE FROM game_scores")
        c.execute("DELETE FROM message_reactions")
        c.execute("DELETE FROM message_reads")

        # Delete all rooms except global
        c.execute("DELETE FROM rooms WHERE room_id != 'global'")

        conn.commit()
        conn.close()

        print(f"✅ Deleted {count} users from the database")
        print("✅ Deleted all messages")
        print("✅ Deleted all room memberships")
        print("✅ Deleted all game scores")
        print("✅ Deleted all reactions and read records")
        print("✅ Deleted all rooms (except global)")

    except Exception as e:
        print(f"❌ Error deleting all users: {e}")


def show_database_stats():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        print("\n📊 Current Database Statistics:")
        print("=" * 50)

        c.execute("SELECT COUNT(*) FROM users")
        print(f"   Total Users: {c.fetchone()[0]}")

        c.execute("SELECT COUNT(*) FROM messages")
        print(f"   Total Messages: {c.fetchone()[0]}")

        c.execute("SELECT COUNT(*) FROM rooms")
        print(f"   Total Rooms: {c.fetchone()[0]}")

        c.execute("SELECT COUNT(*) FROM room_members")
        print(f"   Total Room Members: {c.fetchone()[0]}")

        c.execute("SELECT COUNT(*) FROM game_scores")
        print(f"   Total Game Scores: {c.fetchone()[0]}")

        c.execute("SELECT COUNT(*) FROM message_reactions")
        print(f"   Total Reactions: {c.fetchone()[0]}")

        print("=" * 50)

        conn.close()

    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def list_all_rooms():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        c = conn.cursor()

        c.execute("SELECT room_id, room_name, is_private, creator FROM rooms")
        rooms = c.fetchall()

        print("\n🏠 Available Rooms:")
        print("=" * 80)
        if not rooms:
            print("   No rooms found!")
        else:
            for room in rooms:
                room_type = "🔒 Private" if room[2] else "🌍 Public"
                creator = f"Created by: {room[3]}" if room[3] else "System room"
                print(f"   {room_type} - {room[1]} (ID: {room[0]}) - {creator}")
        print("=" * 80)

        conn.close()

    except Exception as e:
        print(f"❌ Error listing rooms: {e}")


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print("💡 Run setup_database.py first to create the database")
        return

    print("\n" + "=" * 60)
    print("🗑️  ZetaChat Pro - Data Deletion Tool")
    print("=" * 60)

    show_database_stats()

    print("\n📋 Select an option:")
    print("   1. Delete ALL messages")
    print("   2. Delete ALL rooms (except global)")
    print("   3. Delete a specific room")
    print("   4. Delete messages from a specific room")
    print("   5. Delete a specific user")
    print("   6. Delete ALL users")
    print("   7. List all rooms")
    print("   8. List all users")
    print("   9. Show database statistics")
    print("   10. Exit")

    choice = input("\n👉 Enter your choice (1-10): ").strip()

    if choice == '1':
        confirm = input("\n⚠️  Are you sure you want to delete ALL messages? (yes/no): ").strip().lower()
        if confirm == 'yes':
            delete_all_messages()
        else:
            print("❌ Operation cancelled")

    elif choice == '2':
        confirm = input("\n⚠️  Are you sure you want to delete ALL rooms except global? (yes/no): ").strip().lower()
        if confirm == 'yes':
            delete_all_rooms()
        else:
            print("❌ Operation cancelled")

    elif choice == '3':
        list_all_rooms()
        room_id = input("\n👉 Enter room ID to delete: ").strip()
        confirm = input(f"\n⚠️  Delete room '{room_id}' and all its data? (yes/no): ").strip().lower()
        if confirm == 'yes':
            delete_specific_room(room_id)
        else:
            print("❌ Operation cancelled")

    elif choice == '4':
        list_all_rooms()
        room_id = input("\n👉 Enter room ID: ").strip()
        confirm = input(f"\n⚠️  Delete all messages from room '{room_id}'? (yes/no): ").strip().lower()
        if confirm == 'yes':
            delete_messages_from_room(room_id)
        else:
            print("❌ Operation cancelled")

    elif choice == '5':
        list_all_users()
        username = input("\n👉 Enter username to delete: ").strip()
        confirm = input(f"\n⚠️  Delete user '{username}' and ALL their data? (yes/no): ").strip().lower()
        if confirm == 'yes':
            delete_specific_user(username)
        else:
            print("❌ Operation cancelled")

    elif choice == '6':
        list_all_users()
        confirm = input(
            "\n⚠️  Are you sure you want to delete ALL USERS? This will delete everything! (yes/no): ").strip().lower()
        if confirm == 'yes':
            double_confirm = input("⚠️⚠️  Type 'DELETE ALL' to confirm: ").strip()
            if double_confirm == 'DELETE ALL':
                delete_all_users()
            else:
                print("❌ Operation cancelled")
        else:
            print("❌ Operation cancelled")

    elif choice == '7':
        list_all_rooms()

    elif choice == '8':
        list_all_users()

    elif choice == '9':
        show_database_stats()

    elif choice == '10':
        print("\n👋 Goodbye!")
        return

    else:
        print("❌ Invalid choice!")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()