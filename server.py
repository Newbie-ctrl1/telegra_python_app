from flask import Flask, request, jsonify
from flask_cors import CORS
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.account import UpdateUsernameRequest, UpdateProfileRequest
from telethon.tl.functions.channels import LeaveChannelRequest
import asyncio
import os
import json
from dotenv import load_dotenv
import logging
import traceback
from asgiref.sync import async_to_sync
from datetime import datetime

# Setup logging dengan format yang lebih detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables dengan nilai default
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get API credentials from environment variables atau gunakan nilai default
API_ID = os.getenv('API_ID', '20081042')  # Nilai default API_ID
API_HASH = os.getenv('API_HASH', '93fd87dcd1be75b59ba8798fc72f1d31')  # Nilai default API_HASH

# Jika file .env tidak ada, buat file baru dengan nilai default
if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write(f'API_ID={API_ID}\n')
        f.write(f'API_HASH={API_HASH}\n')
    logger.info('Created new .env file with default values')

# Convert API_ID to integer
API_ID = int(API_ID)

logger.info(f'Using API_ID: {API_ID}')
logger.info(f'Using API_HASH: {API_HASH}')

# Dictionary untuk menyimpan phone_code_hash
phone_code_hashes = {}

# Buat folder sessions jika belum ada
SESSIONS_DIR = 'sessions'
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)
    logger.info(f'Created sessions directory at {os.path.abspath(SESSIONS_DIR)}')
else:
    logger.info(f'Using existing sessions directory at {os.path.abspath(SESSIONS_DIR)}')

# Buat folder chat jika belum ada
CHAT_DIR = 'chat'
if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)
    logger.info(f'Created chat directory at {os.path.abspath(CHAT_DIR)}')
else:
    logger.info(f'Using existing chat directory at {os.path.abspath(CHAT_DIR)}')

@app.route('/create_session', methods=['POST'])
def create_session():
    data = request.get_json()
    phone_number = data.get('phone_number')

    logger.info(f'Received create_session request for phone: {phone_number}')

    if not phone_number:
        logger.error('Phone number is missing')
        return jsonify({
            'status': 'error',
            'message': 'Phone number is required'
        }), 400

    # Pastikan folder sessions ada
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
        logger.info(f'Created sessions directory at {os.path.abspath(SESSIONS_DIR)}')

    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.session")
    logger.info(f'Session file will be saved at: {session_file}')

    async def _create_session():
        try:
            client = TelegramClient(session_file, API_ID, API_HASH)
            await client.connect()
            
            if not await client.is_user_authorized():
                result = await client.send_code_request(phone_number)
                phone_code_hashes[phone_number] = result.phone_code_hash
                logger.info(f'Verification code sent to {phone_number}')
                logger.info(f'Phone code hash stored: {phone_code_hashes[phone_number]}')
                return jsonify({
                    'status': 'success',
                    'message': 'Verification code sent',
                    'phone_code_hash': phone_code_hashes[phone_number]
                })
            else:
                logger.warning(f'Session already exists for {phone_number}')
                return jsonify({
                    'status': 'error',
                    'message': 'Session already exists'
                }), 400
        except Exception as e:
            error_msg = f'Error in create_session: {str(e)}\n{traceback.format_exc()}'
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
        finally:
            await client.disconnect()

    return async_to_sync(_create_session)()

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone_number = data.get('phone_number')
    code = data.get('code')

    logger.info(f'Received verify_code request for phone: {phone_number}')
    logger.info(f'Code received: {code}')
    logger.info(f'Available phone_code_hashes: {list(phone_code_hashes.keys())}')

    if not all([phone_number, code]):
        logger.error('Missing required parameters')
        return jsonify({
            'status': 'error',
            'message': 'Phone number and code are required'
        }), 400

    if phone_number not in phone_code_hashes:
        logger.error(f'No phone_code_hash found for {phone_number}')
        return jsonify({
            'status': 'error',
            'message': 'Please request verification code first'
        }), 400

    # Pastikan folder sessions ada
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
        logger.info(f'Created sessions directory at {os.path.abspath(SESSIONS_DIR)}')

    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.session")
    logger.info(f'Session file will be saved at: {session_file}')

    async def _verify_code():
        try:
            client = TelegramClient(session_file, API_ID, API_HASH)
            await client.connect()
            
            logger.info(f'Attempting to sign in with:')
            logger.info(f'- Phone: {phone_number}')
            logger.info(f'- Code: {code}')
            logger.info(f'- Hash: {phone_code_hashes[phone_number]}')
            
            await client.sign_in(
                phone=phone_number, 
                code=code,
                phone_code_hash=phone_code_hashes[phone_number]
            )
            logger.info(f'Session created successfully for {phone_number}')
            logger.info(f'Session file saved at: {session_file}')
            
            # Hapus phone_code_hash setelah berhasil
            del phone_code_hashes[phone_number]
            
            return jsonify({
                'status': 'success',
                'message': f'Session created and saved as {session_file}'
            })
        except Exception as e:
            error_msg = f'Error in verify_code: {str(e)}\n{traceback.format_exc()}'
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
        finally:
            await client.disconnect()

    return async_to_sync(_verify_code)()

@app.route('/chat_history', methods=['POST'])
def get_chat_history():
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        logger.error('Phone number is missing')
        return jsonify({
            'status': 'error',
            'message': 'Phone number is required'
        }), 400

    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.session")
    if not os.path.exists(session_file):
        logger.error(f'Session file not found: {session_file}')
        return jsonify({
            'status': 'error',
            'message': 'Session not found. Please create a session first.'
        }), 404

    async def _read_chat_history():
        try:
            async with TelegramClient(session_file, API_ID, API_HASH) as client:
                logger.info("Client Created")
                logger.info("Reading chat history from Telegram notification service...")

                dialogs = await client.get_dialogs()
                notification_dialog = next((dialog for dialog in dialogs if dialog.name == "Telegram"), None)

                if not notification_dialog:
                    raise Exception("Unable to find Telegram notification service dialog")

                messages = await client(GetHistoryRequest(
                    peer=notification_dialog.input_entity,
                    limit=100,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                # Pastikan folder chat ada
                if not os.path.exists(CHAT_DIR):
                    os.makedirs(CHAT_DIR)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                chat_file_path = os.path.join(CHAT_DIR, f'notification_history_{phone_number}_{timestamp}.txt')
                
                chat_messages = []
                with open(chat_file_path, 'w', encoding='utf-8') as f:
                    for message in messages.messages:
                        message_text = f"[{message.date}] {message.message}"
                        f.write(message_text + '\n')
                        chat_messages.append(message_text)
                        logger.info(message_text)

                logger.info(f"Chat history successfully saved to {chat_file_path}")
                
                return jsonify({
                    'status': 'success',
                    'message': f'Chat history saved to {chat_file_path}',
                    'chat_history': chat_messages
                })

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return async_to_sync(_read_chat_history)()

@app.route('/list_sessions', methods=['GET'])
def list_sessions():
    try:
        if not os.path.exists(SESSIONS_DIR):
            return jsonify({
                'status': 'success',
                'sessions': []
            })

        sessions = []
        for file in os.listdir(SESSIONS_DIR):
            if file.endswith('.session'):
                # Hapus ekstensi .session dan tambahkan ke daftar
                phone_number = file[:-8]  # menghapus '.session'
                sessions.append(phone_number)

        logger.info(f"Found {len(sessions)} sessions: {sessions}")
        return jsonify({
            'status': 'success',
            'sessions': sessions
        })
    except Exception as e:
        error_msg = f"Error listing sessions: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/change_username', methods=['POST'])
def change_username():
    data = request.get_json()
    phone_number = data.get('phone_number')
    new_username = data.get('username')

    if not all([phone_number, new_username]):
        logger.error('Missing required parameters')
        return jsonify({
            'status': 'error',
            'message': 'Phone number and username are required'
        }), 400

    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.session")
    if not os.path.exists(session_file):
        logger.error(f'Session file not found: {session_file}')
        return jsonify({
            'status': 'error',
            'message': 'Session not found. Please create a session first.'
        }), 404

    async def _change_username():
        try:
            async with TelegramClient(session_file, API_ID, API_HASH) as client:
                logger.info("Client Created")
                logger.info(f"Changing username to: {new_username}")

                await client(UpdateUsernameRequest(new_username))
                logger.info(f"Username successfully changed to {new_username}")
                
                return jsonify({
                    'status': 'success',
                    'message': f'Username changed to {new_username}'
                })

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return async_to_sync(_change_username)()

@app.route('/change_name', methods=['POST'])
def change_name():
    data = request.get_json()
    phone_number = data.get('phone_number')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not all([phone_number, first_name]):
        logger.error('Missing required parameters')
        return jsonify({
            'status': 'error',
            'message': 'Phone number and first name are required'
        }), 400

    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.session")
    if not os.path.exists(session_file):
        logger.error(f'Session file not found: {session_file}')
        return jsonify({
            'status': 'error',
            'message': 'Session not found. Please create a session first.'
        }), 404

    async def _change_name():
        try:
            async with TelegramClient(session_file, API_ID, API_HASH) as client:
                logger.info("Client Created")
                logger.info(f"Changing name to: {first_name} {last_name}")

                await client(UpdateProfileRequest(
                    first_name=first_name,
                    last_name=last_name or None
                ))
                logger.info(f"Name successfully changed to: {first_name} {last_name}")
                
                return jsonify({
                    'status': 'success',
                    'message': f'Name changed to {first_name} {last_name or ""}'
                })

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return async_to_sync(_change_name)()

@app.route('/leave_all_channels', methods=['POST'])
def leave_all_channels():
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        logger.error('Phone number is missing')
        return jsonify({
            'status': 'error',
            'message': 'Phone number is required'
        }), 400

    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.session")
    if not os.path.exists(session_file):
        logger.error(f'Session file not found: {session_file}')
        return jsonify({
            'status': 'error',
            'message': 'Session not found. Please create a session first.'
        }), 404

    async def _leave_all_channels():
        try:
            async with TelegramClient(session_file, API_ID, API_HASH) as client:
                logger.info("Client Created")
                
                retries = 3
                while retries > 0:
                    try:
                        dialogs = await client.get_dialogs()
                        tasks = []
                        for dialog in dialogs:
                            if dialog.is_channel or dialog.is_group:
                                tasks.append(client(LeaveChannelRequest(dialog.id)))

                        await asyncio.gather(*tasks)
                        logger.info("Successfully left all channels and groups")
                        return jsonify({
                            'status': 'success',
                            'message': 'Successfully left all channels and groups'
                        })
                    except Exception as e:
                        logger.error(f"Error leaving channels: {e}")
                        retries -= 1
                        if retries > 0:
                            logger.info("Trying again...")
                            await asyncio.sleep(1)
                        else:
                            raise

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return async_to_sync(_leave_all_channels)()

@app.route('/list_channels', methods=['POST'])
def list_channels():
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        logger.error('Phone number is missing')
        return jsonify({
            'status': 'error',
            'message': 'Phone number is required'
        }), 400

    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.session")
    if not os.path.exists(session_file):
        logger.error(f'Session file not found: {session_file}')
        return jsonify({
            'status': 'error',
            'message': 'Session not found. Please create a session first.'
        }), 404

    async def _list_channels():
        try:
            async with TelegramClient(session_file, API_ID, API_HASH) as client:
                logger.info("Client Created")

                dialogs = await client.get_dialogs()
                channels = []
                for dialog in dialogs:
                    if dialog.is_channel or dialog.is_group:
                        channels.append({
                            'title': dialog.title,
                            'id': dialog.id,
                            'type': 'channel' if dialog.is_channel else 'group'
                        })

                logger.info(f"Found {len(channels)} channels and groups")
                return jsonify({
                    'status': 'success',
                    'channels': channels
                })

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return async_to_sync(_list_channels)()

@app.route('/delete_session', methods=['POST'])
def delete_session():
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        logger.error('Phone number is missing')
        return jsonify({
            'status': 'error',
            'message': 'Phone number is required'
        }), 400

    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.session")
    if not os.path.exists(session_file):
        logger.error(f'Session file not found: {session_file}')
        return jsonify({
            'status': 'error',
            'message': 'Session not found'
        }), 404

    try:
        # Hapus file sesi
        os.remove(session_file)
        logger.info(f"Successfully deleted session file: {session_file}")

        # Hapus file chat history yang terkait (jika ada)
        chat_files = [f for f in os.listdir(CHAT_DIR) if f.startswith(f'notification_history_{phone_number}')]
        for chat_file in chat_files:
            chat_file_path = os.path.join(CHAT_DIR, chat_file)
            try:
                os.remove(chat_file_path)
                logger.info(f"Successfully deleted chat history file: {chat_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete chat history file {chat_file_path}: {e}")

        return jsonify({
            'status': 'success',
            'message': 'Session deleted successfully'
        })
    except Exception as e:
        error_msg = f"Error deleting session: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Dapatkan IP address komputer
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\nServer akan dijalankan di:")
    print(f"Local IP  : http://{local_ip}:5000")
    print(f"Localhost : http://localhost:5000")
    print("\nPastikan firewall mengizinkan koneksi ke port 5000")
    
    # Jalankan server di semua interface (0.0.0.0)
    app.run(host='0.0.0.0', port=5000, debug=True) 