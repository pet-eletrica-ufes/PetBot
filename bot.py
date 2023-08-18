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

role_message_id = 0  # ID da mensagem que vai conter as reações
emoji_to_role = {
    discord.PartialEmoji(name='🔴'): 0,  # ID do cargo associado com o emoji '🔴'.
    discord.PartialEmoji(name='🟢'): 0,  # ID do cargo associado com o emoji '🟢'.
    discord.PartialEmoji(name='🔵'): 0,  # ID do cargo associado com o emoji '🔵'.
    }

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """da o cargo baseado no emoji de reacao"""
    if payload.message_id != role_message_id:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    try:
        role_id = emoji_to_role[payload.emoji]
    except KeyError:
        return

    role = guild.get_role(role_id)
    if role is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        return

    try:
        await member.add_roles(role)
        print("Cargo Atribuido Corretamente")
    except discord.HTTPException as e:
        print(f"Um erro ocorreu: {e}")

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """tira o cargo baseado no emoji de reacao"""
    if payload.message_id != role_message_id:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    try:
        role_id = emoji_to_role[payload.emoji]
    except KeyError:
        return

    role = guild.get_role(role_id)
    if role is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        return

    try:
        await member.remove_roles(role)
        print("Cargo Removido Corretamente")
    except discord.HTTPException:
        pass

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
    welcome_channel = bot.get_channel(1091452635728576676)
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
@commands.has_role() #substituir 'nome do cargo' pelo nome do cargo
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

    answered_users = set()  # guarda os id de quem

    user_points = load_user_points()  # carrega pontos do json

    pontos = 10 
    while pontos >= 1:
        try:
            resposta = await bot.wait_for('message', timeout=30.0, check=check_resposta)
            user_id = resposta.author.id

            # procura se o usuário já tem pontos
            user_found = False
            for user in user_points:
                if user['user_id'] == user_id:
                    user['points'] += pontos
                    user_found = True
                    break

            # se não encontrou, cria um novo registro
            if not user_found:
                user_points.append({"user_id": user_id, "points": pontos})

            save_user_points(user_points)  # salva no json

            await ctx.send(f"Parabéns, {resposta.author.mention}! Você acertou e ganhou {pontos} pontos! "
               f"Total acumulado: {next(user['points'] for user in user_points if user['user_id'] == user_id)} pontos")

            pontos -= 1
            answered_users.add(user_id)  # Add user ID to the set
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
async def mensagem(ctx):
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

bot.run('TOKEN')