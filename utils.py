import requests
from config import CHANNEL_USERNAME, OMDB_API
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def is_joined(client, user_id):
    try:
        member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def force_join(message):
    await message.reply_text(
        "🚫 Join channel first!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{SHADOW_Movie23}")]
        ])
    )

def get_movie_details(name):
    url = f"http://www.omdbapi.com/?t={name}&apikey={OMDB_API}"
    res = requests.get(url).json()

    if res.get("Response") == "True":
        return {
            "title": res["Title"],
            "year": res["Year"],
            "rating": res["imdbRating"],
            "genre": res["Genre"],
            "poster": res["Poster"]
        }
    return None
