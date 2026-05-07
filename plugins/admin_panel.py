# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr
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

# extra imports
from config import Config
from helper.database import digital_botz
from helper.utils import get_seconds, humanbytes
import os, sys, time, asyncio, logging, datetime, pytz, traceback

# pyrogram imports
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
 
@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await digital_botz.total_users_count()
    if bot.premium:
        total_premium_users = await digital_botz.total_premium_users_count()
    else:
        total_premium_users = "Disabled ✅"

    uptime_seconds = int(time.time() - bot.uptime)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{days}d {hours}h {minutes}m {seconds}s"

    start_t = time.time()
    rkn = await message.reply('**ᴘʀᴏᴄᴇssɪɴɢ.....**')    
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000

    await rkn.edit(text=(
        f"**--Bᴏᴛ Sᴛᴀᴛᴜꜱ--** \n\n"
        f"**⌚️ Bᴏᴛ Uᴩᴛɪᴍᴇ:** {uptime} \n"
        f"**🐌 Cᴜʀʀᴇɴᴛ Pɪɴɢ:** `{time_taken_s:.3f} ᴍꜱ` \n"
        f"**👭 Tᴏᴛᴀʟ Uꜱᴇʀꜱ:** `{total_users}`\n"
        f"**💸 ᴛᴏᴛᴀʟ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs:** `{total_premium_users}`"
    ))

# ==========================================
# --- LEADERBOARD COMMAND ---
# ==========================================
@Client.on_message(filters.command(["top", "leaderboard"]) & filters.user(Config.ADMIN))
async def leaderboard_cmd(bot, message):
    lb_type = "lifetime"
    if len(message.command) > 1 and message.command[1].lower() == "daily":
        lb_type = "daily"
        
    rkn = await message.reply('**📊 Fᴇᴛᴄʜɪɴɢ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ...**')
    
    try:
        # Fetch Top 20 from DB
        users = await digital_botz.get_leaderboard(lb_type=lb_type, limit=20)
        
        if not users:
            return await rkn.edit("⚠️ **No data found for the leaderboard yet!**")
            
        title = "All-Time" if lb_type == "lifetime" else "Daily"
        text = f"📊 **Digital Rename Bot - Top 20 {title} Uploaders** 📊\n\n"
        
        for i, user in enumerate(users):
            # Medals
            if i == 0: medal = "🥇"
            elif i == 1: medal = "🥈"
            elif i == 2: medal = "🥉"
            else: medal = "🎖"
                
            u_id = user.get('_id', user.get('id'))
            first_name = user.get('first_name')
            username = user.get('username')
            
            # FALLBACK: If name is missing in old DB entries, fetch from Telegram
            if not first_name:
                try:
                    tg_user = await bot.get_users(u_id)
                    first_name = tg_user.first_name or "User"
                    username = tg_user.username
                except Exception:
                    first_name = "User"

            # Clean name to prevent markdown breaking
            first_name = str(first_name).replace('_', ' ').replace('*', '').replace('`', '').replace('[', '').replace(']', '')
            
            # Format clickables
            if username:
                name_link = f"[{first_name}](https://t.me/{username})"
            else:
                name_link = f"[{first_name}](tg://user?id={u_id})"
                
            # Get Correct Bytes
            used_bytes = user.get('lifetime_used_bytes', 0) if lb_type == "lifetime" else user.get('used_limit', 0)
                
            text += f"{medal} **{i+1}.** {name_link} (`{u_id}`)\n"
            text += f"🚀 **Total Used:** `{humanbytes(used_bytes)}`\n\n"
        
        # Add a tip for the other leaderboard (Using double asterisks now)
        if lb_type == "lifetime":
            text += "💡 **Tip: Use `/top daily` for today's leaderboard.**"
        else:
            text += "💡 **Tip: Use `/top` for the all-time leaderboard.**"
            
        await rkn.edit(text, disable_web_page_preview=True)
        
        # --- SEND TO LOGS CHANNEL ---
        if Config.LOG_CHANNEL:
            try:
                await bot.send_message(
                    chat_id=Config.LOG_CHANNEL, 
                    text=f"**Leaderboard Generated By Admin:**\n\n{text}", 
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Could not send leaderboard to log channel: {e}")
                pass
        # ----------------------------
        
    except Exception as e:
        traceback_str = traceback.format_exc()
        await rkn.edit(f"⚠️ **Error Fetching Leaderboard:**\n\n`{e}`")


@Client.on_message(filters.command('logs') & filters.user(Config.ADMIN))
async def log_file(b, m):
    try:
        await m.reply_document('BotLog.txt')
    except Exception as e:
        await m.reply(str(e))


@Client.on_message(filters.command(["addpremium", "add_premium"]) & filters.user(Config.ADMIN))
async def add_premium(client, message):
    if not client.premium:
        return await message.reply_text("premium mode disabled ✅")
     
    if client.uploadlimit:
        if len(message.command) < 4:
            return await message.reply_text(
                "📜 **Usage:** `/addpremium user_id Plan_Type time`\n\n"
                "🔹 **Plan_Type:** `Pro`, `UltraPro`\n"
                "⏱️ **Time Format:**\n"
                "• `1 min` → minutes\n"
                "• `1 hour` → hours\n"
                "• `1 day` → days\n"
                "• `1 month` → months\n"
                "• `1 year` → year\n"
                "• `Lifetime` → Lifetime Plan\n\n"
                "📃 **Example:** `/addpremium 6318135266 Pro 1 month`",
                quote=True
            )

        user_id = int(message.command[1])
        plan_type = message.command[2]

        if plan_type not in ["Pro", "UltraPro"]:
            return await message.reply_text("🧩 Invalid Plan Type. Please use '`Pro`' or '`UltraPro`' ", quote=True)

        time_string = " ".join(message.command[3:])

        time_zone = datetime.datetime.now(pytz.timezone("Africa/Nairobi"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱️ ᴊᴏɪɴɪɴɢ ᴛɪᴍᴇ : %I:%M:%S %p")

        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
        except:
            user_mention = f"User ID {user_id}"

        if plan_type == "Pro":
            limit = 107374182400
            type = "Pro"
        elif plan_type == "UltraPro":
            limit = 1073741824000
            type = "UltraPro"

        # --- LIFETIME FIX START ---
        if time_string.lower() in ["lifetime", "0"]:
            expiry_time = None
            is_lifetime = True
            time_string = "Lifetime ♾️"
        else:
            seconds = await get_seconds(time_string)
            if seconds <= 0:
                return await message.reply_text(
                    "⏰ Invalid time format. Please use `/addpremium user_id Plan_Type 1 month` or `Lifetime`",
                    quote=True
                )
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            is_lifetime = False

        user_data = {"id": user_id, "expiry_time": expiry_time, "is_lifetime": is_lifetime}
        await digital_botz.addpremium(user_id, user_data, limit, type)

        user_data_db = await digital_botz.get_user_data(user_id)
        limit = user_data_db.get('uploadlimit', 0) if user_data_db else limit
        type = user_data_db.get('usertype', "Free") if user_data_db else type
        
        data = await digital_botz.get_user(user_id)
        expiry = data.get("expiry_time") if data else expiry_time
        
        if data and data.get("is_lifetime", False):
            expiry_str_in_ist = "Lifetime ♾️"
        elif isinstance(expiry, datetime.datetime):
            expiry_str_in_ist = expiry.astimezone(
                pytz.timezone("Africa/Nairobi")
            ).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")
        else:
            expiry_str_in_ist = str(expiry)
        # --- LIFETIME FIX END ---

        await message.reply_text(
            f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ✅\n\n"
            f"👤 ᴜꜱᴇʀ : {user_mention}\n"
            f"⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n"
            f"ᴘʟᴀɴ :- `{type}`\n"
            f"ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ ʟɪᴍɪᴛ :- `{humanbytes(limit)}`\n"
            f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time_string}</code>\n\n"
            f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
            f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}",
            quote=True,
            disable_web_page_preview=True
        )

        try:
            await client.send_message(
                chat_id=user_id,
                text=(
                    f"👋 ʜᴇʏ {user_mention},\n"
                    f"ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴘᴜʀᴄʜᴀꜱɪɴɢ ᴘʀᴇᴍɪᴜᴍ.\n"
                    f"ᴇɴᴊᴏʏ !! ✨🎉\n\n"
                    f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time_string}</code>\n"
                    f"ᴘʟᴀɴ :- `{type}`\n"
                    f"ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ ʟɪᴍɪᴛ :- `{humanbytes(limit)}`\n"
                    f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
                    f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}"
                ),
                disable_web_page_preview=True              
            )
        except:
            pass

    else:
        if len(message.command) < 3:
            return await message.reply_text(
                "📜 **Usage:** `/addpremium user_id time`\n\n"
                "⏱️ **Time Format:**\n"
                "• `1 min` → minutes\n"
                "• `1 hour` → hours\n"
                "• `1 day` → days\n"
                "• `1 month` → months\n"
                "• `1 year` → year\n"
                "• `Lifetime` → Lifetime Plan\n\n"
                "📃 **Example:** `/addpremium 6318135266 1 month`",
                quote=True
            )

        user_id = int(message.command[1])
        time_string = " ".join(message.command[2:])

        time_zone = datetime.datetime.now(pytz.timezone("Africa/Nairobi"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱️ ᴊᴏɪɴɪɴɢ ᴛɪᴍᴇ : %I:%M:%S %p")

        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
        except:
            user_mention = f"User ID {user_id}"

        # --- LIFETIME FIX START ---
        if time_string.lower() in ["lifetime", "0"]:
            expiry_time = None
            is_lifetime = True
            time_string = "Lifetime ♾️"
        else:
            seconds = await get_seconds(time_string)
            if seconds <= 0:
                return await message.reply_text(
                    "Invalid time format. Please use `/addpremium user_id 1 year 1 month 1 day 1 min 10 s` or `Lifetime`",
                    quote=True
                )
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            is_lifetime = False

        user_data = {"id": user_id, "expiry_time": expiry_time, "is_lifetime": is_lifetime}
        await digital_botz.addpremium(user_id, user_data)
        
        data = await digital_botz.get_user(user_id)
        expiry = data.get("expiry_time") if data else expiry_time
        
        if data and data.get("is_lifetime", False):
            expiry_str_in_ist = "Lifetime ♾️"
        elif isinstance(expiry, datetime.datetime):
            expiry_str_in_ist = expiry.astimezone(
                pytz.timezone("Africa/Nairobi")
            ).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")
        else:
            expiry_str_in_ist = str(expiry)
        # --- LIFETIME FIX END ---

        await message.reply_text(
            f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ꜱᴜᴄꜱꜱᴇꜱꜰᴜʟʟʏ ✅\n\n"
            f"👤 ᴜꜱᴇʀ : {user_mention}\n"
            f"⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n"
            f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time_string}</code>\n\n"
            f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
            f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}",
            quote=True,
            disable_web_page_preview=True
        )

        try:
            await client.send_message(
                chat_id=user_id,
                text=(
                    f"👋 ʜᴇʏ {user_mention},\n"
                    f"ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴘᴜʀᴄʜᴀꜱɪɴɢ ᴘʀᴇᴍɪᴜᴍ.\n"
                    f"ᴇɴᴊᴏʏ !! ✨🎉\n\n"
                    f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time_string}</code>\n"
                    f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
                    f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}"
                ),
                disable_web_page_preview=True              
            )
        except:
            pass


@Client.on_message(filters.command(["removepremium", "remove_premium"]) & filters.user(Config.ADMIN))
async def remove_premium(bot, message):
    if not bot.premium:
        return await message.reply_text("premium mode disabled ✅")
     
    if len(message.command) == 2:
        user_id = int(message.command[1])
        try:
            user = await bot.get_users(user_id)
            user_mention = user.mention
        except:
            user_mention = f"User ID {user_id}"

        if await digital_botz.has_premium_access(user_id):
            await digital_botz.remove_premium(user_id)
            await message.reply_text(
                f"ʜᴇʏ {user_mention}, ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ.",
                quote=True
            )
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"<b>ʜᴇʏ {user_mention},\n\n"
                        f"✨ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ᴛᴏ ᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ\n\n"
                        f"ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘʟᴀɴ ʜᴇʀᴇ /myplan</b>"
                    )
                )
            except: pass
        else:
            await message.reply_text(
                "ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ !\nᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ, ɪᴛ ᴡᴀꜱ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ɪᴅ ?",
                quote=True
            )
    else:
        await message.reply_text("📜 ᴜꜱᴀɢᴇ : `/remove_premium ᴜꜱᴇʀ ɪᴅ`", quote=True)


@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(b, m):
    rkn = await b.send_message(
        text="**🔄 ᴘʀᴏᴄᴇssᴇs sᴛᴏᴘᴘᴇᴅ. ʙᴏᴛ ɪs ʀᴇsᴛᴀʀᴛɪɴɢ.....**",
        chat_id=m.chat.id
    )
    
    try:
        failed = 0
        success = 0
        deactivated = 0
        blocked = 0
        start_time = time.time()
        total_users = await digital_botz.total_users_count()
        all_users = await digital_botz.get_all_users()
        
        for user in all_users: 
            user_id = user.get('_id', user.get('id'))
            if not user_id:
                continue
                
            try:
                restart_msg = (
                    f"**🔄 ᴘʀᴏᴄᴇssᴇs sᴛᴏᴘᴘᴇᴅ. ʙᴏᴛ ɪs ʀᴇsᴛᴀʀᴛɪɴɢ.....\n\n"
                    f"✅️ ʙᴏᴛ ɪs ʀᴇsᴛᴀʀᴛᴇᴅ. ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ.**"
                )
                await b.send_message(user_id, restart_msg)
                success += 1
            except InputUserDeactivated:
                deactivated += 1
                await digital_botz.delete_user(user_id)
            except UserIsBlocked:
                blocked += 1
                await digital_botz.delete_user(user_id)
            except Exception as e:
                failed += 1
                pass
                
            try:
                if (success + failed + deactivated + blocked) % 50 == 0:
                    await rkn.edit(
                        f"<u>ʀᴇsᴛᴀʀᴛ ɪɴ ᴩʀᴏɢʀᴇꜱꜱ:</u>\n\n"
                        f"• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {total_users}\n"
                        f"• sᴜᴄᴄᴇssғᴜʟ: {success}\n"
                        f"• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n"
                        f"• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n"
                        f"• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}"
                    )
            except FloodWait as e:
                await asyncio.sleep(e.value)

        completed_restart = datetime.timedelta(seconds=int(time.time() - start_time))
        await rkn.edit(
            f"ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʀᴇsᴛᴀʀᴛ: {completed_restart}\n\n"
            f"• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {total_users}\n"
            f"• sᴜᴄᴄᴇssғᴜʟ: {success}\n"
            f"• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n"
            f"• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n"
            f"• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}"
        )
    except Exception as e:
        traceback_str = traceback.format_exc()
        await rkn.edit(f"⚠️ **Critical Error during Restart:**\n\n`{e}`\n\n`{traceback_str[-800:]}`")
        
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.private & filters.command("ban") & filters.user(Config.ADMIN))
async def ban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            f"🚫 Use this command to ban any user from the bot.\n\n"
            f"📜 Usage:\n\n"
            f"`/ban user_id ban_duration ban_reason`\n\n"
            f"🧪 Example:\n"
            f"`/ban 1234567 28 You misused me.`\n\n"
            f"✅ This will ban user with ID `1234567` for `28` days for the reason: `You misused me`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."
        try:
            await c.send_message(
                user_id,              
                f"🚫 You are banned to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n"
                f"**Message from the admin**"
            )
            ban_log_text += '\n\nUser notified successfully!'
        except:
            ban_log_text += f"\n\nUser notification failed (user may have blocked the bot)."

        await digital_botz.ban_user(user_id, ban_duration, ban_reason)
        await m.reply_text(ban_log_text, quote=True)
    except Exception as e:
        await m.reply_text(f"🧪 Error occurred!\n\n`{e}`", quote=True)


@Client.on_message(filters.private & filters.command("unban") & filters.user(Config.ADMIN))
async def unban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            f"🔓 Use this command to unban any user.\n\n"
            f"📜 Usage:\n\n"
            f"`/unban user_id`\n\n"
            f"🧪 Example:\n"
            f"`/unban 1234567`\n\n"
            f"✅ This will unban user with ID `1234567`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user {user_id}"
        try:
            await c.send_message(user_id, f"Your ban was lifted!")
            unban_log_text += '\n\nUser notified successfully!'
        except:
            unban_log_text += f"\n\nUser notification failed!"
            
        await digital_botz.remove_ban(user_id)
        await m.reply_text(unban_log_text, quote=True)
    except Exception as e:
        await m.reply_text(f"🧪 Error occurred!\n\n`{e}`", quote=True)


@Client.on_message(filters.private & filters.command("banned_users") & filters.user(Config.ADMIN))
async def _banned_users(_, m: Message):
    try:
        all_banned_users = await digital_botz.get_all_banned_users()
        banned_usr_count = 0
        text = ''
        for banned_user in all_banned_users: 
            user_id = banned_user.get('_id', banned_user.get('id')) 
            ban_status = banned_user.get('ban_status', {})
            ban_duration = ban_status.get('ban_duration', 0)
            banned_on = ban_status.get('banned_on', 'Unknown')
            ban_reason = ban_status.get('ban_reason', 'None')
            banned_usr_count += 1
            text += (
                f"> **user_id**: `{user_id}`, "
                f"**Ban Duration**: `{ban_duration}`, "
                f"**Banned on**: `{banned_on}`, "
                f"**Reason**: `{ban_reason}`\n\n"
            )
        reply_text = f"📜 Total banned user(s): `{banned_usr_count}`\n\n{text}"
        
        if len(reply_text) > 4096:
            with open('banned-users.txt', 'w') as f:
                f.write(reply_text)
            await m.reply_document('banned-users.txt', True)
            os.remove('banned-users.txt')
            return
            
        await m.reply_text(reply_text, True)
    except Exception as e:
        traceback_str = traceback.format_exc()
        await m.reply_text(f"⚠️ **Error Fetching Banned Users:**\n\n`{e}`\n\n`{traceback_str[-800:]}`")

     
@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN))
async def broadcast_handler(bot: Client, m: Message):
    # Enforce replying to a message
    if not m.reply_to_message:
        return await m.reply_text("⚠️ **Please reply to a message (text, photo, or file) with `/broadcast` to send it to all users.**")

    # Let the admin know it started immediately
    sts_msg = await m.reply_text("🚀 **Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..! Fetching users...**") 

    try:
        # Wrap log channel message in try/except so it doesn't crash the script if log channel is misconfigured
        try:
            if Config.LOG_CHANNEL:
                await bot.send_message(
                    Config.LOG_CHANNEL,
                    f"{m.from_user.mention} or {m.from_user.id} ʜᴀꜱ ꜱᴛᴀʀᴛᴇᴅ ᴀ Bʀᴏᴀᴅᴄᴀꜱᴛ......🌋"
                )
        except Exception as e:
            logger.error(f"Log channel error during broadcast: {e}")
            pass

        all_users = await digital_botz.get_all_users() 
        broadcast_msg = m.reply_to_message
        
        done = 0
        failed = 0
        success = 0
        start_time = time.time()
        total_users = await digital_botz.total_users_count()
        
        for user in all_users: 
            user_id = user.get('_id', user.get('id'))
            if not user_id:
                continue
                
            sts = await send_msg(user_id, broadcast_msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await digital_botz.delete_user(user_id)
                
            done += 1
            if not done % 20:
                await sts_msg.edit(
                    f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \n"
                    f"Tᴏᴛᴀʟ Uꜱᴇʀꜱ: {total_users} \n"
                    f"Cᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\n"
                    f"Sᴜᴄᴄᴇꜱꜱ: {success}\n"
                    f"Fᴀɪʟᴇᴅ: {failed}"
                )
                
        completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts_msg.edit(
            f"✅ Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \n"
            f"Cᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\n"
            f"Tᴏᴛᴀʟ Uꜱᴇʀꜱ: {total_users}\n"
            f"Cᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\n"
            f"Sᴜᴄᴄᴇꜱꜱ: {success}\n"
            f"Fᴀɪʟᴇᴅ: {failed}"
        )

    except Exception as e:
        # IF IT CRASHES, IT WILL PRINT THE ERROR DIRECTLY TO TELEGRAM!
        traceback_str = traceback.format_exc()
        await sts_msg.edit(f"⚠️ **Critical Error during Broadcast:**\n\n`{e}`\n\n`{traceback_str[-800:]}`")

           
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        return 400
    except UserIsBlocked:
        return 400
    except PeerIdInvalid:
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500

# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr
