# Status Discord Bot
A discord bot which gives a role when someone has the specified message in their status, and the role could give access to something premium.

# Config

Explanation to some things in the config.
Do not paste this inside your config, it will not work.
```json
{
    "bot-token": "Here put your 'BOT TOKEN', NOT your 'ACCOUNT TOKEN'",
    "guild-id": "Here put the id of your guild/server",

    "status-message": "The message you want people to have in their status",
    "role-to-give": "ID of the role that you want to give to your users as a reward",
    "logs-channel-id": "ID of the channel where logs come",
    "send-logs": "boolean, switch for logs",
    "check-statuses-on-startup": "boolean, check users if they have the message in their status on bot startup",

    "admins": ["List of users you want the bot to recognize as admin"],
    "blacklisted-users": ["List of users that you dont want the bot to give role to"],
    "footer-msg": "Message that appears on footers of embeds that the bot sends"
}
```

# Errors
Make sure you've filled everything out correctly and in the same type (int, string). If you get any errors, feel free to contact me thru my discord.
