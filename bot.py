from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import *
from db import users, movies, likes, requests, downloads
from utils import is_joined, force_join, get_movie_details

app = Client("Alex", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# START
@app.on_message(filters.command("start"))
async def start(client, message):
    users.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"name": message.from_user.first_name}},
        upsert=True
    )
    await message.reply_text("🎬 Send movie name...")

# REQUEST
@app.on_message(filters.command("request"))
async def request_movie(client, message):
    name = message.text.replace("/request", "").strip()

    if not name:
        return await message.reply_text("Use: /request movie name")

    requests.insert_one({"user_id": message.from_user.id, "movie": name})
    await message.reply_text("✅ Request saved!")

# SEARCH + NETFLIX UI
@app.on_message(filters.text & ~filters.command(["start","request"]))
async def search(client, message):

    user_id = message.from_user.id

    if message.chat.type == "private":
        if not await is_joined(client, user_id):
            return await force_join(message)

    query = message.text.lower()

    movie = movies.find_one({
        "caption": {"$regex": query, "$options": "i"}
    })

    if not movie:
        return await message.reply_text("❌ Movie not found")

    info = get_movie_details(query)

    caption = f"🎬 {movie.get('caption','Movie')}"
    poster = None

    if info:
        caption = f"""
━━━━━━━━━━━━━━━
🎬 {info['title']} ({info['year']})
⭐ {info['rating']}
🎭 {info['genre']}
━━━━━━━━━━━━━━━
"""
        poster = info["poster"]

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶ Watch", callback_data=f"dl_{movie['file_id']}")],
        [
            InlineKeyboardButton("❤️ Like", callback_data=f"like_{movie['file_id']}"),
            InlineKeyboardButton("📥 Download", callback_data=f"dl_{movie['file_id']}")
        ]
    ])

    if poster and poster != "N/A":
        await message.reply_photo(photo=poster, caption=caption, reply_markup=buttons)

    await message.reply_video(movie["file_id"], caption="🎬 Playing...")

# LIKE
@app.on_callback_query(filters.regex("like_"))
async def like(client, query):
    fid = query.data.split("_")[1]

    if not likes.find_one({"user_id": query.from_user.id, "file_id": fid}):
        likes.insert_one({"user_id": query.from_user.id, "file_id": fid})
        await query.answer("❤️ Liked")
    else:
        await query.answer("Already liked")

# DOWNLOAD COUNT
@app.on_callback_query(filters.regex("dl_"))
async def download(client, query):
    fid = query.data.split("_")[1]

    downloads.update_one(
        {"file_id": fid},
        {"$inc": {"count": 1}},
        upsert=True
    )

    await query.answer("📥 Counted")

# SAVE MOVIE + AUTO NOTIFY
@app.on_message(filters.chat(CHANNEL_ID))
async def save(client, message):
    if message.video or message.document:

        caption = message.caption or "Movie"

        movies.insert_one({
            "file_id": message.video.file_id if message.video else message.document.file_id,
            "caption": caption
        })

        # notify
        for r in requests.find():
            if r["movie"].lower() in caption.lower():
                try:
                    await client.send_message(r["user_id"], f"🎬 Your movie uploaded!\n{caption}")
                except:
                    pass

# RUN
app.run()
