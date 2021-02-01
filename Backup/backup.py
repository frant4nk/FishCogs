from redbot.core import commands, events
from redbot.core.bot import Red
import mysql.connector

import discord


class Backup(commands.Cog):
    """Whitelist cog for Helioss"""

    def __init__(self, bot: Red) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel
        member = message.author
        cat_thumb = discord.utils.get(member.guild.emojis, name="cat_thumb")

        if channel.name == 'whitelist':
            if message.author.bot:
                return
            try:
                cnx = mysql.connector.connect(user='whitelist', password='HB*H2EmNv48wQ', host='pan.helioss.co',
                                              database="whitelist")
                sql = """INSERT INTO whitelist (user, wihtelisted) VALUES (%s, %s)"""

                whitelisted = 1
                user = message.content

                cursor = cnx.cursor()
                cursor.execute(sql, (user, whitelisted))
                cnx.commit()
                await message.add_reaction(cat_thumb)

            except mysql.connector.Error as error:
                await channel.send("Failed to insert record into MySQL table {}".format(error))

            finally:
                if cnx.is_connected():
                    cursor.close()
                    cnx.close()
