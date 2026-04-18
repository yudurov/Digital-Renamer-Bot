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
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Telegram Link : https://t.me/Digital_Botz 
Repo Link : https://github.com/DigitalBotz/Digital-Rename-Bot
License Link : https://github.com/DigitalBotz/Digital-Rename-Bot/blob/main/LICENSE
"""

import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # digital_botz client config
    API_ID = os.environ.get("API_ID", "rfl")
    API_HASH = os.environ.get("API_HASH", "rdl")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "rfl") 
    BOT = None

    # premium account string session required 😢 
    STRING_SESSION = os.environ.get("STRING_SESSION", "rfl")
    
    # database config
    DB_NAME = os.environ.get("DB_NAME","rfl")     
    DB_URL = os.environ.get("DB_URL","rdl")
 
    # other configs
    RKN_PIC = os.environ.get("RKN_PIC", "https://i.ibb.co/fzgHjXQn/1752254564132.png")
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6318135266').split()]
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001925329161"))

    # free upload limit 
    FREE_UPLOAD_LIMIT = 6442450944 # calculation 6*1024*1024*1024=results

    # premium mode feature ✅
    UPLOAD_LIMIT_MODE = True 
    PREMIUM_MODE = True 
    
    #force subs
    try:
        FORCE_SUB = int(os.environ.get("FORCE_SUB", "")) 
    except:
        FORCE_SUB = os.environ.get("FORCE_SUB", "OtherBs")
        
    # wes response configuration     
    PORT = int(os.environ.get("PORT", "8590"))
    BOT_UPTIME = time.time()

class rkn(object):
    # part of text configuration
    START_TXT = """👋 <b>Hello, {}!</b>

<b>Welcome to the Fast and simple file renaming Bot.</b>

Send a file to get started.

🛠 <b>Key features:</b>
• Quick Rename files  
• Custom captions  
• Convert videos & documents  
• Customize thumbnails  
• Modify metadata  

🌟 <i>Lightning-fast with premium enchantments!</i>

🛸 <i>Powered By</i> <a href="https://t.me/xspes">NAm</a> <b>|</b> 🪄 <i>Spell Weaver</i>"""

    ABOUT_TXT = """🪄 <b>BOT PROFILE</b> 🔮

├ 🎯 <b>Name:</b> {}
├ 🛠️ <b>Developers:</b> {}
├ 💻 <b>Programer:</b> {}
├ 📦 <b>Library:</b> {}
├ 🐍 <b>Language:</b> {}
├ 🗃️ <b>Data Base:</b> {}
├ ☁️ <b>Server:</b> <a href='https://deluxhost.net//'>DeluxHost</a>
├ 👨‍💻 <b>Wizard:</b> <a href='https://t.me/xspes'>NAm</a>
└ 🆕 <b>Version:</b> <a href='https://github.com/yudurov/Digital-Renamer-Bot'>{}</a>

✨ <i>Where files transform with magical precision!</i>"""
    
    HELP_TXT = """
<b>•></b> /start Tʜᴇ Bᴏᴛ.

✏️ <b><u>Hᴏᴡ Tᴏ Rᴇɴᴀᴍᴇ A Fɪʟᴇ</u></b>
<b>•></b> Sᴇɴᴅ Aɴy Fɪʟᴇ Aɴᴅ Tyᴩᴇ Nᴇᴡ Fɪʟᴇ Nɴᴀᴍᴇ \nAɴᴅ Aᴇʟᴇᴄᴛ Tʜᴇ Fᴏʀᴍᴀᴛ [ document, video, audio ].           
ℹ️ 𝗔𝗻𝘆 𝗢𝘁𝗵𝗲𝗿 𝗛𝗲𝗹𝗽 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 :- <a href=https://t.me/DigitalBotz_Support>𝑺𝑼𝑷𝑷𝑶𝑹𝑻 𝑮𝑹𝑶𝑼𝑷</a>
"""

    UPGRADE_PREMIUM = """
•⪼ ★𝘗𝘭𝘢𝘯𝘴    -  ⏳𝘋𝘢𝘵𝘦 - 💸𝘗𝘳𝘪𝘤𝘦  
•⪼ 🥉𝘉𝘳𝘰𝘯𝘻𝘦   -   3𝘥𝘢𝘺𝘴   -   $0.47  
•⪼ 🥈𝘚𝘪𝘭𝘷𝘦𝘳   -   7𝘥𝘢𝘺𝘴   -   $0.71  
•⪼ 🥇𝘎𝘰𝘭𝘥    -  15𝘥𝘢𝘺𝘴  -   $1.15  
•⪼ 🏆𝘗𝘭𝘢𝘵𝘪𝘯𝘶𝘮 -  1𝘮𝘰𝘯𝘵𝘩  -   $2.11  
•⪼ 💎𝘋𝘪𝘢𝘮𝘰𝘯𝘥  -  2𝘮𝘰𝘯𝘵𝘩  -   $3.00  
•⪼ ♾️𝘓𝘪𝘧𝘦𝘵𝘪𝘮𝘦  -   ∞   -   $10.00  

🚀 Daily Upload Limit: Unlimited  
🎁 Discount All Plans: $0.11  
"""
    
UPGRADE_PLAN = """
🌟 𝘗𝘭𝘢𝘯: 𝘗𝘳𝘰  
📅 𝘋𝘢𝘵𝘦: 1 𝘮𝘰𝘯𝘵𝘩  
💰 𝘗𝘳𝘪𝘤𝘦: $1.55  
📦 𝘓𝘪𝘮𝘪𝘵: 100 𝘎𝘉  

🚀 𝘗𝘭𝘢𝘯: 𝘜𝘭𝘵𝘢 𝘗𝘳𝘰  
📅 𝘋𝘢𝘵𝘦: 1 𝘮𝘰𝘯𝘵𝘩  
💰 𝘗𝘳𝘪𝘤𝘦: $2.11  
📦 𝘓𝘪𝘮𝘪𝘵: 1000 𝘎𝘉  

♾️ 𝘗𝘭𝘢𝘯: 𝘓𝘪𝘧𝘦𝘵𝘪𝘮𝘦  
📅 𝘋𝘢𝘵𝘦: ∞  
💰 𝘗𝘳𝘪𝘤𝘦: $10.00  
📦 𝘓𝘪𝘮𝘪𝘵: Unlimited  

🎁 - 𝘋𝘪𝘴𝘤𝘰𝘶𝘯𝘵 𝘈𝘭𝘭 𝘗𝘭𝘢𝘯𝘴: $0.11  
"""
    
    THUMBNAIL = """
🌌 <b><u>Hᴏᴡ Tᴏ Sᴇᴛ Tʜᴜᴍʙɴɪʟᴇ</u></b>

<b>•></b> Sᴇɴᴅ Aɴy Pʜᴏᴛᴏ Tᴏ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟy Sᴇᴛ Tʜᴜᴍʙɴɪʟᴇ.
<b>•></b> /del_thumb Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Oʟᴅ Tʜᴜᴍʙɴɪʟᴇ.
<b>•></b> /view_thumb Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Vɪᴇᴡ Yᴏᴜʀ Cᴜʀʀᴇɴᴛ Tʜᴜᴍʙɴɪʟᴇ.
"""
    CAPTION= """
📑 <b><u>Hᴏᴡ Tᴏ Sᴇᴛ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ</u></b>

<b>•></b> /set_caption - Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Sᴇᴛ ᴀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ
<b>•></b> /see_caption - Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Vɪᴇᴡ Yᴏᴜʀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ
<b>•></b> /del_caption - Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ

Exᴀᴍᴩʟᴇ:- `/set_caption 📕 Fɪʟᴇ Nᴀᴍᴇ: {filename}
💾 Sɪᴢᴇ: {filesize}
⏰ Dᴜʀᴀᴛɪᴏɴ: {duration}`
"""
    BOT_STATUS = """
⚡️ ʙᴏᴛ sᴛᴀᴛᴜs ⚡️

⌚️ ʙᴏᴛ ᴜᴩᴛɪᴍᴇ: `{}`
👭 ᴛᴏᴛᴀʟ ᴜsᴇʀꜱ: `{}`
💸 ᴛᴏᴛᴀʟ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs: `{}`
֍ ᴜᴘʟᴏᴀᴅ: `{}`
⊙ ᴅᴏᴡɴʟᴏᴀᴅ: `{}`
"""
    LIVE_STATUS = """
⚡ ʟɪᴠᴇ sᴇʀᴠᴇʀ sᴛᴀᴛᴜs ⚡

⏰ ᴜᴘᴛɪᴍᴇ: `{}`
🔥 ᴄᴘᴜ: `{}%`
📊 ʀᴀᴍ: `{}%` 
💾 ᴛᴏᴛᴀʟ ᴅɪsᴋ: `{}`
📉 ᴜsᴇᴅ sᴘᴀᴄᴇ: `{} {}%`
📁 ғʀᴇᴇ sᴘᴀᴄᴇ: `{}`
📤 ᴜᴘʟᴏᴀᴅ: `{}`
📥 ᴅᴏᴡɴʟᴏᴀᴅ: `{}`
🧩 V𝟹.𝟷.𝟶 [STABLE]
"""
    DIGITAL_METADATA = """
❪ SET CUSTOM METADATA ❫

- /metadata - Tᴏ Sᴇᴛ & Cʜᴀɴɢᴇ ʏᴏᴜʀ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴄᴏᴅᴇ

☞ Fᴏʀ Exᴀᴍᴘʟᴇ:-

`--change-title @OtherBs
--change-video-title @OtherBs
--change-audio-title @OtherBs
--change-subtitle-title @OtherBs
--change-author @OtherBs`

📥 Fᴏʀ Hᴇʟᴘ Cᴏɴᴛ. @DigitalBotz_Support
"""
    
    CUSTOM_FILE_NAME = """
<u>🖋️ Custom File Name</u>

you can pre-add a prefix and suffix along with your new filename

➢ /set_prefix - To add a prefix along with your _filename.
➢ /see_prefix - Tᴏ Sᴇᴇ Yᴏᴜʀ Pʀᴇғɪx !!
➢ /del_prefix - Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Pʀᴇғɪx !!
➢ /set_suffix - To add a suffix along with your filename_.
➢ /see_suffix - Tᴏ Sᴇᴇ Yᴏᴜʀ Sᴜғғɪx !!
➢ /del_suffix - Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Sᴜғғɪx !!

Exᴀᴍᴩʟᴇ:- `/set_suffix @OtherBs`
Exᴀᴍᴩʟᴇ:- `/set_prefix @OtherBs`
"""
    
    #⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
#⚠️ Dᴏɴ'ᴛ Rᴇᴍᴏᴠᴇ Oᴜʀ Cʀᴇᴅɪᴛꜱ @RknDeveloper🙏🥲
    # ᴡʜᴏᴇᴠᴇʀ ɪs ᴅᴇᴘʟᴏʏɪɴɢ ᴛʜɪs ʀᴇᴘᴏ ɪs ᴡᴀʀɴᴇᴅ ⚠️ ᴅᴏ ɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛs ɢɪᴠᴇɴ ɪɴ ᴛʜɪs ʀᴇᴘᴏ #ғɪʀsᴛ ᴀɴᴅ ʟᴀsᴛ ᴡᴀʀɴɪɴɢ ⚠️
    DEV_TXT = """<b><u>Sᴩᴇᴄɪᴀʟ Tʜᴀɴᴋꜱ & Dᴇᴠᴇʟᴏᴩᴇʀꜱ</b></u>
    
» 𝗦𝗢𝗨𝗥𝗖𝗘 𝗖𝗢𝗗𝗘 : <a href=https://github.com/yudurov/Digital-Renamer-Bot>Digital-Rename-fork</a>
» 𝗦𝗢𝗨𝗥𝗖𝗘 𝗖𝗢𝗗𝗘 : <a href=https://github.com/DigitalBotz/Digital-Rename-Bot>Digital-Rename-main</a>

• ❣️ <a href=https://github.com/RknDeveloper>RknDeveloper</a>
• ❣️ <a href=https://github.com/DigitalBotz>DigitalBotz</a>
• ❣️ <a href=https://github.com/JayMahakal98>Jay Mahakal</a>
• ❣️ <a href=https://github.com/Yuilariy>Nam Xspes</a> """
    # ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️

    SEND_METADATA = """
❪ SET CUSTOM METADATA ❫

☞ Fᴏʀ Exᴀᴍᴘʟᴇ:-

`--change-title @OtherBs
--change-video-title @OtherBs
--change-audio-title @OtherBs
--change-subtitle-title @OtherBs
--change-author @OtherBs`

📥 Fᴏʀ Hᴇʟᴘ Cᴏɴᴛ. @DigitalBotz_Support
"""
    
    RKN_PROGRESS = """<b>
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣

┃    🗂️ ᴄᴏᴍᴘʟᴇᴛᴇᴅ: {1}

┃    📦 ᴛᴏᴛᴀʟ ꜱɪᴢᴇ: {2}

┃    🔋 ꜱᴛᴀᴛᴜꜱ: {0}%

┃    {3} ꜱᴘᴇᴇᴅ: {5}/s

┃    ⏰ ᴇᴛᴀ: {4}

╰━━━━━━━━━━━━━━━━➣
</b>"""


# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr
# Update Channel @Digital_Botz & @DigitalBotz_Support
