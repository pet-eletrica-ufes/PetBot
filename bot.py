import discord
from discord.ext import commands
import asyncio
import requests
import json
import random

intents = discord.Intents.all()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', case_insensitive = True, intents=intents)

# Lista de perguntas e respostas para o quiz
quiz_data = [
    {
        'pergunta': 'Qual é a capital da França?',
        'resposta': 'Paris'
    },
    {
        'pergunta': 'Quantos planetas fazem parte do nosso sistema solar?',
        'resposta': '8'
    },
    {
        'pergunta': 'Qual ferramenta é usada para realizar um loop condicional?',
        'resposta': 'For Loop'
    },
    # Adicione mais perguntas e respostas aqui
]

filaMonitoria = []
duvidas = []

role_message_id1 = 1144262554705727558  # ID da mensagem para atribuir os cargos de linguagem de prog
role_message_id2 = 1144272153336889364  # ID da mensagem para atribuir os cargos de regras lidas
emoji_to_role = {
    1143905468918534254: 1143899809590292500,    # ID do Emoji : ID do cargo para Arduino
    1143905591346069654: 1143899881375809668,    # ID do Emoji : ID do cargo para C
    1143905329894142093: 1143895173055664198,    # ID do Emoji : ID do cargo para Python
    1144275789823627304: 1144269762302574622,    # ID do Emoji : ID do cargo para Membros
}

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Assign roles based on reaction emoji ID"""
    if payload.message_id in [role_message_id1, role_message_id2]:  # Replace with your message IDs
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return

        role_id = emoji_to_role.get(payload.emoji.id)
        if role_id is None:
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        try:
            await member.add_roles(role)
            print(f"Added role {role.name} to {member.name}")
        except discord.HTTPException as e:
            print(f"An error occurred: {e}")


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.message_id in [role_message_id1, role_message_id2]:
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return

        role_id = emoji_to_role.get(payload.emoji.id)
        if role_id is None:
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        try:
            await member.remove_roles(role)
            print(f"Removed role {role.name} from {member.name}")
        except discord.HTTPException as e:
            print(f"An error occurred: {e}")

@bot.command()
async def send_message(ctx):
    channel = bot.get_channel(1091452635728576672)
    bot_channel = bot.get_channel(1096108547051360316)
    
    if channel:
        message = ("💡- Regras \nQuebrar alguma dessas regras resultará num timeout ou ban do servidor \n\n"
                   "💡Não é permitido a propaganda e divulgação de conteúdos não relacionados a programação nos chats. "
                   "Sujeito a timeout ou ban do servidor.\n\n💡Não envie conteúdo NSFW. A postagem de Imagens, vídeos e "
                   "outros conteúdos inapropriados no chat será penalizada com o ban instantâneo.\n\n💡Propague sempre o "
                   "respeito no chat. Discussões inapropriadas de caráter ilegal e/ou preconceituoso e discriminatório "
                   "garantirão banimento instantâneo dos envolvidos.\n\n💡Não ignore os avisos direcionados a você. "
                   "Podemos estar abordando algo importante, fique atento.\n\n💡 Nicks ofensivos e discriminatórios "
                   "garantirão banimento e/ou timeout dos usuários, até que o nome seja alterado.\n\n💡 Não contribua "
                   "para o spam de mensagens no chat.\n\n💡 Não pingue ou marque monitores e coordenadores desnecessariamente, "
                   "somente se necessário\n\n💡 Verifique se sua dúvida já foi feita e/ou respondida, evite o acúmulo de "
                   "dúvidas semelhantes para que os demais participantes com dúvidas distintas também possam ser atendidos\n\n"
                   "Caso esteja ciente das regras, reaja ao emoji abaixo e se encaminhe para o canal <#{}>."
                   .format(bot_channel.id))
        await channel.send(message)
        print("Message sent to the specified channel.")
    else:
        await ctx.send("Channel not found.")
    

def get_quote():
    inspirar = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(inspirar.text)
    quote = json_data[0]['q'] + " - " + json_data[0]['a']
    return(quote)


@bot.event
async def on_ready():
    print(f'{bot.user.name} está pronto para ser utilizado!')
    
@bot.event
async def on_message(message):
    print(message.content)
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(1144664343846334504)
    regras = bot.get_channel(1091452635728576672)
    mensagem = await welcome_channel.send(f"Bem vindo {member.mention}!\nLeia as regras em {regras.mention} ;)")

    await asyncio.sleep(20)
    await mensagem.delete()

@bot.command()
async def inspirar(ctx):
    quote = get_quote()
    await ctx.send(quote)

def load_user_points():
    try:
        with open('user_points.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_user_points(user_points):
    with open('user_points.json', 'w') as f:
        json.dump(user_points, f, indent=4)

@bot.command()
@commands.has_role('Monitores')
async def quiz(ctx):
    pergunta_atual = random.choice(quiz_data)
    await ctx.send(pergunta_atual['pergunta'])

    def check_resposta(m):
        return (
            m.content == pergunta_atual['resposta'] and
            m.channel == ctx.channel and
            m.author != bot.user and
            m.author.id not in answered_users
        )

    answered_users = set()
    user_points = load_user_points()
    pontos = 10

    while pontos >= 1:
        try:
            resposta = await bot.wait_for('message', timeout=30.0, check=check_resposta)
            user_id = resposta.author.id
            user = bot.get_user(user_id)  # Get user object

            if user:
                dm_channel = await user.create_dm()  # Create a private message channel

                user_found = False
                for user_data in user_points:
                    if user_data['user_id'] == user_id:
                        user_data['points'] += pontos
                        user_found = True
                        break


                if not user_found:
                    user_points.append({"user_id": user_id, "points": pontos})

                save_user_points(user_points)

                await dm_channel.send(f"Parabéns, {user.mention}! Você acertou e ganhou {pontos} pontos! "
                                      f"Total acumulado: {next(user['points'] for user in user_points if user['user_id'] == user_id)} pontos")

                pontos -= 1
                answered_users.add(user_id)
        except TimeoutError:
            await ctx.send("Tempo esgotado. A resposta correta era: " + pergunta_atual['resposta'])
            break



@bot.command()
async def monitoria(ctx):
    if ctx.author.id in filaMonitoria:
        await ctx.send(f'{ctx.author.name}, você já está na fila de monitoria! Ka-chow!!!')
    else:
        filaMonitoria.append(ctx.author.id)
        await ctx.send(f'{ctx.author.name}, você foi adicionado à fila de monitoria! Ka-chow!!!')
        await atualizarFila(ctx)
        
@bot.command()
async def fila(ctx):
    await atualizarFila(ctx)

@bot.command()
async def ajuda(ctx):
    await ctx.send(f'Olá Pessoal!\nMe chamo {bot.user.mention} e me encontro no servidor do PetCode para ajudar! \U0001F4A5\n\n\U0001F4A1 **Comandos:**\n\n- Se você quiser participar da monitoria, mande um **!monitoria** para entrar na fila e espere sua vez para ser atendido \U0001F60E\n\n- Se quiser sair da fila, mande **!sairfila** que eu te removerei. \U0001F44D\n\n- Se quiser acessar a lista da fila, mande **!fila**')

@bot.command()
async def sairfila(ctx):
    if ctx.author.id in filaMonitoria:
        filaMonitoria.remove(ctx.author.id)
        await ctx.send(f'{ctx.author.name}, você foi removido da fila de monitoria! Ka-chow!!!')
        await atualizarFila(ctx)
    else:
        await ctx.send(f'{ctx.author.name}, você não está na fila de monitoria! Ka-chow!!!')

@bot.command()
async def duvida(ctx, *args):
    duvida = ' '.join(args)
    duvidas.append(duvida)
    await ctx.send(f'{ctx.author.mention}, Sua dúvida foi recebida! Aguarde a resposta dos Monitores, que iremos te ajudar :) Ka-chow!!!')

@bot.command()
async def listaDuvidas(ctx):
    string_de_duvidas = ''
    for i in range(len(duvidas)):
        string_de_duvidas += f'{i+1} - {duvidas[i]}\n'

    if len(duvidas) < 1:
        await ctx.send('Não há dúvidas no momento...\nCatchuga :(')
    else:
        await ctx.send(string_de_duvidas)

@bot.command()
@commands.has_role('Coordenadores')
async def DevClearLista(ctx):
    for i in range(len(duvidas)):
        duvidas.remove(duvidas[0])

async def atualizarFila(ctx):
    filaString = 'Fila de monitoria:\n'
    if len(filaMonitoria) == 0:
        filaString += ' Vazia :('
    else:
        for i in range(len(filaMonitoria)):
            user = await bot.fetch_user(filaMonitoria[i])
            filaString += f'- {user.name}\n'
    await ctx.send(filaString)

bot.run('MTA5Mjk2NTYwNDY3NzM5ODU0OA.Gg7Fy8.iLfgWQFFOenYA_5yZ5a4fAZEiTJyo_P1t7z-Qo')