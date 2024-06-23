import discord, json
from datetime import datetime
#from discord import app_commands

users = []

bot = discord.Client(intents=discord.Intents.all())
#tree = app_commands.CommandTree(bot)
config = json.load(open('config.json'))

async def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours} hours, {minutes} minutes and {seconds} seconds"
    elif minutes > 0:
        return f"{minutes} minutes and {seconds} seconds"
    else:
        return f"{seconds} seconds"

async def send_log_to_discord(data):
    if not config['send-logs']:
        return False
    # Check if the logs channel exists
    channel = bot.get_channel(config['logs-channel-id'])
    if channel:
        if data['action'] == 'add':
            embed = discord.Embed(
                title='Added Role',
                description=f"<@{data['userid']}> has been given the role.",
                color=discord.Color.green()
            )
            embed.set_footer(text=config['footer-msg'])
        elif data['action'] == 'remove': 
            current_time = datetime.now().timestamp()
            format_msg = await format_time(int(current_time - data['time']))
            embed = discord.Embed(
                title='Removed Role',
                description=f"<@{data['userid']}> had the role for **{format_msg}**.",
                color=discord.Color.red()
            )
            embed.set_footer(text=config['footer-msg'])
        elif data['action'] == 'started':
            embed = discord.Embed(
                title='Bot started',
                description=f"**Users added**: {data['users_added']}\n**Users removed**: {data['users_removed']}",
                color=discord.Color.blurple()
            )
            embed.set_footer(text=config['footer-msg'])
        await channel.send(embed=embed)
        return True
    else:
        print("Logs channel is not setup correctly, make sure the id is correct.")
    return True

async def add_user_to_list(userid, sendlog = True):
    global users
    current_time = datetime.now().timestamp()
    if sendlog:
        await send_log_to_discord({
            'time': current_time,
            'userid': userid,
            'action': 'add'
        })
    users.append({userid: current_time})


async def remove_user_from_list(userid, sendlog = True):
    global users
    for user in users:
        if userid in user:
            if sendlog:
                await send_log_to_discord({
                    'time': user[userid],
                    'userid': userid,
                    'action': 'remove'
                })
            users.remove(user)
            return True
    return False

async def is_user_in_list(userid):
    for user in users:
        if userid in user:
            return True
    return False


@bot.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    _before = [i.name for i in before.activities]
    _after = [i.name for i in after.activities]
    # Debug - print("after", _after, "\nBefore", _before)

    # User doesn't have the specified message anymore
    if _after and _after[0] != config['status-message']:
        guild = discord.utils.get(bot.guilds, id=int(config['guild-id']))
        spec_role = discord.utils.get(guild.roles, id=int(config['role-to-give']))
        await after.remove_roles(spec_role, reason="Removed status")
        await remove_user_from_list(after.id)
        print(f"Removed role from {after.id}")
    
    # The user now has the specified status message
    elif _after and _after[0] == config['status-message']:
        if after.id not in config['blacklisted-users']:
            guild = discord.utils.get(bot.guilds, id=int(config['guild-id']))
            spec_role = discord.utils.get(guild.roles, id=int(config['role-to-give']))
            await after.add_roles(spec_role, reason="Added status")
            await add_user_to_list(after.id)
            print(f"Added role to {after.id}")
    
    # Just remove the role if they have it
    else:
        hasRole = False
        for role in after.roles:
            hasRole = True if int(role.id) == int(config['role-to-give']) else False
        if hasRole:
            guild = discord.utils.get(bot.guilds, id=int(config['guild-id']))
            spec_role = discord.utils.get(guild.roles, id=int(config['role-to-give']))
            await after.remove_roles(spec_role, reason="Status change?")
            await remove_user_from_list(after.id)
            print(f"Removed role from {after.id}")



@bot.event
async def on_ready():

    # This might be not needed, since im not actually using any commands.
    # await tree.sync(guild=discord.Object(id=config["guild-id"]))

    if config['check-statuses-on-startup']:
        try:
            users_added = 0
            users_removed = 0
            guild = discord.utils.get(bot.guilds, id=int(config['guild-id']))
            if guild:
                spec_role = discord.utils.get(guild.roles, id=int(config['role-to-give']))
                async for member in guild.fetch_members(limit=None):
                    if member.id not in config['admins'] and not member.bot: # Member is not an admin
                        _member = discord.utils.get(guild.members, id=int(member.id))
                        hasStatus = [i.name for i in _member.activities]
                        for role in member.roles: # Loop over all member's roles
                            if int(role.id) == int(config['role-to-give']): # Member has the specified role
                                if hasStatus and not hasStatus[0] == config['status-message']:
                                    await member.remove_roles(spec_role, reason="Removed status")
                                    users_removed += 1
                                elif not hasStatus:
                                    await member.remove_roles(spec_role, reason="Removed status")
                                    users_removed += 1
                        if hasStatus and hasStatus[0] == config['status-message']:
                            if member.id not in config['blacklisted-users']:
                                await member.add_roles(spec_role, reason="Has status")
                                current_time = datetime.now().timestamp()
                                users_added += 1
                                users.append({member.id: current_time})
                            else:
                                await member.remove_roles(spec_role, reason="Removed status")
                                users_removed += 1

                if config['send-logs']:
                    await send_log_to_discord({
                        'action': 'started',
                        'users_added': users_added,
                        'users_removed': users_removed,
                    })
            else:
                print('Invalid Guild ID (%s) in config.') % (str(config['guild-id']))

        except Exception as e:
            print("Status check on startup failed. -", e.args)

    print("Logged in as {0.user}".format(bot))

bot.run(config['bot-token'])