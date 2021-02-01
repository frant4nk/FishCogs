from redbot.core import commands, events
from redbot.core.bot import Red
import mysql.connector

import discord


class Whitelist(commands.Cog):
    """Whitelist cog for Helioss"""

    def __init__(self, bot: Red) -> None:
        self.bot = bot

    @commands.command(name="_whitelist")
    async def whitelist(self, ctx, args=None, username=None):
        if not args:
            await ctx.send("Available subcommands: info, add, del <username>")
        if (args == "add" or args == "info" or args == "del") and username is None:
            await ctx.send("Missing <username>")
        if args == "info" and username is not None:
            cat_thumb = discord.utils.get(ctx.guild.emojis, name="cat_thumb")
            cat_sad = discord.utils.get(ctx.guild.emojis, name="cat_sad")
            try:
                cnx = mysql.connector.connect(user='whitelist', password='HB*H2EmNv48wQ',
                                              host='pan.helioss.co',
                                              database="whitelist")
                sql = """SELECT * FROM whitelist WHERE USER = %s"""

                cursor = cnx.cursor()
                cursor.execute(sql, (username, ))
                record = cursor.fetchone()

                if record is None:
                    await ctx.send(f"**{username}** is **not** in the whitelist {cat_sad}")
                if record is not None:
                    await ctx.send(f"**{username}** is in the whitelist {cat_thumb}")
            except mysql.connector.Error as error:
                await ctx.send("Failed to insert record into MySQL table {}".format(error))
            finally:
                if cnx.is_connected():
                    cursor.close()
                    cnx.close()
        if args == "add" and username is not None:
            cat_thumb = discord.utils.get(ctx.guild.emojis, name="cat_thumb")
            try:
                cnx = mysql.connector.connect(user='whitelist', password='HB*H2EmNv48wQ',
                                              host='pan.helioss.co',
                                              database="whitelist")
                sql = """INSERT INTO whitelist (user, wihtelisted) VALUES (%s, %s)"""

                whitelisted = 1

                cursor = cnx.cursor()
                cursor.execute(sql, (username, whitelisted))
                cnx.commit()
                await ctx.send(f"Added **{username}** to the whitelist {cat_thumb}")
            except mysql.connector.Error as error:
                await ctx.send("Failed to insert record into MySQL table {}".format(error))
            finally:
                if cnx.is_connected():
                    cursor.close()
                    cnx.close()
        if args == "del" and username is not None:
            cat_thumb = discord.utils.get(ctx.guild.emojis, name="cat_thumb")
            try:
                cnx = mysql.connector.connect(user='whitelist', password='HB*H2EmNv48wQ',
                                              host='pan.helioss.co',
                                              database="whitelist")
                sql = """DELETE FROM whitelist WHERE user = %s"""

                cursor = cnx.cursor()
                cursor.execute(sql, (username, ))
                cnx.commit()
                await ctx.send(f"Removed **{username}** from the whitelist {cat_thumb}")
            except mysql.connector.Error as error:
                await ctx.send("Failed to insert record into MySQL table {}".format(error))
            finally:
                if cnx.is_connected():
                    cursor.close()
                    cnx.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel
        member = message.author
        if channel.name == 'test':
            if message.author.bot:
                return
            for role in message.author.roles:
                if role.id == 736828584987197470: # Cambiar por la de staff despues
                    return

            hap = discord.utils.get(member.guild.emojis, name="Hap")
            sad = discord.utils.get(member.guild.emojis, name="SadQ")

            await message.add_reaction(hap)
            await message.add_reaction(sad)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            channel = reaction.message.channel

            hap = discord.utils.get(user.guild.emojis, name="Hap")
            sad = discord.utils.get(user.guild.emojis, name="SadQ")
            updoot = discord.utils.get(reaction.message.guild.emojis, name="Updoot")
            downdoot = discord.utils.get(reaction.message.guild.emojis, name="Downdoot")
            cat_thumb = discord.utils.get(reaction.message.guild.emojis, name="cat_thumb")

            # Roles
            minecraft = discord.utils.get(reaction.message.guild.roles, name="Minecraft")
            applicant = discord.utils.get(reaction.message.guild.roles, name="Applicant")

            async for _user in reaction.users():
                for role in _user.roles:
                    if role.id == 736828584987197470:
                        if reaction.emoji == hap:
                            try:
                                username = reaction.message.content.splitlines()[1].split(':')
                                user = username[1].strip()
                            except:
                                await channel.send("```Could not read the username from the application\n"
                                                   "Please add it manually```")
                            try:
                                cnx = mysql.connector.connect(user='whitelist', password='HB*H2EmNv48wQ',
                                                              host='pan.helioss.co',
                                                              database="whitelist")
                                sql = """INSERT INTO whitelist (user, wihtelisted) VALUES (%s, %s)"""

                                whitelisted = 1

                                cursor = cnx.cursor()
                                cursor.execute(sql, (user, whitelisted))
                                cnx.commit()
                                await reaction.message.clear_reaction(hap)
                                await reaction.message.clear_reaction(sad)
                                await reaction.message.add_reaction(cat_thumb)
                            except mysql.connector.Error as error:
                                await channel.send("Failed to insert record into MySQL table {}".format(error))
                            finally:
                                if cnx.is_connected():
                                    cursor.close()
                                    cnx.close()
                            await reaction.message.author.add_roles(minecraft)
                            await reaction.message.author.remove_roles(applicant)

                        if reaction.emoji == sad:
                            await reaction.message.add_reaction(updoot)
                            await reaction.message.add_reaction(downdoot)

                        if reaction.emoji == downdoot:
                            await reaction.message.clear_reaction(downdoot)
                            await reaction.message.clear_reaction(updoot)
                            await reaction.message.remove_reaction(sad, user)

                        if reaction.emoji == updoot:
                            await reaction.message.delete()
                            await reaction.message.author.kick(reason="You were not accepted!")