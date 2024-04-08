# -*- coding: utf-8 -*-

import datetime
import json
import os
from ftplib import FTP

import discord
import pycountry
import yaml
from discord.ext import tasks
from imap_tools import MailBox

import config

# Init
bot = discord.Bot(intents=discord.Intents.all())
servers = [
    528346798138589215, # Vampirism.co
    430326060635258881, # Vampirism Mod
    692526341987369021 # Dev
]

# Presence
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="vampirism.co"))
    update_mails_task.start()
    check_roles_task.start()
    snitch_xray_task.start()
    print("Tasks started, ready!")

# Automatically answer certain messages
@bot.event
async def on_message(message):
    try:
        # Custom welcome message for support tickets
        if message.author.id == 557628352828014614 and "Support will be with you shortly." in message.embeds[0].description:
            await message.edit(suppress=True)
            embed=discord.Embed(title="Welcome to your support ticket.", description="Please describe your problem or question and include your Minecraft username or any details that might be relevant, so our staff members can help you as quickly as possbible with the minimum amount of additional questions.", color=0x5865F2)
            await message.channel.send(embed=embed)
        # Auto-respond to messages regarding cracked Minecraft accounts
        if (message.author.joined_at > datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)) and (("tlauncher" in message.content) or ("premium" in message.content) or ("crack" in message.content) or ("verify" in message.content)):
            embed = discord.Embed(title="You need a genuine Minecraft account that you've paid money for.", description="Software piracy is illegal. You're trusting shady developers with access to the files on your computer - in a world where cyber attacks happen on a daily basis.", color=0xFF0000)
            await message.reply(embed=embed)
        # Whats the IP?
        if (" ip " in message.content or " ip?" in message.content) and (message.author.joined_at > datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)):
            await message.reply("Our IP is `vampirism.co`.\nLearn more in <#593208607642877973>")
    except:
        pass

#------------------------------------------------------------------------------#

# Log upload guide
@bot.slash_command(guild_ids=servers)
async def logs(ctx):
    """A guide to upload logs"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    embed=discord.Embed(title="Upload your logs", description="Guides:\n<:curseforge:904463104505688124> [CurseForge](https://vampirism.co/install-curseforge/upload-logs/) <:external_link:904418888551391243>\n<:technic:904463105780752444> [TechnicLauncher](https://vampirism.co/install-technic/upload-logs/) <:external_link:904418888551391243>\n<:modrinth:1203478892837478410> [Modrinth](https://vampirism.co/modrinth-upload-logs/) <:external_link:904418888551391243>", color=0x5865F2)
    await ctx.respond(content=":white_check_mark:", ephemeral=True)
    await ctx.channel.send(embed=embed)

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
    id: discord.Option(str, "Select an embed to send", choices=["welcome", "rules", "support"])
):
    """Send embeds"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    if id == "welcome":
        await ctx.send(files=[discord.File(open(f"{config.BOT_PATH}/img/apex_hosting.gif", "rb"))])
        embed = discord.Embed(title="Welcome to Vampirism.co, the modpack and server that will transport you to a supernatural realm filled with dark mysteries and thrilling adventures.", description="Our modpack features the Vampirism mod, which allows you to become a powerful vampire with unique abilities and weaknesses. You can transform into a bat, and use your improved strength and speed to take over entire kingdoms. But beware, the sun can be your undoing!\n\nIn addition, our server offers the Werewolves add-on, where you can embrace the full moon and transform into a ferocious werewolf. Hunt for prey, howl at the moon, and join forces with your fellow lycanthropes to defend your territory.\n\nOr, do you prefer to fight against the forces of darkness? Arm yourself with crossbows, weapons made of silver, garlic, and stakes to take down the vampires and werewolves that roam the land with the fellow hunters of your guild.\n\nBut wait, there’s more! We have carefully curated an assortment of other fantastic mods, carefully selected to enhance your immersion without diverting attention from the heart of the Vampirism experience. These modifications work in harmony to elevate your adventure, ensuring a seamless blend of creativity and exploration.\n\nSo gather your friends, form a coven or pack, and embark on an epic journey through the night. Will you choose the path of the vampire, werewolf, hunter, or maybe a human? The choice is yours, on Vampirism.co 🌙\n\n**Get one of our modpacks to get started:**\n<:curseforge:904463104505688124> **[CurseForge](https://vampirism.co/install-curseforge)** <:external_link:904418888551391243>\nAlways up-to-date and a good way to play modded Minecraft in general.\n\n<:technic:904463105780752444> **[Technic Launcher](https://vampirism.co/install-technic)** <:external_link:904418888551391243>\nAlways up-to-date and an easy way to play on our server, without much fuss.\n\n<:modrinth:1203478892837478410> **[Modrinth](https://modrinth.com/modpack/vampirism.co)** <:external_link:904418888551391243>\nAn open source modding platform, built to be performant and modern.\n\n<:diy:904463219635130408> **[More launchers & DIY](https://vampirism.co/install-manually)** <:external_link:904418888551391243>\nYou know what you're doing? Then this might be the right choice for you.", color=0x7246F8)
        await ctx.send(files=[discord.File(open(f"{config.BOT_PATH}/img/banner_bat.png", "rb"))], embeds=embed, content="** **")
    elif id == "rules":
        embeds = [
            discord.Embed(title="Treat everyone with respect. Absolutely no harassment, sexism, racism, hate speech, swearing, derogatory language, witch hunting or any other discrimination will be tolerated.", color=0x5865F2),
            discord.Embed(title="Be civil and use common sense. If you do something that's not explicitly prohibited by the rules, but we think isn't okay nonetheless, we'll still take actions as mentioned further down below.", color=0x5865F2),
            discord.Embed(title="Keep things family friendly. No NSFW or obscene content. This includes but is not limited to text, images, or links featuring nudity, sex, hard violence, or other graphically disturbing content.", color=0x5865F2),
            discord.Embed(title="No spam or self-promotion (server invites, advertisements, etc.) without permission from a staff member. This includes DMing fellow members.", color=0x5865F2),
            discord.Embed(title="Speak English in public chats and avoid excessive use of caps, symbols, emojis, or other elements that clutter the conversation.", color=0x5865F2),
            discord.Embed(title="If you see something against the rules or something that makes you feel unsafe, message staff immediately. We want this server to be a welcoming and safe space!", color=0xED4245),
            discord.Embed(title="Breaking any of these rules will result in your message(s) being deleted, a temporary mute, a warning (multiple will lead to bans), a temporary ban or a permanent ban.", color=0xED4245)
        ]
        # Todo: This might work in one line.
        view=discord.ui.View()
        view.add_item(discord.ui.Button(emoji="<:minecraft:904427541656371240>", label="See also: Rules for the Minecraft server", url="https://vampirism.co/rules"))
        await ctx.channel.send(view=view, file=discord.File(open(f"{config.BOT_PATH}/img/rules.png", "rb")), embeds=embeds)
    elif id == "support":
        embed = discord.Embed(title="Welcome to our support channel.", description="If you have connections issues, take a look at this first:")
        embed.set_image(url="https://files.vampirism.co/support.png")
        await ctx.channel.send(file=discord.File(open(f"{config.BOT_PATH}/img/support.png", "rb")), embed=embed)
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
            await user.send(f"Hey! Your application has been accepted. You will hear from us shortly.\n\nIn the meantime, you can take a look at this: <https://1literzinalco.github.io/vampirism/staff.html>\n\nWe're using \"Trello\" to organize everything important, such as bugs and punishments. Check out this brief overview: <https://youtu.be/AphRCn5__38> and then join our board: ||<{config.TRELLO}>|| (keep this link secret!)")
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
        os.system(f"rm {config.BOT_PATH}/usernamecache.json {config.BOT_PATH}/{local}/* -r")
    except:
        pass

    try:
        status = await ctx.channel.send(f"{config.EMOJI_LOADING} Updating database...")
    except:
        status = await ctx.send(f"{config.EMOJI_LOADING} Updating database...")

    ftp = FTP(config.FTP_HOST)
    ftp.login(config.FTP_NAME, config.FTP_PASS)

    ftp.retrbinary("RETR usernamecache.json", open(f"{config.BOT_PATH}/usernamecache.json", "wb").write)
    ftp.cwd(remote)
    files = ftp.nlst()

    for i, file in enumerate(files):
        ftp.retrbinary(f"RETR {file}", open(f"{config.BOT_PATH}/{local}/{file}", "wb").write)
        if i % 25 == 0:
            try: # Discord timeout might stop loop execution
                await status.edit(f"{config.EMOJI_LOADING} [{int(i/len(files)*100)}%] Downloaded file {i} of {len(files)}...")
            except:
                pass

    await status.edit(f"{config.EMOJI_OK} Successfully downloaded {len(files)} files.")
    ftp.close()

# Username cache
def uuid_to_username(uuid):
    try:
        with open(f"{config.BOT_PATH}/usernamecache.json", "r") as file:
            cache = json.load(file)
            return cache[uuid]
    except:
        return uuid

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
        await ctx.channel.send(f"{config.EMOJI_OK} Loaded {len(os.listdir(f'{config.BOT_PATH}/claims'))} cached claims from {datetime.datetime.fromtimestamp(os.path.getmtime(f'{config.BOT_PATH}/claims')).strftime('%Y-%m-%d %H:%M')} UTC")

    for filename in os.listdir(f"{config.BOT_PATH}/claims"):
        if filename.endswith(".yml"):
            with open(f"{config.BOT_PATH}/claims/{filename}", "r") as file:
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
                    await ctx.channel.send(f"({dim}) `{owner}` **♯{id}**")

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
        await ctx.channel.send(f"{config.EMOJI_OK} Loaded {len(os.listdir(f'{config.BOT_PATH}/hwid'))} cached hardware IDs from {datetime.datetime.fromtimestamp(os.path.getmtime(f'{config.BOT_PATH}/hwid')).strftime('%Y-%m-%d %H:%M')} UTC")

    if search == "*":
        search = " "

    for filename in os.listdir(f"{config.BOT_PATH}/hwid"):
        with open(f"{config.BOT_PATH}/hwid/{filename}", "r") as file:
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

# Get new emails via imap and send the content to the staff channel
async def update_mails():
    channel = bot.get_channel(564783779474833431)
    
    # Connect to imap
    with MailBox(config.IMAP_HOST).login(config.IMAP_NAME, config.IMAP_PASS, "INBOX") as mailbox:

        # Cycle through inbox
        for mail in mailbox.fetch():

            # Try to split the email into the form's parts
            try:
                content = mail.text.split("§§")
            except:
                pass

            # Switch submission types

            # Staff application
            if len(content) == 11:
                word_count = len(content[7].split()) + len(content[8].split()) + len(content[9].split())

                embed=discord.Embed(title=content[0], description=f"{content[1]} years old, {content[2]}\n:flag_{content[3].lower()}: {pycountry.countries.get(alpha_2=content[3]).name}")
                embed.add_field(name="Minecraft Username", value=f"`{content[4]}`", inline=True)
                embed.add_field(name="Discord#Tag", value=f"`{content[5]}`", inline=True)
                embed.add_field(name="Email", value=f"`{content[6]}`", inline=True)
                embed.add_field(name="Do you have experience as staff?", value=content[7], inline=False)
                embed.add_field(name="Why do you want to be staff?", value=content[8], inline=False)
                embed.add_field(name="Why should you be chosen instead of someone else?", value=content[9], inline=False)
                embed.add_field(name="How many hours could you approximately contribute per week?", value=content[10], inline=False)
                embed.set_footer(text=f"{word_count} words")

                try:
                    if word_count > 50:
                        msg = await channel.send(content="**STAFF APPLICATION** <@&844592732001009686>", embed=embed)
                    else:
                        msg = await channel.send(content="**STAFF APPLICATION**", embed=embed)

                    await msg.add_reaction("<:vote_yes:601899059417972737>")
                    await msg.add_reaction("<:vote_no:601898704231989259>")
                    await msg.create_thread(name=f"{content[0]}\'s Staff Application")

                except:
                    embed=discord.Embed(title=content[0], description=f"{content[1]} years old, {content[2]}\n:flag_{content[3].lower()}: {pycountry.countries.get(alpha_2=content[3]).name}")
                    embed.add_field(name="Minecraft Username", value=f"`{content[4]}`", inline=True)
                    embed.add_field(name="Discord#Tag", value=f"`{content[5]}`", inline=True)
                    embed.add_field(name="Email", value=f"`{content[6]}`", inline=True)
                    embed.add_field(name="Do you have experience as staff? Why do you want to be staff? Why should you be chosen instead of someone else?", value="Check the thread 🧵", inline=False)
                    embed.add_field(name="How many hours could you approximately contribute per week?", value=content[10], inline=False)
                    embed.set_footer(text=f"{word_count} words")

                    msg = await channel.send(content="**STAFF APPLICATION** <@&844592732001009686>", embed=embed)
                    await msg.add_reaction("<:vote_yes:601899059417972737>")
                    await msg.add_reaction("<:vote_no:601898704231989259>")
                    thread = await msg.create_thread(name=f"{content[0]}\'s Staff Application")
                    await thread.send(f"**Do you have experience as staff?**\n>>> {content[7]}")
                    await thread.send(f"**Why do you want to be staff?**\n>>> {content[8]}")
                    await thread.send(f"**Why should you be chosen instead of someone else?**\n>>> {content[9]}")                

            # Ban appeal
            elif len(content) == 7:
                word_count = len(content[5].split()) + len(content[6].split())

                if content[0] == "mc":
                    embed=discord.Embed(title="Ban Appeal", description=f"Bans: Minecraft\nType: {content[1]}")
                elif content[0] == "dc":
                    embed=discord.Embed(title="Ban Appeal", description=f"Bans: Discord\nType: {content[1]}")
                else:
                    embed=discord.Embed(title="Ban Appeal", description=f"Bans: Minecraft & Discord\nType: {content[1]}")
                embed.add_field(name="Minecraft Username", value=f"`{content[2]}`", inline=True)
                embed.add_field(name="Discord#Tag", value=f"`{content[3]}`", inline=True)
                embed.add_field(name="Email", value=f"`{content[4]}`", inline=True)
                embed.add_field(name="Why have you been banned?", value=content[5], inline=False)
                embed.add_field(name="Why should you be unbanned?", value=content[6], inline=False)
                embed.set_footer(text=f"{word_count} words")

                try:
                    if word_count > 50:
                        msg = await channel.send(content="<@&844592732001009686>", embed=embed)
                    else:
                        msg = await channel.send(embed=embed)

                    await msg.add_reaction("<:vote_yes:601899059417972737>")
                    await msg.add_reaction("<:vote_no:601898704231989259>")
                    await msg.create_thread(name=f"{content[2]}\'s Ban Appeal")

                except:
                    if content[0] == "mc":
                        embed=discord.Embed(title="Ban Appeal", description=f"Bans: Minecraft\nType: {content[1]}")
                    elif content[0] == "dc":
                        embed=discord.Embed(title="Ban Appeal", description=f"Bans: Discord\nType: {content[1]}")
                    else:
                        embed=discord.Embed(title="Ban Appeal", description=f"Bans: Minecraft & Discord\nType: {content[1]}")
                    embed.add_field(name="Minecraft Username", value=f"`{content[2]}`", inline=True)
                    embed.add_field(name="Discord#Tag", value=f"`{content[3]}`", inline=True)
                    embed.add_field(name="Email", value=f"`{content[4]}`", inline=True)
                    embed.add_field(name="Why have you been banned? Why should you be unbanned?", value="Check the thread 🧵", inline=False)
                    embed.set_footer(text=f"{word_count} words")

                    msg = await channel.send(content="**BAN APPEAL** <@&844592732001009686>", embed=embed)
                    await msg.add_reaction("<:vote_yes:601899059417972737>")
                    await msg.add_reaction("<:vote_no:601898704231989259>")
                    thread = await msg.create_thread(name=f"{content[2]}\'s Ban Appeal")
                    await thread.send(f"**Why have you been banned?**\n>>> {content[5]}")
                    await thread.send(f"**Why should you be unbanned?**\n>>> {content[6]}")                

            # Unknown
            else:
                embed = discord.Embed(title="Unknown email", description="I've received an email that doesn't match the layout of any form:")
                embed.add_field(name="Sender", value=mail.from_, inline=True)
                embed.add_field(name="Subject", value=mail.subject, inline=True)
                await channel.send(embed=embed)
                return

            # Delete the email and log out
            mailbox.delete(mail.uid)

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

    with open(f"{config.BOT_PATH}/xray.log", "r") as file:
        cache = file.read()

    new = False
    for filename in os.listdir(f"{config.BOT_PATH}/xray"):
        
        if filename.split('.')[0] in config.STAFF_UUIDS:
            continue

        with open(f"{config.BOT_PATH}/xray/{filename}", "r") as file:
            lines = file.readlines()
            content = f"- **__`{uuid_to_username(filename.split('.')[0])}`__**\n"
            hit = False
            for line in lines:
                if f"{filename.split('.')[0]} | {line.strip()}" in cache:
                    continue
                content += f"  - `{line.strip()}`\n"
                with open(f"{config.BOT_PATH}/xray.log", "a") as file:
                    file.write(f"{filename.split('.')[0]} | {line.strip()}\n")
                new, hit = True, True

            if hit:
                await channel.send(content)

    await channel.send(f"{config.EMOJI_NO} Couldn't find any xrayers." if not new else "> *No further results*")


#------------------------------------------------------------------------------#

# Update mails
@tasks.loop(hours=1)
async def update_mails_task():
    await update_mails()

# Check roles
@tasks.loop(hours=24)
async def check_roles_task():
    await check_roles()

# Snitch xray
@tasks.loop(hours=24)
async def snitch_xray_task():
    await snitch_xray()

#------------------------------------------------------------------------------#

# Take-off
bot.run(config.BOT_TOKEN)
