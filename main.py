import datetime
import json
import os
import hashlib
import paramiko

import discord
import yaml
from discord.ext import tasks

import config

# Init
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Set working directory to script location
bot = discord.Bot(intents=discord.Intents.all())
servers = [
    528346798138589215, # Vampirism.co
    430326060635258881, # Vampirism Mod
    692526341987369021 # Dev
]

#------------------------------------------------------------------------------#

# Message handler
@bot.event
async def on_message(message):

    # Custom welcome message for support tickets
    if message.author.id == 557628352828014614 and "Support will be with you shortly." in message.embeds[0].description:
        await message.edit(suppress=True)
        embed=discord.Embed(title="Welcome to your support ticket.", description="Please describe your problem or question and include your Minecraft username or any details that might be relevant, so our staff members can help you as quickly as possbible with the minimum amount of additional questions.", color=0x5865F2)
        await message.channel.send(embed=embed)

    # Form submissions
    if message.author.id == 1407060394253746317:
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        await message.create_thread(name=f"Vote: {message.embeds[0].title}", auto_archive_duration=10080)

#------------------------------------------------------------------------------#

# Ticket close
@bot.slash_command(guild_ids=servers)
async def close(ctx,
    user: discord.Option(str, "@Tag the user, then press TAB"),
    mode: discord.Option(str, "Write, click or select an option with the arrow keys, then press TAB", choices=["Regular", "Stale"])
):
    """Ask if the ticket can be closed"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    if mode == "Regular":
        embed=discord.Embed(title="If there's nothing else we can help you with, we would like to go ahead close this ticket now.", color=0x5865F2)
    else:
        embed=discord.Embed(title="If you still require help, please answer now.", description="It's been a while since you last sent a message and we will go ahead and close this ticket soon if we don't hear from you.", color=0x5865F2)
    await ctx.respond(content=":white_check_mark:", ephemeral=True)
    await ctx.channel.send(content=f"{user}", embed=embed)

# Delete
@bot.slash_command(guild_ids=servers)
async def delete(ctx,
    latest: discord.Option(str, "The ID of the latest message to delete"),
    oldest: discord.Option(str, "The ID of the oldest message to delete")
):
    """Delete all messages between two given IDs"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    try: # No validation for input = int and that the IDs actually exist
        await ctx.respond(content=":white_check_mark:", ephemeral=True)
        latest = await ctx.channel.fetch_message(latest)
        oldest = await ctx.channel.fetch_message(oldest)
        bucket = await ctx.channel.history(limit=500, before=latest.created_at, after=oldest.created_at, oldest_first=False).flatten()
        await latest.delete()
        for message in bucket:
            await message.delete()
        await oldest.delete()
    except Exception as e:
        await ctx.respond(f":warning: {e}", ephemeral=True)

# Embeds
@bot.slash_command(guild_ids=servers)
async def embed(ctx,
    id: discord.Option(str, "Select an embed to send", choices=["welcome", "rules"])
):
    """Send embeds"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    if id == "welcome":
        await ctx.send(files=[discord.File(open("img/banner_bat.png", "rb"))])
        await ctx.channel.send("# Welcome to Vampirism.co, the modpack and server that will transport you to a supernatural realm filled with dark mysteries and thrilling adventures.\n\nOur modpack features the Vampirism mod, which allows you to become a powerful vampire with unique abilities and weaknesses. You can transform into a bat, and use your improved strength and speed to take over entire kingdoms. But beware, the sun can be your undoing!\n\nIn addition, our server offers the Werewolves add-on, where you can embrace the full moon and transform into a ferocious werewolf. Hunt for prey, howl at the moon, and join forces with your fellow lycanthropes to defend your territory.\n\nOr, do you prefer to fight against the forces of darkness? Arm yourself with crossbows, weapons made of silver, garlic, and stakes to take down the vampires and werewolves that roam the land with the fellow hunters of your guild.\n\nBut wait, there’s more! We have carefully curated an assortment of other fantastic mods, carefully selected to enhance your immersion without diverting attention from the heart of the Vampirism experience. These modifications work in harmony to elevate your adventure, ensuring a seamless blend of creativity and exploration.\n\nSo gather your friends, form a coven or pack, and embark on an epic journey through the night. Will you choose the path of the vampire, werewolf, hunter, or maybe a human? The choice is yours, on Vampirism.co\n** **")
        await ctx.channel.send("## Get one of our modpacks to get started:\n\n<:modrinth:1203478892837478410> **[Modrinth](https://modrinth.com/modpack/vampirism.co)** <:external_link:904418888551391243> — Simple and modern by default, yet powerful when needed; our clear recommendation.\n<:curseforge:904463104505688124> **[CurseForge](https://vampirism.co/install-curseforge)** <:external_link:904418888551391243> — The true classic everyone knows and a good way to play modded Minecraft in general.")
    elif id == "rules":
        embeds = [
            discord.Embed(title="Treat everyone with respect. Absolutely no harassment, sexism, racism, hate speech, swearing, derogatory language, witch hunting or any other discrimination will be tolerated.", color=0x7246F8),
            discord.Embed(title="Be civil and use common sense. If you do something that’s not explicitly prohibited by the rules, but isn’t okay nonetheless, we’ll still take actions.", color=0x7246F8),
            discord.Embed(title="Keep things family friendly. No NSFW or obscene content. This includes but is not limited to nudity, sex, hard violence, or other graphically disturbing content.", color=0x7246F8),
            discord.Embed(title="No spam or self-promotion (server invites, advertisements, etc.) without permission from a staff member. This includes directly messaging other members.", color=0x7246F8),
            discord.Embed(title="Speak English in public chats and avoid excessive use of caps, symbols, emojis, or other elements that clutter the conversation.", color=0x7246F8),
            discord.Embed(title="If you see someone breaking the rules or something that makes you feel unsafe, message staff immediately. We want this server to be a welcoming and safe space and will resolve the situation as fast as possible.", color=0xBB1234),
            discord.Embed(title="Breaking any of these rules will result in your messages being deleted, a temporary mute, a warning, a temporary ban or a permanent ban.", color=0xBB1234)
        ]
        # Todo: This might work in one line.
        view=discord.ui.View()
        view.add_item(discord.ui.Button(emoji="<:minecraft:904427541656371240>", label="ʟᴇᴀʀɴ ᴍᴏʀᴇ: Rules for the Minecraft server", url="https://vampirism.co/wiki/rules/"))
        await ctx.channel.send(view=view, embeds=embeds)

    await ctx.respond(content=":white_check_mark:", ephemeral=True)

# Forms
@bot.slash_command(guild_ids=servers)
async def forms(ctx,
    type: discord.Option(str, choices=["Staff Application", "Ban Appeal"]),
    action: discord.Option(str, choices=["Accept", "Reject"]),
    user: discord.Option(discord.Member),
    reason: discord.Option(str, required = False)
):
    """Send automated answers"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    try:
        if type == "Staff Application" and action == "Accept":
            await user.send(f"Hey! Your application has been accepted. You will hear from us shortly.")
        elif type == "Staff Application" and action == "Reject":
            await user.send("Hey! Your application has been rejected. You can reapply in two weeks at the earliest!")
            if reason:
                await user.send(f">>> {reason}")

        elif type == "Ban Appeal" and action == "Accept":
            await user.send("Your ban appeal has been accepted. You will be unbanned within 24 hours.")
        elif type == "Ban Appeal" and action == "Reject":
            await user.send("Your ban appeal has been rejected. You can appeal again in two weeks at the earliest.")
            if reason:
                await user.send(f">>> {reason}")

        await ctx.respond(f"`{user.name}`'s {type.lower()} has been {action.lower()}ed!")
    except Exception as e:
        await ctx.respond(f":warning: {e}")

# FTP update
async def ftp_update(ctx, local, remote):
    try:
        os.system(f"rm usernamecache.json {local}/* -r")
    except:
        pass

    try:
        status = await ctx.channel.send(f"{config.EMOJI_LOADING} Updating database...")
    except:
        status = await ctx.send(f"{config.EMOJI_LOADING} Updating database...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        config.PTERO_HOST.split(":")[0],
        int(config.PTERO_HOST.split(":")[1]) if ":" in config.PTERO_HOST else 22,
        username=config.PTERO_USER,
        key_filename=config.PTERO_KEY,
        passphrase=getattr(config, "PTERO_KEY_PASSPHRASE", None),
        allow_agent=True,
        look_for_keys=True
    )
    sftp = client.open_sftp()

    sftp.get("usernamecache.json", "usernamecache.json")

    files = sftp.listdir(remote)

    for i, file in enumerate(files):
        sftp.get(f"{remote}/{file}", f"{local}/{file}")
        if i % 25 == 0:
            try: # Discord timeout might stop loop execution
                await status.edit(f"{config.EMOJI_LOADING} [{int(i/len(files)*100)}%] Downloaded file {i} of {len(files)}...")
            except:
                pass

    await status.edit(f"{config.EMOJI_OK} Successfully downloaded {len(files)} files.")
    sftp.close()
    client.close()

# Username cache
def uuid_to_username(uuid):
    try:
        with open("usernamecache.json", "r") as file:
            cache = json.load(file)
            return cache[uuid]
    except:
        return uuid

# SHA for caching
def sha256(file_path):
    hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            hash.update(byte_block)
    return hash.hexdigest()

# Claims
@bot.slash_command(guild_ids=servers)
async def claims(ctx,
    x: discord.Option(int, "X coordinate of a block in the claim"),
    z: discord.Option(int, "Z coordinate of a block in the claim"),
    update: discord.Option(bool, "Update the database?")
):
    """Find out which claim was created first"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    await ctx.respond(f":mag_right: Searching for claims at X: `{x}`, Z: `{z}`...")
    hit = False

    if update:
        await ftp_update(ctx, "claims", "plugins/GriefPreventionData/ClaimData")
    else:
        await ctx.channel.send(f"{config.EMOJI_OK} Loaded {len(os.listdir('claims'))} cached claims from {datetime.datetime.fromtimestamp(os.path.getmtime('claims')).strftime('%Y-%m-%d %H:%M')} UTC")

    for filename in os.listdir("claims"):
        if filename.endswith(".yml"):
            with open(f"claims/{filename}", "r") as file:
                claim = yaml.safe_load(file.read())
                id = filename.split(".")[0]

                dim = claim["Lesser Boundary Corner"].split(";")[0]
                if dim == "world":
                    dim = "Overworld"
                elif dim == "DIM1":
                    dim = "End"
                elif dim == "DIM-1":
                    dim = "Nether"

                x_l = int(claim["Lesser Boundary Corner"].split(";")[1])
                x_g = int(claim["Greater Boundary Corner"].split(";")[1])
                z_l = int(claim["Lesser Boundary Corner"].split(";")[3])
                z_g = int(claim["Greater Boundary Corner"].split(";")[3])
                x1, x2 = sorted([x_l, x_g])
                z1, z2 = sorted([z_l, z_g])

                if x1 <= x <= x2 and z1 <= z <= z2:
                    hit = True
                    owner = "Admin" if claim["Owner"] == "" else uuid_to_username(claim["Owner"])
                    await ctx.channel.send(f"({dim}) `{owner}` **#{id}**")

    await ctx.channel.send(f"{config.EMOJI_NO} Couldn't find any claim for those coordinates." if not hit else "> *No further results*")

# Alts
@bot.slash_command(guild_ids=servers)
async def alts(ctx,
    search: discord.Option(str, "Search term (Username, UUID or parts of both)"),
    update: discord.Option(bool, "Update the database?")
):
    """Find alts based on hardware IDs"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    await ctx.respond(f":mag_right: Searching alts for `{search}`...")
    hit = False

    if update:
        await ftp_update(ctx, "hwid", "config/hwid")
    else:
        await ctx.channel.send(f"{config.EMOJI_OK} Loaded {len(os.listdir('hwid'))} cached hardware IDs from {datetime.datetime.fromtimestamp(os.path.getmtime('hwid')).strftime('%Y-%m-%d %H:%M')} UTC")

    if search == "*":
        search = " "

    for filename in os.listdir("hwid"):
        with open(f"hwid/{filename}", "r") as file:
            lines = file.readlines()
            if len(lines) > 1:
                content = f"- **__`{filename.split('.')[0]}`__**\n"
                for line in lines:
                    uuid = line.strip()
                    name = uuid_to_username(uuid)
                    content += f"  - `{uuid}` `{name}`\n"

                if any(uuid in content for uuid in config.STAFF_UUIDS):
                    continue

                if search.lower() in content.lower():
                    hit = True
                    await ctx.channel.send(content)

    await ctx.channel.send(f"{config.EMOJI_NO} Couldn't find any alts based on hardware IDs." if not hit else "> *No further results*")

#------------------------------------------------------------------------------#

async def check_roles():
    channel = bot.get_channel(831713643090804777)
    exclusive = ["Vampire", "Hunter", "Werewolf", "Human"]
    for member in channel.guild.members:
        roles = []
        for role in member.roles:
            if role.name in exclusive:
                roles.append(role.name)
        if len(roles) > 1:
            await channel.send(f"{member.mention} has multiple exclusive roles: `{'`, `'.join(roles)}`... Removing all of them.")
            for role in member.roles:
                if role.name in roles:
                    await member.remove_roles(role)

async def snitch_xray():
    channel = bot.get_channel(831713643090804777)
    await channel.send(":mag_right: Searching for xrayers...")
    await ftp_update(channel, "xray", "config/xray_snitch")

    with open("xray.log", "r") as file:
        cache = file.read()

    new = False
    for filename in os.listdir("xray"):

        if filename.split('.')[0] in config.STAFF_UUIDS:
            continue

        with open(f"xray/{filename}", "r") as file:
            lines = file.readlines()
            content = f"- **__`{uuid_to_username(filename.split('.')[0])}`__** - `{filename.split('.')[0]}`\n"
            hit = False
            for line in lines:
                if f"{filename.split('.')[0]} | {line.strip()}" in cache:
                    continue
                content += f"  - `{line.strip()}`\n"
                with open("xray.log", "a") as file:
                    file.write(f"{filename.split('.')[0]} | {line.strip()}\n")
                new, hit = True, True

            if hit:
                await channel.send(content)

    await channel.send(f"{config.EMOJI_NO} Couldn't find any xrayers." if not new else "> *No further results*")

async def new_alts():
    channel = bot.get_channel(831713643090804777)
    await channel.send(":mag_right: Searching for HWID changes...")
    await ftp_update(channel, "hwid", "config/hwid")

    with open("hwid.log", "r") as file:
        cache = file.read()

    new = False
    for filename in os.listdir("hwid"):

        hash = sha256(f"hwid/{filename}")
        if hash in cache:
            continue
        else:
            with open("hwid.log", "a") as file:
                file.write(f"{hash}\n")

        with open(f"hwid/{filename}", "r") as file:
            lines = file.readlines()
            if len(lines) > 1:
                message = f"-# `{filename.split('.')[0]}`\n"
                for line in lines:
                    uuid = line.strip()
                    name = uuid_to_username(uuid)
                    message += f"- `{uuid}` `{name}`\n"

                if any(uuid in message for uuid in config.STAFF_UUIDS):
                    continue

                await channel.send(message)
                new = True

    await channel.send(f"{config.EMOJI_NO} Couldn't find any HWID changes." if not new else "> *No further results*")

#------------------------------------------------------------------------------#

# Daily tasks
@tasks.loop(hours=24)
async def daily_task():
    await check_roles()
    await snitch_xray()
    await new_alts()

# Presence
@bot.event
async def on_ready():
    print("Ready!")
    await bot.change_presence(activity=discord.Game(name="vampirism.co"))
    daily_task.start()

#------------------------------------------------------------------------------#

# Take-off
bot.run(config.BOT_TOKEN)
