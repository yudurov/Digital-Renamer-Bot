# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr
# Special Thanks To (https://github.com/JayMahakal98)
# Update Channel @Digital_Botz & @DigitalBotz_Support

"""
Apache License 2.0
Copyright (c) 2022 @Digital_Botz
"""

import datetime, time
from typing import Optional, Any
from pymongo import AsyncMongoClient
from pydantic import BaseModel, Field
from beanie import Document, init_beanie
from config import Config
from helper.utils import send_log

# ==========================================
# --- BEANIE & PYDANTIC MODELS ---
# ==========================================
class BanStatus(BaseModel):
    is_banned: bool = False
    ban_duration: int = 0
    banned_on: str = Field(default_factory=lambda: datetime.date.max.isoformat())
    ban_reason: str = ""

class User(Document):
    id: int = Field(alias="_id")
    join_date: str = Field(default_factory=lambda: datetime.date.today().isoformat())
    file_id: Optional[str] = None
    caption: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    used_limit: int = 0
    usertype: str = "Free"
    uploadlimit: int = Config.FREE_UPLOAD_LIMIT
    daily: Any = None
    metadata_mode: bool = False
    metadata_code: str = "--change-title @OtherBs\n--change-video-title @OtherBs\n--change-audio-title @OtherBs\n--change-subtitle-title @OtherBs\n--change-author @OtherBs"
    ban_status: BanStatus = Field(default_factory=BanStatus)

    class Settings:
        name = "user"

class PremiumUser(Document):
    user_id: int = Field(alias="id")
    expiry_time: Optional[datetime.datetime] = None
    has_free_trial: bool = False

    class Settings:
        name = "premium"

class BotStats(Document):
    id: str = Field(default="network_stats", alias="_id")
    sent: int = 0
    recv: int = 0

    class Settings:
        name = "stats"

class Task(Document):
    user_id: int
    file_msg_id: int
    new_name: str
    upload_type: str
    status: str = "pending"
    created_at: float = Field(default_factory=time.time)

    class Settings:
        name = "tasks"

# ==========================================
# --- DATABASE WRAPPER CLASS ---
# ==========================================
class Database:
    def __init__(self, uri, database_name):
        self.uri = uri
        self.database_name = database_name
        self._client = None
        self.db = None

    async def init_db(self):
        self._client = AsyncMongoClient(self.uri)
        self.db = self._client[self.database_name]
        await init_beanie(database=self.db, document_models=[User, PremiumUser, BotStats, Task])
        print("✅ Database Layer Initialized via Beanie/Pydantic")

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = User(id=u.id)
            await user.insert()
            await send_log(b, u)

    async def is_user_exist(self, id: int):
        return await User.get(id) is not None

    async def total_users_count(self):
        return await User.count()

    async def get_all_users(self):
        users = await User.find_all().to_list()
        return [user.model_dump(by_alias=True) for user in users]

    async def delete_user(self, user_id: int):
        user = await User.get(user_id)
        if user: await user.delete()
    
    async def set_thumbnail(self, id: int, file_id: str):
        user = await User.get(id)
        if user:
            user.file_id = file_id
            await user.save()

    async def get_thumbnail(self, id: int):
        user = await User.get(id)
        return user.file_id if user else None

    async def set_caption(self, id: int, caption: str):
        user = await User.get(id)
        if user:
            user.caption = caption
            await user.save()

    async def get_caption(self, id: int):
        user = await User.get(id)
        return user.caption if user else None

    async def set_prefix(self, id: int, prefix: str):
        user = await User.get(id)
        if user:
            user.prefix = prefix
            await user.save()

    async def get_prefix(self, id: int):
        user = await User.get(id)
        return user.prefix if user else None

    async def set_suffix(self, id: int, suffix: str):
        user = await User.get(id)
        if user:
            user.suffix = suffix
            await user.save()

    async def get_suffix(self, id: int):
        user = await User.get(id)
        return user.suffix if user else None

    async def set_metadata_mode(self, id: int, bool_meta: bool):
        user = await User.get(id)
        if user:
            user.metadata_mode = bool_meta
            await user.save()

    async def get_metadata_mode(self, id: int):
        user = await User.get(id)
        return user.metadata_mode if user else False

    async def set_metadata_code(self, id: int, metadata_code: str):
        user = await User.get(id)
        if user:
            user.metadata_code = metadata_code
            await user.save()

    async def get_metadata_code(self, id: int):
        user = await User.get(id)
        return user.metadata_code if user else None

    async def set_used_limit(self, id: int, used: int):
        user = await User.get(id)
        if user:
            user.used_limit = used
            await user.save()
      
    async def set_usertype(self, id: int, type: str):
        user = await User.get(id)
        if user:
            user.usertype = type
            await user.save()

    async def set_uploadlimit(self, id: int, limit: int):
        user = await User.get(id)
        if user:
            user.uploadlimit = limit
            await user.save()
  
    async def set_reset_dailylimit(self, id: int, date):
        user = await User.get(id)
        if user:
            user.daily = date
            await user.save()
        
    async def reset_uploadlimit_access(self, user_id: int):
        seconds = 1440 * 60
        reset_date = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        
        user = await User.get(user_id)
        if user:
            expiry_time = user.daily
            current_time = datetime.datetime.now()
            
            needs_reset = (
                expiry_time is None or
                expiry_time == 0 or
                not isinstance(expiry_time, datetime.datetime) or
                current_time > expiry_time
            )
            
            if needs_reset:
                user.daily = reset_date
                user.used_limit = 0
                await user.save()
                        
    async def get_user_data(self, id: int) -> dict:
        user = await User.get(id)
        return user.model_dump(by_alias=True) if user else None
        
    async def get_user(self, user_id: int):
        prem = await PremiumUser.find_one(PremiumUser.user_id == user_id)
        return prem.model_dump(by_alias=True) if prem else {}

    async def add_premium(self, user_id: int, user_data: dict, limit=None, type=None):    
        prem = await PremiumUser.find_one(PremiumUser.user_id == user_id)
        if not prem:
            prem = PremiumUser(user_id=user_id)
        
        prem.expiry_time = user_data.get("expiry_time")
        prem.has_free_trial = user_data.get("has_free_trial", False)
        await prem.save()
        
        if Config.UPLOAD_LIMIT_MODE and limit and type:
            user = await User.get(user_id)
            if user:
                user.usertype = type
                user.uploadlimit = limit
                await user.save()
    
    addpremium = add_premium
    
    async def remove_premium(self, user_id: int, limit=Config.FREE_UPLOAD_LIMIT, type="Free"):
        prem = await PremiumUser.find_one(PremiumUser.user_id == user_id)
        if prem:
            prem.expiry_time = None
            prem.has_free_trial = False
            await prem.save()
        
        if Config.UPLOAD_LIMIT_MODE and limit and type:
            user = await User.get(user_id)
            if user:
                user.usertype = type
                user.uploadlimit = limit
                await user.save()
          
    async def checking_remaining_time(self, user_id: int):
        prem = await PremiumUser.find_one(PremiumUser.user_id == user_id)
        if prem and prem.expiry_time:
            time_left_str = prem.expiry_time - datetime.datetime.now()
            return time_left_str
        return datetime.timedelta(0)

    async def has_premium_access(self, user_id: int):
        prem = await PremiumUser.find_one(PremiumUser.user_id == user_id)
        if prem:
            if prem.expiry_time is None:
                return False
            elif isinstance(prem.expiry_time, datetime.datetime) and datetime.datetime.now() <= prem.expiry_time:
                return True
            else:
                await self.remove_premium(user_id)
        return False

    async def total_premium_users_count(self):
        return await PremiumUser.find(PremiumUser.expiry_time > datetime.datetime.now()).count()

    async def get_all_premium_users(self):
        users = await PremiumUser.find(PremiumUser.expiry_time > datetime.datetime.now()).to_list()
        return [u.model_dump(by_alias=True) for u in users]

    async def get_free_trial_status(self, user_id: int):
        prem = await PremiumUser.find_one(PremiumUser.user_id == user_id)
        return prem.has_free_trial if prem else False

    async def give_free_trial(self, user_id: int):
        seconds = 720 * 60
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        user_data = {
            "id": user_id, 
            "expiry_time": expiry_time, 
            "has_free_trial": True
        }
        
        if Config.UPLOAD_LIMIT_MODE:
            limit_type = "Trial"
            upload_limit = 536870912000
            await self.add_premium(user_id, user_data, upload_limit, limit_type)
        else:
            await self.add_premium(user_id, user_data)
                    
    async def remove_ban(self, id: int):
        user = await User.get(id)
        if user:
            user.ban_status = BanStatus()
            await user.save()

    async def ban_user(self, user_id: int, ban_duration: int, ban_reason: str):
        user = await User.get(user_id)
        if user:
            user.ban_status = BanStatus(
                is_banned=True,
                ban_duration=ban_duration,
                banned_on=datetime.date.today().isoformat(),
                ban_reason=ban_reason
            )
            await user.save()

    async def get_ban_status(self, id: int):
        user = await User.get(id)
        return user.ban_status.model_dump() if user else BanStatus().model_dump()

    async def get_all_banned_users(self):
        users = await User.find(User.ban_status.is_banned == True).to_list()
        return [u.model_dump(by_alias=True) for u in users]

    # --- NETWORK STATS ---
    async def update_network_stats(self, sent_delta: int, recv_delta: int):
        stats = await BotStats.get("network_stats")
        if not stats:
            stats = BotStats()
        stats.sent += sent_delta
        stats.recv += recv_delta
        await stats.save()

    async def get_network_stats(self):
        stats = await BotStats.get("network_stats")
        return {"sent": stats.sent, "recv": stats.recv} if stats else {"sent": 0, "recv": 0}

    # --- PERSISTENT QUEUE (TASK) FUNCTIONS ---
    async def add_task(self, user_id: int, file_msg_id: int, new_name: str, upload_type: str):
        task = Task(user_id=user_id, file_msg_id=file_msg_id, new_name=new_name, upload_type=upload_type)
        await task.insert()
        return task.id

    async def update_task_status(self, task_id, status: str):
        task = await Task.get(task_id)
        if task:
            task.status = status
            await task.save()

    async def delete_task(self, task_id):
        task = await Task.get(task_id)
        if task: await task.delete()

digital_botz = Database(Config.DB_URL, Config.DB_NAME)
