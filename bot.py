import hikari
import os, time
from dotenv import load_dotenv
directory = os.path.dirname(os.path.realpath(__file__))
load_dotenv(f"{directory}{os.path.sep}uptime.env")
TOKEN = os.getenv("TOKEN")
TARGET_BOT_ID = int(os.getenv("BOT_ID"))
MUTUAL_GUILD_ID = int(os.getenv("MUTUAL_GUILD_ID"))
USER_ID = int(os.getenv("USER_ID"))
DM_CHANNEL = None

bot = hikari.GatewayBot(TOKEN, intents = hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.GUILD_PRESENCES)
is_online = True


def do_something():
    """
    if you want, you can add code here that notifies the user in different way, or start bot from this machine.
    make sure there is no blocking code here
    """
    pass


@bot.listen(hikari.PresenceUpdateEvent)
async def presence_update(event: hikari.MemberPresence):
    global is_online
    # check if it is the target presence has changed
    if event.user_id != TARGET_BOT_ID: return # not the bot
    
    if event.presence == None:
        is_currently_online = False
    elif event.presence.visible_status == hikari.Status.OFFLINE:
        is_currently_online = False
    else:
        is_currently_online = True

    if is_online == is_currently_online: return # status didn't changed at all
    
    # if the status changed, notify user accordingly
    if not is_currently_online:
        await bot.rest.create_message(DM_CHANNEL, embed=hikari.Embed(title=f"{TARGET_BOT_ID} is offline! - click for bot info", description=f"### [{TARGET_BOT_ID}](https://discordapp.com/users/{TARGET_BOT_ID}) is offline since <t:{int(time.time())}>! <t:{int(time.time())}:R>", color=(255, 0, 0), url=f"https://discordapp.com/users/{TARGET_BOT_ID}").set_footer("you will get a message when it will go back online"))
        print(f"\033[91m{TARGET_BOT_ID} is offline!\ta message sent to {USER_ID}\033[0m")
        do_something()
    
    else:
        await bot.rest.create_message(DM_CHANNEL, embed=hikari.Embed(title=f"{TARGET_BOT_ID} is online! - click for bot info", description=f"### [{TARGET_BOT_ID}](https://discordapp.com/users/{TARGET_BOT_ID}) is back online since <t:{int(time.time())}> <t:{int(time.time())}:R>", color=(0, 255, 0), url = f"https://discordapp.com/users/{TARGET_BOT_ID}").set_footer("if it will go back down, you will get a message"))
        print(f"\033[92m{TARGET_BOT_ID} is back online!\ta message sent to {USER_ID}\033[0m")
    is_online = is_currently_online


async def check_if_online():
    target_bot_status = await bot.rest.fetch_member(MUTUAL_GUILD_ID, TARGET_BOT_ID)
    if target_bot_status.get_presence() == None: return False
    return target_bot_status.get_presence().visible_status != hikari.Status.OFFLINE

@bot.listen(hikari.StartedEvent)
async def bot_started(event):
    global is_online, DM_CHANNEL
    is_online = await check_if_online()
    DM_CHANNEL = await bot.rest.create_dm_channel(USER_ID)
    embed = hikari.Embed(title=f"monitoring {TARGET_BOT_ID} status - click for bot info", description="if the bot goes offline, a message will be sent to you", colour=(255, 255, 0), url=f"https://discordapp.com/users/{TARGET_BOT_ID}")
    if is_online:
        embed.add_field("current status", "the bot is now online!", inline=True)
    else:
        embed.add_field("current status", "the bot is now offline!", inline=True)
    await bot.rest.create_message(DM_CHANNEL, embed=embed)
    
    if is_online:
        status_text = "online"
    else:
        status_text = "offline"
    print(f"\033[94mstarting monitoring {TARGET_BOT_ID}\tcurrent status: {status_text}\033[0m")

@bot.listen(hikari.StoppedEvent)
async def bot_stopped(event):
    if is_online:
        status_text = "online"
    else:
        status_text = "offline"
    print(f"\033[94mstopped monitoring {TARGET_BOT_ID}\tlast status: {status_text}\033[0m")

bot.run(activity=hikari.Activity(name="bot status", type=hikari.ActivityType.LISTENING), status=hikari.Status.ONLINE)