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
intents.typing = False
intents.presences = False

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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='!ajuda p/ ver comandos'))
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

    await asyncio.sleep(120)
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

    user_points = load_user_points()
    responded_users = set()  # Conjunto para rastrear quem já respondeu
    max_responses = 5  # Máximo de respostas aceitas por pergunta (pode ser ajustado)

    def check_resposta(m):
        return (
            m.channel == ctx.channel and
            m.author != bot.user and
            m.author.id not in responded_users  # Verifica se o usuário já respondeu
        )

    respostas_corretas = 0

    try:
        while respostas_corretas < max_responses:
            resposta = await bot.wait_for('message', timeout=30.0, check=check_resposta)
            user_id = resposta.author.id
            user = bot.get_user(user_id)

            if resposta.content.lower() == pergunta_atual['resposta'].lower():
                respostas_corretas += 1
                responded_users.add(user_id)  # Marca o usuário como já tendo respondido

                # Atualiza os pontos do usuário
                user_found = False
                for user_data in user_points:
                    if user_data['user_id'] == user_id:
                        user_data['points'] += 1
                        user_found = True
                        break

                if not user_found:
                    user_points.append({"user_id": user_id, "points": 1})

                save_user_points(user_points)

                # Envia mensagem privada ao usuário
                total_pontos = next(user['points'] for user in user_points if user['user_id'] == user_id)
                dm_channel = await user.create_dm()
                await dm_channel.send(f"Parabéns, {user.mention}! Você acertou e ganhou 1 ponto! "
                                      f"Total acumulado: {total_pontos} pontos")

            else:
                responded_users.add(user_id)  # Marca o usuário, mesmo com resposta incorreta
                await ctx.send(f"{resposta.author.mention} errou! A resposta correta é {pergunta_atual['resposta']}.")

    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado! O quiz terminou.")

    if respostas_corretas == max_responses:
        await ctx.send("Número máximo de respostas corretas alcançado! O quiz terminou.")

@bot.command()
async def pontos(ctx):
    """
    Comando para usuários consultarem seus pontos acumulados.
    """
    user_points = load_user_points()
    user_id = ctx.author.id
    user = bot.get_user(user_id)

    if user:
        pontos_user = next((user['points'] for user in user_points if user['user_id'] == user_id), 0)
        await ctx.send(f"{user.mention}, você tem {pontos_user} pontos acumulados no quiz!")
    else:
        await ctx.send("Não foi possível encontrar suas informações.")




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
    """
    Envia uma mensagem explicando os comandos disponíveis e como utilizá-los.
    """
    ajuda_message = (
        f"Olá Pessoal!\nMe chamo {bot.user.mention} e estou aqui no servidor do PetCode para ajudar! 💥\n\n"
        f"💡 **Comandos Disponíveis:**\n\n"
        f"**!monitoria** - Entra na fila de monitoria para receber ajuda. Você será atendido na ordem da fila. 😎\n"
        f"**!sairfila** - Sai da fila de monitoria caso você não precise mais de ajuda. 👍\n"
        f"**!fila** - Mostra a lista atual de pessoas na fila de monitoria. 📋\n"
        f"**!duvida [sua dúvida]** - Envia uma dúvida específica para os monitores responderem. 🔍\n"
        f"**!listaDuvidas** - Exibe a lista de dúvidas que foram enviadas e estão aguardando resposta. 📜\n"
        f"**!listaDuvidasResolvidas** - Exibe a lista de dúvidas que já foram resolvidas. ✅\n\n"
        f"Para mais informações, você pode sempre digitar **!ajuda**."
    )
    await ctx.send(ajuda_message)

@bot.command()
@commands.has_any_role('Coordenadores', 'Monitores')
async def ajuda_admin(ctx):
    """
    Envia uma mensagem com os comandos disponíveis para administradores, coordenadores e monitores.
    """
    ajuda_admin_message = (
        f"👮 **Comandos Administrativos Disponíveis:**\n\n"
        f"**!removerDuvida [número]** - Remove uma dúvida da lista de dúvidas ativas. Use o número da dúvida na lista. 🗑️\n"
        f"**!marcarResolvida [número]** - Marca uma dúvida como resolvida e a move para a lista de dúvidas resolvidas. ✅\n"
        f"**!DevClearListaDuvidas** - Limpa completamente a lista de dúvidas ativas. ⚠️ Use com cuidado! ⚠️\n"
        f"**!DevClearListaResolvidas** - Limpa completamente a lista de dúvidas resolvidas. ⚠️ Use com cuidado! ⚠️\n"
        f"**!quiz** - Inicia um quiz para os membros do servidor responderem. 🧠\n"
        f"\nEsses comandos são restritos a coordenadores e monitores para gerenciamento eficaz do servidor."
    )
    await ctx.send(ajuda_admin_message)


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

# Nova lista para armazenar dúvidas resolvidas
duvidas_resolvidas = []

@bot.command()
@commands.has_role('Monitores')
async def removerDuvida(ctx, numero: int):
    """
    Remove uma dúvida específica da lista pelo seu número.
    """
    if 1 <= numero <= len(duvidas):
        duvida_removida = duvidas.pop(numero - 1)
        await ctx.send(f'A dúvida "{duvida_removida}" foi removida da lista! Ka-chow!!!')
        await atualizarFila(ctx)  # Se necessário atualizar a fila de monitoria
    else:
        await ctx.send(f'Número inválido. Por favor, escolha um número entre 1 e {len(duvidas)}.')

@bot.command()
@commands.has_role('Monitores')
async def marcarResolvida(ctx, numero: int):
    """
    Marca uma dúvida como resolvida e a move para uma lista de dúvidas resolvidas.
    """
    if 1 <= numero <= len(duvidas):
        duvida_resolvida = duvidas.pop(numero - 1)
        duvidas_resolvidas.append(duvida_resolvida)
        await ctx.send(f'A dúvida "{duvida_resolvida}" foi marcada como resolvida e movida da lista! Ka-chow!!!')
    else:
        await ctx.send(f'Número inválido. Por favor, escolha um número entre 1 e {len(duvidas)}.')

@bot.command()
async def listaDuvidasResolvidas(ctx):
    """
    Lista todas as dúvidas que foram marcadas como resolvidas.
    """
    if len(duvidas_resolvidas) == 0:
        await ctx.send('Não há dúvidas resolvidas até o momento... Ka-chow!!!')
    else:
        string_de_duvidas_resolvidas = 'Dúvidas resolvidas:\n'
        for i, duvida in enumerate(duvidas_resolvidas, start=1):
            string_de_duvidas_resolvidas += f'{i} - {duvida}\n'
        await ctx.send(string_de_duvidas_resolvidas)

@bot.command()
@commands.has_role('Coordenadores')
async def DevClearListaDuvidas(ctx):
    for i in range(len(duvidas)):
        duvidas.remove(duvidas[0])

@bot.command()
@commands.has_role('Coordenadores')
async def DevClearListaResolvidas(ctx):
    for i in range(len(duvidas_resolvidas)):
        duvidas_resolvidas.remove(duvidas_resolvidas[0])

async def atualizarFila(ctx):
    filaString = 'Fila de monitoria:\n'
    if len(filaMonitoria) == 0:
        filaString += ' Vazia :('
    else:
        for i in range(len(filaMonitoria)):
            user = await bot.fetch_user(filaMonitoria[i])
            filaString += f'- {user.name}\n'
    await ctx.send(filaString)

@bot.event
async def on_message(message):
    # Verifica se a mensagem veio de um DM e se contém anexos
    if isinstance(message.channel, discord.DMChannel) and message.attachments:
        # Envia uma confirmação ao usuário
        await message.channel.send("Arquivo recebido! Enviarei para o canal adequado.")
        
        # Especifica o ID do canal no servidor onde os arquivos serão enviados
        target_channel_id = 1278055577100226682  # Substitua pelo ID do canal desejado
        target_channel = bot.get_channel(target_channel_id)

        if target_channel is not None:
            for attachment in message.attachments:
                # Envia o arquivo ao canal especificado
                await target_channel.send(f"Arquivo enviado por {message.author}:", file=await attachment.to_file())
            await message.channel.send("Arquivo enviado com sucesso!")
        else:
            await message.channel.send("Ocorreu um erro ao tentar enviar o arquivo. Canal não encontrado.")
    else:
        # Processa outros comandos e mensagens
        await bot.process_commands(message)


bot.run('token')