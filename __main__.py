import asyncio
import datetime
import difflib
import pathlib
import zoneinfo
from typing import Optional

import discord
from discord import app_commands as slash


AVAILABLE_TIMEZONES = {
    name.replace('_', ' '): zone
    for zone in zoneinfo.available_timezones()
    for namespace, sep, name in [zone.rpartition('/')]
}

client = discord.Client(application_id=408985804577439775)
tree = slash.CommandTree(client)


def time_command(time_format, **kwargs):

    async def reply(interaction, timezone: Optional[str] = None):
        if timezone not in AVAILABLE_TIMEZONES and timezone is not None:
            return await interaction.response.send_message(f'{timezone} is not a valid timezone. Please pick one from the list.', ephemeral=True)

        timezone = zoneinfo.ZoneInfo('Europe/Helsinki') if timezone is None else zoneinfo.ZoneInfo(timezone)
        now = datetime.datetime.now(tz=timezone)

        await interaction.response.send_message(format(now, time_format))

    return tree.command(**kwargs)(reply)



now = time_command(name='now', description='Shows the current time', time_format='%H:%M (%Z)')
longnow = time_command(name='longnow', description='Shows the current date and time', time_format='%A %d %B %Y %H:%M:%S (%Z)')


@now.autocomplete('timezone')
@longnow.autocomplete('timezone')
async def get_timezones(interaction, current, namespace):
    options = set(AVAILABLE_TIMEZONES)

    # Perform a fuzzy match for what the user might want
    close_match = difflib.get_close_matches(
        word=current,
        possibilities=options,
        cutoff=0.6,
        n=25,
    )


    # then do the classic autocomplete thing of simply checking that the user starts with the correct letters
    starts_with = [
        zone for zone in options.difference(close_match)
        if zone.lower().startswith(current.lower())
    ]

    # we want to limit our maximum to 25 responses and value close matches more
    cutoff_point = 25 - len(close_match)
    view_order = starts_with[:cutoff_point] + close_match

    return [
        slash.Choice(name=name, value=AVAILABLE_TIMEZONES[name])
        for name in view_order
    ]


async def main():
    token = pathlib.Path('token.txt').read_text()

    # aaaaaaAAAAAAAAAAAAAAAAAAAAAAAA
    await client.login(token)
    await tree.sync()
    await client.connect()



if __name__ == '__main__':
    # lol aiohttp
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
