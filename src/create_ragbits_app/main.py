import asyncio

from inquirer.shortcuts import list_input
import aiohttp

async def get_latest_ragbits_version():
    url = 'https://pypi.org/pypi/ragbits/json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response = await response.json()
            return response['info']['version']

async def run():
    print('Creating ragbits app')
    version = await get_latest_ragbits_version()
    print(f'Latest ragbits version is {version}')

def entrypoint():
    asyncio.run(run())