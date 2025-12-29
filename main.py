import discord
import asyncio
import json
import random
from datetime import datetime
import aiohttp

class AutoAdBot:
    def __init__(self):
        self.config_file = "config.json"
        self.clients = []
        self.running = True
        self.load_config()
    
    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
    
    async def create_client(self, token):
        """Create a client for each token"""
        intents = discord.Intents.default()
        intents.message_content = True
        
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            print(f"Logged in as {client.user} (Token: {token[:20]}...)")
        
        @client.event
        async def on_message(message):
            # Ignore messages from self
            if message.author == client.user:
                return
            
            # Handle DMs to this bot
            if isinstance(message.channel, discord.DMChannel):
                await self.handle_dm(message, client)
        
        self.clients.append({
            "client": client,
            "token": token
        })
        
        return client
    
    async def handle_dm(self, message, client):
        """Handle DMs sent to the ad bot"""
        response = f"Hello! I'm an automated bot. Your message: {message.content[:100]}"
        await message.channel.send(response)
    
    async def send_ads(self):
        """Send ads to all configured channels"""
        while self.running:
            try:
                self.load_config()  # Reload config for updates
                
                if not self.config["channel_ids"] or not self.config["ad_messages"]:
                    print("No channels or messages configured. Skipping...")
                    await asyncio.sleep(self.config["time_interval"])
                    continue
                
                for client_data in self.clients:
                    client = client_data["client"]
                    if not client.is_ready():
                        continue
                    
                    for channel_id in self.config["channel_ids"]:
                        try:
                            channel = client.get_channel(channel_id)
                            if channel:
                                message = random.choice(self.config["ad_messages"])
                                await channel.send(message)
                                print(f"[{datetime.now()}] Sent ad to channel {channel_id}: {message[:50]}...")
                                
                                # Small delay between messages
                                await asyncio.sleep(5)
                        except Exception as e:
                            print(f"Error sending to channel {channel_id}: {e}")
                
                print(f"[{datetime.now()}] Cycle completed. Waiting {self.config['time_interval']} seconds...")
                await asyncio.sleep(self.config["time_interval"])
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(60)
    
    async def start(self):
        """Start all bot instances"""
        print("Starting Auto-Ad Bot...")
        
        # Create clients for each token
        for token in self.config["user_tokens"]:
            if token.strip():
                client = await self.create_client(token)
                asyncio.create_task(client.start(token, bot=False))
                await asyncio.sleep(5)  # Delay between starting clients
        
        # Start ad sending loop
        await self.send_ads()
    
    async def stop(self):
        """Stop all bot instances"""
        self.running = False
        for client_data in self.clients:
            await client_data["client"].close()

async def main():
    bot = AutoAdBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        await bot.stop()
    except Exception as e:
        print(f"Fatal error: {e}")
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
