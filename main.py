# -*- coding: utf-8 -*-

import config, discord, os, datetime, time, requests, yaml, pycountry
from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from ftplib import FTP
from imap_tools import MailBox

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
    print("Ready!")

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
            embed = discord.Embed(title="You need a genuine Minecraft account that you've paid money for.", description=f"Software piracy is illegal. You're trusting shady developers with access to the files on your computer - in a world where cyber attacks happen on a daily basis.", color=0xFF0000)
            await message.reply(embed=embed)
        # Whats the IP?
        if (" ip " in message.content or " ip?" in message.content) and (message.author.joined_at > datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)):
            await message.reply("Our IP is `vampirism.co`.\nLearn more in <#593208607642877973>")
    except:
        pass

#------------------------------------------------------------------------------#


# Ping
@bot.slash_command(guild_ids=servers)
async def ping(ctx):
    """Test bot functionality"""
    embed=discord.Embed(title="Dracula")
    embed.add_field(name="Host", value=f"{os.uname()}", inline=False)
    embed.add_field(name="Latency", value=f"{bot.latency}", inline=True)
    embed.add_field(name="ClientUser", value=f"{bot.user}", inline=True)
    embed.add_field(name="Websocket Gateway", value=f"{bot.ws}", inline=False)
    await ctx.respond(embed=embed)

# Log upload guide
@bot.slash_command(guild_ids=servers)
async def logs(ctx):
    """A guide to upload logs"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    embed=discord.Embed(title="Upload your logs", description="<:curseforge:904463104505688124> [CurseForge](https://vampirism.co/install-curseforge/upload-logs/) <:external_link:904418888551391243>\n<:technic:904463105780752444> [TechnicLauncher](https://vampirism.co/install-technic/upload-logs/) <:external_link:904418888551391243>")
    await ctx.respond(content=":white_check_mark:", ephemeral=True)
    await ctx.channel.send(embed=embed)

# Ticket close
@bot.slash_command(guild_ids=servers)
async def reject(ctx,
    reason: discord.Option(str, "Reason for rejection")
):
    """Reject a suggestion"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    # Make sure it's a thread
    if ctx.channel.type != discord.ChannelType.public_thread:
        await ctx.respond(":warning: This command can only be used in threads.", ephemeral=True)
        return

    try:
        await ctx.channel.owner.send(f"{ctx.author.mention} has closed your suggestion thread with the title *{ctx.channel.name}*.\n{reason}")
        await ctx.respond(":white_check_mark:", ephemeral=True)
    except:
        await ctx.respond("Couldn't message the thread owner.", ephemeral=True)
    time.sleep(3)
    
    await ctx.channel.delete()

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
        embed=discord.Embed(title="If there's nothing else we can help you with, we would like to go ahead close this ticket now.", description="You can either do this yourself by scrolling up to the start of the ticket and then clicking the \"Close\" button, or just let us know that you've read this and we'll do it.")
        embed.set_footer(text="And feel free to open a new ticket at any time if there's something we can do for you!")
    else:
        embed=discord.Embed(title="If you still require help, please answer now.", description="It's been a while now since you last sent a message and we will go ahead close this ticket soon.")
    await ctx.respond(content=f"{user}", embed=embed)

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
        embeds=[
            discord.Embed(title="Get started", description="Get one of our official modpacks with automatic updates or build your own! For a guide, simply click on your choice below!\n\n<:technic:904463105780752444> **[Technic Launcher](https://vampirism.co/install-technic)** <:external_link:904418888551391243>\nAlways up-to-date and the easiest choice, if you just want to play on our server.\n\n<:curseforge:904463104505688124> **[CurseForge](https://vampirism.co/install-curseforge)** <:external_link:904418888551391243>\nFormerly known as the \"Twitch App\", this launcher is also always up-to-date and easy to use.\n\n<:diy:904463219635130408> **[Get the modlist](https://vampirism.co/install-manually)** <:external_link:904418888551391243>\nYou know what you're doing? Then this might be the right choice for you.", color=0x5865F2),
            discord.Embed(title="Useful links", description="• [Get a brief overview](https://teamlapen.github.io/Vampirism/) about the Vampirism mod and its basic features\n• [Read the wiki](https://github.com/TeamLapen/Vampirism/wiki/Getting-Started) if you want to know how everything works in detail\n• [Apply to become a staff member](https://vampirism.co/staff-applications/)\n• [Appeal your ban](https://vampirism.co/appeal-your-ban/)", color=0x5865F2),
            discord.Embed(title="Nice to know", description="• The server's IP is `vampirism.co`!\n• The server automatically restarts at [02:00 UTC](https://time.is/UTC) <:external_link:904418888551391243>\n• If <@802604397967179776> is online, the server is online as well!", color=0x5865F2)
        ]
        await ctx.send(file=discord.File(open(f"{config.BOT_PATH}/img/welcome.png", "rb")), embeds=embeds)
    elif id == "rules":
        embeds = [
            discord.Embed(title="Treat everyone with respect. Absolutely no harassment, sexism, racism, hate speech, strong/derogatory language, witch hunting or any other discrimination will be tolerated.", color=0x5865F2),
            discord.Embed(title="Be civil and use common sense. If you do something that's not explicitly prohibited by the rules, but we think isn't okay nonetheless, we'll still take actions as mentioned further down below.", color=0x5865F2),
            discord.Embed(title="Keep things family friendly. No NSFW or obscene content. This includes but is not limited to text, images, or links featuring nudity, sex, hard violence, or other graphically disturbing content.", color=0x5865F2),
            discord.Embed(title="No spam or self-promotion (server invites, advertisements, etc) without permission from a staff member. This includes DMing fellow members.", color=0x5865F2),
            discord.Embed(title="Speak English in public chats. Vampirism's community is spread all over the world and we want that everyone can be a part of it.", color=0x5865F2),
            discord.Embed(title="If you see something against the rules or something that makes you feel unsafe, message staff immediately. We want this server to be a welcoming space!", color=0x5865F2),
            discord.Embed(title="Breaking any of these rules will result in your message(s) being deleted, a temporary mute, a warning (multiple will lead to bans), a temporary ban or a permanent ban.", color=0x5865F2)
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
    type: discord.Option(str, "Write, click or select an option with the arrow keys, then press TAB", choices=["Staff Application", "Ban Appeal"]),
    action: discord.Option(str, "Write, click or select an option with the arrow keys, then press TAB", choices=["Accept", "Reject"]),
    user: discord.Option(str, "@Tag the user, write their ID or full name (with #discriminator), then press TAB")
):
    """Send automated answers"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    try:
        member = ctx.guild.get_member(int(user))
    except:
        member = ctx.guild.get_member_named(user)

    if member is not None:
        try:
            if type == "Staff Application" and action == "Accept":
                await member.send(f"Hey! Your application has been accepted. You will hear from us shortly.\n\nIn the meantime, you can take a look at this: <https://1literzinalco.github.io/vampirism/staff.html>\n\nWe're using \"Trello\" to organize everything important, such as bugs and punishments. Check out this brief overview: <https://youtu.be/AphRCn5__38> and then join our board: ||<{config.TRELLO}>|| (keep this link secret!)")
            elif type == "Staff Application" and action == "Reject":
                await member.send(f"Hey! Your application has been rejected. You can reapply in two weeks at the earliest!")
            elif type == "Ban Appeal" and action == "Accept":
                await member.send("Your ban appeal has been accepted. You will be unbanned within 24 hours.")
            elif type == "Ban Appeal" and action == "Reject":
                await member.send("Your ban appeal has been rejected. You can appeal again in two weeks at the earliest.")
            await ctx.respond(f"{member.name}'s {type.lower()} has been {action.lower()}ed!")
        except Exception as e:
            await ctx.respond(f":warning: {e}")
    else:
        await ctx.respond(f":warning: I couldn't find a user by searching for `{user}`.")

# Restart
@bot.slash_command(guild_ids=servers)
async def restart(ctx):
    """Restarts the server"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    try:
        await ctx.respond("Alright, one moment.")
        # Init
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        # Login
        browser.get("https://panel.apexminecrafthosting.com/site/login")
        browser.find_element_by_id("LoginForm_name").send_keys(config.APEX_NAME)
        browser.find_element_by_id("LoginForm_password").send_keys(config.APEX_PASS)
        browser.find_element_by_name("yt0").click()
        # Console
        browser.get("https://panel.apexminecrafthosting.com/server/log/79157")
        browser.find_element_by_id("command").send_keys("save-all")
        browser.find_element_by_name("yt4").click()
        time.sleep(10)
        # Restart
        browser.find_element_by_name("yt3").click()
        time.sleep(1)
        browser.find_element_by_class_name("swal2-confirm").click()
        time.sleep(5)
        browser.find_element_by_name("yt0").click()
        # Finally
        browser.quit()
        await ctx.channel.send("I've restarted the server!")
    except Exception as e:
        await ctx.channel.send(f":warning: {e}")

# Claims
@bot.slash_command(guild_ids=servers)
async def claim(ctx,
    x: discord.Option(int, "X coordinate of a block in the claim"),
    z: discord.Option(int, "Z coordinate of a block in the claim")
):
    """Find out which claim was created first"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    claims = []
    result = False

    await ctx.respond("Loading claims...")

    for filename in os.listdir(f"{config.BOT_PATH}/claims"):
        if filename.endswith(".yml"):
            with open(f"{config.BOT_PATH}/claims/{filename}", "r") as file:
                content = yaml.safe_load(file.read())
                content["id"] = filename.split(".")[0]
                claims.append(content)

    await ctx.channel.send(f"Loaded {len(claims)} claims.")

    for claim in claims:
        dim = claim["Lesser Boundary Corner"].split(";")[0]
        x_l = int(claim["Lesser Boundary Corner"].split(";")[1])
        x_g = int(claim["Greater Boundary Corner"].split(";")[1])
        z_l = int(claim["Lesser Boundary Corner"].split(";")[3])
        z_g = int(claim["Greater Boundary Corner"].split(";")[3])

        if dim == "world": # Pretty print the dimension
            dim = "Overworld"
        elif dim == "DIM1":
            dim = "End"
        elif dim == "DIM-1":
            dim = "Nether"
        if x_l > x_g: # Sort X coords so x1 is smaller than x2
            x1 = x_g
            x2 = x_l
        else:
            x1 = x_l
            x2 = x_g
        if z_l > z_g: # Sort Z coords so z1 is smaller than z2
            z1 = z_g
            z2 = z_l
        else:
            z1 = z_l
            z2 = z_g

        if (x >= x1) and (x <= x2):
            if (z >= z1) and (z <= z2):
                result = True
                owner = requests.get(f"https://api.mojang.com/user/profile/{claim['Owner']}").json()
                await ctx.channel.send(f"Found a claim in the **{dim}** owned by **``{owner['name']}``** with ID **{claim['id']}**")

    if result == False:
        await ctx.channel.send(":warning: Couldn't find any claim for that coordinates. Is the database up to date?")
    else:
        await ctx.channel.send("*No further results*")

# Update claims
@bot.slash_command(guild_ids=servers)
async def updateclaims(ctx):
    """Update the local database of claims"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    try:
        os.system(f"rm {config.BOT_PATH}/claims/* -r")
    except:
        pass

    await ctx.respond("Hang on for a few minutes!")

    ftp = FTP(config.FTP_HOST)
    ftp.login(config.FTP_NAME, config.FTP_PASS)
    status = await ctx.channel.send("Connection established...")

    ftp.cwd("plugins/GriefPreventionData/ClaimData")
    files = ftp.nlst() # Gets all files

    for i, file in enumerate(files):
        ftp.retrbinary(f"RETR {file}", open(f"{config.BOT_PATH}/claims/{file}", "wb").write)
        if str(i).endswith("00") or str(i).endswith("25") or str(i).endswith("50") or str(i).endswith("75"):
            try: # Discord timeout might stop loop execution
                await status.edit(f"[{int(i/len(files)*100)}%] Downloaded file {i} of {len(files)}...")
            except:
                pass

    await status.edit(f"Successfully downloaded {len(files)} files.")
    #ftp.close()

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

                    msg = await channel.send(content=f"**STAFF APPLICATION** <@&844592732001009686>", embed=embed)
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

                    msg = await channel.send(content=f"**BAN APPEAL** <@&844592732001009686>", embed=embed)
                    await msg.add_reaction("<:vote_yes:601899059417972737>")
                    await msg.add_reaction("<:vote_no:601898704231989259>")
                    thread = await msg.create_thread(name=f"{content[2]}\'s Ban Appeal")
                    await thread.send(f"**Why have you been banned?**\n>>> {content[5]}")
                    await thread.send(f"**Why should you be unbanned?**\n>>> {content[6]}")                

            # Unknown
            else:
                embed = discord.Embed(title="Unknown email", description=f"I've received an email that doesn't match the layout of any form:")
                embed.add_field(name="Sender", value=mail.from_, inline=True)
                embed.add_field(name="Subject", value=mail.subject, inline=True)
                await channel.send(embed=embed)
                return

            # Delete the email and log out
            mailbox.delete(mail.uid)

# Update mails
@bot.slash_command(guild_ids=servers)
async def updatemails(ctx):
    """Check for new staff applications and ban appeals"""
    if "Staff" not in str(ctx.author.roles):
        await ctx.respond(":warning: Insufficient permission.", ephemeral=True)
        return

    await ctx.respond(content=":white_check_mark:", ephemeral=True)
    await update_mails()

#------------------------------------------------------------------------------#

# Update mails
@tasks.loop(hours=4)
async def update_mails_task():
    await update_mails()

#------------------------------------------------------------------------------#

# Take-off
bot.run(config.BOT_TOKEN)
