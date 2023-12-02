import os
import discord
from discord.ext import commands
import dotenv
import aiohttp
import requests
import random
from data import db_session
from data.games import Game
import base64
from io import BytesIO
from PIL import Image
from imagegenerate import ImageApi
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

KANDINSKY_API_KEY = os.getenv("KANDINSKY_API_KEY")
KANDINSKY_SECRET_KEY = os.getenv("KANDINSKY_SECRET_KEY")
TOKEN_BOT = os.getenv("TOKEN_BOT")
TOKEN_API = os.getenv("TOKEN_API")

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
chat = GigaChat(credentials=TOKEN_API, verify_ssl_certs=False)

messages = [
    SystemMessage(
        content="Ты ведущий игры Dungeon and Dragons, твоя задача выдавать роли и придумывать игровую историю для "
                "участников игры."
    )
]
base_message = messages


@bot.event
async def master():
    print('Бот запущен')


@bot.event
async def on_member_join(member):
    await member.send('Привет, я бот для игры в Dungeon and Dragons, я помогу тебе погрузиться в мир фентези ')

    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == '🤜welcome🤛':
            await bot.get_channel(ch.id).send(f'{member}, Рад поприветствовать вас в нашем сказочном мире!')


@bot.command()
async def master(ctx: commands.Context, *, prompt: str):
    global messages, chat
    messages.append(HumanMessage(content=prompt))
    res = chat(messages)
    messages.append(res)
    await ctx.send(res.content)


@bot.command()
async def info(ctx):
    await ctx.send("""Для удобного пользования ботом вам доступен список команд:\n
    !master (prompt) - для запроса к боту и получения ответа\n
    !new_story - для создания новой истории и дальнейшего взаимодействия с расказчиком""")


@bot.command()
async def new_story(ctx):
    global messages, base_message
    messages = base_message
    db_sess = db_session.create_session()
    game = Game()
    id = random.randint(1, 1000)
    while db_sess.query(Game).filter(Game.id == id).first():
        id = random.randint(1, 1000)
    game.make_new(id)
    db_sess.commit()
    channelname = f"Game №{game.id}"
    mbed = discord.Embed(title="Канал для вашей игры успешно создан", description=f"Желаем удачной игры, переходите в канал {channelname}")
    category = discord.utils.get(ctx.message.guild.categories, id = 1180585027046735872)
    await category.create_text_channel(f"{channelname}")
    await ctx.send(embed = mbed)


@bot.command()
async def image_generate(ctx: commands.Context, *, prompt: str):
    api = ImageApi(KANDINSKY_API_KEY, KANDINSKY_SECRET_KEY)
    model_id = api.get_model()
    uuid = api.generate(prompt, model_id)
    images = api.check_generation(uuid)
    decoded_bytes = base64.b64decode(images[0])
    im = Image.open(BytesIO(decoded_bytes))
    im.save('decoded_image.jpg')
    with open('decoded_image.jpg', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)


if __name__ == "__main__":
    db_session.global_init("main")
    bot.run(TOKEN_BOT)