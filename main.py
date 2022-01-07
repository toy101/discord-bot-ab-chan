import os
import json
import random

import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from discord.errors import Forbidden

from mod.utiles import get_clean_display_name, get_relative_complement_list
from mod.msg_buffer import MessageBuffer

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
bot = commands.Bot(command_prefix="!")

# setting.jsoの読み込み
with open("./setting.json") as f:
    tag_data = json.load(f)
team_tags = [
    tag_data["a_tag"]+tag_data["end_mark"],
    tag_data["b_tag"]+tag_data["end_mark"]
]

react_emoji = "👀"

# bot起動完了時に実行される処理


@bot.event
async def on_ready():
    print('準備完了')


@bot.event
async def on_guild_join(guild):
    print("サーバーに参加")

    embed = discord.Embed(title="簡単な説明", colour=discord.Colour(
        0xf5a623), description="このBotはボイスチャンネルにいるユーザーをA, Bの2チームに分けます\n※サーバー主は権限の問題で変えることができません...申し訳ありません🙏\n(鯖主はチャットでお知らせします)")

    embed.set_footer(text="Copyright © 登生(Github:toy101, twitter:@toy101_mov)",
                     icon_url="https://avatars.githubusercontent.com/u/45931528?v=4")

    embed.add_field(name="使い方：```!ab```", value="名前の前にチームタグをつけます", inline=True)
    embed.add_field(name="使い方：```!reset```", value="チームタグを外します", inline=True)
    embed.add_field(
        name="ご注意✅", value="・途中でニックネームを変えると予期せぬ挙動をします\n・Heroku上で動かしてますのでレスポンスが遅い時があります。", inline=False)
    embed.add_field(name="Source Code🤖",
                    value="https://github.com/toy101/discord-bot-ab-chan",
                    inline=False)

    await guild.system_channel.send(content="Botを導入していただきありがとうございます！",
                                    embed=embed
                                    )

# メッセージ受信時に実行される処理


@bot.event
async def on_message(message):
    # on_messageイベントの取得とコマンド機能を併用する際に必要な処理
    await bot.process_commands(message)


@bot.command()
async def ab(ctx):

    # コマンド送信主の入ってるチャンネルを取得
    try:
        v_channel = ctx.author.voice.channel
    except CommandInvokeError:
        await ctx.send("コマンドの実行者はボイスチャンネルに入室してください")
        return

    m_buffer = MessageBuffer()

    bot_id = ctx.me.id
    t_channel = ctx.channel
    msg = await t_channel.history().get(author__id=bot_id)

    not_taken_users = None
    for react in msg.reactions:
        if react.emoji != react_emoji:
            continue
        not_taken_users = [user async for user in react.users() if not user.bot]

    # そのチャンネルに参加しているユーザーを取得
    member_ids = v_channel.voice_states.keys()
    users = await ctx.message.guild.query_members(user_ids=[int(m) for m in member_ids])

    if not_taken_users:
        users = get_relative_complement_list(users, not_taken_users)

    if len(users) == 0:
        m_buffer.append("対象となるユーザーがいません。（全員が不参加のリアクションをしているなど）")
    elif len(users) == 1:

        current_display_name = users[0].display_name
        orig_display_name = get_clean_display_name(
            current_display_name,
            team_tags
        )

        tag = random.choice(team_tags)

        try:
            await users[0].edit(nick=tag+orig_display_name)
            m_buffer.append(
                f"{orig_display_name}さんは{random.choice(team_tags)}です！")
        except Forbidden:
            m_buffer.append(
                f"{orig_display_name}さんは{tag}です！（サーバー主は権限の問題で変更できません...）")
    else:
        random.shuffle(users)

        m_buffer.append(f"{len(users)}人を2チームに分けました")

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
                await user.edit(nick=team_tags[i % 2]+orig_display_name)
            except Forbidden:
                m_buffer.append(
                    f"{orig_display_name}さんは{team_tags[i%2]}です！（サーバー主は権限の問題で変更できません...）")

    # m_buffer.append(f"このメッセージに「{react_emoji}」でリアクションすると次のチーム分けは不参加にできます.")
    embed = discord.Embed(colour=discord.Colour(
        0xf5a623), description=f"「{react_emoji}」でリアクションすると次のチーム分けは不参加にできます")

    new_msg = await ctx.send(content=str(m_buffer), embed=embed)
    await new_msg.add_reaction(react_emoji)


# タグを外す
@bot.command()
async def reset(ctx):

    try:
        v_channel = ctx.author.voice.channel
    except CommandInvokeError:
        await ctx.send("コマンドの実行者はボイスチャンネルに入室してください")
        return

    member_ids = v_channel.voice_states.keys()
    users = await ctx.message.guild.query_members(user_ids=[int(m) for m in member_ids])
    for user in users:

        current_display_name = user.display_name

        # (2回目以降) 今のdisplay_nameからチームタグを取り除く
        orig_display_name = get_clean_display_name(
            current_display_name,
            team_tags
        )

        try:
            await user.edit(nick=orig_display_name)
        except Forbidden:
            pass

    await ctx.send("チームタグを外しました！")

bot.run(TOKEN)
