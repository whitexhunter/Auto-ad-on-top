import discord
from discord.ext import commands, tasks
import json
import os
import asyncio
import subprocess
import sys
from datetime import datetime

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Embed colors
COLORS = {
    "success": 0x00ff00,
    "error": 0xff0000,
    "info": 0x0099ff,
    "warning": 0xffaa00
}

# Simple file-based database
class UserDatabase:
    def __init__(self):
        self.db_file = "users_data.json"
        self.load()
    
    def load(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
    
    def save(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def create_user(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "status": "inactive",
                "tokens": [],
                "channels": [],
                "messages": ["Welcome to our server!", "Check this out!"],
                "interval": 300,
                "is_running": False,
                "worker_pid": None,
                "stats": {"messages_sent": 0, "errors": 0, "last_sent": None}
            }
            self.save()
            return True
        return False
    
    def get_user(self, user_id):
        return self.data.get(str(user_id))
    
    def update_user(self, user_id, updates):
        user_id = str(user_id)
        if user_id in self.data:
            self.data[user_id].update(updates)
            self.save()
            return True
        return False
    
    def get_all_users(self):
        return self.data

db = UserDatabase()

# Interactive Components
class TokenModal(discord.ui.Modal, title="Add Discord Token"):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
    
    token = discord.ui.TextInput(
        label="Discord Token",
        placeholder="Paste your Discord account token here...",
        style=discord.TextStyle.paragraph,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        user_data = db.get_user(self.user_id)
        tokens = user_data.get("tokens", [])
        if self.token.value not in tokens:
            tokens.append(self.token.value)
            db.update_user(self.user_id, {"tokens": tokens})
            await interaction.response.send_message(
                f"✅ Token added! Total: {len(tokens)}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("⚠️ Token already exists!", ephemeral=True)

class ChannelModal(discord.ui.Modal, title="Add Target Channel"):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
    
    channel_id = discord.ui.TextInput(
        label="Channel ID",
        placeholder="112233445566778899",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel_id.value)
            user_data = db.get_user(self.user_id)
            channels = user_data.get("channels", [])
            
            if channel_id not in channels:
                channels.append(channel_id)
                db.update_user(self.user_id, {"channels": channels})
                await interaction.response.send_message(
                    f"✅ Channel added! Total: {len(channels)}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message("⚠️ Channel already exists!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid Channel ID!", ephemeral=True)

class MessageModal(discord.ui.Modal, title="Add Advertisement Message"):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
    
    message = discord.ui.TextInput(
        label="Ad Message",
        placeholder="Enter your advertisement message here...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        user_data = db.get_user(self.user_id)
        messages = user_data.get("messages", [])
        messages.append(self.message.value)
        db.update_user(self.user_id, {"messages": messages})
        await interaction.response.send_message(
            f"✅ Message added! Total: {len(messages)}",
            ephemeral=True
        )

class SettingsModal(discord.ui.Modal, title="Bot Settings"):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
    
    interval = discord.ui.TextInput(
        label="Interval (seconds)",
        placeholder="300 (5 minutes)",
        default="300",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            interval = int(self.interval.value)
            if interval < 60:
                await interaction.response.send_message("❌ Minimum 60 seconds!", ephemeral=True)
                return
            
            db.update_user(self.user_id, {"interval": interval})
            await interaction.response.send_message(
                f"✅ Interval set to {interval} seconds",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message("❌ Invalid number!", ephemeral=True)

class SetupView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
    
    @discord.ui.button(label="🔑 Add Token", style=discord.ButtonStyle.primary, emoji="🔑")
    async def add_token(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TokenModal(self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔗 Add Channel", style=discord.ButtonStyle.primary, emoji="🔗")
    async def add_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChannelModal(self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="💬 Add Message", style=discord.ButtonStyle.primary, emoji="💬")
    async def add_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MessageModal(self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⚙️ Settings", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = SettingsModal(self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🚀 Start Bot", style=discord.ButtonStyle.success, emoji="🚀")
    async def start_bot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        user_data = db.get_user(self.user_id)
        if not user_data["tokens"]:
            await interaction.followup.send("❌ Add at least one token first!", ephemeral=True)
            return
        
        # Start worker
        success = await start_worker(self.user_id)
        if success:
            db.update_user(self.user_id, {"is_running": True, "status": "active"})
            
            embed = discord.Embed(
                title="✅ Bot Started Successfully!",
                description="Your auto-ad bot is now running in the background.",
                color=COLORS["success"]
            )
            embed.add_field(name="Tokens", value=str(len(user_data["tokens"])), inline=True)
            embed.add_field(name="Channels", value=str(len(user_data["channels"])), inline=True)
            embed.add_field(name="Interval", value=f"{user_data['interval']}s", inline=True)
            embed.set_footer(text="Use !dashboard to monitor your bot")
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Failed to start bot!", ephemeral=True)
    
    @discord.ui.button(label="📊 Dashboard", style=discord.ButtonStyle.secondary, emoji="📊")
    async def dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await show_dashboard(interaction, self.user_id)

async def show_dashboard(interaction, user_id):
    user_data = db.get_user(user_id)
    
    embed = discord.Embed(
        title=f"📊 Dashboard - {interaction.user.name}",
        color=COLORS["info"]
    )
    
    # Status
    status_emoji = "🟢" if user_data["is_running"] else "🔴"
    embed.add_field(name="Status", value=f"{status_emoji} {user_data['status'].upper()}", inline=True)
    
    # Stats
    embed.add_field(name="Tokens", value=str(len(user_data["tokens"])), inline=True)
    embed.add_field(name="Channels", value=str(len(user_data["channels"])), inline=True)
    embed.add_field(name="Messages", value=str(len(user_data["messages"])), inline=True)
    embed.add_field(name="Interval", value=f"{user_data['interval']}s", inline=True)
    embed.add_field(name="Sent", value=str(user_data["stats"]["messages_sent"]), inline=True)
    
    # Preview
    if user_data["messages"]:
        preview = user_data["messages"][0][:100] + "..." if len(user_data["messages"][0]) > 100 else user_data["messages"][0]
        embed.add_field(name="Message Preview", value=preview, inline=False)
    
    # Control buttons
    view = ControlView(user_id)
    await interaction.followup.send(embed=embed, view=view)

class ControlView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
    
    @discord.ui.button(label="▶️ Start", style=discord.ButtonStyle.success)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        success = await start_worker(self.user_id)
        if success:
            db.update_user(self.user_id, {"is_running": True, "status": "active"})
            await interaction.response.send_message("✅ Bot started!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Failed to start!", ephemeral=True)
    
    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        success = await stop_worker(self.user_id)
        if success:
            db.update_user(self.user_id, {"is_running": False, "status": "paused"})
            await interaction.response.send_message("⏸️ Bot paused!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Bot not running!", ephemeral=True)
    
    @discord.ui.button(label="🛑 Stop", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        success = await stop_worker(self.user_id)
        if success:
            db.update_user(self.user_id, {"is_running": False, "status": "stopped"})
            await interaction.response.send_message("🛑 Bot stopped!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Bot not running!", ephemeral=True)
    
    @discord.ui.button(label="🗑️ Clear Data", style=discord.ButtonStyle.danger)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        db.update_user(self.user_id, {
            "tokens": [],
            "channels": [],
            "messages": ["Welcome!"],
            "is_running": False,
            "status": "reset"
        })
        await interaction.response.send_message("🗑️ All data cleared!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Dashboard Bot logged in as {bot.user}")
    print(f"📊 Total users: {len(db.get_all_users())}")
    check_workers.start()

@bot.command()
async def setup(ctx):
    """Start your auto-ad bot setup"""
    # Create user profile
    db.create_user(ctx.author.id)
    
    embed = discord.Embed(
        title="🤖 Auto-Ad Bot Setup Wizard",
        description="Welcome! Follow these steps to set up your auto-ad bot:",
        color=COLORS["info"]
    )
    
    steps = """
**1️⃣ Add Discord Tokens**
Click "Add Token" to add your Discord account tokens

**2️⃣ Add Target Channels**  
Click "Add Channel" to add channel IDs where ads will be sent

**3️⃣ Create Ad Messages**
Click "Add Message" to write your advertisement texts

**4️⃣ Configure Settings**
Click "Settings" to set time interval (recommended: 300+ seconds)

**5️⃣ Start Your Bot**
Click "Start Bot" to begin automated advertising!
"""
    
    embed.add_field(name="Setup Steps", value=steps, inline=False)
    embed.set_footer(text="Your data is stored privately and securely")
    
    view = SetupView(ctx.author.id)
    await ctx.send(embed=embed, view=view)

@bot.command()
async def dashboard(ctx):
    """View your bot dashboard"""
    if not db.get_user(ctx.author.id):
        await ctx.send("❌ Please use `!setup` first!")
        return
    
    await show_dashboard(ctx, ctx.author.id)

@bot.command()
async def help(ctx):
    """Show help menu"""
    embed = discord.Embed(
        title="🤖 Auto-Ad Bot Help Center",
        description="Complete guide to using the auto-ad system",
        color=COLORS["info"]
    )
    
    commands = """
**📋 MAIN COMMANDS**
`!setup` - Start setup wizard
`!dashboard` - View your control panel
`!help` - Show this help menu

**🎯 HOW TO USE**
1. Use `!setup` to begin
2. Add your Discord tokens
3. Add target channel IDs
4. Write your ad messages
5. Start the bot!

**⚠️ IMPORTANT NOTES**
• Use reasonable intervals (5+ minutes)
• Keep your tokens secure
• Monitor your bot's performance
• Respect Discord's guidelines
"""
    
    embed.add_field(name="Commands & Usage", value=commands, inline=False)
    embed.set_footer(text="Support: Contact server admin")
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def admin(ctx):
    """Admin panel (Owner only)"""
    users = db.get_all_users()
    
    embed = discord.Embed(
        title="👑 Admin Dashboard",
        color=COLORS["info"]
    )
    
    total = len(users)
    active = sum(1 for u in users.values() if u["is_running"])
    total_msgs = sum(u["stats"]["messages_sent"] for u in users.values())
    
    embed.add_field(name="Total Users", value=str(total), inline=True)
    embed.add_field(name="Active Bots", value=str(active), inline=True)
    embed.add_field(name="Total Messages", value=str(total_msgs), inline=True)
    
    # Recent activity
    recent = list(users.items())[-3:] if len(users) > 3 else list(users.items())
    activity = []
    for user_id, data in recent:
        user = await bot.fetch_user(int(user_id))
        name = user.name if user else f"User {user_id}"
        activity.append(f"**{name}**: {data['status']} ({data['stats']['messages_sent']} msgs)")
    
    if activity:
        embed.add_field(name="Recent Activity", value="\n".join(activity), inline=False)
    
    await ctx.send(embed=embed)

async def start_worker(user_id):
    """Start a worker process for user"""
    try:
        # Save user config
        user_data = db.get_user(user_id)
        config_file = f"user_{user_id}.json"
        
        with open(config_file, 'w') as f:
            json.dump({
                "tokens": user_data["tokens"],
                "channels": user_data["channels"],
                "messages": user_data["messages"],
                "interval": user_data["interval"],
                "user_id": str(user_id)
            }, f)
        
        # Start worker
        process = subprocess.Popen([
            sys.executable, "worker.py", str(user_id)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        db.update_user(user_id, {"worker_pid": process.pid})
        return True
    except Exception as e:
        print(f"Error starting worker {user_id}: {e}")
        return False

async def stop_worker(user_id):
    """Stop user's worker"""
    user_data = db.get_user(user_id)
    if user_data and user_data.get("worker_pid"):
        try:
            import psutil
            process = psutil.Process(user_data["worker_pid"])
            process.terminate()
            db.update_user(user_id, {"worker_pid": None})
            return True
        except:
            pass
    return False

@tasks.loop(seconds=60)
async def check_workers():
    """Monitor worker processes"""
    try:
        import psutil
        for user_id, data in db.get_all_users().items():
            if data.get("worker_pid"):
                try:
                    process = psutil.Process(data["worker_pid"])
                    if not process.is_running():
                        db.update_user(user_id, {"is_running": False, "worker_pid": None, "status": "crashed"})
                except psutil.NoSuchProcess:
                    db.update_user(user_id, {"is_running": False, "worker_pid": None, "status": "crashed"})
    except ImportError:
        pass  # psutil not installed
    except Exception as e:
        print(f"Monitor error: {e}")
