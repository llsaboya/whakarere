import gi, sqlite3, os, threading, requests, base64
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, GdkPixbuf, Gio, GLib
from whakarere.images.unknown_contact import UnknownContact
from whakarere.api.whatsapp import WhatsAppAPI

class WhatsAppSessionManager:
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.whatsapp_manager = WhatsAppAPI(self)
        #self.app_manager.whatsapp_manager.terminate_inactive_sessions()
        self.chats = {}  # Changed to a dictionary to map session IDs to chats
        self.chats_avatar = {}  # Presumably for future functionality
        self.databases = {}  # Changed to a dictionary to map session IDs to databases

    def load_or_create_databases(self):
        db_directory = os.path.expanduser("~/.config/whakarere/dbs")

        # Ensure the database directory exists
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

        for session_id in self.app_manager.session_manager.session_ids:
            db_file = f"{session_id}.db"
            db_path = os.path.join(db_directory, db_file)

            # Connect to the SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Store the connection in the dictionary
            self.databases[session_id] = conn

            # Close the cursor
            cursor.close()

    def initialize(self):
        sessions_thread = threading.Thread(target=self.initialize_sessions)
        sessions_thread.start()

    def initialize_sessions(self):
        for session in self.app_manager.session_manager.session_ids:
            if self.whatsapp_manager.check_session_status(session):
                result = self.whatsapp_manager.get_chats(session)  # Fixed assignment
                self.chats[session] = result  # Store chats indexed by session ID
                for chat in result:
                    self.chats_avatar[chat["id"]["_serialized"]] = self.whatsapp_manager.get_user_profile_picture(chat["id"]["_serialized"], session)
        print("Initialized sessions")

    def get_chats(self, session_id):
        # Return chats for the given session_id or an empty list if not found
        return self.chats.get(session_id, [])

    def get_chat_avatar(self, chat_id):
        url = self.chats_avatar.get(chat_id, None)
        if url is not None:
            response = requests.get(url)
            loader = GdkPixbuf.PixbufLoader()
            loader.write(response.content)
            loader.close()
            return Gdk.Texture.new_for_pixbuf(loader.get_pixbuf())
        else:
            binary_data = base64.b64decode(UnknownContact.base64image)
            gbytes = GLib.Bytes.new(binary_data)
            input_stream = Gio.MemoryInputStream.new_from_bytes(gbytes)
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
            return Gdk.Texture.new_for_pixbuf(pixbuf)
                
    def get_messages(self, chat_id):
        # Return messages for the given chat_id or an empty list if not found
        return self.messages_by_chat.get(chat_id, [])

    def get_user_id(self, session_id):
        return self.whatsapp_manager.get_user_id(session_id)

    def get_user_name(self, session_id):
        return self.whatsapp_manager.get_user_name(session_id)

    def get_user_profile_picture(self, userid, session_id):
        return self.whatsapp_manager.get_user_profile_picture(userid, session_id)

    def check_session_status(self, session_id):
        return self.whatsapp_manager.check_session_status(session_id)

    def get_chat_messages(self, chat_id, session_id):
        return self.whatsapp_manager.get_chat_messages(chat_id, session_id)

    def get_chat_name(self, chat_id, session_id):
        return self.whatsapp_manager.get_chat_name(chat_id, session_id)

    def get_chat_unread_count(self, chat_id, session_id):
        return self.whatsapp_manager.get_chat_unread_count(chat_id, session_id)

    def get_chat_last_message(self, chat_id, session_id):
        return self.whatsapp_manager.get_chat_last_message(chat_id, session_id)

    def get_chat_last_message_timestamp(self, chat_id, session_id):
        return self.whatsapp_manager.get_chat_last_message_timestamp(chat_id, session_id)

    def get_chat_last_message_author(self, chat_id, session_id):
        return self.whatsapp_manager.get_chat_last_message_author(chat_id, session_id)

    # QR Code methods

    def get_qr_code_data(self, session_id):
        return self.whatsapp_manager.get_qr_code_data(session_id)

    # Contact methods

    def get_contact_info(self, contact_id, session_id):
        return self.whatsapp_manager.get_contact_info(contact_id, session_id)
