import os
import json
import random

import discord
from discord.ext import commands
from discord.utils import get

from my_functions import *

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
bot = commands.Bot(command_prefix="!")

# setting.jsoの読み込み
with open("./setting.json") as f:
    tag_data = json.load(f)
team_tags=[
        tag_data["a_tag"]+tag_data["end_mark"],
        tag_data["b_tag"]+tag_data["end_mark"]
]

# bot起動完了時に実行される処理
@bot.event
async def on_ready():
    print('準備完了')

@bot.event
async def on_guild_join(guild):
    print("サーバーに参加")

    embed = discord.Embed(title="簡単な説明", colour=discord.Colour(0xf5a623), description="このBotはボイスチャンネルにいるユーザーをA, Bの2チームに分けます\n※サーバー主は権限の問題で変えることができません...申し訳ありません🙏\n(鯖主はチャットでお知らせします)")

    embed.set_footer(text="Copyright © 登生(Github:toy101, twitter:@toy101_mov)", icon_url="https://avatars.githubusercontent.com/u/45931528?v=4")

    embed.add_field(name="使い方：```!ab```", value="名前の前にチームタグをつけます", inline=True)
    embed.add_field(name="使い方：```!reset```", value="チームタグを外します", inline=True)
    embed.add_field(name="ご注意✅", value="・途中でニックネームを変えると予期せぬ挙動をします\n・Heroku上で動かしてますのでレスポンスが遅い時があります。", inline=False)
    embed.add_field(name="Source Code🤖", value="https://github.com/toy101/discord-bot-ab-chan", inline=False)

    await guild.system_channel.send(content="Botを導入していただきありがとうございます！", embed=embed)

#メッセージ受信時に実行される処理
@bot.event
async def on_message(message):
    #on_messageイベントの取得とコマンド機能を併用する際に必要な処理
    await bot.process_commands(message)

@bot.command()
async def ab(ctx):
    # コマンド送信主の入ってるチャンネルを取得
    try:
        channel= ctx.author.voice.channel
    except:
        await ctx.send("コマンドの実行者はボイスチャンネルに入室してください")
        return

    # そのチャンネルに参加しているユーザーを取得
    member_ids = channel.voice_states.keys()
    users = await ctx.message.guild.query_members(user_ids=[ int(m) for m in member_ids])
    
    random.shuffle(users)

    for i, user in enumerate(users):

        if user.bot:
            continue
        
        current_display_name = user.display_name

        # (2回目以降) 今のdisplay_nameからチームタグを取り除く
        orig_display_name = get_clean_display_name(
                                current_display_name, 
                                team_tags
                            )
        try:
            await user.edit(nick=team_tags[i%2]+orig_display_name)
        except:
            await ctx.send(f"{orig_display_name}さんは{team_tags[i%2]}です！（サーバー主は権限の問題で変更できません...）")
    # await ctx.send("hello")

# タグを外す
@bot.command()
async def reset(ctx):

    try:
        channel= ctx.author.voice.channel
    except:
        await ctx.send("コマンドの実行者はボイスチャンネルに入室してください")
        return

    member_ids = channel.voice_states.keys()
    users = await ctx.message.guild.query_members(user_ids=[ int(m) for m in member_ids])
    for user in users:
        
        current_display_name = user.display_name

        # (2回目以降) 今のdisplay_nameからチームタグを取り除く
        orig_display_name = get_clean_display_name(
                                current_display_name, 
                                team_tags
                            )

        try:
            await user.edit(nick=orig_display_name)
        except:
            pass

bot.run(TOKEN)