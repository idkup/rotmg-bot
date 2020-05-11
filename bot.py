# IMPORTS
import asyncio
from discord import Embed
from discord.ext import commands
import pickle
from random import randint
from realmeye_api import *
from resources import AFKCheck, DUNGEONS, Raider

# CONSTANTS
bot = commands.Bot('!')
with open("key.txt", "r") as k:
    KEY = k.readline()
    k.close()
VERIFICATION_CHANNEL = 708455069686825060
VERIFIED_ROLE = 708454765113114834
AFK_CHECK_CHANNEL = 708455325136715818
BOT_SPAM_CHANNEL = 708456601551634453
LOG_CHANNEL = 708463968838221926
RAIDING_CHANNELS = [708455974402261022, 708456022091628598]
AFK_VOICE_CHANNEL = 708462706557976588
ADMIN_ROLE = 708454460439003206
RL_ROLE = 708454738441666561
AFK_TITLE = "AFK Check for {} started by {} in Raiding-{}!"
AFK_DESC = "React with {} to join, {} if you have a key, and {} to indicate your choice of class or gear!"

# FIELDS
afk_checks = []
awaiting_verification = []
try:
    with open('raiders.txt', 'rb') as raiders:
        verified_raiders = pickle.load(raiders)
        raiders.close()
except FileNotFoundError:
    verified_raiders = []


# COMMANDS


@bot.command()
async def headcount(ctx, dungeon):
    if ctx.guild.get_role(RL_ROLE) not in ctx.author.roles:
        return await ctx.author.send("You are not a Raid Leader!")
    if dungeon.title() not in DUNGEONS.keys():
        return await ctx.author.send("Dungeon not recognized.")
    message = await bot.get_channel(AFK_CHECK_CHANNEL).send("@here Headcount started by {} for {}! \
React if you can make it!".format(ctx.author.mention, DUNGEONS[dungeon.title()]["embed"][0]))
    await message.add_reaction(bot.get_emoji(DUNGEONS[dungeon.title()]["reacts"][0]))
    await message.add_reaction(bot.get_emoji(DUNGEONS[dungeon.title()]["reacts"][1]))


@bot.command()
async def start_afk(ctx, chl=None, dungeon=None, location=None):
    await ctx.message.delete()
    if not chl or not dungeon or not location:
        return await ctx.author.send("The correct syntax for this command is \
!start_afk <channel> <dungeon> <location>. Ex: !start_afk 1 Shatters \"USS L\"")
    chl = int(chl)
    dungeon = dungeon.title()
    if ctx.guild.get_role(RL_ROLE) not in ctx.author.roles:
        return await ctx.author.send("You are not a Raid Leader!")
    if dungeon not in DUNGEONS.keys():
        return await ctx.author.send("Dungeon not recognized.")
    if chl > len(RAIDING_CHANNELS):
        return await ctx.send("we don't have that many raiding channels...")
    for a in afk_checks:
        if a.leader == ctx.author.id:
            return await ctx.author.send("cant lead two runs at once idiot")
        if a.channel == RAIDING_CHANNELS[chl - 1]:
            return await ctx.author.send("cant have two runs in the same channel")
    e = Embed(title=AFK_TITLE.format(DUNGEONS[dungeon]["embed"][0], ctx.author.name, chl),
              description=AFK_DESC.format(bot.get_emoji(DUNGEONS[dungeon]["embed"][1]),
                                          bot.get_emoji(DUNGEONS[dungeon]["embed"][2]),
                                          "".join([str(bot.get_emoji(x)) for x in DUNGEONS[dungeon]["embed"][3]])))
    msg = await bot.get_channel(AFK_CHECK_CHANNEL).send("@here AFK Check for {} started in <#{}> by {}!".format(
        DUNGEONS[dungeon]["embed"][0], RAIDING_CHANNELS[chl - 1], ctx.author.mention), embed=e)
    for e in DUNGEONS[dungeon]["reacts"]:
        await msg.add_reaction(bot.get_emoji(e))
    await msg.add_reaction("❌")
    afk_checks.append(AFKCheck(RAIDING_CHANNELS[chl - 1], msg.id, ctx.author.id, dungeon, location))


@bot.command()
async def end_run(ctx, success=1):
    success = int(success)
    for a in afk_checks:
        if a.leader == ctx.author.id:
            channel = bot.get_channel(AFK_CHECK_CHANNEL)
            msg = await channel.fetch_message(a.message_id)
            if success > 0 and a.status == 1:
                a.status = 2
                e_str = "Run completed!"
                for p in a.raiders:
                    for v in verified_raiders:
                        if v.discord_id == p.id:
                            v.runs_completed += success
                            if v.discord_id == a.leader:
                                v.is_rl = True
                                v.runs_led += success
                            if v.discord_id == a.key:
                                v.keys_opened += 1
                            break
            else:
                a.status = -1
                e_str = "Run aborted."
            await msg.edit(embed=Embed(title=msg.embeds[0].title, description=e_str))
            with open('raiders.txt', 'wb+') as f:
                pickle.dump(verified_raiders, f)
            await ctx.message.delete()
            return afk_checks.remove(a)
    else:
        await ctx.message.delete()
        return await ctx.author.send("you dont have an afk check up")


@bot.command()
async def pop(ctx):
    for u in ctx.message.mentions:
        for v in verified_raiders:
            if u.id == v.discord_id:
                v.keys_opened += 1


@bot.command()
async def member_count(ctx):
    await ctx.author.send("There are {} verified raiders in the server!".format(len(verified_raiders)))


@bot.command()
async def purge(ctx, ct=10):
    if ctx.author.guild_permissions.manage_messages:
        try:
            count = int(ct) + 1
        except ValueError:
            return
        async for msg in ctx.channel.history(limit=count):
            if not msg.pinned:
                if ctx.message.mentions:
                    if msg.author in ctx.message.mentions:
                        await msg.delete()
                else:
                    await msg.delete()


@bot.command()
async def stats(ctx):
    if ctx.channel.id != BOT_SPAM_CHANNEL:
        return
    for p in verified_raiders:
        if p.discord_id == ctx.author.id:
            await ctx.author.send("""Stats for {} in Event Dungeons:
Runs completed: {}
Keys opened: {}
Runs led: {}""".format(p.ign, p.runs_completed, p.keys_opened, p.runs_led))


@bot.command()
async def verify(ctx, uid, ign):
    if ctx.guild.get_role(ADMIN_ROLE) not in ctx.author.roles:
        return
    verified_raiders.append(Raider(int(uid), ign))
    with open('raiders.txt', 'wb+') as f:
        pickle.dump(verified_raiders, f)
        f.close()
    await ctx.guild.get_member(int(uid)).add_roles(ctx.guild.get_role(VERIFIED_ROLE))
    await ctx.send("{} has been verified!".format(ign))


@bot.event
async def on_message_delete(message):
    await bot.get_channel(LOG_CHANNEL).send(
        "Deleted message in #{}, sent by {}: ```{}```".format(message.channel, message.author, message.content))


@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    if payload.user_id == bot.user.id:
        return
    try:
        user = guild.get_member(payload.user_id)
    except AttributeError:
        user = None
    if payload.channel_id == VERIFICATION_CHANNEL:
        # VERIFICATION
        role = guild.get_role(VERIFIED_ROLE)
        if role in user.roles:
            return await user.send("You already have the Verified role.")
        for e in awaiting_verification:
            if payload.user_id == e[0]:
                name = user.nick if user.nick is not None else user.name
                player = get_player(name)
                print(e[2])
                print(get_desc(player))
                if e[2] in get_desc(player):
                    await user.add_roles(role)
                    verified_raiders.append(Raider(e[0], name))
                    awaiting_verification.remove(e)
                    with open('raiders.txt', 'wb+') as f:
                        pickle.dump(verified_raiders, f)
                        f.close()
                    return await user.send("You are now verified.")
                else:
                    return await user.send("Please put the verification key ({}) in your profile. \
(It may take up to a minute for your profile to update.)".format(e[2]))
        else:
            key = "ASDF" + str(randint(1, 10000))
            try:
                name = user.nick if user.nick is not None else user.name
                for raider in verified_raiders:
                    if raider.ign.lower() == name.lower():
                        if raider.discord_id == user.id:
                            await user.add_roles(role)
                            return await user.send("You've been verified again. Wonder what happened?")
                        return await user.send("This account already has a verified Discord associated with it!")
                get_player(name)
            except RuntimeError:
                return await user.send("Could not find your Realmeye. \
Please make sure your IGN matches your Discord name and that your Realmeye is not private.")

            await user.send('Please put this verification key in your Realmeye profile then re-react to the message \
in #verify-test: {}'.format(key))
            awaiting_verification.append([user.id, name, key])
    elif payload.channel_id == AFK_CHECK_CHANNEL:
        # AFK CHECK BEHAVIOR
        for afk in afk_checks:
            if payload.message_id == afk.message_id:
                curr_afk = afk
                break
        else:
            return
        if str(payload.emoji) == "❌":
            # LEADER ENDING AFK
            if curr_afk.leader != payload.user_id:
                return
            channel = bot.get_channel(AFK_CHECK_CHANNEL)
            msg = await channel.fetch_message(curr_afk.message_id)
            await msg.edit(embed=Embed(title=msg.embeds[0].title,
                                       description="We are currently running with {} raiders.".format(
                                           len(afk.raiders))))
            curr_afk.status = 1
            reacted = await msg.reactions[0].users().flatten()
            for user in bot.get_channel(curr_afk.channel).members:
                if user not in reacted:
                    await user.move_to(bot.get_channel(AFK_VOICE_CHANNEL))
            for user in reacted:
                if user.voice is None:
                    continue
                await user.move_to(bot.get_channel(curr_afk.channel))
                curr_afk.raiders.append(user)
            for r in msg.reactions:
                await r.clear()
        if payload.emoji == bot.get_emoji(DUNGEONS[curr_afk.dungeon]["reacts"][0]):
            # RAIDER REACTING TO AFK
            if user.voice is not None:
                await user.move_to(bot.get_channel(curr_afk.channel))
        if payload.emoji == bot.get_emoji(DUNGEONS[curr_afk.dungeon]["reacts"][1]) and curr_afk.key is None:
            # KEY REACT
            confirm = await user.send("Do you confirm that you are willing to open a {} key?".format(curr_afk.dungeon))
            curr_afk.key_reacts.append(confirm.id)
            await confirm.add_reaction("\U0001f1fe")
    else:
        for afk in afk_checks:
            if payload.message_id in afk.key_reacts:
                if afk.key is not None:
                    return
                await bot.get_channel(payload.channel_id).send("You have been confirmed as the key!")
                await bot.get_channel(payload.channel_id).send("The location is {}.".format(afk.location))
                afk.key = payload.user_id
                await bot.get_user(afk.leader).send("<@{}> has agreed to open a key.".format(afk.key))
                break


@bot.event
async def on_ready():
    print("hello world")
    print([str(x) for x in verified_raiders])


bot.run(KEY)
