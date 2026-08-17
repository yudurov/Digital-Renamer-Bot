# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr
# Special Thanks To @ReshamOwner
# Update Channel @Digital_Botz & @DigitalBotz_Support
"""
Apache License 2.0
Copyright (c) 2022 @Digital_Botz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

# pyrogram imports
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

# hachoir imports
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

# bots imports
from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, remove_path
from helper.database import digital_botz, Task
from helper.ffmpeg import change_metadata
from config import Config

# extra imports
from asyncio import sleep
import os, time, asyncio, shutil

UPLOAD_TEXT = "📤 Uploading file..."
DOWNLOAD_TEXT = "📥 Downloading file..."

app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)

# ==========================================
# --- GLOBAL PREMIUM UPLOAD LOCK ---
# Prevents FILE_PART_INVALID by making 2GB+ files take turns on the string session
upload_lock = asyncio.Lock()
# ==========================================

# ==========================================
# --- ACTIVE TASKS TRACKER (FOR CANCELLATION) ---
# ==========================================
active_tasks = {}
# ==========================================

# ==========================================
# --- LEAST BUSY WORKER LOAD BALANCER ---
# ==========================================
worker_loads = {} # Tracks how many active tasks each worker has

def get_least_busy_worker(main_client):
    """Finds the worker currently handling the fewest files."""
    workers = getattr(Config, "WORKER_CLIENTS", [])
    if not workers:
        return main_client
    
    # Initialize tracking if not present
    for w in workers:
        if w not in worker_loads:
            worker_loads[w] = 0
            
    # Return the worker with the minimum active tasks
    least_busy = min(workers, key=lambda w: worker_loads.get(w, 0))
    return least_busy
# ==========================================

# ==========================================
# --- REBOOT RESUME FUNCTION ---
# ==========================================
async def resume_all_tasks(client):
    print("🔄 Checking for incomplete tasks to resume...")
    try:
        tasks = await Task.find_all().to_list()
        count = 0
        for task in tasks:
            try:
                file_msg = await client.get_messages(task.user_id, task.file_msg_id)
                if not file_msg or file_msg.empty:
                    await task.delete()
                    continue

                # --- 1. THE ASSASSIN: Silently delete the old frozen progress bar! ---
                if getattr(task, "processing_msg_id", 0) != 0:
                    try:
                        await client.delete_messages(task.user_id, task.processing_msg_id)
                    except:
                        pass
                # -------------------------------------------------------------------
                    
                # Generate the new "Resuming" message which will naturally morph into the new progress bar
                processing_msg = await client.send_message(task.user_id, "🔄 **Rᴇꜱᴜᴍɪɴɢ Iɴᴄᴏᴍᴩʟᴇᴛᴇ Tᴀꜱᴋ...**\n⏳ **Pʀᴏᴄᴇꜱꜱɪɴɢ...**")
                
                # --- 2. UPDATE DB: Save the new progress bar ID just in case it crashes again! ---
                task.processing_msg_id = processing_msg.id
                await task.save()
                # ---------------------------------------------------------------------------------

                # Assign to the least busy worker immediately
                assigned_worker = get_least_busy_worker(client)
                if assigned_worker != client:
                    worker_loads[assigned_worker] = worker_loads.get(assigned_worker, 0) + 1
                
                # Start task in parallel and track it for cancellation
                task_obj = asyncio.create_task(process_single_file(client, assigned_worker, task.user_id, file_msg, task.new_name, task.upload_type, task.id, processing_msg))
                active_tasks[task.id] = task_obj
                count += 1
            except Exception as e:
                print(f"Failed to resume task {task.id}: {e}")
                
        if count > 0:
            print(f"✅ Resumed {count} tasks successfully.")
        else:
            print("✅ No pending tasks to resume.")
    except Exception as e:
        print(f"Error in resume_all_tasks: {e}")


@Client.on_message(filters.private & (filters.audio | filters.document | filters.video))
async def rename_start(client, message):
    user_id  = message.from_user.id
    rkn_file = getattr(message, message.media.value)
    filename = rkn_file.file_name or "Unknown_File"
    filesize = humanbytes(rkn_file.file_size)
    mime_type = rkn_file.mime_type or "application/octet-stream"
    dcid = FileId.decode(rkn_file.file_id).dc_id
    extension_type = mime_type.split('/')[0]
    file_ext = filename.split('.')[-1].lower() if '.' in filename else ""

    FILE_TYPE_EMOJIS = {
        "audio": "🎵", "video": "🎬", "image": "🖼️", "application": "📦", "text": "📄", "default": "📁"
    }

    EXTENSION_EMOJIS = {
        "zip": "🗜️", "rar": "📚", "7z": "🧳", "pdf": "📕", "apk": "🤖", "exe": "💻", 
        "mp4": "🎥", "mkv": "📽️", "mp3": "🎶", "jpg": "🖼️", "png": "🖼️"
    }

    async def send_media_info():
        emoji = EXTENSION_EMOJIS.get(file_ext) or FILE_TYPE_EMOJIS.get(extension_type, FILE_TYPE_EMOJIS["default"])
        text = (
            f"**__{emoji} ᴍᴇᴅɪᴀ ɪɴꜰᴏ:\n\n"
            f"🗃️ ᴏʟᴅ ꜰɪʟᴇ ɴᴀᴍᴇ: `{filename}`\n\n"
            f"🏷️ ᴇxᴛᴇɴꜱɪᴏɴ: `{file_ext.upper()}`\n"
            f"📏 ꜰɪʟᴇ ꜱɪᴢᴇ: `{filesize}`\n"
            f"🧬 ᴍɪᴍᴇ ᴛʏᴘᴇ: `{mime_type}`\n"
            f"🆔 ᴅᴄ ɪᴅ: `{dcid}`\n\n"
            f"✏️ ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ɴᴇᴡ ғɪʟᴇɴᴀᴍᴇ ᴡɪᴛʜ ᴇxᴛᴇɴsɪᴏɴ ᴀɴᴅ ʀᴇᴘʟʏ ᴛᴏ ᴛʜɪs ᴍᴇssᴀɢᴇ...__**"
        )
        await message.reply_text(text, reply_to_message_id=message.id, reply_markup=ForceReply(True))

    if client.premium and client.uploadlimit:
        await digital_botz.reset_uploadlimit_access(user_id)
        
        # Check if user has Lifetime Plan
        prem_data = await digital_botz.get_user(user_id)
        is_lifetime = prem_data.get("is_lifetime", False) if prem_data else False
        
        user_data = await digital_botz.get_user_data(user_id)
        limit = user_data.get('uploadlimit', 0)
        used = user_data.get('used_limit', 0)
        remain = int(limit) - int(used)
        used_percentage = (int(used) / int(limit) * 100) if limit else 0
        
        # Only block if they aren't Lifetime and their limit is exceeded
        if not is_lifetime and remain < int(rkn_file.file_size):
            return await message.reply_text(
                f"{used_percentage:.2f}% Of Daily Upload Limit {humanbytes(limit)}.\n\n"
                f"📦 Media Size: {filesize}\n"
                f"📊 Your Used Daily Limit: {humanbytes(used)}\n\n"
                f"You have only **{humanbytes(remain)}** left.\nPlease, Buy Premium Plan.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🪪 UᴘɢʀᴀᴅE", callback_data="plans")]])
            )

    if await digital_botz.has_premium_access(user_id) and client.premium:
        if not getattr(Config, 'STRING_SESSION', None):
            if rkn_file.file_size > 2000 * 1024 * 1024:
                return await message.reply_text("⚠️ Sᴏʀʀy, Tʜɪꜱ Bᴏᴛ Dᴏᴇꜱɴ'ᴛ Sᴜᴩᴩᴏʀᴛ Uᴩʟᴏᴀᴅɪɴɢ ꜰɪʟᴇꜱ ʙɪɢɢᴇʀ ᴛʜᴀɴ 2Gʙ+")

        try:
            await send_media_info()
        except FloodWait as e:
            await sleep(e.value)
            await send_media_info()
    else:
        if rkn_file.file_size > 2000 * 1024 * 1024 and client.premium:
            return await message.reply_text("‼️Hi, If you want to rename 2GB+ files, you’ll need to buy premium. See /plans")

        try:
            await send_media_info()
        except FloodWait as e:
            await sleep(e.value)
            await send_media_info()


@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message
    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text 
        await message.delete() 
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
        if not "." in new_name:
            if "." in (media.file_name or ""):
                extn = media.file_name.rsplit('.', 1)[-1]
            else:
                extn = "mkv"
            new_name = new_name + "." + extn
        await reply_message.delete()

        button = [[InlineKeyboardButton("📁 Dᴏᴄᴜᴍᴇɴᴛ",callback_data = "upload_document")]]
        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton("🎥 Vɪᴅᴇᴏ", callback_data = "upload_video")])
        elif file.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton("🎵 Aᴜᴅɪᴏ", callback_data = "upload_audio")])
        await message.reply(
            text=f"**Sᴇʟᴇᴄᴛ Tʜᴇ Oᴜᴛᴩᴜᴛ Fɪʟᴇ Tyᴩᴇ**\n**• Fɪʟᴇ Nᴀᴍᴇ :-**`{new_name}`",
            reply_to_message_id=file.id,
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        await message.continue_propagation()


@Client.on_callback_query(filters.regex("upload"))
async def doc(client, update):
    # Fix: Instantly answer the callback so the user's telegram client doesn't freeze the buttons!
    try: await update.answer("Processing...", show_alert=False)
    except: pass

    user_id = int(update.message.chat.id) 
    new_name = update.message.text
    new_filename_ = new_name.split(":-")[1].strip().replace("`","")
    type = update.data.split("_")[1]
    file_msg = update.message.reply_to_message
    
    rkn_processing = await update.message.edit("`⏳ Processing...`")

    # Add to DB for persistence WITH the progress bar tracking ID!
    task_id = await digital_botz.add_task(user_id, file_msg.id, new_filename_, type, rkn_processing.id)
    
    # Check for least busy worker immediately
    assigned_worker = get_least_busy_worker(client)
    if assigned_worker != client:
        worker_loads[assigned_worker] = worker_loads.get(assigned_worker, 0) + 1

    # Start download/upload in parallel without blocking and track it!
    task_obj = asyncio.create_task(process_single_file(client, assigned_worker, user_id, file_msg, new_filename_, type, task_id, rkn_processing))
    active_tasks[task_id] = task_obj


async def process_single_file(main_client, worker_client, user_id, file_msg, new_filename_, upload_type, task_id, rkn_processing):
    dl_path = None
    file_path = None
    metadata_path = None
    ph_path = None
    log_msg_down = None
    
    # Establish dynamic, unique folder paths based on the DB task_id
    task_renames_dir = f"Renames/{task_id}"
    task_meta_dir = f"Metadata/{task_id}"
    
    try:
        await digital_botz.update_task_status(task_id, "processing")
        
        user_data = await digital_botz.get_user_data(user_id)
        media = getattr(file_msg, file_msg.media.value)

        try:
            prefix = await digital_botz.get_prefix(user_id)
            suffix = await digital_botz.get_suffix(user_id)
            new_filename = add_prefix_suffix(new_filename_, prefix, suffix)
            
            # SANITIZE: Prevent directory traversal crashes, but perfectly preserve dots and spaces
            new_filename = new_filename.replace("/", "-").replace("\\", "-")
        except Exception as e:
            await digital_botz.delete_task(task_id)
            try: await rkn_processing.edit(f"⚠️ Prefix/Suffix Error \nError: {e}")
            except: pass
            return

        # UNIQUE FOLDER: Prevent identical file disk collisions, keep filename completely pristine!
        os.makedirs(task_renames_dir, exist_ok=True)
        os.makedirs(task_meta_dir, exist_ok=True)

        file_path = f"{task_renames_dir}/{new_filename}"
        metadata_path = f"{task_meta_dir}/{new_filename}"    

        try: await rkn_processing.edit("`☄️Trying To Download....`")
        except: pass
        
        if main_client.premium and main_client.uploadlimit:
            await digital_botz.increment_used_limit(user_id, media.file_size)
        
        if worker_client != main_client:
            try:
                log_msg_down = await file_msg.copy(Config.LOG_CHANNEL)
                target_msg = await worker_client.get_messages(Config.LOG_CHANNEL, log_msg_down.id)
            except Exception as e:
                if main_client.premium and main_client.uploadlimit:
                    await digital_botz.increment_used_limit(user_id, -media.file_size)
                await digital_botz.delete_task(task_id)
                try: await rkn_processing.edit(f"⚠️ **Fleet Error:** Main bot must be Admin in LOG_CHANNEL.\n{e}")
                except: pass
                return
        else:
            target_msg = file_msg
            
        # --- CANCELLATION CHECK 1: Before Download ---
        check_task = await Task.get(task_id)
        if not check_task:
            print(f"Task {task_id} cancelled before download.")
            return
        
        try:
            dl_path = await worker_client.download_media(
                message=target_msg,
                file_name=file_path,
                progress=progress_for_pyrogram,
                progress_args=(DOWNLOAD_TEXT, rkn_processing, time.time())
            )
        except Exception as e:
            if main_client.premium and main_client.uploadlimit:
                await digital_botz.increment_used_limit(user_id, -media.file_size)
            await digital_botz.delete_task(task_id)
            try: await rkn_processing.edit(f"Download Error: {e}")
            except: pass
            return
        finally:
            if log_msg_down:
                try: 
                    await main_client.delete_messages(Config.LOG_CHANNEL, log_msg_down.id)
                except FloodWait as fw:
                    try:
                        await worker_client.delete_messages(Config.LOG_CHANNEL, log_msg_down.id)
                    except: 
                        pass
                except Exception:
                    try:
                        await worker_client.delete_messages(Config.LOG_CHANNEL, log_msg_down.id)
                    except: 
                        pass

        metadata_mode = await digital_botz.get_metadata_mode(user_id)
        if (metadata_mode):        
            metadata = await digital_botz.get_metadata_code(user_id)
            if metadata:
                try: await rkn_processing.edit("I Fᴏᴜɴᴅ Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ\n\n__**Pʟᴇᴀsᴇ Wᴀɪᴛ...**__\n**Aᴅᴅɪɴɢ Mᴇᴛᴀᴅᴀᴛᴀ Tᴏ Fɪʟᴇ....**")            
                except: pass
                if change_metadata(dl_path, metadata_path, metadata):            
                    try: await rkn_processing.edit("Metadata Added.....")
                    except: pass
            try: await rkn_processing.edit("**Metadata added to the file successfully ✅**\n\n**Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....**")
            except: pass
        else:
            try: await rkn_processing.edit("`☄️Trying To Upload....`")
            except: pass
            
        duration = 0
        try:
            parser = createParser(file_path)
            metadata_ext = extractMetadata(parser)
            if metadata_ext and metadata_ext.has("duration"):
                duration = metadata_ext.get('duration').seconds
            if parser: parser.close()
        except: pass
            
        c_caption = await digital_botz.get_caption(user_id)
        c_thumb = await digital_botz.get_thumbnail(user_id)

        if c_caption:
            try:
                caption = c_caption.format(
                    filename=new_filename,
                    filesize=humanbytes(media.file_size),
                    duration=convert(duration)
                )
            except Exception as e:
                if main_client.premium and main_client.uploadlimit:
                    await digital_botz.increment_used_limit(user_id, -media.file_size)
                await digital_botz.delete_task(task_id)
                try: await rkn_processing.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ: ({e})")
                except: pass
                return
        else:
            caption = f"**{new_filename}**"
     
        if (media.thumbs or c_thumb):
            if c_thumb: ph_path = await main_client.download_media(c_thumb) 
            else: ph_path = await main_client.download_media(media.thumbs[0].file_id)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")

        if media.file_size > 2000 * 1024 * 1024 and getattr(Config, 'STRING_SESSION', None):
            uploader = app
            is_main_bot = False
        else:
            uploader = worker_client
            is_main_bot = (uploader == main_client)
            
        file_to_upload = metadata_path if metadata_mode else file_path
        
        # --- CANCELLATION CHECK 2: Before Upload ---
        check_task = await Task.get(task_id)
        if not check_task:
            print(f"Task {task_id} cancelled before upload.")
            return
        
        try:
            async def perform_upload():
                filw = None
                try:
                    if not is_main_bot:
                        if upload_type == "document":
                            filw = await uploader.send_document(Config.LOG_CHANNEL, document=file_to_upload, file_name=new_filename, thumb=ph_path, caption=caption, progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
                        elif upload_type == "video":
                            filw = await uploader.send_video(Config.LOG_CHANNEL, video=file_to_upload, file_name=new_filename, caption=caption, thumb=ph_path, duration=duration, progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
                        elif upload_type == "audio":
                            filw = await uploader.send_audio(Config.LOG_CHANNEL, audio=file_to_upload, file_name=new_filename, caption=caption, thumb=ph_path, duration=duration, progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
                        
                        await asyncio.sleep(1.5)
                        
                        delivered = False
                        while not delivered:
                            try:
                                await main_client.copy_message(user_id, Config.LOG_CHANNEL, filw.id)
                                delivered = True
                            except FloodWait as fw:
                                await asyncio.sleep(fw.value)
                            except Exception:
                                try:
                                    await uploader.copy_message(user_id, Config.LOG_CHANNEL, filw.id)
                                    delivered = True
                                except Exception:
                                    delivered = True 
                    else:
                        if upload_type == "document":
                            await main_client.send_document(user_id, document=file_to_upload, file_name=new_filename, thumb=ph_path, caption=caption, progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
                        elif upload_type == "video":
                            await main_client.send_video(user_id, video=file_to_upload, file_name=new_filename, caption=caption, thumb=ph_path, duration=duration, progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
                        elif upload_type == "audio":
                            await main_client.send_audio(user_id, audio=file_to_upload, file_name=new_filename, caption=caption, thumb=ph_path, duration=duration, progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
                finally:
                    if filw and not is_main_bot:
                        for attempt in range(3):
                            try:
                                await main_client.delete_messages(Config.LOG_CHANNEL, filw.id)
                                break
                            except FloodWait:
                                try:
                                    await uploader.delete_messages(Config.LOG_CHANNEL, filw.id)
                                    break
                                except Exception:
                                    pass
                            except Exception:
                                try:
                                    await uploader.delete_messages(Config.LOG_CHANNEL, filw.id)
                                    break
                                except Exception:
                                    pass

            if uploader == app:
                try: await rkn_processing.edit("📤 **Wᴀɪᴛɪɴɢ ꜰᴏʀ Pʀᴇᴍɪᴜᴍ Sᴇꜱꜱɪᴏɴ...**")
                except: pass
                async with upload_lock:
                    try: await rkn_processing.edit("📤 **Uᴩʟᴏᴀᴅɪɴɢ...**")
                    except: pass
                    await perform_upload()
            else:
                try: await rkn_processing.edit("📤 **Uᴩʟᴏᴀᴅɪɴɢ...**")
                except: pass
                await perform_upload()
            
            await digital_botz.delete_task(task_id)
            try: await rkn_processing.edit("🎈 Uploaded Successfully....")
            except: pass
            
        except FloodWait as e:
            if main_client.premium and main_client.uploadlimit:
                await digital_botz.increment_used_limit(user_id, -media.file_size)
            await digital_botz.delete_task(task_id)
            try:
                await rkn_processing.edit(f"⚠️ **Telegram Rate Limit:** Waiting {e.value} seconds...")
            except:
                pass
        except Exception as e:
            if main_client.premium and main_client.uploadlimit:
                await digital_botz.increment_used_limit(user_id, -media.file_size)
            await digital_botz.delete_task(task_id)
            try:
                await rkn_processing.edit(f" Eʀʀᴏʀ {e}")
            except:
                pass

    except asyncio.CancelledError:
        print(f"Task {task_id} was successfully cancelled via active_tasks.")
        if main_client.premium and main_client.uploadlimit:
            await digital_botz.increment_used_limit(user_id, -media.file_size)
        await digital_botz.delete_task(task_id)
        try:
            await rkn_processing.edit("❌ **Tᴀꜱᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟy!**")
        except:
            pass

    finally:
        # Erase task from memory once it finishes or gets cancelled
        if task_id in active_tasks:
            del active_tasks[task_id]
            
        if worker_client != main_client:
            worker_loads[worker_client] = max(0, worker_loads.get(worker_client, 0) - 1)
            
        await remove_path(ph_path, file_path, dl_path, metadata_path)
        
        try:
            shutil.rmtree(task_renames_dir, ignore_errors=True)
            shutil.rmtree(task_meta_dir, ignore_errors=True)
        except:
            pass
