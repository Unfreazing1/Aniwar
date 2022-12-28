import re

import requests

import discord

from discord import Embed

from discord.ext import commands

from discord.ext import tasks

import asyncio

import random

import pymongo

#shard1 :-   ac-yilvpcz-shard-00-01.duq2zgt.mongodb.net:27017

#shard2 :-  ac-yilvpcz-shard-00-02.duq2zgt.mongodb.net:27017

#shard3 :-  ac-yilvpcz-shard-00-00.duq2zgt.mongodb.net:27017

#

intents = discord.Intents.all()

intents.messages = True

intents.dm_messages = True

intents.guild_messages = True

client = commands.Bot(command_prefix=['.'], case_insensitive=True, help_command=None, intents=intents)

cluster = pymongo.MongoClient('database add krke aage ka kaam krna')

db = cluster["aniwar"]

playerdb = db["playerdb"]

guilddb =  db["guilddb"]

tempguilddb =  db["tempguilddb"]

base = db["base"]

activespawns = db["activespawns"]

allcards = db["allcards"]

card_rarity = [0, 'Common', 'Uncommon', 'Super Rare', 'Ultra Rare']

@client.event

async def on_ready():

    print('ready')

#ping command

@client.command()

async def ping(ctx):

    await ctx.send(f'Pong! {round(client.latency*100)}ms')

@client.command()

async def start(ctx, *, nickname = ''):

    name = str(ctx.author)

    name = name[:-5]

    nickname = nickname.strip(' ')

    if playerdb.count_documents({'_id':ctx.author.id}) == 0:

        user = str(ctx.author)[:-5]

        check = allcards.insert_one({'id': allcards.count_documents({'hell': None}) + 1, 'char': random.randint(1,17), 'rarity': 3, 'owner': ctx.author.id})

        data = {'_id': ctx.author.id, 'balance': 1000, 'selected':1, 'level':0, 'dungeon': 1, 'subdungeon': 1,

                'nick': nickname, 'guild': '', }

        ok = playerdb.insert_one(data)

        embed = Embed(title=f'Welcome {name}',

                      description=f"""**Hello {name}\n\n Welcome to the world of Aniwar!!**\nA random Gold Edition Character has been added to your inventory. Please check using `.info`""",

                      colour=0xff0086)

    else:

        embed = Embed(title=f'Welcome {name}',

                      description=f"""Human you can't start twice, BAKA!!!""",

                      colour=0xff0086)

    await ctx.send(embed=embed)

@client.command(aliases=['bal'])

async def balance(ctx):

    bal = playerdb.find_one({"_id": ctx.author.id})

    embed = Embed(title=f"{str(ctx.author)[:-5]}'s Bal:",

                  description=f"""{bal['balance']}  Gold""",

                  colour=0xff0086)

    await ctx.send(embed=embed)

@client.command(aliases=['gc'])

async def guildcreate(ctx, *, name = 'hkhdfklhldflj'):

    bal = playerdb.find_one({"_id": ctx.author.id})

    if bal['guild'] != "":

        await ctx.send('You are already in a Guild')

    elif bal['balance'] < 100000:

        await ctx.send("You dont have enough gold to establish a guild.")

    elif name == 'hkhdfklhldflj' or name.strip(' ') == '':

        await ctx.send("Please mention proper guild name.")

    else:

        guildid = guilddb.count_documents({'hell': None})

        ok = guilddb.insert_one({'_id': guildid, 'owner': ctx.author.id, 'members': 1, 'level': 1, 'name': name})

        ok = playerdb.update_one({"_id": ctx.author.id}, {'$set': {'guild': guildid}})

        embed = Embed(title=f"{str(ctx.author)[:-5]}",

                      description=f"""Created {name}""",

                      colour=0xff0086)

        await ctx.send(embed=embed)

@client.command(aliases=['gj'])

async def guildjoin(ctx, *, name = 'hkhdfklhldflj'):

    bal = playerdb.find_one({"_id": ctx.author.id})

    owner = int(re.findall(name)[0])

    guilds = guilddb.find_one({'owner': owner})

    if bal['guild'] != "":

        await ctx.send('You are already in a Guild')

    elif guilds is None:

        await ctx.send(f"<@{owner}> is not owner of any guild")

    else:

        await ctx.send(f"<@{owner}> please accept or deny <@{ctx.author.id} reuest. \n`.accept` `.deny'>")

        ok = tempguilddb.insert_one({'_id': ctx.author.id, 'owner': owner})

        embed = Embed(title=f"{str(ctx.author)[:-5]}",

                      description=f"""Joined {name}""",

                      colour=0xff0086)

        await ctx.send(embed=embed)

@ client.command(aliases=['ga'])

async def guildaccept(ctx, *, nickname):

    master = guilddb.find_one({'owner': ctx.author.id})

    req = tempguilddb.find_one({'owner': ctx.author.id})

    if req is not None:

        ok = guilddb.update_one({'owner':ctx.author.id}, {'$inc': {'member': 1}})

        ok = tempguilddb.delete_one({'owner': ctx.author.id})

        ok = playerdb.update_one({'_id': req['_id']}, {'set': {'guild': master['_id']}})

        await ctx.send(f'Guild Join Successfull')

@client.command(aliases=['gl'])

async def guildleave(ctx):

    bal = playerdb.find_one({"_id": ctx.author.id})

    if bal['guild'] == "":

        await ctx.send('You are not in any Guild')

    else:

        check = guilddb.find_one({'owner': ctx.author.id})

        if check is not None:

            await ctx.send('You can not leave guild as you are guild owner.')

        else:

            embed = Embed(title=f"{str(ctx.author)[:-5]}",

                          description=f"""Left Guild""",

                          colour=0xff0086)

            ok = playerdb.update_one({"_id": ctx.author.id}, {'$set': {'guild':""}})

            ok = guilddb.update_one({'_id': check['_id']}, {'inc' : {'member': -1}})

            await ctx.send(embed=embed)

@client.command()

async def setnick(ctx, *, nickname):

    bal = playerdb.update_one({"_id": ctx.author.id}, {'$set': {'nick': nickname.strip(' ')}})

    await ctx.send(f'Updated Nickname to {nickname}')

@client.command()

async def claim(ctx):

    check = activespawns.find_one({'_id': ctx.channel.id})

    if check is not None:

        check2 = playerdb.find_one({'_id': ctx.author.id})

        if check2 is not None:

            id = allcards.count_documents({'hell': None})

            ok = base.find_one({'charid': check['sp']})

            check3 = allcards.insert_one({'owner': ctx.author.id, 'id': id, 'char': check['sp'], 'rarity': check['rp']})

            if check3 is not None:

                await ctx.send(f'Claimed {ok["name"]} {card_rarity[check["rp"]]}')

                check = activespawns.delete_one({'_id': ctx.channel.id})

        else:

            await ctx.send("You haven't started yet")

@client.command(aliases=['pf'])

async def profile(ctx, *, name = 'haahh'):

    if name == 'haahh' or name.strip(' ') == '':

        details = playerdb.find_one({"_id": ctx.author.id})

    else:

        name = re.findall(r'\d+', name)

        name = int(name[0])

        details = playerdb.find_one({"_id": name})

    if details is not None:

        guildname = guilddb.find_one({'_id': details['guild']})

        if guildname is None:

             g = ''

        else:

            g = guildname['name']

        embed = Embed(title=f"{str(ctx.author)[:-5]}",

                      description=f"""<@{details['_id']}>'s Profile\nNickname: **{details['nick']}**

Level: {details['level']}

Guild: {g}

Balance: {details['balance']} Gold

Floor: {details['dungeon']}-{details['subdungeon']}""",

                      colour=0xff0086)

        await ctx.send(embed=embed)

    else:

        await ctx.send('Could not find the player')

@client.command(aliases=['c'])

async def cards(ctx):

    cards = allcards.find({'owner': ctx.author.id}).limit(20)

    desc = ''

    for c in cards:

        cursor = base.find_one({'charid': c['char'], 'rarity': c['rarity']})

        desc = desc + cursor['name'].capitalize() + '   |   ' + card_rarity[c['rarity']] + '\n'

    embed = Embed(title=f'{ctx.author}',

                  description=desc,

                  colour=0xff0086)

    await ctx.channel.send(embed=embed)

#Dex Commands

@client.command()

async def info(ctx, *, name = 'Nonenone'):

    if name != 'Nonenone':

        rgx = re.compile(f'.*{name}.*', re.IGNORECASE)

        cursor = base.find_one({'name': rgx})

    else:

        ok = playerdb.find_one({'_id': ctx.author.id})

        ok2 = allcards.find_one({'id': ok['selected']})

        cursor = base.find_one({'charid': ok2['char'], 'rarity': ok2['rarity']})

    desc = f"""

Name: {cursor['name'].capitalize()}

Element: {cursor['element'].capitalize()}

Class: {cursor['class'].capitalize()}    Ability: {cursor['ability'].capitalize()}

HP:     {cursor['hp']}

ATK:     {cursor['atk']}

DEF:     {cursor['defx']}

SPD:     {cursor['spd']}

Total:     {cursor['total']}

"""

    embed = Embed(title=f'{ctx.author}',

                  description=desc,

                  colour=0xff0086)

    img = f'https://raw.githubusercontent.com/f04102005/AniWar/main/image-db/{cursor["charid"]}_1.png'

    embed.set_image(url=img)

    await ctx.channel.send(embed=embed)

@client.event

async def on_message(message):

    spawnthreshold = random.randint(1,30)

    if spawnthreshold in [1,2,3,4]:

        sp = random.randint(1,17)

        rp = random.randint(1,4052)

        if rp < 3001:

            rp = 1

        elif rp < 4001:

            rp = 2

        elif rp < 4050:

            rp = 3

        else:

            rp = 4

        channel = client.get_channel(int(message.channel.id))

        embed = Embed(title=f'Some has Summoned ginger',

                      colour=0xff0086)

        img = f'https://raw.githubusercontent.com/f04102005/AniWar/main/image-db/{sp}_{rp}.png'

        embed.set_image(url=img)

        check = activespawns.delete_one({'_id': message.channel.id})

        check = activespawns.insert_one({'_id': message.channel.id, 'sp': sp, 'rp': rp})

        await message.channel.send(embed=embed)

    await client.process_commands(message)

client.run('token')
