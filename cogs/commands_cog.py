import discord
from discord.ext import commands

class SystemListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Plannercord online')

    @commands.Cog.listener()
    async def on_member_join(self,member):
        print(f'{member} has joined a server.')

    @commands.Cog.listener() 
    async def on_member_remove(self,member):
        print(f'{member} has left the server.')

    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('{}, that command does not exist.'.format(ctx.author.mention))

class ExampleCommandGroup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #Commands
    
    @commands.command(
      help = "Play ping-pong with me", #shows when ;help [command] called
      brief = "Prints pong" #shows when ;help is called 
    )
    async def ping(self,ctx):
	    await ctx.channel.send("pong") #bot reply

    @commands.command()
    async def hello(ctx, *, user: discord.Member = None):
      if user:
          await ctx.send(f"hello, {user.mention}") #bot reply if correct parameters
      else:
          await ctx.send('You have to say who do you want to say hello to') #bot reply if wrong/incomplete parameters

    @commands.command()
    async def say(ctx, *args):
      response = ""
      for arg in args: #iterate through all parameters given
          response = response + " " + arg
      await ctx.channel.send(response)


class ExampleCommandGroup1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      
    @commands.command()
    async def command1(self,ctx, member : discord.Member, area=''):
        if (area != ''):
          await ctx.send('{} has <command> {} on the {}'.format(ctx.author.mention, member.mention, area))
        else:
          await ctx.send('{} has <command> {}'.format(ctx.author.mention, member.mention))

    @commands.command()
    async def command2(self,ctx, member : discord.Member):
        await ctx.send('{} has <command> {}'.format(ctx.author.mention, member.mention))

    @commands.command()
    async def command3(self,ctx, member : discord.Member):
        if(str(ctx.author)== "test"):
          await ctx.send('{} command {}'.format(ctx.author.mention, member.mention))
        else:
          await ctx.send('{} command {}'.format(ctx.author.mention, member.mention))

    @commands.command()
    async def command4(self,ctx, member : discord.Member):
        await ctx.send('{} <command> {}'.format(ctx.author.mention, member.mention))


# Add the command group classes
def setup(bot):
  bot.add_cog(SystemListeners(bot))
  bot.add_cog(ExampleCommandGroup(bot))
  bot.add_cog(ExampleCommandGroup1(bot))