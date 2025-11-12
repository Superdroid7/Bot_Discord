import os
import discord
from discord.ext import commands
import requests
import config
from autocorrect import Speller 

spell = Speller(lang='es') 
intents = discord.Intents.default()  # Declaro la intención de acceder a diferentes eventos de la API de Discord
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.command()
async def poke(ctx, arg):
    try:
        pokemon = arg.split(" ", 1)[0].lower()
        result = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")
        if result.status_code == 404: 
            await ctx.send("Pokemon no encontrado pai")
        else:
            data = result.json()
            image_url = data["sprites"]["front_default"]

            stats = data.get("stats", [])
            stats_text = ""
            for stat in stats:
                stat_name = stat["stat"]["name"].capitalize()
                base_value = stat["base_stat"]
                stats_text += f"**{stat_name}**: {base_value}\n"
               
            embed = discord.Embed(
                title=f"Estadísticas de {pokemon.capitalize()}",
                description=stats_text,
                color=0x0983D6
            )
            embed.set_image(url=image_url)
               
            await ctx.send(embed=embed)

    except Exception as e:
        print("error: ", e)
           
@poke.error
async def error_type(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("brother me tenes que pasar es un pokemon no un espacio en blanco")

@bot.event
async def on_message(message):
    if message.author.bot == bot.user:  # Ignora mensajes del propio bot para evitar bucles
        return
       
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
       
    palabras = message.content.split()
    palabras_corregidas = []
    tiene_correcciones = False

    for palabra in palabras:
        limpia_palabra = "".join(c for c in palabra if c.isalnum()).lower()  # Limpia la palabra (quita puntuación básica)
        if limpia_palabra:
            correccion = spell(limpia_palabra)
            if correccion and correccion != limpia_palabra:
                palabras_corregidas.append(f"**{palabra}** -> *{correccion}*")
                tiene_correcciones = True
            else:
                palabras_corregidas.append(palabra)
        else:
            palabras_corregidas.append(palabra)

    if tiene_correcciones:
        respuesta = f"oe {message.author.mention} parece que tenes algunos error ortografico, se sugiere la siguiente palabra: \n" + "\n".join(palabras_corregidas)
        await message.reply(respuesta)

    await bot.process_commands(message)  # IMPORTANTE: Procesa comandos después, si los hay

@bot.event
async def on_ready():
    print(f"estamos meloskis {bot.user}")

bot.run(os.getenv('TOKEN')) #para leer el token en railway