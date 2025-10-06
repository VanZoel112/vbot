# Developer Assistant Configuration

## Overview

The `developer_assistant.json` file maps Telegram user IDs to their assistant bot credentials. When a developer deploys VZ Assistant, the userbot will automatically use the bot configured for their user ID instead of creating a new one.

## Benefits

- **No duplicate bots**: Developers reuse their existing assistant bot
- **Faster setup**: Skip BotFather bot creation process
- **Consistent naming**: All developers use pre-configured bot usernames
- **Easy sharing**: Add new developers by updating this JSON file

## How to Add Yourself

1. **Get your Telegram user ID**:
   ```
   Send a message to @userinfobot on Telegram
   Or run the userbot and check startup logs for "Current user: ... - ID: XXXXXXX"
   ```

2. **Create your assistant bot** (if you don't have one):
   ```
   Message @BotFather on Telegram:
   /newbot
   Name: VZ Assistant (or your preferred name)
   Username: yourname_assistant_bot (must end with 'bot')

   Save the token BotFather gives you
   ```

3. **Add your config to `developer_assistant.json`**:
   ```json
   {
     "developers": {
       "YOUR_USER_ID": {
         "name": "Your Name",
         "telegram_username": "@YourUsername",
         "assistant_bot": {
           "token": "YOUR_BOT_TOKEN_FROM_BOTFATHER",
           "username": "yourbot_username",
           "bot_name": "Your Assistant Bot Name",
           "description": "Your bot description",
           "about": "Short about text"
         }
       }
     }
   }
   ```

4. **Commit and push**:
   ```bash
   git add config/developer_assistant.json
   git commit -m "Add assistant bot config for [Your Name]"
   git push
   ```

## Example Entry

```json
{
  "developers": {
    "6584698403": {
      "name": "Vzoel Fox",
      "telegram_username": "@VZLfxs",
      "assistant_bot": {
        "token": "8200379693:AAHQa9WlTNB_ynWgXBk1PDy7r0CJYzZQUtE",
        "username": "vzoelversirobot",
        "bot_name": "VZ Assistant",
        "description": "Asisten untuk VzUserbot..",
        "about": "by VzBot"
      }
    }
  }
}
```

## Priority Order

The userbot checks for bot credentials in this order:

1. **Developer Assistant Config** (`config/developer_assistant.json`)
   - Checks if your user ID is in the `developers` object
   - If found, uses your configured bot

2. **.env file** (fallback)
   - Checks `ASSISTANT_BOT_TOKEN` and `ASSISTANT_BOT_USERNAME`
   - You can override the config by setting these in `.env`

3. **Auto-create** (last resort)
   - If neither config nor .env has bot credentials
   - Automatically creates a new bot via BotFather
   - Saves to `.env` for future use

## Troubleshooting

**Bot not detected?**
- Check your user ID matches exactly (case-sensitive)
- Ensure token and username are correct
- Try adding to `.env` file as override

**Want to use different bot temporarily?**
- Set `ASSISTANT_BOT_TOKEN` and `ASSISTANT_BOT_USERNAME` in `.env`
- `.env` values override the config file

**Multiple developers using same bot?**
- Each developer should have their own bot
- Use different usernames for each bot
- Update config with unique entries for each user ID

## Security Notes

- **Bot tokens are NOT secret** (they're meant to be shared with the bot)
- However, **don't commit real .env files** (they contain SESSION_STRING)
- The config file is safe to commit to public repos
- Each developer's userbot uses their own session, but can share assistant bots

## Questions?

Contact: @VZLfxs
