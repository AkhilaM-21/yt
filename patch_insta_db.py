with open("backend/services/instagram_service.py", "r") as f:
    content = f.read()

# Currently server.py uses `client = AsyncIOMotorClient(...)` and `db = client[db_name]`
# So db is a motor.motor_asyncio.AsyncIOMotorDatabase
# We can use db["profiles"].find() instead of aggregate which is fine for simple queries, but let's fix the aggregate call

content = content.replace("cursor = col.aggregate(pipeline)", "cursor = col.aggregate(pipeline)")

with open("backend/services/instagram_service.py", "w") as f:
    f.write(content)
