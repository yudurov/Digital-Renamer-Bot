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
import os, time, asyncio

UPLOAD_TEXT = "📤 Uploading file..."
DOWNLOAD_TEXT = "📥 Downloading file..."

app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)

# ==========================================
# --- QUEUE MANAGER CLASS ---
# ==========================================
class QueueManager:
    def __init__(self):
        self.user_tasks = {}    
        self.upload_queues = {} 
        self.workers = {}       

    def add_task(self, user_id, processing_msg, file_msg, new_name, upload_type, task_id):
        if user_id not in self.user_tasks:
            self.user_tasks[user_id] = []
        self.user_tasks[user_id].append({
            'processing_msg': processing_msg,
            'file_msg': file_msg,
            'new_name': new_name,
            'upload_type': upload_type,
            'task_id': task_id
        })
        return len(self.user_tasks[user_id])

    def has_worker(self, user_id):
        return user_id in self.workers

    def init_upload_queue(self, user_id):
        if user_id not in self.upload_queues:
            self.upload_queues[user_id] = asyncio.Queue()
        return self.upload_queues[user_id]

    def register_workers(self, user_id, dl_task, ul_task):
        self.workers[user_id] = {'dl': dl_task, 'ul': ul_task}

    def cleanup(self, user_id):
        if user_id in self.workers:
            del self.workers[user_id]
        if user_id in self.upload_queues:
            del self.upload_queues[user_id]
        if user_id in self.user_tasks:
            del self.user_tasks[user_id]

manager = QueueManager()

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
                    
                processing_msg = await client.send_message(task.user_id, "🔄 **Rᴇꜱᴜᴍɪɴɢ Iɴᴄᴏᴍᴩʟᴇᴛᴇ Tᴀꜱᴋ...**\n⏳ **Pʀᴏᴄᴇꜱꜱɪɴɢ...**")
                manager.add_task(task.user_id, processing_msg, file_msg, task.new_name, task.upload_type, task.id)
                
                if not manager.has_worker(task.user_id):
                    manager.init_upload_queue(task.user_id)
                    dl_task = asyncio.create_task(download_worker(client, task.user_id))
                    ul_task = asyncio.create_task(upload_worker(client, task.user_id))
                    manager.register_workers(task.user_id, dl_task, ul_task)
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
        user_data = await digital_botz.get_user_data(user_id)
        limit = user_data.get('uploadlimit', 0)
        used = user_data.get('used_limit', 0)
        remain = int(limit) - int(used)
        used_percentage = (int(used) / int(limit) * 100) if limit else 0
        if remain < int(rkn_file.file_size):
            return await message.reply_text(
                f"{used_percentage:.2f}% Of Daily Upload Limit {humanbytes(limit)}.\n\n"
                f"📦 Media Size: {filesize}\n"
                f"📊 Your Used Daily Limit: {humanbytes(used)}\n\n"
                f"You have only **{humanbytes(remain)}** left.\nPlease, Buy Premium Plan.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🪪 Uᴘɢʀᴀᴅᴇ", callback_data="plans")]])
            )

    if await digital_botz.has_premium_access(user_id) and client.premium:
        if not Config.STRING_SESSION:
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
        # CRITICAL FIX: If it is not a ForceReply (like when using /broadcast), pass it along!
        await message.continue_propagation()


@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    user_id = int(update.message.chat.id) 
    new_name = update.message.text
    new_filename_ = new_name.split(":-")[1].strip().replace("`","")
    type = update.data.split("_")[1]
    file_msg = update.message.reply_to_message
    
    rkn_processing = await update.message.edit("`⏳ Added to Queue...`")

    # Add to DB for persistence
    task_id = await digital_botz.add_task(user_id, file_msg.id, new_filename_, type)
    
    pos = manager.add_task(user_id, rkn_processing, file_msg, new_filename_, type, task_id)
    if manager.has_worker(user_id):
        await rkn_processing.edit(f"✅ **Added to Queue!**\nPosition: {pos}")
        return

    manager.init_upload_queue(user_id)
    dl_task = asyncio.create_task(download_worker(bot, user_id))
    ul_task = asyncio.create_task(upload_worker(bot, user_id))
    manager.register_workers(user_id, dl_task, ul_task)

async def download_worker(client, user_id):
    try:
        while user_id in manager.user_tasks and manager.user_tasks[user_id]:
            item = manager.user_tasks[user_id].pop(0)
            rkn_processing = item['processing_msg']
            file_msg = item['file_msg']
            new_filename_ = item['new_name']
            upload_type = item['upload_type']
            task_id = item['task_id']
            
            await digital_botz.update_task_status(task_id, "processing")
            
            if not os.path.isdir("Metadata"): os.mkdir("Metadata")
            if not os.path.isdir("Renames"): os.mkdir("Renames")
            
            user_data = await digital_botz.get_user_data(user_id)
            media = getattr(file_msg, file_msg.media.value)

            try:
                prefix = await digital_botz.get_prefix(user_id)
                suffix = await digital_botz.get_suffix(user_id)
                new_filename = add_prefix_suffix(new_filename_, prefix, suffix)
            except Exception as e:
                await digital_botz.delete_task(task_id)
                await rkn_processing.edit(f"⚠️ Prefix/Suffix Error \nError: {e}")
                continue

            file_path = f"Renames/{new_filename}"
            metadata_path = f"Metadata/{new_filename}"    

            await rkn_processing.edit("`☄️Trying To Download....`")
            
            if client.premium and client.uploadlimit:
                limit = user_data.get('uploadlimit', 0)
                used = user_data.get('used_limit', 0)
                await digital_botz.set_used_limit(user_id, media.file_size)
                total_used = int(used) + int(media.file_size)
                await digital_botz.set_used_limit(user_id, total_used)
            
            try:
                dl_path = await client.download_media(
                    message=file_msg,
                    file_name=file_path,
                    progress=progress_for_pyrogram,
                    progress_args=(DOWNLOAD_TEXT, rkn_processing, time.time())
                )
            except Exception as e:
                if client.premium and client.uploadlimit:
                    used_remove = int(used) - int(media.file_size)
                    await digital_botz.set_used_limit(user_id, used_remove)
                await digital_botz.delete_task(task_id)
                await rkn_processing.edit(f"Download Error: {e}")
                continue

            metadata_mode = await digital_botz.get_metadata_mode(user_id)
            if (metadata_mode):        
                metadata = await digital_botz.get_metadata_code(user_id)
                if metadata:
                    await rkn_processing.edit("I Fᴏᴜɴᴅ Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ\n\n__**Pʟᴇᴀsᴇ Wᴀɪᴛ...**__\n**Aᴅᴅɪɴɢ Mᴇᴛᴀᴅᴀᴛᴀ Tᴏ Fɪʟᴇ....**")            
                    if change_metadata(dl_path, metadata_path, metadata):            
                        await rkn_processing.edit("Metadata Added.....")
                await rkn_processing.edit("**Metadata added to the file successfully ✅**\n\n**Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....**")
            else:
                await rkn_processing.edit("`☄️Trying To Upload....`")
                
            duration = 0
            try:
                parser = createParser(file_path)
                metadata = extractMetadata(parser)
                if metadata and metadata.has("duration"):
                    duration = metadata.get('duration').seconds
                if parser: parser.close()
            except: pass
                
            ph_path = None
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
                     if client.premium and client.uploadlimit:
                         used_remove = int(used) - int(media.file_size)
                         await digital_botz.set_used_limit(user_id, used_remove)
                     await digital_botz.delete_task(task_id)
                     await rkn_processing.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ: ({e})")
                     continue
            else:
                 caption = f"**{new_filename}**"
         
            if (media.thumbs or c_thumb):
                 if c_thumb: ph_path = await client.download_media(c_thumb) 
                 else: ph_path = await client.download_media(media.thumbs[0].file_id)
                 Image.open(ph_path).convert("RGB").save(ph_path)
                 img = Image.open(ph_path)
                 img.resize((320, 320))
                 img.save(ph_path, "JPEG")

            upload_data = {
                'file_path': file_path, 'ph_path': ph_path, 'metadata_path': metadata_path,
                'caption': caption, 'duration': duration, 'rkn_processing': rkn_processing,
                'upload_type': upload_type, 'file_size': media.file_size, 'user_id': user_id,
                'metadata_mode': metadata_mode, 'task_id': task_id, 'dl_path': dl_path, 'used': used
            }
            
            await manager.upload_queues[user_id].put(upload_data)
            await asyncio.sleep(1)
            
    finally:
        if user_id in manager.upload_queues:
            await manager.upload_queues[user_id].put(None)

async def upload_worker(client, user_id):
    try:
        while True:
            if user_id not in manager.upload_queues: break
            data = await manager.upload_queues[user_id].get()
            if data is None: break
                
            uploader = app if (data['file_size'] > 2000 * 1024 * 1024) else client
            file_to_upload = data['metadata_path'] if data['metadata_mode'] else data['file_path']
            
            try:
                if data['file_size'] > 2000 * 1024 * 1024:
                    if data['upload_type'] == "document":
                        filw = await app.send_document(Config.LOG_CHANNEL, document=file_to_upload, thumb=data['ph_path'], caption=data['caption'], progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, data['rkn_processing'], time.time()))
                    elif data['upload_type'] == "video":
                        filw = await app.send_video(Config.LOG_CHANNEL, video=file_to_upload, caption=data['caption'], thumb=data['ph_path'], duration=data['duration'], progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, data['rkn_processing'], time.time()))
                    elif data['upload_type'] == "audio":
                        filw = await app.send_audio(Config.LOG_CHANNEL, audio=file_to_upload, caption=data['caption'], thumb=data['ph_path'], duration=data['duration'], progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, data['rkn_processing'], time.time()))
                    
                    from_chat = filw.chat.id
                    mg_id = filw.id
                    time.sleep(2)
                    await client.copy_message(user_id, from_chat, mg_id)
                    await client.delete_messages(from_chat, mg_id)
                else:
                    if data['upload_type'] == "document":
                        await client.send_document(user_id, document=file_to_upload, thumb=data['ph_path'], caption=data['caption'], progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, data['rkn_processing'], time.time()))
                    elif data['upload_type'] == "video":
                        await client.send_video(user_id, video=file_to_upload, caption=data['caption'], thumb=data['ph_path'], duration=data['duration'], progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, data['rkn_processing'], time.time()))
                    elif data['upload_type'] == "audio":
                        await client.send_audio(user_id, audio=file_to_upload, caption=data['caption'], thumb=data['ph_path'], duration=data['duration'], progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, data['rkn_processing'], time.time()))
                
                await digital_botz.delete_task(data['task_id'])
                await data['rkn_processing'].edit("🎈 Uploaded Successfully....")
                
            except Exception as e:
                if client.premium and client.uploadlimit:
                    used_remove = int(data['used']) - int(data['file_size'])
                    await digital_botz.set_used_limit(user_id, used_remove)
                await digital_botz.delete_task(data['task_id'])
                await data['rkn_processing'].edit(f" Eʀʀᴏʀ {e}")

            finally:
                await remove_path(data['ph_path'], data['file_path'], data['dl_path'], data['metadata_path'])
            
    finally:
        manager.cleanup(user_id)
