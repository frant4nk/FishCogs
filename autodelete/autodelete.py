from redbot.core import commands, events
from redbot.core.bot import Red

import discord
import requests
import paramiko

from hurry.filesize import size, alternative

class AutoDelete(commands.Cog):
    """Autodelete cog for Helioss"""

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.user = ""
        self.password = ""

        self.name_list = []
        self.uuid_list = []
        self.ip_list = []
        self.identifier_list = []
        self.pan_list = []
        self.germany_list = []
        self.node_list = []
        self.germany_names = []
        self.pan_names = []
        
        self.headers_app = {"Accept": "application/json",
                            "Content-Type": "application/json",
                            "Authorization": "Bearer "}
        
        self.headers_client = {"Accept": "application/json",
                               "Content-Type": "application/json",
                               "Authorization": "Bearer "}
        self.fetchIds()

    def fetchIds(self):
        self.name_list.clear()
        self.uuid_list.clear()
        self.ip_list.clear()
        self.identifier_list.clear()
        self.node_list.clear()
        self.pan_list.clear()
        self.germany_list.clear()
        self.germany_names.clear()
        self.pan_names.clear()
        
        r = requests.get("https://pan.helioss.co/api/application/servers", headers=self.headers_app)
        rToJson = r.json()
        
        for index in range(len(rToJson['data'])):
            self.name_list.append(rToJson['data'][index]['attributes']['name'])
            self.uuid_list.append(rToJson['data'][index]['attributes']['uuid'])
            self.identifier_list.append(rToJson['data'][index]['attributes']['identifier'])
            self.node_list.append(rToJson['data'][index]['attributes']['node'])
           
        for i in range(len(self.node_list)):
            if self.node_list[i] == 1:
                self.pan_list.append(self.identifier_list[i])
                self.pan_names.append(self.name_list[i])
            if self.node_list[i] == 2:
                self.germany_list.append(self.identifier_list[i])
                self.germany_names.append(self.name_list[i])


    def getBackups(self, host, user):
        transport = paramiko.Transport((host, 2022))
        transport.connect(username=user, password=self.password)

        sftp = paramiko.SFTPClient.from_transport(transport)
        files = sftp.listdir('./backups')
        sizes = []
        paths = []

        if files[0] == 'world':
            files = sftp.listdir('./backups/world')

            for file in files:
                info = sftp.stat('./backups/world/' + file)
                sizes.append(size(info.st_size, system=alternative))
                paths.append('./backups/world/' + file)
            return files, sizes, paths

        else:	
            for file in files:
                info = sftp.stat('./backups/' + file)
                sizes.append(size(info.st_size, system=alternative))
                paths.append('./backups/' + file)
            return files, sizes, paths

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel
        guild = channel.guild
        #member = message.author
        cat_thumb = discord.utils.get(guild.emojis, name="cat_thumb")
        del_list = []
        del_list_servers = []

        if channel.name == 'server-health-germany':
            if message.webhook_id is not None: # Cambiar a "is not"
                if message.author.bot is True:
                    if message.content.find('676125994389602306') > -1: # Cambiar a >
                        self.fetchIds()
                        for identifier, idx in zip(self.germany_list, range(len(self.germany_list))):
                            auxUser = self.user
                            files, sizes, paths = self.getBackups(host="newgermany.helioss.co", user=auxUser+identifier)
                            if len(files) == 1:
                                del_list.append('\u274e')
                            else:
                                for j in range(len(paths) - 1):
                                    del_list.append('\u2705')
                                del_list.append('\u274e')
                            
                            embed = discord.Embed(title=self.germany_names[idx], color=0x00ff00)
                            embed.add_field(name='Backups', value='\n'.join(paths), inline=True)
                            embed.add_field(name='Sizes', value='\n'.join(sizes), inline=True)
                            embed.add_field(name='Delete', value='\n'.join(del_list), inline=True)
                            msg = await channel.send(embed=embed)
                            for number in range(len(files)):
                                react = str(number) + '\u20e3'
                                await msg.add_reaction(react)
                            await msg.add_reaction('\u2705')
                            await msg.add_reaction('\u274e')
                            del_list.clear()
                    else:
                        print('No deletion needed')
        
        if channel.name == 'servers-disk-space':
            if message.webhook_id is not None: # Cambiar a "is not"
                if message.author.bot is True: # Cambiar a True
                    if message.content.find('676125994389602306') > -1:
                        self.fetchIds()
                        server_names = []
                        msg_list = message.content.split('\n')
                        msg_list.pop(0)
                        for name in msg_list:
                            server_names.append(name.split(' filled')[0]) # En server_names tenemos los nombres de los servers llenos
                        for name in server_names: # Para cada nombre comprobamos si esta en pan o newgermany
                            if name in self.pan_names: #Comprobamos si esta en pan
                                _id = self.pan_list[self.pan_names.index(name)]
                                auxUser = self.user
                                files, sizes, paths = self.getBackups(host="pan.helioss.co", user=auxUser+_id)
                                if len(files) == 1:
                                    del_list_servers.append('\u274e')
                                else:
                                    for j in range(len(paths) - 1):
                                        del_list_servers.append('\u2705')
                                    del_list_servers.append('\u274e')
                                
                                embed = discord.Embed(title=name, color=0x00ff00)
                                embed.add_field(name='Backups', value='\n'.join(paths), inline=True)
                                embed.add_field(name='Sizes', value='\n'.join(sizes), inline=True)
                                embed.add_field(name='Delete', value='\n'.join(del_list_servers), inline=True)
                                msg = await channel.send(embed=embed)
                                
                                for number in range(len(files)):
                                    react = str(number) + '\u20e3'
                                    await msg.add_reaction(react)
                                await msg.add_reaction('\u2705')
                                await msg.add_reaction('\u274e')
                                del_list_servers.clear()

                            if name in self.germany_names:
                                _id = self.germany_list[self.germany_names.index(name)]
                                auxUser = self.user
                                files, sizes, paths = self.getBackups(host="newgermany.helioss.co", user=auxUser+_id)
                                if len(files) == 1:
                                    del_list_servers.append('\u274e')
                                else:
                                    for j in range(len(paths) - 1):
                                        del_list_servers.append('\u2705')
                                    del_list_servers.append('\u274e')
                                
                                embed = discord.Embed(title=name, color=0x00ff00)
                                embed.add_field(name='Backups', value='\n'.join(paths), inline=True)
                                embed.add_field(name='Sizes', value='\n'.join(sizes), inline=True)
                                embed.add_field(name='Delete', value='\n'.join(del_list_servers), inline=True)
                                msg = await channel.send(embed=embed)
                                
                                for number in range(len(files)):
                                    react = str(number) + '\u20e3'
                                    await msg.add_reaction(react)
                                await msg.add_reaction('\u2705')
                                await msg.add_reaction('\u274e')
                                del_list_servers.clear()

    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            channel = reaction.message.channel
            cat_thumb = discord.utils.get(channel.guild.emojis, name="cat_thumb")

            if channel.name == 'server-health-germany':
                message = reaction.message
                if reaction.emoji != '\u2705' and reaction.emoji != '\u274e':
                    await reaction.message.remove_reaction(reaction.emoji, user)
                    title = message.embeds[0].title
                    paths = message.embeds[0].fields[0].value.split('\n')
                    sizes = message.embeds[0].fields[1].value.split('\n')
                    marks = message.embeds[0].fields[2].value.split('\n')

                    numb = int(reaction.emoji.encode('unicode-escape').decode('ASCII')[:-6])

                    if marks[numb] == '\u274e':
                        marks[numb] = '\u2705'
                    else:
                        marks[numb] = '\u274e'
                    
                    embed = discord.Embed(title=title, color=0x00ff00)
                    embed.add_field(name='Backups', value='\n'.join(paths), inline=True)
                    embed.add_field(name='Sizes', value='\n'.join(sizes), inline=True)
                    embed.add_field(name='Delete', value='\n'.join(marks), inline=True)
                    await message.edit(embed=embed)

                if reaction.emoji == '\u274e': # denied
                    await message.clear_reactions()
                    await message.add_reaction(cat_thumb)
                
                if reaction.emoji == '\u2705': # accepted
                    # delete backups markeds
                    title = message.embeds[0].title
                    paths = message.embeds[0].fields[0].value.split('\n')
                    sizes = message.embeds[0].fields[1].value.split('\n')
                    marks = message.embeds[0].fields[2].value.split('\n')

                    for index in range(len(self.name_list)):
                        if self.name_list[index] == title:
                            _id = self.identifier_list[index]

                    for index in range(len(marks)):
                        if marks[index] == '\u2705':
                            transport = paramiko.Transport(('newgermany.helioss.co', 2022))
                            aux_user = self.user
                            transport.connect(username=aux_user + _id, password=self.password)
                            sftp = paramiko.SFTPClient.from_transport(transport)
                            sftp.remove(paths[index])
                            aux_path = '~~' + paths[index] + '~~'
                            aux_size = '~~' + sizes[index] + '~~'
                            paths[index] = aux_path
                            sizes[index] = aux_size
                            
                    embed = discord.Embed(title=title, color=0x00ff00)
                    embed.add_field(name='Backups', value='\n'.join(paths), inline=True)
                    embed.add_field(name='Sizes', value='\n'.join(sizes), inline=True)
                    embed.add_field(name='Delete', value='\n'.join(marks), inline=True)

                    await message.edit(embed=embed)
                    await message.clear_reactions()
                    await message.add_reaction(cat_thumb)

            if channel.name == 'servers-disk-space':
                message = reaction.message
                if reaction.emoji != '\u2705' and reaction.emoji != '\u274e':
                    await reaction.message.remove_reaction(reaction.emoji, user)
                    title = message.embeds[0].title
                    paths = message.embeds[0].fields[0].value.split('\n')
                    sizes = message.embeds[0].fields[1].value.split('\n')
                    marks = message.embeds[0].fields[2].value.split('\n')

                    numb = int(reaction.emoji.encode('unicode-escape').decode('ASCII')[:-6])

                    if marks[numb] == '\u274e':
                        marks[numb] = '\u2705'
                    else:
                        marks[numb] = '\u274e'
                    
                    embed = discord.Embed(title=title, color=0x00ff00)
                    embed.add_field(name='Backups', value='\n'.join(paths), inline=True)
                    embed.add_field(name='Sizes', value='\n'.join(sizes), inline=True)
                    embed.add_field(name='Delete', value='\n'.join(marks), inline=True)
                    await message.edit(embed=embed)

                if reaction.emoji == '\u274e': # denied
                    await message.clear_reactions()
                    await message.add_reaction(cat_thumb)
                
                if reaction.emoji == '\u2705': # accepted
                    # delete backups markeds
                    title = message.embeds[0].title
                    paths = message.embeds[0].fields[0].value.split('\n')
                    sizes = message.embeds[0].fields[1].value.split('\n')
                    marks = message.embeds[0].fields[2].value.split('\n')

                    for index in range(len(self.name_list)):
                        if self.name_list[index] == title:
                            _id = self.identifier_list[index]

                    for index in range(len(marks)):
                        if marks[index] == '\u2705':
                            if title in self.pan_names:
                                transport = paramiko.Transport(('pan.helioss.co', 2022))
                            if title in self.germany_names:
                                transport = paramiko.Transport(('newgermany.helioss.co', 2022))
                            aux_user = self.user
                            transport.connect(username=aux_user + _id, password=self.password)
                            sftp = paramiko.SFTPClient.from_transport(transport)
                            sftp.remove(paths[index])
                            aux_path = '~~' + paths[index] + '~~'
                            aux_size = '~~' + sizes[index] + '~~'
                            paths[index] = aux_path
                            sizes[index] = aux_size
                            
                    embed = discord.Embed(title=title, color=0x00ff00)
                    embed.add_field(name='Backups', value='\n'.join(paths), inline=True)
                    embed.add_field(name='Sizes', value='\n'.join(sizes), inline=True)
                    embed.add_field(name='Delete', value='\n'.join(marks), inline=True)

                    await message.edit(embed=embed)
                    await message.clear_reactions()
                    await message.add_reaction(cat_thumb)
