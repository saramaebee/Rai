import os
import re
from typing import Union, List

import discord
import discord.ext.commands as commands

from .utils import helper_functions as hf


dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BLACKLIST_CHANNEL_ID = 533863928263082014
BANS_CHANNEL_ID = 329576845949534208
MODCHAT_SERVER_ID = 257984339025985546
RYRY_SPAM_CHAN = 275879535977955330
JP_SERVER_ID = 189571157446492161
SP_SERVER_ID = 243838819743432704
CH_SERVER_ID = 266695661670367232
CL_SERVER_ID = 320439136236601344
RY_SERVER_ID = 275146036178059265
FEDE_TESTER_SERVER_ID = 941155953682821201


class Interactions(commands.Cog):
    """A module for Discord interactions such as slash commands and context commands"""

    @commands.slash_command(guild_ids=[JP_SERVER_ID, SP_SERVER_ID, RY_SERVER_ID, FEDE_TESTER_SERVER_ID])
    async def staffping(self,
                        ctx: discord.ApplicationContext,
                        users: discord.Option(str, "The user/s:"),
                        reason: discord.Option(str, "Specify the reason for your report:")):
        """Notifies the staff team about a current and urgent issue."""
        await self.staffping_code(ctx, users, reason)

    async def staffping_code(self,
                             ctx: Union[discord.ApplicationContext, commands.Context],
                             users: str,
                             reason: str):
        """The main code for the staffping command. This will be referenced by the above slash
        command, but also by the mods_ping() function in on_message()"""
        regex_result = re.findall(r'<?@?!?(\d{17,22})>?', users)

        jump_url = None
        if isinstance(ctx, discord.ApplicationContext):
            slash = True  # This was called from a slash command
            channel = ctx.interaction.channel
            last_message: discord.Message = ctx.interaction.channel.last_message
            if last_message:
                jump_url = last_message.jump_url
        else:
            slash = False  # This was called from on_message
            channel = ctx.channel
            jump_url = ctx.message.jump_url

        if not jump_url:
            messages = await channel.history(limit=1).flatten()
            if messages:
                jump_url = messages[0].jump_url

        if not regex_result:
            if slash:
                await ctx.respond("I couldn't find the specified user/s.\n"
                                  "Please, mention the user/s or write their ID/s in the user prompt.",
                                  ephemeral=True)
                return
            else:
                pass

        for result in regex_result:
            if not ctx.guild.get_member(int(result)):
                regex_result.remove(result)
                if slash:
                    await ctx.respond(f"I couldn't find the user {result} in this server", ephemeral=True)

        if not regex_result and slash:
            await ctx.respond("I couldn't find any of the users that you specified, try again.\n"
                              "Please, mention the user/s or write their ID/s in the user prompt.", ephemeral=True)
            return

        member_list: List[discord.Member] = list(set(regex_result))  # unique list of users

        if len(member_list) > 9:
            if slash:
                await ctx.respond("You're trying to report too many people at the same time. Max per command: 9.\n"
                                  "Please, mention the user/s or write their ID/s in the user prompt.",
                                  ephemeral=True)
                return
            else:
                member_list = []

        invis = "⠀"  # an invisible character that's not a space to avoid stripping of whitespace
        user_id_list = [f'\n{invis * 1}- <@{i}> (`{i}`)' for i in member_list]
        user_id_str = ''.join(user_id_list)
        if slash:
            confirmation_text = f"You've reported the user: {user_id_str} \nReason: {reason}."
            if len(member_list) > 1:
                confirmation_text = confirmation_text.replace('user', 'users')
            await ctx.respond(f"{confirmation_text}", ephemeral=True)

        alarm_emb = discord.Embed(title=f"Staff Ping",
                                  description=f"- **From**: {ctx.author.mention} ({ctx.author.name})"
                                              f"\n- **In**: {ctx.channel.mention}",
                                  color=discord.Color(int('FFAA00', 16)),
                                  timestamp=discord.utils.utcnow())
        if jump_url:
            alarm_emb.description += f"\n[**`JUMP URL`**]({jump_url})"
        if reason:
            alarm_emb.description += f"\n\n- **Reason**: {reason}."
        if user_id_str:
            alarm_emb.description += f"\n- **Reported Users**: {user_id_str}"

        button_author = discord.ui.Button(label='0', style=discord.ButtonStyle.primary)

        button_1 = discord.ui.Button(label='1', style=discord.ButtonStyle.gray)
        button_2 = discord.ui.Button(label='2', style=discord.ButtonStyle.gray)
        button_3 = discord.ui.Button(label='3', style=discord.ButtonStyle.gray)
        button_4 = discord.ui.Button(label='4', style=discord.ButtonStyle.gray)
        button_5 = discord.ui.Button(label='5', style=discord.ButtonStyle.gray)
        button_6 = discord.ui.Button(label='6', style=discord.ButtonStyle.gray)
        button_7 = discord.ui.Button(label='7', style=discord.ButtonStyle.gray)
        button_8 = discord.ui.Button(label='8', style=discord.ButtonStyle.gray)
        button_9 = discord.ui.Button(label='9', style=discord.ButtonStyle.gray)

        button_solved = discord.ui.Button(label='Mark as Solved', style=discord.ButtonStyle.green)

        buttons = [button_author, button_1, button_2, button_3, button_4,
                   button_5, button_6, button_7, button_8, button_9]

        view = discord.ui.View()
        for button in buttons[:len(member_list) + 1]:
            view.add_item(button)
        view.add_item(button_solved)

        async def button_callback_action(button_index):
            if button_index == 0:
                modlog_target = ctx.author.id
            else:
                modlog_target = member_list[int(button_index) - 1]
            channel_mods = self.bot.get_cog("ChannelMods")
            await channel_mods.modlog(ctx, modlog_target, delete_parameter=30)
            await msg.edit(content=f"{modlog_target}", embed=alarm_emb, view=view)

        async def author_button_callback(interaction):
            await button_callback_action(0)

        button_author.callback = author_button_callback

        async def button_1_callback(interaction):
            await button_callback_action(1)

        button_1.callback = button_1_callback

        async def button_2_callback(interaction):
            await button_callback_action(2)

        button_2.callback = button_2_callback

        async def button_3_callback(interaction):
            await button_callback_action(3)

        button_3.callback = button_3_callback

        async def button_4_callback(interaction):
            await button_callback_action(4)

        button_4.callback = button_4_callback

        async def button_5_callback(interaction):
            await button_callback_action(5)

        button_5.callback = button_5_callback

        async def button_6_callback(interaction):
            await button_callback_action(6)

        button_6.callback = button_6_callback

        async def button_7_callback(interaction):
            await button_callback_action(7)

        button_7.callback = button_7_callback

        async def button_8_callback(interaction):
            await button_callback_action(8)

        button_8.callback = button_8_callback

        async def button_9_callback(interaction):
            await button_callback_action(9)

        button_9.callback = button_9_callback

        async def solved_button_callback(interaction):
            for button in buttons:
                button.disabled = True
            button_solved.disabled = True
            await msg.edit(content=f":white_check_mark: - **Solved Issue**.",
                           embed=alarm_emb,
                           view=view)

        button_solved.callback = solved_button_callback

        if slash:
            guild_id = str(ctx.interaction.guild.id)
        else:
            guild_id = str(ctx.guild.id)

        # Try to find the channel set by the staffping command first
        mod_channel = None
        mod_channel_id = self.bot.db['staff_ping'].get(guild_id, {}).get("channel")
        if mod_channel_id:
            mod_channel = ctx.guild.get_channel_or_thread(mod_channel_id)
            if not mod_channel:
                del self.bot.db['staff_ping'][guild_id]['channel']
                mod_channel_id = None
                # guild had a staff ping channel once but it seems it has been deleted

        # Failed to find a staffping channel, search for a submod channel next
        mod_channel_id = self.bot.db['submod_channel'].get(guild_id)
        if not mod_channel and mod_channel_id:
            mod_channel = ctx.guild.get_channel_or_thread(mod_channel_id)
            if not mod_channel:
                del self.bot.db['submod_channel'][guild_id]
                mod_channel_id = None
                # guild had a submod channel once but it seems it has been deleted

        # Failed to find a submod channel, search for mod channel
        if not mod_channel and mod_channel_id:
            mod_channel_id = self.bot.db['mod_channel'].get(guild_id)
            mod_channel = ctx.guild.get_channel_or_thread(mod_channel_id)
            if not mod_channel:
                del self.bot.db['mod_channel'][guild_id]
                mod_channel_id = None
                # guild had a mod channel once but it seems it has been deleted

        if not mod_channel:
            return  # this guild does not have any kind of mod channel configured

        # Send notification to a mod channel
        content = None
        staff_role_id = ""
        if slash:
            config = self.bot.db['staff_ping'].get(guild_id)
            if config:
                staff_role_id = config.get("role")  # try to get role id from staff_ping db
                if not staff_role_id:  # no entry in staff_ping db
                    staff_role_id = self.bot.db['mod_role'].get(guild_id, {}).get("id")
        if staff_role_id:
            content = f"<@&{staff_role_id}>"
        msg = await hf.safe_send(mod_channel, content, embed=alarm_emb, view=view)

        # Send notification to users who subscribe to mod pings
        for user_id in self.bot.db['staff_ping'].get(guild_id, {}).get('users', []):
            try:
                user = self.bot.get_user(user_id)
                if user:
                    await hf.safe_send(user, embed=alarm_emb)
            except discord.Forbidden:
                pass

        return msg

    # guilds = [RY_TEST_SERV_ID, FEDE_TEST_SERV_ID, JP_SERV_ID, SP_SERV_ID]
    # for guild in guilds:
    #     if guild not in [g.id for g in self.guilds]:
    #         guilds.remove(guild)
    #
    # if guilds:
    #     @self.message_command(name="Delete message", guild_ids=guilds)
    #     async def delete_and_log(ctx, message: discord.Message):
    #         delete = ctx.bot.get_command("delete")
    #         try:
    #             if await delete.can_run(ctx):
    #                 await delete.__call__(ctx, str(message.id))
    #                 await ctx.interaction.response.send_message("The message has been successfully deleted",
    #                                                             ephemeral=True)
    #             else:
    #                 await ctx.interaction.response.send_message("You don't have the permission to use that command",
    #                                                             ephemeral=True)
    #         except commands.BotMissingPermissions:
    #             await ctx.interaction.response.send_message("The bot is missing permissions here to use that command.",
    #                                                         ephemeral=True)
    #
    #     @self.message_command(name="1h text/voice mute", guild_ids=guilds)
    #     async def context_message_mute(ctx, message: discord.Message):
    #         mute = ctx.bot.get_command("mute")
    #         ctx.message = ctx.channel.last_message
    #
    #         try:
    #             if await mute.can_run(ctx):
    #                 await mute.__call__(ctx, args=f"{str(message.author.id)} 1h")
    #                 await ctx.interaction.response.send_message("Command completed", ephemeral=True)
    #
    #             else:
    #                 await ctx.interaction.response.send_message("You don't have the permission to use that command",
    #                                                             ephemeral=True)
    #         except commands.BotMissingPermissions:
    #             await ctx.interaction.response.send_message("The bot is missing permissions here to use that command.",
    #                                                         ephemeral=True)
    #
    #     @self.user_command(name="1h text/voice mute", guild_ids=guilds)
    #     async def context_user_mute(ctx, member: discord.Member):
    #         mute = ctx.bot.get_command("mute")
    #         ctx.message = ctx.channel.last_message
    #
    #         try:
    #             if await mute.can_run(ctx):
    #                 await mute.__call__(ctx, args=f"{str(member.id)} 1h")
    #                 await ctx.interaction.response.send_message("Command completed", ephemeral=True)
    #
    #             else:
    #                 await ctx.interaction.response.send_message("You don't have the permission to use that command",
    #                                                             ephemeral=True)
    #         except commands.BotMissingPermissions:
    #             await ctx.interaction.response.send_message("The bot is missing permissions here to use that command.",
    #                                                         ephemeral=True)
    #
    #     """
    #     @bot.message_command(name="Ban and clear3", check=hf.admin_check)  # creates a global message command
    #     async def ban_and_clear(ctx, message: discord.Message):  # message commands return the message
    #         ban = ctx.bot.get_command("ban")
    #         if await ban.can_run(ctx):
    #             await ban.__call__(ctx, args=f"{str(message.author.id)} ⁣")  # invisible character to trigger ban shortcut
    #             await ctx.interaction.response.send_message("The message has been successfully deleted", ephemeral=True)
    #         else:
    #             await ctx.interaction.response.send_message("You don't have the permission to use that command", ephemeral=True)
    #     """


def setup(bot):
    bot.add_cog(Interactions(bot))
