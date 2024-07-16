import os
import discord
import aiohttp
from replit import db

print(db['key'])

headers = {
    'accept': 'application/json',
}

async def get_description():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://biggamesapi.io/api/clan/x70', headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Failed to get clan description: {e}")
            return None

async def get_user(id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'https://users.roblox.com/v1/users/{id}') as response:
                response.raise_for_status()
                data = await response.json()
                return data['name']
        except aiohttp.ClientError as e:
            print(f"Failed to get user {id}: {e}")
            return None

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    prefix = "."
    if message.author == client.user:
        return

    if message.content.startswith(prefix + 'members'):
        embed = discord.Embed(
            title="x70's Members",
            description="This command shows all members of x70's clan.",
            color=0x7785cc
        )
        response = await get_description()

        if response:
            members = response['data']['Members']
            for member in members:
                user_id = member['UserID']
                if str(user_id) in db['key']:
                    await message.channel.send(db['key'][str(user_id)])
                else:
                    user_name = await get_user(user_id)
                    print("retriving")
                    if user_name:
                        db['key'][str(user_id)] = user_name
                        await message.channel.send(user_name)
        await message.channel.send(embed=embed)

def get_token():
    try:
        token = os.environ["TOKEN"]
        if not token:
            raise ValueError("Token is empty. Please set your token in the environment variables.")
        return token
    except KeyError:
        raise ValueError("Token not found in environment variables. Please set your token.")

try:
    token = get_token()
    client.run(token)
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e
except ValueError as e:
    print(e)
