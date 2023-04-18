# coding: utf-8
from pdf2image import convert_from_path
from datetime import datetime, date
import asyncio
import requests
import os.path
import json
import time
import sys
import discord
from system.lib import *

Lib = Lib_UsOS()

app_version = "4.0.2"
classbot_folder = f"classbot_folder"
classbot_config_file = (classbot_folder,"classbot_config.json")
edt_database_path = (classbot_folder,"edt_database.json")
edt_path = f"pdf"


programmer = os.path.basename(sys.argv[0])


vals = [classbot_folder, edt_path]

launch_check_edt = True
hide_edt = False
current_semester = "infoS1"

liscInfo = {
    "infoS1": {
        "l1t7": [
            0,
            0,
            0,
            "l1t7.pdf",
            0
        ],
        "l1t5": [
            0,
            0,
            0,
            "l1t5.pdf",
            0
        ],
        "l2t7": [
            0,
            0,
            0,
            "l2t7.pdf",
            0
        ],
        "l2t5": [
            0,
            0,
            0,
            "l2t5.pdf",
            0
        ],
        "l3t7": [
            0,
            0,
            0,
            "l3t7.pdf",
            0
        ],
        "l3t5": [
            0,
            0,
            0,
            "l3t5.pdf",
            0
        ],
        "l4t7": [
            0,
            0,
            0,
            "l4t7.pdf",
            0
        ],
        "l3t7miage": [
            0,
            0,
            0,
            "l3t7miage.pdf",
            0
        ],
        "l4t7miage": [
            0,
            0,
            0,
            "l4t7miage.pdf",
            0
        ]
    },
    "infoS2": {
        "l1t7": [
            0,
            0,
            0,
            "l1t7.pdf",
            0
        ],
        "l1t5": [
            0,
            0,
            0,
            "l1t5.pdf",
            0
        ],
        "l2t7": [
            0,
            0,
            0,
            "l2t7.pdf",
            0
        ],
        "l2t5": [
            0,
            0,
            0,
            "l2t5.pdf",
            0
        ],
        "l3t7": [
            0,
            0,
            0,
            "l3t7.pdf",
            0
        ],
        "l3t5": [
            0,
            0,
            0,
            "l3t5.pdf",
            0
        ],
        "l3t7miage": [
            0,
            0,
            0,
            "l3t7miage.pdf",
            0
        ]
    }
}

@Lib.event.event()
async def on_ready():
    global bot_config, launch_check_edt, current_semester, liscInfo, hide_edt
    for name in vals:
        Lib.save.add_folder(name)
    
    try:
        bot_config = json.loads(Lib.save.read(path=classbot_config_file[0], name=classbot_config_file[1]))
        launch_check_edt = bot_config["edt"]
        hide_edt = bot_config["hide"]

    except (FileNotFoundError, KeyError):
        Lib.save.add_file(path=classbot_config_file[0], name=classbot_config_file[1])
        Lib.save.write(path=classbot_config_file[0], name=classbot_config_file[1], data=json.dumps(get_config(), indent=4))


    current_semester = "infoS1"
    try:
        liscInfo = json.loads(Lib.save.read(path=edt_database_path[0], name=edt_database_path[1]))[current_semester]
        
    except (FileNotFoundError, KeyError, json.decoder.JSONDecodeError):
        Lib.save.add_file(path=edt_database_path[0], name=edt_database_path[1], over_write=True)
        Lib.save.write(path=edt_database_path[0], name=edt_database_path[1], data=json.dumps(liscInfo))
    

def get_config():
    return {"edt": launch_check_edt, "hide": hide_edt}



intents = discord.Intents.default()
intents.members = True



def convert_time(value: int):
    val3, val2, val = 0, value//60, value % 60
    message = f"{val2}min {val}s."

    if val2 > 60:
        val3, val2 = val2//60, val2 % 60
        message = f"{val3}h {val2}min {val}s."

    return message


def update_edt_database(key, value):
    global liscInfo
    database = json.loads(Lib.save.read(path=edt_database_path[0], name=edt_database_path[1]))

    val = database[current_semester].get(key)

    if not val:
        return False

    try:
        database[current_semester][key][0] = value[0]
        database[current_semester][key][1] = value[1]
        database[current_semester][key][2] = value[2]
    except Exception:
        return False
        
    Lib.save.write(path=edt_database_path[0], name=edt_database_path[1], data=json.dumps(database, indent=4))
    
    liscInfo = database[current_semester]
    return True


def convert_url(url: str = "", cle_dico=None):
    if "edtweb2" not in url:
        return False

    current_date = date.isocalendar(datetime.now())
    num_semaine = current_date[1]

    if current_date[2] > 5:
        num_semaine += 1

    temp_url = url.split("edtweb2")[1:].pop(0)
    temp_url = temp_url.split("/")[1:]

    magic = temp_url.pop(0).split(".")
    magic2 = temp_url[0].replace("PDF_EDT_", "")
    magic2 = magic2.split(".pdf")[0].split("_")

    id0 = int(magic.pop(0))
    id1 = int(magic2.pop(0))

    chiffre_temporaire = int(magic2[0])

    temp = int(magic[0])

    if num_semaine - chiffre_temporaire < 0:
       pass
        #return False

    id2 = chiffre_temporaire - temp

    value = [id0, id1, id2]

    infos = check_edt_info(value, decal=8 if cle_dico=="l1t7"else 0)

    try:
        size = int(infos["Content-Length"])
    except KeyError:
        size = 0
    status = int(infos["status"])

    if size < 500 or status != 200:
        return False

    return value


def is_it_me(ctx):
    if ctx.author.id in (366055261930127360, 649532920599543828):
        return True


def is_dev(ctx):
    if ctx.author.id in (366055261930127360, 649532920599543828):
        return True

    member = ctx.message.author
    roles = [role.name for role in member.roles]
    admins = ["Bot Dev"]

    for role in roles:
        if role in admins:
            return True

def is_in_maintenance(ctx):
    if ctx.author.id in (366055261930127360, 649532920599543828):
        return True

    member = ctx.message.author
    roles = [role.name for role in member.roles]
    admins = ["Admin", "Modo", "Bot Dev"]

    for role in roles:
        if role in admins:
            return True

        if "maint." in role:
            return True


timer = time.time()

async def binaire(ctx, message):
    message = "Error!"
    try:
        message = f"Binaire : {bin(int(message))[2:]}\nEntier : {int(message, 2)}"
    except ValueError:
        message = f"Entier : {int(message, 2)}"

    await ctx.send(message)

#@Lib.app.slash(name="sedt", description="Switch auto edt update on/off")
#@Lib.app.command(name="sedt", aliases=["sedt"], help_text="Switch auto edt update on/off")
async def sedt(ctx:discord.Interaction, auto_check=launch_check_edt, hide = hide_edt):
    global launch_check_edt, hide_edt

    launch_check_edt = auto_check
    hide_edt = hide
    #Lib.save.add_file(path=classbot_config_file[0], name=classbot_config_file[1])
    Lib.save.write(path=classbot_config_file[0], name=classbot_config_file[1], data=json.dumps(get_config(), indent=4))
    
    await valide_intaraction(ctx)
    #await ctx.channel.send(f"check edt set on : {val}")

#@Lib.app.command(name="uptedt", aliases=["uptedt"], checks=[Lib.is_in_staff])
async def uptedt(ctx: discord.Interaction, url: str, cle_dico: str = ""):
    gestion = "maint."
    val = convert_url(url, cle_dico)

    if not val:
        await ctx.response.send_message(content="`Error! Something went wrong with the url!`", ephemeral=True)
        return

    member = ctx.message.author
    roles = [role.name for role in member.roles]

    if "Admin" not in roles:
        for role in roles:
            if gestion not in role:
                continue

            role = role.lower().replace(gestion, "").replace(" ", "")

            if role in liscInfo.keys():
                cle_dico = role
                break

    if not cle_dico:
        await ctx.response.send_message(content="`Error! Something went wrong with the role!`", ephemeral=True)
        return

    check = update_edt_database(cle_dico, val)

    if not check:
        await ctx.response.send_message(content="`Error! Something went wrong with the role!`", ephemeral=True)
        return

    await ctx.response.send_message(content="`EDT database successfully updated!`", ephemeral=True)

@Lib.app.command(name="getdb", help_text="Envoie la bd")
async def getdb(ctx):
    await ctx.send(file=discord.File(Lib.save.open(path=edt_database_path[0], name=edt_database_path[1]), "edt_database.json"))


async def pushdb(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Error! No file attached!")
        return

    attachment = ctx.message.attachments[0].url
    name = ctx.message.attachments[0].filename

    if name.lower() != "edt_database.json":
        await ctx.send("Error! Not a valid filename!")
        return

    with requests.get(attachment, stream=True) as r:
        for chunk in r.iter_content(1000):
            Lib.save.write(path=edt_database_path[0], name=edt_database_path[1], data=chunk, binary_mode=True)

    await ctx.send(f"File installed at : {edt_database_path}")

@Lib.app.slash(name="edt", description="Envoie ton emploi du temps", direct_command=True)
async def edt(ctx:discord.Interaction, cle_dico:str="", plus:int=0):
    #plus = plus.replace("+", "")

    if cle_dico not in liscInfo.keys():
        cle_dico = None

    if cle_dico==None:
        member = ctx.user
        roles = [role.name for role in member.roles]
        for role in roles:
            role = role.lower().replace(" ", "")
            if role in liscInfo.keys():
                cle_dico = role
                
    if cle_dico==None:
        await ctx.response.send_message(content="Vous n'avez pas de role assosié à votre classe, prenez en un ou précisez votre classe lors de la commande.", ephemeral=True)
        return
    pdf_name = f"ask-{cle_dico}.pdf"

    try:
        plus = int(plus)
    except Exception:
        plus = 0

    corrupt = False
    infos = check_edt_info(liscInfo[cle_dico], plus, 8 if cle_dico=="l1t7"else 0)
    try:
        size = int(infos["Content-Length"])
    except KeyError:
        size = 0
    status = int(infos["status"])

    if (size < 500) or (status != 200):
        pdf_name = f"{cle_dico}.pdf"
        corrupt = True
        print("pass")
    else:
        download_edt(pdf_name, liscInfo[cle_dico], plus, decal=8 if cle_dico=="l1t7" else 0)
    channel = ctx.channel

    message = f"EDT pour : {cle_dico.upper()}"
    if plus:
        message += f' ({"+" if plus >0 else ""}{plus})'

    current_date = date.isocalendar(datetime.now())
    week_end = False
    if current_date[2] > 5:
        week_end = True

    if corrupt and week_end:
        await ctx.response.send_message(content=f"\nURL générée invalide, voir sur le site, en attendant un Admin\n`Ceci est une ancienne version!`", ephemeral=True)
        # await channel.send("`URL générée invalide, contactez un Admin pour de l'aide`")

    elif corrupt:
        message += f"\nURL générée invalide, voir sur le site, en attendant un Admin\n`Ceci est une ancienne version!`"
        # message += "\n`EDT Corrompu! Ceci est une ancienne version!`"
    else:
        pass
    
    try:
        await send_edt_to_chat(ctx, message, pdf_name, cle_dico, plus, liscInfo[cle_dico])
    except Exception as error:
        print(error)



async def edtpush(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Error! No file attached!")
        return

    attachment = ctx.message.attachments[0].url
    name = ctx.message.attachments[0].filename

    if name.lower() in ["liste_de_fichiers"]:
        await ctx.send("Error! Forbidden files!")
        return

    with requests.get(attachment, stream=True) as r:
        pat = f"{edt_path}/{name}"
        for chunk in r.iter_content(1000):
            Lib.save.add_file(path=edt_path, name=name)
            Lib.save.write(name,edt_path, chunk, True)

    await ctx.send(f"File installed at : {pat}")


# ----------------------------------- EDT ----------------------------------
class edt_view(discord.ui.View):
    def __init__(self, key, plus, ctx, *, timeout=180) -> None:
        super().__init__(timeout=timeout)
        self.key = key
        self.plus = plus
        self.ctx = ctx
        indices = liscInfo[self.key]
        current_date = date.isocalendar(datetime.now())
        num_semaine = current_date[1]
        annee = current_date[0]

        if current_date[2] > 5:
            num_semaine += 1

        while num_semaine-indices[2] < 0:
            num_semaine += 1
        url_edt = f"http://applis.univ-nc.nc/gedfs/edtweb2/{indices[0]}.{num_semaine - indices[2] + self.plus}/PDF_EDT_{indices[1]}_{num_semaine + self.plus}_{annee}.pdf"
        self.download = discord.ui.Button(label="Download", url=url_edt)

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji="\U00002b05")
    async def prev_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await edt(interaction, cle_dico=self.key, plus=self.plus-1)
        #await interaction.response.send_message(content="ok", ephemeral=True)

    @discord.ui.button(label="Aujourd'hui", style=discord.ButtonStyle.gray, emoji="\U0001F4C5")
    async def today_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await edt(interaction, cle_dico=self.key, plus=0)
        #await interaction.response.send_message(content="ok", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji="\U000027a1")
    async def next_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await edt(interaction, cle_dico=self.key, plus=self.plus+1)
        #await interaction.response.send_message(content="ok", ephemeral=True)

    async def on_timeout(self):
        await self.ctx.edit_original_response(view=None)
    
    def init_download(self):
        self.add_item(self.download)


def compare_edt(pdf_name, indices: list = None, plus: int = 0):
    #print("compare_edt")
    path_to_pdf = (pdf_name,edt_path)

    try:
        poid_old = os.path.getsize(Lib.save.get_full_path(*path_to_pdf))
    except Exception:
        poid_old = 0
    #print("check_edt_info start")
    infos = check_edt_info(indices, plus)
    #print("check_edt_info end")
    try:
        poid_new = int(infos["Content-Length"])
    except KeyError:
        return 5

    # status = infos["status"]

    if poid_old == poid_new and poid_new < 500:
        # même taille et corrompu
        return 5

    elif poid_old == poid_new and poid_new < 2000:
        # même taille et erreur serveur
        return 6

    elif poid_old == poid_new:
        # même taille
        return 2

    elif poid_new < 500:
        # pdf corrompu
        return 3

    elif poid_new < 2000:
        # erreur serveur
        return 4

    return 0


def download_edt(pdf_name: str, indices: list = None, plus: int = 0, decal=0):
    # permet de transfomer la date en compteur du jour dans la semaine
    # et de la semaine dans l'année (retourne l'année, le numéro de semaine et le numéro du jour)
    # utilisé pour les ids du liens pour l'edt
    
    current_date = date.isocalendar(datetime.now())

    num_semaine = current_date[1]
    annee = current_date[0]

    if current_date[2] > 5:
        num_semaine += 1

    while num_semaine-indices[2] < 0:
        num_semaine += 1

    url_edt = "http://applis.univ-nc.nc/gedfs/edtweb2/{}.{}/PDF_EDT_{}_{}_{}.pdf"
    url = url_edt.format(indices[0], num_semaine - indices[2] + plus + decal, indices[1], num_semaine + plus, annee)

    path_to_pdf = f"{edt_path}/{pdf_name}"
    Lib.save.add_file(path=edt_path, name=pdf_name, over_write=True)
    with requests.get(url, stream=True) as r:
        for chunk in r.iter_content(1000):
            data=Lib.save.read(path=edt_path, name=pdf_name, binary_mode=True)
            Lib.save.write(path=edt_path, name=pdf_name, data=data+chunk, binary_mode=True)
    return path_to_pdf


def check_edt_info(indices: list = None, plus: int = 0, decal=0):
    # permet de transfomer la date en compteur du jour dans la semaine
    # et de la semaine dans l'année (retourne l'année, le numéro de semaine et le numéro du jour)
    # utilisé pour les ids du liens pour l'edt

    current_date = date.isocalendar(datetime.now())

    num_semaine = current_date[1]
    annee = current_date[0]

    if current_date[2] > 5:
        num_semaine += 1

    while num_semaine-indices[2] < 0:
        num_semaine += 1
    
    url_edt = "http://applis.univ-nc.nc/gedfs/edtweb2/{}.{}/PDF_EDT_{}_{}_{}.pdf"
    url = url_edt.format(indices[0], num_semaine - indices[2] + plus + decal, indices[1], num_semaine + plus, annee)

    edt_info = {}

    val = requests.head(url)
    val.close()

    edt_info = dict(val.headers)
    edt_info["status"] = val.status_code

    return edt_info


async def send_edt_to_chat(ctx:discord.Interaction, message:str, pdf_name: str, key:str, plus:int, indices: list = None):
    if not Lib.save.existe(path=edt_path, name=pdf_name):
        embed = discord.Embed(title=message, description=f"Aucun EDT disponible", color=discord.Color.yellow())
        if type(ctx) == discord.Interaction:
            await ctx.response.send_message(embed=embed, ephemeral=True)
        elif type(ctx) == discord.TextChannel:
            await ctx.send(embed=embed)
        return
    edt_id = indices[0]

    pages = convert_from_path(Lib.save.get_full_path(name=pdf_name, path=edt_path), 150)
    i = 1
    
    for page in pages:
        embed = discord.Embed(title=message, description=f"", color=discord.Color.yellow())
        file = Lib.save.get_full_path(name=f"edt{edt_id}_{i}.jpg", path=edt_path)
        page.save(file, 'JPEG')
        file=(discord.File(file,f"edt{edt_id}_{i}.jpg"))
        embed.set_image(url=f"attachment://edt{edt_id}_{i}.jpg")
        if i==1:
            embed.description = f"({i}/{len(pages)})" if len(pages)>1 else ""

            if type(ctx) == discord.Interaction:
                try:
                    view = edt_view(key, plus, ctx)
                    view.init_download()
                    await ctx.response.send_message(embed=embed,file=file, ephemeral=hide_edt, view=view)
                except Exception as error:
                    print(error)

            else:
                await ctx.send(embed=embed, file=file)

        else:
            embed.footer = f"({i}/{len(pages)})" 
            await ctx.followup.send(embed=embed,file=file, ephemeral=hide_edt)
        i += 1

async def check_edt_update(pdf_name: str, cle_dico: str, chat_id: int, dico_licence: dict = liscInfo):
    #print("check_edt_update start")
    #print(dico_licence[current_semester])
    check = compare_edt(pdf_name, dico_licence[current_semester][cle_dico])
    corrupt = False
    
    if check == 0:
        download_edt(pdf_name, dico_licence[current_semester][cle_dico], decal=8 if cle_dico=="l1t7" else 0)

    elif check in (2, 5, 6):
        return

    elif check in (3, 4):
        corrupt = True
        return

    servers = Lib.client.guilds
    
    for server in servers:
        chat = server.text_channels
        for channel in chat:
            if chat_id == channel.id:
                formated_role = cle_dico.upper().replace("MIAGE", " miage")
                role = discord.utils.get(server.roles, name=formated_role)
                message = ""
                if corrupt:
                    dev = discord.utils.get(server.roles, name="Bot Dev")
                    message += f"Changement d'edt pour : {role.mention} (pdf corrompu, voir sur le site, en attendant un {dev.mention})\n`Ceci est une ancienne version!`" # role.mention dev.mention
                else:
                    message += f"Changement d'edt pour : {role.mention}"

                await send_edt_to_chat(channel, message, pdf_name, cle_dico, 0, dico_licence[current_semester][cle_dico])
                break

# -------------------------------------- EDT UPDATE ------------------------------

@Lib.app.loop(minutes=15)
async def check_edt_lisc():
    try:
        if not launch_check_edt:
            print("returned")
            return

        this_time = datetime.now()
        database = json.loads(Lib.save.read(path=edt_database_path[0], name=edt_database_path[1]))

        class_liste = [[stat[-2], _class, stat[-1]] for _class,stat in database[current_semester].items() if stat[-1]!=0]

        if not (6 <= this_time.hour <= 22):
            return

        for i in range(len(class_liste)):
            await check_edt_update(*class_liste[i], dico_licence=database)
            await asyncio.sleep(10)
    except Exception as error:
        print("errors")
        raise error

# -------------------------------------- EDT Config ---------------------------------

# ----------------------------------------- View ------------------------------------

class Uptedt_view(discord.ui.View):
    def __init__(self, *, ctx: discord.Interaction, url="", _class=None, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.url = url
        self._class = _class

        self.add_item(self.Url_button(view=self, label="URL", style=discord.ButtonStyle.gray if self.url=="" else discord.ButtonStyle.green))
        self.add_item(self.Class_select(view=self, placeholder="Choisir une classe"))
        self.add_item(self.Valide_button(view=self, label="Valider", style=discord.ButtonStyle.blurple, disabled=(self.url=="" or self._class==None)))

    class Url_button(discord.ui.Button):
        def __init__(self, *, view, style: discord.ButtonStyle = discord.ButtonStyle.secondary, label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None, row: Optional[int] = None):
            super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
            self.per_view = view

        async def callback(self, interaction: discord.Interaction) -> Any:
            await interaction.response.send_modal(Uptedt_modal(view=self.per_view, title="URL"))

    class Class_select(discord.ui.Select):
        def __init__(self, *, view, custom_id: str = MISSING, placeholder: Optional[str] = None, min_values: int = 1, max_values: int = 1, options: List[discord.SelectOption] = MISSING, disabled: bool = False, row: Optional[int] = None) -> None:
            self.per_view = view
            database = json.loads(Lib.save.read(path=edt_database_path[0], name=edt_database_path[1]))
            keys = database[current_semester].keys()
            options = [discord.SelectOption(label=key, default=True if self.per_view._class == key else False) for key in keys]
            super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=options, disabled=disabled, row=row)

        async def callback(self, interaction: discord.Interaction) -> Any:
            await updtedt_menu(self.per_view.ctx, self.per_view.url, self.values[0])
            await valide_intaraction(interaction)

    class Valide_button(discord.ui.Button):
        def __init__(self, *, view, style: discord.ButtonStyle = discord.ButtonStyle.secondary, label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None, row: Optional[int] = None):
            super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
            self.edt_url = view.url
            self._class = view._class

        async def callback(self, interaction: discord.Interaction) -> Any:
            await uptedt(interaction, self.edt_url, self._class)

class EditChannel_view(discord.ui.View):
    def __init__(self, *, ctx: discord.Interaction, _class=None, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.ctx=ctx
        self.add_item(self.Back_button(ctx=self.ctx, label="Back"))
        self.add_item(self.ClassSelect(ctx=self.ctx, _class=_class, placeholder="Choisir une class"))
        if _class!=None:
            self.add_item(self.ChannelSelect(ctx=self.ctx, _class=_class, placeholder="Choisir un channel"))

    class Back_button(discord.ui.Button):
        def __init__(self, *, ctx: discord.Interaction, style: discord.ButtonStyle = discord.ButtonStyle.secondary, label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None, row: Optional[int] = None):
            super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
            self.ctx=ctx

        async def callback(self, interaction: discord.Interaction) -> Any:
            await config(self.ctx)
            await valide_intaraction(interaction)

    class ClassSelect(discord.ui.Select):
        def __init__(self, *, ctx: discord.Interaction, _class=None, custom_id: str = MISSING, placeholder: Optional[str] = None, min_values: int = 1, max_values: int = 1, options: List[discord.SelectOption] = MISSING, disabled: bool = False, row: Optional[int] = None) -> None:
            self.ctx = ctx
            database = json.loads(Lib.save.read(path=edt_database_path[0], name=edt_database_path[1]))
            keys = database[current_semester].keys()
            options = [discord.SelectOption(label=key, default=(key ==_class)) for key in keys]
            super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=options, disabled=disabled, row=row)

        async def callback(self, interaction: discord.Interaction) -> Any:
            await channel_edit_menu(self.ctx, self.values[0])
            await valide_intaraction(interaction)

    class ChannelSelect(discord.ui.ChannelSelect):
        def __init__(self, *, ctx: discord.Interaction, _class, custom_id: str = MISSING, channel_types: List[discord.ChannelType] = MISSING, placeholder: Optional[str] = None, min_values: int = 1, max_values: int = 1, disabled: bool = False, row: Optional[int] = None) -> None:
            super().__init__(custom_id=custom_id, channel_types=channel_types, placeholder=placeholder, min_values=min_values, max_values=max_values, disabled=disabled, row=row)
            self.ctx = ctx
            self._class = _class

        async def callback(self, interaction: discord.Interaction) -> Any:
            database = json.loads(Lib.save.read(path=edt_database_path[0], name=edt_database_path[1]))
            for semestre in ["infoS1","infoS2"]:
                if self._class in database[semestre].keys():
                    database[semestre][self._class][-1]=self.values[0].id
                    Lib.save.write(path=edt_database_path[0], name=edt_database_path[1], data=json.dumps(database))
                    await channel_edit_menu(self.ctx)                     
                    await valide_intaraction(interaction)

class Config_view(discord.ui.View):
    def __init__(self, *, ctx: discord.Interaction, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.ctx=ctx

    @discord.ui.button(label="Update EDT",style=discord.ButtonStyle.gray)
    async def uptedt_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await updtedt_menu(self.ctx)
        await valide_intaraction(interaction)

    @discord.ui.button(label="Auto EDT Check",style=discord.ButtonStyle.gray)
    async def sedt_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await sedt(interaction, not launch_check_edt)
        await config(self.ctx)
        
    @discord.ui.button(label="EDT Visibility",style=discord.ButtonStyle.gray)
    async def hide_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await sedt(interaction, hide = not hide_edt)
        await config(self.ctx)

    @discord.ui.button(label="EDT Notification",style=discord.ButtonStyle.gray)
    async def channel_edit_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await channel_edit_menu(self.ctx)
        await valide_intaraction(interaction)

# ----------------------------------------- Modal -----------------------------------

class Uptedt_modal(discord.ui.Modal):
    def __init__(self, *, view: Uptedt_view, title: str = MISSING, timeout: Optional[float] = None, custom_id: str = MISSING) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.url = discord.ui.TextInput(label="url", placeholder="//applis.univ-nc.nc/gedfs/edtweb2/{}.{}/PDF_EDT_{}_{}_{}.pdf")
        self.add_item(self.url)
        self.per_view = view

    async def on_submit(self, interaction: discord.Interaction) -> None:
        val = convert_url(self.url.__str__(),self.per_view._class)
        if not val:
            raise Exception()
        else:
            await updtedt_menu(self.per_view.ctx, self.url.__str__(), self.per_view._class)
            await valide_intaraction(interaction)

# ----------------------------------------- Menu ------------------------------------

async def updtedt_menu(ctx: discord.Interaction, url="", _class=None):
    embed=discord.Embed(title=":gear:  ClassBot EDT Config")
    embed.description = "Update EDT url"
    await ctx.edit_original_response(embed=embed, view=Uptedt_view(ctx=ctx, url=url, _class=_class))

async def channel_edit_menu(ctx: discord.Interaction, _class=None):
    embed=discord.Embed(title=":gear:  ClassBot EDT Config")
    embed.description = "Edit Class Channel"
    await ctx.edit_original_response(embed=embed, view=EditChannel_view(ctx=ctx, _class=_class))

@Lib.app.config()
async def config(ctx: discord.Interaction):
    if not ctx.response.is_done():
        await ctx.response.send_message(embed=discord.Embed(title="Chargement..."), ephemeral=True)
    embed=discord.Embed(title=":gear:  ClassBot EDT Config")
    embed.add_field(name="Info :", value=f"Auto EDT check : {'actived' if launch_check_edt else 'disactived'}")
    embed.add_field(name="Info :", value=f"EDT otification : {'hide' if hide_edt else 'show'}")
    await ctx.edit_original_response(embed=embed, view=Config_view(ctx=ctx))
