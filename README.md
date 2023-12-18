# Discord Bot

캐릭터 A를 언급하면 해당 캐릭터가 대답하는 것처럼 반응하는 디스코드 봇

봇이 음성 채널에 들어와 있다면 음성 메시지가, 들어와 있지 않다면 채팅 메시지가 출력됨

 ![Python](https://img.shields.io/badge/Python-^3.10.12-3776AB?Style=flat&logo=Python&logoColor=3776AB) ![Jupyter](https://img.shields.io/badge/Jupyter-^6.5.3-F37626?Style=flat&logo=Jupyter&logoColor=F37626)![Amazon EC2](https://img.shields.io/badge/Amazon_EC2--FF9900?Style=flat&logo=Amazon-EC2&logoColor=FF9900)

제작 시기: 2023. 05.



## 1. 실행

#### 실행 예시 영상
https://github.com/pepprbell/discord-voice-bot/assets/67995526/ded3e0f4-e51d-441b-8b61-6bba1d64d2ac
<br>

## 2. 제작 과정

디스코드를 자주 이용하곤 하는데, 디스코드 채팅에서 특정 캐릭터 A의 이름이 언급되면 해당 캐릭터가 대답하는 것처럼 봇이 응답한다면 재미있지 않을까 라는 생각에서 출발했다.

디스코드 공식 API는 바로 코드에 적용하기엔 어려워서, [discord.py](https://discordpy.readthedocs.io/en/stable/#)라는 라이브러리를 사용했다.

<br>

그리고, Spring이나 Django를 이용한 서버 구축 방법을 정확히 모르기 때문에 대학 시절 이미 사용해 보아 익숙해져 있던 Jupyter notebook을 사용해 러닝커브를 최소화하고자 했다.

해서 AWS EC2 micro 서버에 Python, Jupyter notebook 등을 설치하고 Jupyter notebook을 상시 가동하는 것으로 서버 문제를 해결했다.

<br>

### 코드 해석

#### 라이브러리 import

```python
import discord
import nest_asyncio
import nacl
import time
import random
from discord.ext import commands
nest_asyncio.apply()
```

`discord` - 디스코드 API 불러오기

`nest_asyncio` - 주피터 노트북 자체 이벤트 루프 이슈 해결용 (Jupyer: RuntimeError) [참고 링크](https://www.markhneedham.com/blog/2019/05/10/jupyter-runtimeerror-this-event-loop-is-already-running/)

`time`, `random` - 기능 구현에 필요한 수학 라이브러리

<br>

#### 초기 세팅

```python
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
```

Intents는 client에게 작업을 요청할 때 필요한 객체.

이 봇은 메시지 컨텐츠만을 이용할 예정이라  message_content만 True로 설정해 두었다.

<br>

#### 클라이언트 이벤트 - 접속

```python
@client.event
async def on_ready():
    print(f'{client.user}로 로그인 완료')
```

클라이언트에 로그인이 되면 Jupyter notebook에 로그가 적힌다.

<br>

#### 클라이언트 이벤트 - 메시지 작성

```python
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    server = find_client(message)
    print(server)
    print(client.voice_clients)

    if message.content.startswith('$A 들어와'):
        time.sleep(0.5)

        await join(message, server)
        return

    if message.content.startswith('$A 나가'):
        time.sleep(0.5)

        await disconnect(message, server)
        return
    
    if message.content.startswith('안불렀') and len(message.content) <= 7:
        time.sleep(0.5)

        if random.random() < 0.5:
            return

        reply = choices(['알겠어.', '섭섭하네...', '음.', '또 불러줘.', '...'])
        await send(message, reply)
```

`on_message`는 서버에 메시지가 타이핑되었을 때 반응하는 함수다.

명령어 `$A`를 타이핑하고 '들어와', '나가' 를 입력하면 잠시의 딜레이 후에 봇이 메시지를 적은 사람의 음성 채널에 입장한다.

반응속도가 지나치게 빠르면 이질감이 들 수 있어 전체적으로 약간의 딜레이를 추가하였다.

내가 소속된 채널 이용자들은 ''안불렀어.' 라는 말도 종종 하곤 해서, 재미를 위해 이런 메시지가 들려온다면 랜덤하게 반응하도록 했다.

<br>

```python
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
```

`do_reply`는 메시지가 응답할 만한 메시지인가를 판단하는 함수이다. (후술)

이 함수의 결과값으로 `True`가 나온다면, `what_to_say`라는 함수를 통해 어떤 문구로 응답할 지 결정한다.

- 이 때 만약 `client.voice_clients`가 `True`라면 (캐릭터가 음성 채널에 접속해 있다면) 여덟 개의 짧은 음성 중 무엇을 재생할 지 골라 재생한다.

- `False`라면 (캐릭터가 음성 채널에 접속해 있지 않다면) 채팅으로 메시지를 골라 보낸다.

<br>

#### 기능 함수 - 채팅 보내기

```python
# --------------------------채팅 보내기------------------------------------
async def send(message, content):
    reference = message.to_reference()
    await message.channel.send(content, reference=reference)
```

채팅을 보내는 함수.

`message` 변수 안에 메시지를 보낸 사람/채널의 정보가 포함되어 있으므로, `message`에서 참조할 정보(`to_reference`)를 추출해 해당 주소로 메시지를 보내는 함수다.

<br>

#### 기능 함수 - 음성채널 연결 / 연결끊기

```python
# ---------------------음성채널 연결 / 연결끊기 -------------------------------
async def join(message, server):

    if not message.author.voice:  # 유저가 아직 음성 채널 접속을 안함
        await message.channel.send('네가 있는 채널로 들어갈게. 먼저 들어가.')
        return

    channel = message.author.voice.channel

    if message.author.voice.channel == server:  # 유저 채널 = 캐릭터 채널
        await send(message, '이미 들어와 있어.')
        return

    if not server:  # 캐릭터가 어느 채널에도 들어가 있지 않음
        reply = choices(['그럴게.', '알겠어.', '알았어.', '내가 필요해?'])

        await send(message, reply)
        await channel.connect()

    else:  # 유저 채널 != 캐릭터 채널
        await server.move_to(channel)


async def disconnect(message, server):

    if not server:
        await message.channel.send('이미 나왔어.')
        return

    reply = choices(['...알겠어.', '섭섭하네...', '또 불러줘.', '응.'])

    await send(message, reply)
    await server.disconnect()
```

캐릭터가 음성 채널에 들어가거나 나오게 하는 함수.

캐릭터는 유저가 속한 음성 채널에 들어가도록 되어 있으므로, 유저가 어떤 음성 채널에도 접속해 있지 않거나 이미 유저와 캐릭터가 같은 음성 채널에 들어가 있을 경우들을 예외처리했다.

명령어를 입력할 때마다 대답도 미리 입력된 범위 안에서 송출된다. 생성형 AI를 사용한다면 더 다채로운 대답을 할 수 있지 않을까.

<br>

#### 기능 함수 - Etc

```python
# -----------------------대답하는데 쓰는 함수들---------------------------------
def find_client(message):

    clients = client.voice_clients
    for server in clients:
        if server.guild == message.author.guild:
            return server

    return False
```

`message` 정보를 받고, 해당 메시지가 어느 서버(`guild`)에서 보내졌는 지 판단하는 함수.

이 봇은 여러 개의 서버에서 작동 가능한 봇이어야 하므로 작성하였다.

<br>

```python
def do_reply(content, server):  # 대답할지 결정

    content = content.strip()
    content = content.strip('.')

    if len(content) >= 50:  # 글자수 20자 이상 return
        return False

    if 'A' not in content and 'A야' not in content:  # 'A'랑 'A야'가 포함되지 않았을 때 return
        return False

    if not server and random.random() < 0.3:  # 불렀소? 확률 설정
        return False

    return True
```

채널에 업로드된 메시지에 봇이 대답할지를 결정하는 함수.

'진지한' 메시지에 봇이 응답하는 것을 방지하기 위한 최소한의 선으로 글자수 20자 이상의 메시지엔 응답을 하지 않도록 했고, 캐릭터가 언급되지 않았을 경우 응답하지 않는다.

마지막으로, 응답 확률을 설정해 모든 메시지에 지나치게 응답하지 않도록 조정했다.

<br>

```python
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
            mentions = ['섭섭하네...', '음...', '으음...']
        else:
            mentions = ['불렀어?', '나를 찾아?', '여기 있어.', '응.', '으음.', '음. 나야.']  # 대사목록
            weights = [100, 20, 20, 10, 10, 10]  # 가중치

    return choices(mentions, weights)


def choices(seq, weights=None):  # array 중 랜덤으로 선택하는 함수
    return random.choices(seq, weights=weights, k=1)[0]
```

두 함수는 캐릭터가 어떤 말을 하게 할 지 결정하기 위해 만든 함수.

`random.choices` 를 통해 응답 목록에 `weights`를 주어 어떤 말을 자주 할 지 설정할 수 있도록 했다.

<br>

```python
client.run(key)
```

마지막으로 클라이언트를 실행시켜 주면 마무리.

<br>
