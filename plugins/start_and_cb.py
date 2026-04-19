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
"""

# extra imports
import random, asyncio, datetime, pytz, time, psutil, shutil

# pyrogram imports
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from pyrogram.enums import ChatAction

# bots imports
from helper.database import digital_botz
from config import Config, rkn
from helper.utils import humanbytes
from plugins import __version__ as _bot_version_, __developer__, __database__, __library__, __language__, __programer__

# --- GLOBAL VARIABLES FOR NETWORK STATS ---
STATS_STARTED = False
LAST_SENT = 0
LAST_RECV = 0

async def stats_loop():
    """Background task to accumulate network usage to DB"""
    global LAST_SENT, LAST_RECV
    # Initialize with current values
    LAST_SENT = psutil.net_io_counters().bytes_sent
    LAST_RECV = psutil.net_io_counters().bytes_recv
    
    while True:
        try:
            await asyncio.sleep(60) # Update every 1 minute
            
            curr_sent = psutil.net_io_counters().bytes_sent
            curr_recv = psutil.net_io_counters().bytes_recv
            
            # Calculate delta (difference since last check)
            # If current < last, it means VPS restarted and counters reset
            if curr_sent < LAST_SENT:
                sent_delta = curr_sent
            else:
                sent_delta = curr_sent - LAST_SENT
                
            if curr_recv < LAST_RECV:
                recv_delta = curr_recv
            else:
                recv_delta = curr_recv - LAST_RECV
            
            # Update global counters
            LAST_SENT = curr_sent
            LAST_RECV = curr_recv
            
            # Send delta to database to add to total
            if sent_delta > 0 or recv_delta > 0:
                await digital_botz.update_network_stats(sent_delta, recv_delta)
                
        except Exception as e:
            print(f"Error in stats_loop: {e}")
            await asyncio.sleep(60)

def format_uptime(seconds: int) -> str:
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"


upgrade_button = InlineKeyboardMarkup([[        
        InlineKeyboardButton('buy premium ✓', user_id=int(6318135266)),
         ],[
        InlineKeyboardButton("Bᴀᴄᴋ", callback_data = "start")
]])

upgrade_trial_button = InlineKeyboardMarkup([[        
        InlineKeyboardButton('buy premium ✓', user_id=int(6318135266)),
         ],[
        InlineKeyboardButton("ᴛʀɪᴀʟ - 𝟷𝟸 ʜᴏᴜʀs ✓", callback_data = "give_trial"),
        InlineKeyboardButton("Bᴀᴄᴋ", callback_data = "start")
]])


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    # --- START NETWORK STATS COLLECTOR ---
    global STATS_STARTED
    if not STATS_STARTED:
        asyncio.create_task(stats_loop())
        STATS_STARTED = True
    # -------------------------------------

    start_button = [[
        InlineKeyboardButton('Uᴩᴅᴀ𝚃ᴇꜱ', url='https://t.me/OtherBs'),
        InlineKeyboardButton('Sᴜᴩᴩᴏʀ𝚃', url='https://t.me/DigitalBotz_Support')
    ],[
        InlineKeyboardButton('Aʙᴏυᴛ', callback_data='about'),
        InlineKeyboardButton('Hᴇʟᴩ', callback_data='help')
    ]]

    if client.premium:
        start_button.append([
            InlineKeyboardButton('💸 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ 💸', callback_data='upgrade')
        ])

    user = message.from_user
    await digital_botz.add_user(client, message)

    # 🧩 Send sticker
    await message.reply_sticker(
        "CAACAgQAAxkBAAEQpqxppEM8tUFUsnly1FGKhfuvYYJgbQACDAoAAnmg0VDxpztbUXqCbDoE"
    )

    # ⏳ Wait 2 seconds
    await asyncio.sleep(1)

    # ⌨️ Typing animation
    await client.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    # ⏳ Typing duration
    await asyncio.sleep(1)

    # 📝 Send start message
    if Config.RKN_PIC:
        await message.reply_photo(
            Config.RKN_PIC,
            caption=rkn.START_TXT.format(user.mention),
            reply_markup=InlineKeyboardMarkup(start_button)
        )
    else:
        await message.reply_text(
            rkn.START_TXT.format(user.mention),
            reply_markup=InlineKeyboardMarkup(start_button),
            disable_web_page_preview=True
        )


@Client.on_message(filters.private & filters.command("myplan"))
async def myplan(client, message):
    if not client.premium:
        return # premium mode disabled ✓

    user_id = message.from_user.id
    user = message.from_user.mention
    
    if await digital_botz.has_premium_access(user_id):
        data = await digital_botz.get_user(user_id)
        
        # --- LIFETIME PLAN FIX ---
        if data.get("is_lifetime", False):
            expiry_str_in_ist = "Lifetime ♾️"
            time_left_str = "Unlimited ♾️"
        else:
            expiry_str_in_ist = data.get("expiry_time")
            if expiry_str_in_ist:
                time_left_str = expiry_str_in_ist - datetime.datetime.now()
            else:
                expiry_str_in_ist = "Unknown"
                time_left_str = "Unknown"
        # -------------------------

        text = f"👤 ᴜꜱᴇʀ :- {user}\n🆔 ᴜꜱᴇʀ ɪᴅ :- <code>{user_id}</code>\n"

        if client.uploadlimit:
            await digital_botz.reset_uploadlimit_access(user_id)                
            user_data = await digital_botz.get_user_data(user_id)
            limit = user_data.get('uploadlimit', 0)
            used = user_data.get('used_limit', 0)
            remain = int(limit) - int(used)
            type = user_data.get('usertype', "Free")
            
            # PERFECT LIFETIME LIMITS FIX
            if data.get("is_lifetime", False):
                type = "Lifetime ♾️"
                limit_text = "Unlimited ♾️"
                remain_text = "Unlimited ♾️"
            else:
                limit_text = humanbytes(limit)
                remain_text = humanbytes(remain)

            text += f"📦 ᴘʟᴀɴ :- `{type}`\n📈 ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ ʟɪᴍɪᴛ :- `{limit_text}`\n📊 ᴛᴏᴅᴀʏ ᴜsᴇᴅ :- `{humanbytes(used)}`\n🧮 ʀᴇᴍᴀɪɴ :- `{remain_text}`\n\n"

        text += f"⏳ ᴛɪᴍᴇ ʟᴇꜰᴛ : {time_left_str}\n\n📅 ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}"

        await message.reply_text(text, quote=True)

    else:
        if client.uploadlimit:
            user_data = await digital_botz.get_user_data(user_id)
            limit = user_data.get('uploadlimit', 0)
            used = user_data.get('used_limit', 0)
            remain = int(limit) - int(used)
            type = user_data.get('usertype', "Free")

            text = f"👤 ᴜꜱᴇʀ :- {user}\n🆔 ᴜꜱᴇʀ ɪᴅ :- <code>{user_id}</code>\n📦 ᴘʟᴀɴ :- `{type}`\n📈 ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ ʟɪᴍɪᴛ :- `{humanbytes(limit)}`\n📊 ᴛᴏᴅᴀʏ ᴜsᴇᴅ :- `{humanbytes(used)}`\n🧮 ʀᴇᴍᴀɪɴ :- `{humanbytes(remain)}`\n📅 ᴇxᴘɪʀᴇᴅ ᴅᴀᴛᴇ :- ʟɪғᴇᴛɪᴍᴇ\n\n💎 ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ, ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ 👇"

            await message.reply_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 ᴄʜᴇᴄᴋᴏᴜᴛ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ 💸", callback_data='upgrade')]]), quote=True)

        else:
            m=await message.reply_sticker("CAACAgIAAxkBAAIBTGVjQbHuhOiboQsDm35brLGyLQ28AAJ-GgACglXYSXgCrotQHjibHgQ")
            await message.reply_text(
                f"ʜᴇʏ {user},\n\nʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ. ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ ᴘʀᴇᴍɪᴜᴍ, ᴘʟᴇᴀꜱᴇ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ. 👇",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 ᴄʜᴇᴄᴋᴏᴜᴛ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ 💸", callback_data='upgrade')]]))			 
            await asyncio.sleep(2)
            await m.delete()

@Client.on_message(filters.private & filters.command("plans"))
async def plans(client, message):
    if not client.premium:
        return # premium mode disabled ✓

    user = message.from_user
    upgrade_msg = rkn.UPGRADE_PLAN.format(user.mention) if client.uploadlimit else rkn.UPGRADE_PREMIUM.format(user.mention)
    
    free_trial_status = await digital_botz.get_free_trial_status(user.id)
    if not await digital_botz.has_premium_access(user.id):
        if not free_trial_status:
            await message.reply_text(text=upgrade_msg, reply_markup=upgrade_trial_button, disable_web_page_preview=True)
        else:
            await message.reply_text(text=upgrade_msg, reply_markup=upgrade_button, disable_web_page_preview=True)
    else:
        await message.reply_text(text=upgrade_msg, reply_markup=upgrade_button, disable_web_page_preview=True)
   
  
@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    # --- ENSURE STATS ARE RUNNING ---
    global STATS_STARTED
    if not STATS_STARTED:
        asyncio.create_task(stats_loop())
        STATS_STARTED = True
    # --------------------------------

    data = query.data 
    if data == "start":
        start_button = [[        
            InlineKeyboardButton('Uᴩᴅᴀ𝚃ᴇꜱ', url='https://t.me/OtherBs'),
            InlineKeyboardButton('Sᴜᴩᴩᴏʀ𝚃', url='https://t.me/DigitalBotz_Support')
        ],[
            InlineKeyboardButton('Aʙᴏυᴛ', callback_data='about'),
            InlineKeyboardButton('Hᴇʟᴩ', callback_data='help')       
        ]]
        if client.premium:
            start_button.append([InlineKeyboardButton('💸 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ 💸', callback_data='upgrade')])
        await query.message.edit_text(
            text=rkn.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(start_button))

    elif data == "help":
        await query.message.edit_text(
            text=rkn.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="thumbnail"),
                InlineKeyboardButton("ᴄᴀᴘᴛɪᴏɴ", callback_data="caption")
            ],[
                InlineKeyboardButton("ᴄᴜsᴛᴏᴍ ғɪʟᴇ ɴᴀᴍᴇ", callback_data="custom_file_name")
            ],[
                InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton("ᴍᴇᴛᴀᴅᴀᴛᴀ", callback_data="digital_meta_data")
            ],[
                InlineKeyboardButton("Bᴀᴄᴋ", callback_data="start")
            ]])) 

    elif data == "about":
        about_button = [[
            InlineKeyboardButton("𝚂ᴏᴜʀᴄᴇ", callback_data="source_code"),
            InlineKeyboardButton("ʙᴏᴛ sᴛᴀᴛᴜs", callback_data="bot_status")
        ],[
            InlineKeyboardButton("ʟɪᴠᴇ sᴛᴀᴛᴜs", callback_data="live_status")
        ]]
        if client.premium:
            about_button[-1].append(InlineKeyboardButton("ᴜᴘɢʀᴀᴅᴇ", callback_data="upgrade"))
            about_button.append([InlineKeyboardButton("Bᴀᴄᴋ", callback_data="start")])
        else:
            about_button[-1].append(InlineKeyboardButton("Bᴀᴄᴋ", callback_data="start"))
        await query.message.edit_text(
            text=rkn.ABOUT_TXT.format(client.mention, __developer__, __programer__, __library__, __language__, __database__, _bot_version_),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(about_button))

    elif data == "upgrade":
        if not client.premium:
            return await query.message.delete()
        user = query.from_user
        upgrade_msg = rkn.UPGRADE_PLAN.format(user.mention) if client.uploadlimit else rkn.UPGRADE_PREMIUM.format(user.mention)
        free_trial_status = await digital_botz.get_free_trial_status(query.from_user.id)
        if not await digital_botz.has_premium_access(query.from_user.id):
            if not free_trial_status:
                await query.message.edit_text(text=upgrade_msg, disable_web_page_preview=True, reply_markup=upgrade_trial_button)
            else:
                await query.message.edit_text(text=upgrade_msg, disable_web_page_preview=True, reply_markup=upgrade_button)
        else:
            await query.message.edit_text(text=upgrade_msg, disable_web_page_preview=True, reply_markup=upgrade_button)

    elif data == "give_trial":
        if not client.premium:
            return await query.message.delete()
        await query.message.delete()
        free_trial_status = await digital_botz.get_free_trial_status(query.from_user.id)
        if not free_trial_status:
            await digital_botz.give_free_trial(query.from_user.id)
            new_text = "**ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴛʀɪᴀʟ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ 𝟷𝟸 ʜᴏᴜʀs...**"
        else:
            new_text = "**🤣 ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ᴜsᴇᴅ ғʀᴇᴇ...**"
        await client.send_message(query.from_user.id, text=new_text)

    elif data == "thumbnail":
        await query.message.edit_text(text=rkn.THUMBNAIL, disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Bᴀᴄᴋ", callback_data="help")]]))

    elif data == "caption":
        await query.message.edit_text(text=rkn.CAPTION, disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Bᴀᴄᴋ", callback_data="help")]]))

    elif data == "custom_file_name":
        await query.message.edit_text(text=rkn.CUSTOM_FILE_NAME, disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Bᴀᴄᴋ", callback_data="help")]]))

    elif data == "digital_meta_data":
        await query.message.edit_text(text=rkn.DIGITAL_METADATA, disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Bᴀᴄᴋ", callback_data="help")]]))

    elif data == "bot_status":
        #📜 fetch real values
        real_total_users = await digital_botz.total_users_count()
        real_total_premium_users = await digital_botz.total_premium_users_count()
        #🪄 Magic Boost
        total_users = real_total_users + 1009
        total_premium_users = real_total_premium_users + 50 if client.premium else "Disabled ✅"
        
        uptime = format_uptime(int(time.time() - client.uptime))
        
        # --- FETCH NETWORK FROM DB ---
        stats = await digital_botz.get_network_stats()
        sent = humanbytes(stats['sent'])
        recv = humanbytes(stats['recv'])
        # -----------------------------
        
        await query.message.edit_text(
            text=rkn.BOT_STATUS.format(uptime, total_users, total_premium_users, sent, recv),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Bᴀᴄᴋ", callback_data="about")]]))

    elif data == "live_status":
        uptime = format_uptime(int(time.time() - client.uptime))
        total, used, free = shutil.disk_usage(".")
        total = humanbytes(total)
        used = humanbytes(used)
        free = humanbytes(free)
        
        # --- FETCH NETWORK FROM DB ---
        stats = await digital_botz.get_network_stats()
        sent = humanbytes(stats['sent'])
        recv = humanbytes(stats['recv'])
        # -----------------------------
        
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        await query.message.edit_text(
            text=rkn.LIVE_STATUS.format(uptime, cpu_usage, ram_usage, total, used, disk_usage, free, sent, recv),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Bᴀᴄᴋ", callback_data="about")]]))

    elif data == "source_code":
        await query.message.edit_text(
            text=rkn.DEV_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                # ⚠️ DO NOT REMOVE MAIN SOURCE ⚠️
                InlineKeyboardButton(
                    "💞 Mᴀɪɴ Sᴏᴜʀᴄᴇ 💞",
                    url="https://github.com/DigitalBotz/Digital-Rename-Bot"
                )
            ],
            [
                # ✅ Forked source button
                InlineKeyboardButton(
                    "🍴 Fᴏʀᴋᴇᴅ Sᴏᴜʀᴄᴇ 🍴",
                    url="https://github.com/yudurov/Digital-Renamer-Bot"
                )
            ],[
                InlineKeyboardButton("🔒 Cʟᴏꜱᴇ", callback_data="close"),
                InlineKeyboardButton("◀️ Bᴀᴄᴋ", callback_data="start")
            ]])
    )

    elif data.startswith("upload"):
        await upload_doc(client, query)

    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()
