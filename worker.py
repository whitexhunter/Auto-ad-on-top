import discord
import asyncio
import json
import random
import sys
import os
from datetime import datetime

print(f"🤖 Worker starting...")

class WorkerBot:
    def __init__(self, user_id):
        self.user_id = user_id
        self.config_file = f"user_{user_id}.json"
        self.load_config()
        self.clients = []
        self.running = True
        print(f"[User {user_id}] Worker initialized")
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            print(f"[User {self.user_id}] Config loaded: {len(self.config.get('tokens', []))} tokens")
        except Exception as e:
            print(f"[User {self.user_id}] Config error: {e}")
            self.config = {"tokens": [], "channels": [], "messages": [], "interval": 300}
    
    def save_stats(self):
        stats_file = f"user_{self.user_id}_stats.json"
        stats = {
            "last_active": datetime.now().isoformat(),
            "config": {
                "tokens_count": len(self.config.get("tokens", [])),
                "channels_count": len(self.config.get("channels", [])),
                "messages_count": len(self.config.get("messages", [])),
                "interval": self.config.get("interval", 300)
            }
        }
        try:
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except:
            pass
    
    async def create_client(self, token, index):
        """Create and login Discord client"""
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            print(f"[User {self.user_id}] Client {index+1} ready: {client.user}")
        
        @client.event
        async def on_error(event, *args, **kwargs):
            print(f"[User {self.user_id}] Client {index+1} error: {event}")
        
        return client
    
    async def run(self):
        """Main worker loop"""
        print(f"[User {self.user_id}] Starting main loop")
        
        # Start all clients
        for i, token in enumerate(self.config.get("tokens", [])):
            if token and token.strip():
                try:
                    client = await self.create_client(token, i)
                    self.clients.append(client)
                    # Start client in background
                    asyncio.create_task(client.start(token, bot=False))
                    print(f"[User {self.user_id}] Starting client {i+1}")
                    await asyncio.sleep(3)  # Delay between logins
                except Exception as e:
                    print(f"[User {self.user_id}] Failed client {i+1}: {e}")
        
        # Wait for clients to connect
        print(f"[User {self.user_id}] Waiting for clients to connect...")
        await asyncio.sleep(10)
        
        # Count ready clients
        ready_clients = [c for c in self.clients if c.is_ready()]
        print(f"[User {self.user_id}] {len(ready_clients)}/{len(self.clients)} clients ready")
        
        if not ready_clients:
            print(f"[User {self.user_id}] No clients ready, exiting")
            return
        
        # Main sending loop
        cycle = 0
        while self.running:
            try:
                cycle += 1
                print(f"[User {self.user_id}] Cycle {cycle} starting")
                
                # Reload config for updates
                self.load_config()
                
                tokens = self.config.get("tokens", [])
                channels = self.config.get("channels", [])
                messages = self.config.get("messages", [])
                interval = self.config.get("interval", 300)
                
                if not channels or not messages:
                    print(f"[User {self.user_id}] Waiting for config...")
                    await asyncio.sleep(30)
                    continue
                
                # Send messages
                for client in ready_clients:
                    if not client.is_ready():
                        continue
                    
                    for channel_id in channels:
                        try:
                            channel = client.get_channel(channel_id)
                            if channel:
                                # Select random message
                                if messages:
                                    msg = random.choice(messages)
                                    await channel.send(msg)
                                    print(f"[User {self.user_id}] Sent to {channel_id}")
                                    
                                    # Save stats
                                    self.save_stats()
                                    
                                    # Random delay between messages
                                    delay = random.uniform(5, 15)
                                    await asyncio.sleep(delay)
                        except discord.errors.HTTPException as e:
                            if e.status == 429:  # Rate limited
                                print(f"[User {self.user_id}] Rate limited, waiting...")
                                await asyncio.sleep(60)
                            else:
                                print(f"[User {self.user_id}] Send error: {e}")
                        except Exception as e:
                            print(f"[User {self.user_id}] Error: {e}")
                
                print(f"[User {self.user_id}] Cycle {cycle} complete, waiting {interval}s")
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                print(f"[User {self.user_id}] Interrupted")
                break
            except Exception as e:
                print(f"[User {self.user_id}] Loop error: {e}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Clean shutdown"""
        self.running = False
        print(f"[User {self.user_id}] Shutting down...")
        for client in self.clients:
            try:
                await client.close()
            except:
                pass

async def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python worker.py <user_id>")
        return
    
    user_id = sys.argv[1]
    print(f"🚀 Starting worker for user {user_id}")
    
    worker = WorkerBot(user_id)
    try:
        await worker.run()
    except KeyboardInterrupt:
        print(f"\n🛑 Worker {user_id} stopping...")
    except Exception as e:
        print(f"💥 Worker {user_id} crashed: {e}")
    finally:
        await worker.stop()

if __name__ == "__main__":
    asyncio.run(main())
