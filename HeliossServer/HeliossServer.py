from redbot.core import commands, Config
from redbot.core.bot import Red

from typing import Literal
import discord, requests, json
#from mcipc.query import Client
from mcstatus import MinecraftServer

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class HeliossServer(commands.Cog):

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(self,
                                      identifier=6546491998687,
                                      force_registration=True)
        default_guild = \
            {
                "uuid": [],
                "name": [],
                "version": [],
                "dns": [],
                "ip": [],
                "port": [],
                "channelID": [],
                "short": []
            }
        self.config.register_guild(**default_guild)

    @staticmethod
    def printBytes(_B, _from, _to):
        defs = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3, 'TB': 1024 ** 4}
        b = float(_B) * defs[_from]

        return '{:,.2f} {}'.format(b / defs[_to], _to)

    @staticmethod
    def getIndex(lst, element):
        result = []
        offset = -1
        while True:
            try:
                offset = lst.index(element, offset + 1)
            except ValueError:
                return result
            result.append(offset)

    @staticmethod
    def getServerInfo(uuid) -> object:
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Authorization": "Bearer "}
        r = requests.get("https://pan.helioss.co/api/client/servers/" + uuid + "/resources", headers=headers)
        disk_bytes = int(r.json()["attributes"]["resources"]["disk_bytes"])
        memory_bytes = int(r.json()["attributes"]["resources"]["memory_bytes"])
        current_state = r.json()["attributes"]["current_state"]

        l = requests.get("https://pan.helioss.co/api/client/servers/" + uuid, headers=headers)
        disk_limit = l.json()["attributes"]["limits"]["disk"]  # Esta en megas
        memory_limit = l.json()["attributes"]["limits"]["memory"]  # Esta en megas

        return current_state, disk_bytes, disk_limit, memory_bytes, memory_limit

    @commands.command()
    @commands.has_role(736828584987197470)
    async def add_server(self, ctx, uuid: str, name: str, version: str,
                         dns: str, ip: str, port: int, channel_id: int,
                         short_name: str):
        """Add node to net"""
        try:
            guild_group = self.config.guild(ctx.guild)

            async with guild_group.uuid() as _uuid:
                _uuid.append(uuid)
            async with guild_group.name() as _name:
                _name.append(name)
            async with guild_group.version() as _version:
                _version.append(version)
            async with guild_group.dns() as _dns:
                _dns.append(dns)
            async with guild_group.ip() as _ip:
                _ip.append(ip)
            async with guild_group.port() as _port:
                _port.append(port)
            async with guild_group.channelID() as _channel_id:
                _channel_id.append(channel_id)
            async with guild_group.short() as _short:
                _short.append(short_name)

            emoji = discord.utils.get(ctx.guild.emojis, name="Finished")
            await ctx.send("{} {}".format(name, emoji))
        except:
            cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
            await ctx.send(f"Something went wrong, please ping Fran or Sardine {cat_ban}")

    @commands.command()
    @commands.has_role(736828584987197470)
    async def delete(self, ctx, id: int):
        """Delete node by ID"""
        try:
            guild_group = self.config.guild(ctx.guild)

            async with guild_group.uuid() as _uuid:
                _uuid.pop(id)
            async with guild_group.name() as _name:
                _name.pop(id)
            async with guild_group.version() as _version:
                _version.pop(id)
            async with guild_group.dns() as _dns:
                _dns.pop(id)
            async with guild_group.ip() as _ip:
                _ip.pop(id)
            async with guild_group.port() as _port:
                _port.pop(id)
            async with guild_group.channelID() as _channel_id:
                _channel_id.pop(id)
            async with guild_group.short() as _short:
                _short.pop(id)
            await ctx.send("Node successfully removed!")
        except:
            cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
            await ctx.send(f"Something went wrong, please ping Fran or Sardine {cat_ban}")

    @commands.command()
    @commands.has_role(736828584987197470)
    async def net(self, ctx):
        """List all the nodes and info"""
        # try:
        uuid = await self.config.guild(ctx.guild).uuid()
        name = await self.config.guild(ctx.guild).name()
        version = await self.config.guild(ctx.guild).version()
        dns = await self.config.guild(ctx.guild).dns()
        ip = await self.config.guild(ctx.guild).ip()
        port = await self.config.guild(ctx.guild).port()
        channel_id = await self.config.guild(ctx.guild).channelID()
        short = await self.config.guild(ctx.guild).short()

        helioss = discord.utils.get(ctx.guild.emojis, name="Helioss")
        run = discord.utils.get(ctx.guild.emojis, name="Run")
        importantcustom = discord.utils.get(ctx.guild.emojis, name="importantcustom")
        cat_dab = discord.utils.get(ctx.guild.emojis, name="cat_dab")

        for i in range(len(uuid)):
            current_state, disk_bytes, disk_limit, memory_bytes, memory_limit = self.getServerInfo(uuid[i])

            if current_state == "running":
                color = 0x2ef406
                s = "Running "
                status = run

                server = MinecraftServer(ip[i], int(port[i]))
                server_status = server.status()
                num_players = str(server_status.players.online)
                max_players = str(server_status.players.max)
            if current_state == "offline":
                color = 0xf40606
                s = "Offline "
                status = importantcustom
                num_players = ""
                max_players = ""
            if current_state == "starting":
                color = 0xff9500
                s = "Starting "
                status = cat_dab
                num_players = ""
                max_players = ""

            embed = discord.Embed(title=f"{helioss} {str(name[i])} {helioss}", color=color)
            embed.add_field(name="UUID: ", value=str(uuid[i]), inline=False)
            embed.add_field(name="Name: ", value=str(name[i]), inline=False)
            embed.add_field(name="Version: ", value=str(version[i]), inline=True)
            embed.add_field(name="DNS: ", value=str(dns[i]), inline=True)
            embed.add_field(name="IP: ", value=str(ip[i]), inline=True)
            embed.add_field(name="Port: ", value=str(port[i]), inline=True)
            embed.add_field(name="ID: ", value=str(i), inline=True)
            embed.add_field(name="Channel ID: ", value=str(channel_id[i]), inline=True)

            embed.add_field(name="Online players: ",
                            value=num_players + " / " + max_players, inline=True)
            embed.add_field(name="Status: ", value=f"{s}{status}", inline=True)
            embed.add_field(name="Short name: ", value=str(short[i]), inline=True)
            embed.add_field(name="Disk Space: ",
                            value=self.printBytes(disk_bytes, "B", "GB") + " of " + self.printBytes(disk_limit,
                                                                                                    "MB",
                                                                                                    "GB"),
                            inline=False)
            embed.add_field(name="RAM: ",
                            value=self.printBytes(memory_bytes, "B", "GB") + " of " + self.printBytes(memory_limit,
                                                                                                      "MB", "GB"),
                            inline=False)
            await ctx.send(embed=embed)
        # except:
        #    cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
        #    await ctx.send(f"Something went wrong, please ping Fran or Sardine {cat_ban}")

    @commands.command()
    async def list(self, ctx):
        """List the amount of online players on a server"""
        #try:
        uuid = await self.config.guild(ctx.guild).uuid()
        channel_id = await self.config.guild(ctx.guild).channelID()
        ip = await self.config.guild(ctx.guild).ip()
        port = await self.config.guild(ctx.guild).port()
        name = await self.config.guild(ctx.guild).name()

        try:
            _index = self.getIndex(channel_id, ctx.channel.id)
        except:
            cat_sad = discord.utils.get(ctx.guild.emojis, name="cat_sad")
            await ctx.send(f"There is no server asociated to this channel {cat_sad}")
            cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
            await ctx.send(f"If the server exists, please ping Fran or Sardine {cat_ban}")
            return

        helioss = discord.utils.get(ctx.guild.emojis, name="Helioss")
        wuv = discord.utils.get(ctx.guild.emojis, name="wuv")
        _name = f"Server is offline or starting, please wait {wuv}"

        for index in _index:
            current_state, disk_bytes, disk_limit, memory_bytes, memory_limit = self.getServerInfo(uuid[index])
            players = " "
            if current_state == "running":
                server = MinecraftServer(ip[index], int(port[index]))
                server_stats = server.status()
                query = server.query()

                players = ", ".join(query.players.names)

                if int(server_stats.players.online) < 0 or int(server_stats.players.online) > 1:
                    _name = "There are " + str(server_stats.players.online) + " players online!"
                if int(server_stats.players.online) == 1:
                    _name = "There is " + str(server_stats.players.online) + " player online!"

            embed = discord.Embed(title=f"{helioss} {str(name[index])} {helioss}", color=0x0d11e7)
            embed.add_field(name=_name, value="```" + players + "```")

            await ctx.send(embed=embed)
        """except:
            cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
            await ctx.send(f"Something went wrong, please ping Fran or Sardine {cat_ban}")"""

    @commands.command()
    async def server(self, ctx, args=None):
        """Get all server info, works on #bot-commands, #bot-playground and each server channel"""
        try:
            uuid = await self.config.guild(ctx.guild).uuid()
            name = await self.config.guild(ctx.guild).name()
            version = await self.config.guild(ctx.guild).version()
            ip = await self.config.guild(ctx.guild).ip()
            port = await self.config.guild(ctx.guild).port()
            dns = await self.config.guild(ctx.guild).dns()
            channel_id = await self.config.guild(ctx.guild).channelID()
            short = await self.config.guild(ctx.guild).short()

            helioss = discord.utils.get(ctx.guild.emojis, name="Helioss")
            run = discord.utils.get(ctx.guild.emojis, name="Run")
            importantcustom = discord.utils.get(ctx.guild.emojis, name="importantcustom")
            cat_dab = discord.utils.get(ctx.guild.emojis, name="cat_dab")

            if (ctx.channel.id == 786224142051573770 or ctx.channel.id == 730021784144969789
                or ctx.channel.id == 732258457721503764) and args is None:
                await ctx.send("Please specify your request. Use ^server list to see all available servers.")
                return

            if (ctx.channel.id == 786224142051573770 or ctx.channel.id == 730021784144969789
                or ctx.channel.id == 732258457721503764) and args == "list":
                await ctx.send("**Available Servers**: " + ', '.join(short))
                return

            if (ctx.channel.id == 786224142051573770 or ctx.channel.id == 730021784144969789
                or ctx.channel.id == 732258457721503764) and args != "list" and args is not None:
                try:
                    index = short.index(args)
                except:
                    cat_sad = discord.utils.get(ctx.guild.emojis, name="cat_sad")
                    await ctx.send(f"There is no server named {args} {cat_sad}")
                    cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
                    await ctx.send(f"If the server exists, please ping Fran or Sardine {cat_ban}")
                    return

                current_state, disk_bytes, disk_limit, memory_bytes, memory_limit = self.getServerInfo(uuid[index])

                if current_state == "running":
                    color = 0x2ef406
                    s = "Running "
                    status = run

                    server = MinecraftServer(ip[index], int(port[index]))
                    server_status = server.status()
                    num_players = str(server_status.players.online)
                    max_players = str(server_status.players.max)
                if current_state == "offline":
                    color = 0xf40606
                    s = "Offline "
                    status = importantcustom
                    num_players = ""
                    max_players = ""
                if current_state == "starting":
                    color = 0xff9500
                    s = "Starting "
                    status = cat_dab
                    num_players = ""
                    max_players = ""

                embed = discord.Embed(title=f"{helioss} {str(name[index])} {helioss}", color=color)
                embed.add_field(name="Name: ", value=str(name[index]), inline=False)

                embed.add_field(name="Status: ", value=f"{s}{status}", inline=True)
                embed.add_field(name="Version: ", value=str(version[index]), inline=True)
                embed.add_field(name="IP: ", value=str(dns[index]), inline=False)
                embed.add_field(name="Player: ",
                                value=num_players + " / " + max_players,
                                inline=False)
                embed.add_field(name="Disk Space: ",
                                value=self.printBytes(disk_bytes, "B", "GB") + " of " + self.printBytes(disk_limit,
                                                                                                        "MB",
                                                                                                        "GB"),
                                inline=False)
                embed.add_field(name="RAM: ",
                                value=self.printBytes(memory_bytes, "B", "GB") + " of " + self.printBytes(memory_limit,
                                                                                                          "MB",
                                                                                                          "GB"),
                                inline=False)

                await ctx.send(embed=embed)
                return

            try:
                _index = self.getIndex(channel_id, ctx.channel.id)
            except:
                cat_sad = discord.utils.get(ctx.guild.emojis, name="cat_sad")
                await ctx.send(f"There is no server asociated to this channel {cat_sad}")
                cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
                await ctx.send(f"If the server exists, please ping Fran or Sardine {cat_ban}")
                return
            for index in _index:
                current_state, disk_bytes, disk_limit, memory_bytes, memory_limit = self.getServerInfo(uuid[index])

                if current_state == "running":
                    color = 0x2ef406
                    s = "Running "
                    status = run

                    server = MinecraftServer(ip[index], int(port[index]))
                    server_status = server.status()
                    num_players = str(server_status.players.online)
                    max_players = str(server_status.players.max)
                if current_state == "offline":
                    color = 0xf40606
                    s = "Offline "
                    status = importantcustom
                    num_players = ""
                    max_players = ""
                if current_state == "starting":
                    color = 0xff9500
                    s = "Starting "
                    status = cat_dab
                    num_players = ""
                    max_players = ""

                embed = discord.Embed(title=f"{helioss} {str(name[index])} {helioss}", color=color)
                embed.add_field(name="Name: ", value=str(name[index]), inline=False)

                embed.add_field(name="Status: ", value=f"{s}{status}", inline=True)
                embed.add_field(name="Version: ", value=str(version[index]), inline=True)
                embed.add_field(name="IP: ", value=str(dns[index]), inline=False)
                embed.add_field(name="Player: ",
                                value=num_players + " / " + max_players,
                                inline=False)
                embed.add_field(name="Disk Space: ",
                                value=self.printBytes(disk_bytes, "B", "GB") + " of " + self.printBytes(disk_limit, "MB",
                                                                                                        "GB"),
                                inline=False)
                embed.add_field(name="RAM: ",
                                value=self.printBytes(memory_bytes, "B", "GB") + " of " + self.printBytes(memory_limit,
                                                                                                          "MB",
                                                                                                          "GB"),
                                inline=False)

                await ctx.send(embed=embed)
        except:
            cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
            await ctx.send(f"Something went wrong, please ping Fran or Sardine {cat_ban}")

    @commands.command()
    async def ips(self, ctx):
        """Get all Helioss IPs and versions, only works on #bot-commands and #bot-playground"""
        try:
            if ctx.channel.id == 704089351260209262 or ctx.channel.id == 730021784144969789:
                dns = await self.config.guild(ctx.guild).dns()
                version = await self.config.guild(ctx.guild).version()
                name = await self.config.guild(ctx.guild).name()

                helioss = discord.utils.get(ctx.guild.emojis, name="Helioss")

                for i in range(len(name)):
                    embed = discord.Embed(title=f"{helioss} {str(name[i])} {helioss}", color=0x0be0d2)
                    embed.add_field(name="IP: ", value=str(dns[i]), inline=True)
                    embed.add_field(name="Version: ", value=str(version[i]), inline=True)
                    await ctx.send(embed=embed)
        except:
            cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
            await ctx.send(f"Something went wrong, please ping Fran or Sardine {cat_ban}")

    @commands.command()
    async def commands(self, ctx):
        """List the available commands for players on #bot-commands"""
        try:
            if ctx.channel.id == 704089351260209262:
                await ctx.send("**Available commands**: ^server, ^ips")
        except:
            cat_ban = discord.utils.get(ctx.guild.emojis, name="cat_ban")
            await ctx.send(f"Something went wrong, please ping Fran or Sardine {cat_ban}")

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        # TODO: Replace this with the proper end user data removal handling.
        super().red_delete_data_for_user(requester=requester, user_id=user_id)
