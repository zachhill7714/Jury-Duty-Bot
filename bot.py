import discord
import asyncio
import random
import time


class JuryDutyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = self.get_guild(476393300358856724)
        self.general = self.get_channel(620724471413604366)
        self.jury = []
        for id in get_jury():
            self.jury.append(self.get_user(id))
        self.decisions = get_decisions()
        self.banee = self.get_user(get_banee())
        self.counter = get_decision_time() - time.time()

    async def setup_hook(self) -> None:
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def my_background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            self.counter += 1
            await asyncio.sleep(1)
            if self.counter == 86400 * 7:  # every WEEK the jury script runs
                await self.general.send(f"@here It's time!")
                await asyncio.sleep(10)
                await self.general.send(f'The jig is up, {self.banee.name}... the jury has spoken!')
                await asyncio.sleep(1)
                num_guilty = 0
                for decision in self.decisions:
                    if decision: num_guilty += 1
                await self.general.send(f'They have decided: {num_guilty} Guilty, {5-num_guilty} Not Guilty')
                await asyncio.sleep(1)
                if num_guilty >= 3:
                    await self.general.send(f'As per the ruling of the jury, {self.banee.name} will be'
                                            f'BANNED from Arrow Smashers. It was a good run!')
                    await self.server.ban(self.banee, reason="The jury has decided.")
                    await asyncio.sleep(3)
                else:
                    await self.general.send(f'As per the ruling of the jury, {self.banee.name} will'
                                            f'NOT be banned from Arrow Smashers. You got lucky...')
                    await asyncio.sleep(3)
                await self.make_new_loadout()
                jury_string = ""
                for juror in self.jury:
                    jury_string += f'{juror.mention}, '
                jury_string = jury_string[len(jury_string) - 2]
                await self.general.send(f'The new jury is as follows: {jury_string}')
                await asyncio.sleep(1)
                await self.general.send(f'The new defendant is: {self.banee.mention}')
                await asyncio.sleep(1)
                await self.general.send(f'The next decision is due by <t:{time.time() + (86400 * 7)}:F>.'
                                        f'Good luck!')
                self.counter = 0

    async def on_message(self, message):
        if message.content.startswith("<@1054848322780790805>") and message.author in self.jury:
            pos = self.jury.index(message.author)
            prev_decision = self.decisions[pos]
            new_decision = None
            if "guilty" in message.content.lower():
                new_decision = True
            elif "not guilty" in message.content.lower():
                new_decision = False
            if prev_decision is not None and prev_decision is not new_decision:
                await self.general.send(f'You changed your vote from {get_decision(self)} to {new_decision}.')
            self.decisions[pos] = new_decision
        if None not in self.decisions:
            result_timestamp = int(time.time() + ((86400 * 7) - self.counter))
            response = (f'All votes submitted! Please wait until <t:{result_timestamp}:F> for'
                        f'the decision to be made. You are allowed to change your vote.')
            await self.general.send(response)

    async def make_new_loadout(self):
        jury_list = []
        jury_file = open("bot_info/jury.txt", "w")
        banee_file = open("bot_info/banee.txt", "w")
        while len(jury_list) != 5:
            user = random.choice(self.server.members)
            if user is not client.user and not user.bot:  # if the chosen user isn't this bot or another
                jury_list.append(user)
                jury_file.write(str(user.id) + "\n")
        jury_file.close()
        self.decisions = [None] * 5
        banee = None
        while banee is None:
            user = random.choice(self.server.members)
            if user is not client.user and not user.bot:  # same thing here
                banee = user
                banee_file.write(str(user.id))



def get_token():
    return open("token.txt").readline().split("=")[1]


def get_jury():
    jury = []
    jury_file = open("bot_info/jury.txt")
    for line in jury_file.readlines():
        jury.append(int(line))
    return jury


def get_decisions():
    decisions = []
    decisions_file = open("bot_info/decisions.txt")
    for line in decisions_file.readlines():
        decisions.append(bool(line))
    return decisions


def get_banee():
    banee_file = open("bot_info/banee.txt")
    return int(banee_file.readline())


def get_decision_time():
    decision_time_file = open("bot_info/decision_time.txt")
    return int(decision_time_file.readline())


def get_decision(decision):
    return "Guilty" if decision else "Not Guilty"


intents = discord.Intents.default()
intents.message_content = True

client = JuryDutyBot(intents=intents)
client.run(get_token())