import asyncio
from roblox import Client
client = Client()

async def main():
    user = await client.get_user_by_username("app091111")
    print("Name:", user.name)
    print("Display Name:", user.display_name)
    print("Description:", user.description)

    

asyncio.get_event_loop().run_until_complete(main())
