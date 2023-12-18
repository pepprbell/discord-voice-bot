import discord
import nest_asyncio
import time
import nacl
import random
from discord.ext import commands
nest_asyncio.apply()


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user}로 로그인 완료')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    server = find_client(message)
    print(server)
    print(client.voice_clients)

    if message.content.startswith('$이상 들어와'):
        time.sleep(0.5)

        await join(message, server)
        return

    if message.content.startswith('$이상 나가'):
        time.sleep(0.5)

        await disconnect(message, server)
        return

    if message.content.startswith('안불렀') and len(message.content) <= 7:
        time.sleep(0.5)

        if random.random() < 0.5:
            return

        reply = choices(['...알겠소.', '섭섭하오...', '음.', '그리하지.', '또 불러주시오.', '...'])
        await send(message, reply)

    if do_reply(message.content, server):
        content = what_to_say(message.content, server)

        if client.voice_clients:
            path = f'./source/{content}'
            if content == 'dot':
                path += str(random.randint(1, 8))
            path += '.wav'

            source = discord.FFmpegPCMAudio(path)
            server.play(source)

        else:
            time.sleep(random.randint(0, 1))  # 시간 딜레이 설정
            await send(message, content)


# --------------------------채팅 보내기------------------------------------

async def send(message, content):
    reference = message.to_reference()
    await message.channel.send(content, reference=reference)

# ---------------------음성채널 연결 / 연결끊기 -------------------------------

async def join(message, server):

    if not message.author.voice:  # 유저가 아직 접속을 안함
        await message.channel.send('그대가 있는 채널로 들어가겠소. 먼저 들어가시오.')
        return

    channel = message.author.voice.channel

    if message.author.voice.channel == server:  # 유저 채널 = 이상 채널
        await send(message, '이미 들어와 있소.')
        return

    if not server:  # 이상이 어느 곳에도 들어가 있지 않음
        reply = choices(['음.', '그리하겠소.', '알겠소.', '알았소.', '그리하지.', '내가 필요하오?'])

        await send(message, reply)
        await channel.connect()

    else:  # 유저 채널 != 이상 채널
        await server.move_to(channel)


async def disconnect(message, server):

    if not server:
        await message.channel.send('이미 그리하였소.')
        return

    reply = choices(['...알겠소.', '섭섭하오...', '음.', '그리하지.', '또 불러주시오.', '...'])

    await send(message, reply)
    await server.disconnect()


# -----------------------대답하는데 쓰는 함수들---------------------------------

def find_client(message):

    clients = client.voice_clients
    for server in clients:
        if server.guild == message.author.guild:
            return server

    return False


def do_reply(content, server):  # 대답할지 결정

    content = content.strip()
    content = content.strip('.')

    if len(content) >= 50:  # 글자수 20자 이상 return
        return False

    if '이상' not in content and '조상님' not in content:  # '이상'이랑 '조상님'이 포함되지 않았을 때 return
        return False

    if not server and random.random() < 0.3:  # 불렀소? 확률 설정
        return False

    return True


def what_to_say(content, server):  # 무슨 말로 대답할지 결정
    weights = None

    if server:
        if '안' in content and '불렀' in content:
            mentions = ['dot3', 'dot4', 'dot5', 'dot6', 'dot7', 'dot8', 'sigh', 'subsub', 'julmang', 'ani']
        else:
            if '이상하' in content:
                mentions = ['dot', 'bullusso', 'yisanghao', 'yisangio', 'julmang', 'ani']
                weights = [200, 100, 100, 100, 10, 10]
            else:
                mentions = ['dot', 'bullusso', 'yisangio', 'julmang', 'ani']
                weights = [200, 100, 100, 10, 10]
    else:
        if '안' in content and '불렀' in content:
            mentions = ['섭섭하오...', '음...', '으음...']
        else:
            mentions = ['불렀소?', '나를 찾소?', '여기 있소.', '음...', '으음...', '음. 이상이오.']  # 대사목록
            weights = [100, 20, 20, 10, 10, 10]  # 가중치

    return choices(mentions, weights)


def choices(seq, weights=None):  # array 중 랜덤으로 선택하는 함수
    return random.choices(seq, weights=weights, k=1)[0]


client.run('MTEwMjEwMzYzMzE2NTgyNDA4MA.GYwgXt.zlyXMCRlIVUV8ZftYrw3IqENqN-0flwh9pjMCM')