import asyncio
import threading
from keep_alive import keep_alive
import dashboard_bot
import sys
import os

# Start keep-alive server
keep_alive()
print("🌐 Web server started on port 8080")
print("🤖 Starting Dashboard Bot...")
print("📊 Multiple users can now use !setup")

# Start dashboard bot
async def run_bot():
    token = os.environ.get("DASHBOARD_BOT_TOKEN")
    if not token:
        print("❌ ERROR: DASHBOARD_BOT_TOKEN not found in Secrets!")
        print("Please add your bot token to Replit Secrets")
        return
    
    try:
        await dashboard_bot.bot.start(token)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Critical error: {e}")        print("\nShutting down...")
        await bot.stop()
    except Exception as e:
        print(f"Fatal error: {e}")
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
