import discord
from discord.ext import commands
import json
import asyncio

class ControlBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
    async def setup_hook(self):
        await self.add_cog(ControlCommands(self))
        print(f"Control Bot logged in as {self.user}")

class ControlCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "config.json"
        self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "user_tokens": [],
                "channel_ids": [],
                "time_interval": 3600,
                "ad_messages": [],
                "control_bot_token": "",
                "owner_id": ""
            }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author.id != self.bot.user.id:
            if message.author.id == int(self.config.get("owner_id", 0)):
                await self.handle_dm_command(message)
    
    async def handle_dm_command(self, message):
        content = message.content.lower()
        
        if content.startswith("add token "):
            token = message.content[10:].strip()
            if token not in self.config["user_tokens"]:
                self.config["user_tokens"].append(token)
                self.save_config()
                await message.channel.send("✅ Token added successfully!")
            else:
                await message.channel.send("⚠️ Token already exists!")
        
        elif content.startswith("remove token "):
            token = message.content[13:].strip()
            if token in self.config["user_tokens"]:
                self.config["user_tokens"].remove(token)
                self.save_config()
                await message.channel.send("✅ Token removed successfully!")
            else:
                await message.channel.send("❌ Token not found!")
        
        elif content.startswith("add channel "):
            try:
                channel_id = int(message.content[12:].strip())
                if channel_id not in self.config["channel_ids"]:
                    self.config["channel_ids"].append(channel_id)
                    self.save_config()
                    await message.channel.send("✅ Channel ID added successfully!")
                else:
                    await message.channel.send("⚠️ Channel ID already exists!")
            except:
                await message.channel.send("❌ Invalid Channel ID!")
        
        elif content.startswith("remove channel "):
            try:
                channel_id = int(message.content[15:].strip())
                if channel_id in self.config["channel_ids"]:
                    self.config["channel_ids"].remove(channel_id)
                    self.save_config()
                    await message.channel.send("✅ Channel ID removed successfully!")
                else:
                    await message.channel.send("❌ Channel ID not found!")
            except:
                await message.channel.send("❌ Invalid Channel ID!")
        
        elif content.startswith("interval "):
            try:
                seconds = int(message.content[9:].strip())
                if seconds >= 60:
                    self.config["time_interval"] = seconds
                    self.save_config()
                    await message.channel.send(f"✅ Interval set to {seconds} seconds!")
                else:
                    await message.channel.send("❌ Interval must be at least 60 seconds!")
            except:
                await message.channel.send("❌ Invalid interval!")
        
        elif content.startswith("add message "):
            ad_text = message.content[12:].strip()
            if ad_text:
                self.config["ad_messages"].append(ad_text)
                self.save_config()
                await message.channel.send("✅ Message added successfully!")
            else:
                await message.channel.send("❌ Message cannot be empty!")
        
        elif content.startswith("remove message "):
            try:
                index = int(message.content[15:].strip()) - 1
                if 0 <= index < len(self.config["ad_messages"]):
                    removed = self.config["ad_messages"].pop(index)
                    self.save_config()
                    await message.channel.send(f"✅ Message removed: `{removed[:50]}...`")
                else:
                    await message.channel.send("❌ Invalid message index!")
            except:
                await message.channel.send("❌ Invalid message index!")
        
        elif content == "list tokens":
            if self.config["user_tokens"]:
                tokens_list = "\n".join([f"{i+1}. `{t[:20]}...`" for i, t in enumerate(self.config["user_tokens"])])
                await message.channel.send(f"**Active Tokens:**\n{tokens_list}")
            else:
                await message.channel.send("No tokens added yet!")
        
        elif content == "list channels":
            if self.config["channel_ids"]:
                channels_list = "\n".join([f"{i+1}. `{cid}`" for i, cid in enumerate(self.config["channel_ids"])])
                await message.channel.send(f"**Target Channels:**\n{channels_list}")
            else:
                await message.channel.send("No channels added yet!")
        
        elif content == "list messages":
            if self.config["ad_messages"]:
                messages_list = "\n".join([f"{i+1}. `{msg[:50]}...`" for i, msg in enumerate(self.config["ad_messages"])])
                await message.channel.send(f"**Ad Messages:**\n{messages_list}")
            else:
                await message.channel.send("No messages added yet!")
        
        elif content == "status":
            status_msg = f"""
**Status Overview:**
• Tokens: {len(self.config['user_tokens'])}
• Channels: {len(self.config['channel_ids'])}
• Messages: {len(self.config['ad_messages'])}
• Interval: {self.config['time_interval']} seconds
• Next send in: {(self.config['time_interval'] // 60)} minutes
            """
            await message.channel.send(status_msg)
        
        elif content == "help":
            help_msg = """
**Available Commands (DM only):**
`add token YOUR_TOKEN` - Add a user token
`remove token YOUR_TOKEN` - Remove a user token
`add channel CHANNEL_ID` - Add target channel
`remove channel CHANNEL_ID` - Remove channel
`interval SECONDS` - Set sending interval (minimum 60)
`add message YOUR_TEXT` - Add ad message
`remove message INDEX` - Remove message by index
`list tokens` - Show all tokens
`list channels` - Show all channels
`list messages` - Show all messages
`status` - Show current status
`help` - Show this help
            """
            await message.channel.send(help_msg)

async def main():
    with open("config.json", 'r') as f:
        config = json.load(f)
    
    bot = ControlBot()
    await bot.start(config["control_bot_token"])

if __name__ == "__main__":
    asyncio.run(main())
