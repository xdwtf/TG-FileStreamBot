import pymongo

class Database:
    def __init__(self, uri, database_name):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[database_name]
        self.users = self.db["users"]
        self.banned_users = self.db["banned_users"]
        self.allowed_users = self.db["allowed_users"]

    async def insert_user(self, user_id):
        if not self.users.find_one({"_id": user_id}):
            self.users.insert_one({"_id": user_id, "file_count": 0})

    async def delete_user(self, user_id):
        self.users.delete_one({"_id": user_id})

    async def get_all_users(self):
        allusers = list(self.users.find())
        return allusers

    async def total_users_count(self):
        count = self.users.count_documents({})
        return count

    async def total_files_count(self):
        total_files = sum(user["file_count"] for user in self.users.find())
        return total_files
    
    async def increment_file_count(self, user_id):
        self.users.update_one({"_id": user_id}, {"$inc": {"file_count": 1}})

    async def ban_user(self, user_id):
        self.banned_users.insert_one({"_id": user_id})

    async def unban_user(self, user_id):
        self.banned_users.delete_one({"_id": user_id})

    async def is_user_banned(self, user_id):
        return bool(self.banned_users.find_one({"_id": user_id}))
    
    async def total_banned_users_count(self):
        count = self.banned_users.count_documents({})
        return count
    
    async def add_allowed_user(self, user_id):
        self.allowed_users.insert_one({"_id": user_id})

    async def remove_allowed_user(self, user_id):
        self.allowed_users.delete_one({"_id": user_id})

    async def get_allowed_users(self):
        allowed_users = self.allowed_users.find()
        return [str(user["_id"]) for user in allowed_users]
    
    async def is_user_allowed(self, user_id):
        return bool(self.allowed_users.find_one({"_id": user_id}))
    
    async def total_allowed_user_count(self):
        count = self.allowed_users.count_documents({})
        return count