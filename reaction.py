from pyrogram import Client, filters 
from pyrogram.types import (ReplyKeyboardMarkup )
from collections import defaultdict
import sqlite3 , os , requests , json , asyncio , random

def last_message_func(): # for save steps
    return defaultdict(last_message_func)
lm = last_message_func() # for save steps


pannel_admin = [["Add Token ➕"  , "Delete Token ➖" ] , [ "On Robot 🌕" , "Off Robot 🌑"] , ["Change Emoji 🤡" , "Status ⏳"] , ["Send Database📄"]]

emoji = "🤣" # Your Bot Send Reaction This Emoji To Your Posts

bot_status = True # To make Bot off Or On At The First Bot is ON

admins = [] # List Of Your Admins s Id in Telegram 

report = 0000 # Telegram Id For Send Report Of The Activity

api_id = 0000 # Your Api Id The Same As You Have Received From The Telegram Site ( https://my.telegram.org/auth?to=apps )
api_hash = 0000 # Your Api Hash The Same As You Have Received From The Telegram Site ( https://my.telegram.org/auth?to=apps )
bot_token = 0000 # Your Main bot Token The Same As You Have Received From The Bot Father ( https://t.me/BotFather)

conn = sqlite3.connect("database.db")

app = Client("bot", api_id = api_id , api_hash = api_hash, bot_token = bot_token)


def create_table_Channel() :

    cursor = conn.cursor()
    columns = {"bots" : [("token", "TEXT", True),("id", "TEXT", False),("time", "TEXT", False)]}


    for i in columns.keys() :

        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS `{i}` (
                {", ".join("`"+col[0]+"` "+col[1]+" PRIMARY KEY" if col[2] else "`"+col[0]+"` "+col[1] for col in columns[i])}
            );
        """
        cursor.execute(create_table_sql)

    conn.commit()
    cursor.close()

create_table_Channel()

@app.on_message(filters.command("start")) 
async def start(Client , m): # ✔️

    ID = m.from_user.id 
    if ID in admins :
        lm[ID] = "start"
        await m.reply_text(text = "Wellcome to Main Menu🏠" , reply_markup = ReplyKeyboardMarkup (pannel_admin , resize_keyboard=True ))

@app.on_message(filters.channel)
async def channel(client , m):

    global bot_status , report , emoji

    if bot_status :

        tokens_list = await get_data()

        count = 0

        for i in tokens_list :

            token = i[0]
            response = requests.post("https://api.telegram.org/bot" + token + "/" + 'setmessagereaction', data={'chat_id': m.chat.id,'message_id': m.id,'reaction': json.dumps([{'type': "emoji", "emoji": emoji}])})
            
            await asyncio.sleep(random.choice([0.5 , 0.25 , 0.2 , 0.4 , 0.3 , 0.1 , 0.45 , 0.2 , 0.3 , 0.35]))

            if response.status_code == 200 :
                count += 1
    
        await app.send_message(chat_id=report, text=f'''
All Efforts : {len(tokens_list)}

Successful All Efforts : {count}

Post : {m.link}''' , disable_web_page_preview=True)

@app.on_message(filters.private)
async def private(client , m):  # ✔️
    
    global bot_status , emoji

    ID = m.from_user.id 

    if ID in admins and m.text == "Back 🔙" :  # ✔️
        await back_main_menu(m)

    elif ID in admins and lm[ID] == "start" and m.text == "Add Token ➕":  # ✔️
        await m.reply("Now Send Your Bot Token In First Line And In The Second Line Send Your Bot Username ⏳" , reply_markup = ReplyKeyboardMarkup ([["Back 🔙"]] , resize_keyboard=True ))
        lm[ID] = "Add Token ➕"

    elif ID in admins and lm[ID] == "start" and m.text == "Delete Token ➖":  # ✔️
        await m.reply("Now Just Send Your Bot Token ⏳" , reply_markup = ReplyKeyboardMarkup ([["Back 🔙"]] , resize_keyboard=True ))
        lm[ID] = "Delete Token ➖"

    elif ID in admins and lm[ID] == "Add Token ➕":  # ✔️

        text = m.text.replace("\n" , " ").split()

        if len(text) <= 3 :
            
            all_tokens = await get_data()
            token_list = []
            for i in all_tokens :
                token_list += [i[0]]

            if text[0] not in token_list :

                await add_token(token=text[0] , ID = text[1] , time = m.date)

                await back_main_menu(m , "توکن با موفقیت اضافه شد ✅")
                
            else :
                await back_main_menu(m , "توکن در حال حاضر در دیتابیس وجود دارد ❌")

        else :
            await back_main_menu(m , "فرمت ارسالی مشکل دارد ❌")

    elif ID in admins and lm[ID] == "Delete Token ➖":  # ✔️
            
        all_tokens = await get_data()
        token_list = []
        for i in all_tokens :
            token_list += [i[0]]

        if  m.text in token_list :

            await del_token(token=m.text)
            await back_main_menu(m , "توکن با موفقیت حذف شد ✅")

        else :
            await back_main_menu(m , "توکن در حال حاضر در دیتابیس وجود ندارد ❌")

    elif ID in admins and lm[ID] == "start" and m.text == "On Robot 🌕":  # ✔️

        if not bot_status :

            bot_status = True

            await back_main_menu(m , "ربات با موفقیت روشن شد ✅")

        else :
            await back_main_menu(m , "ربات روشن است ❌")
 
    elif ID in admins and lm[ID] == "start" and m.text == "Off Robot 🌑":  # ✔️

        if bot_status :

            bot_status = False

            await back_main_menu(m , "ربات با موفقیت خاموش شد ✅")

        else :
            await back_main_menu(m , "ربات خاموش است ❌")
 
    elif ID in admins and lm[ID] == "start" and m.text == "Status ⏳":  # ✔️

        count = 1
        tokens_list  = await get_data()
        text_t = ""
        for i in tokens_list :
            text_t += f"{count} - token : `{i[0]}` , id : {i[1]}\n\n"
            count += 1

        if tokens_list :
            await m.reply(text_t)
        await back_main_menu(m)

    elif  ID in admins and lm[ID] == "start" and m.text == "Send Database📄" : # ✅

        try: 
            await app.send_document(ID , "database.db" , caption="db")
        except:
            pass

    elif  ID in admins and lm[ID] == "start" and m.text == "Change Emoji 🤡" : # ✅

        lm[ID] = "Change Emoji 🤡"
        await m.reply(f"ایموجی ثبت شده در حال حاضر {emoji} است اگر میخواهید آن را تغییر دهید فقط یک ایموجی بفرستید" , reply_markup = ReplyKeyboardMarkup ([["Back 🔙"]] , resize_keyboard=True ))

    elif  ID in admins and lm[ID] == "Change Emoji 🤡" :


        if len(m.text) == 1 :

            emoji = m.text
            await back_main_menu(m , f"ایموجی شما به {emoji} تغییر کرد")

        else :
            await back_main_menu(m , "فرمت ارسالی مشکل دارد ❌")

async def back_main_menu(m , text=""):  # ✔️

    ID = m.from_user.id
    lm[ID] = "start"

    if text == "" :
        totall_text = "**You Are Back To Main Menu 🟢**"

    else :
        totall_text = "**" + text + "\n\nYou Are Back To Main Menu 🟢**"

    await m.reply_text(text = totall_text , reply_markup = ReplyKeyboardMarkup (pannel_admin , resize_keyboard=True ))

async def get_data():
    
    cursor = conn.cursor()
    cursor.execute("SELECT token , id FROM bots WHERE time IS NOT NULL")
    result = cursor.fetchall()
    cursor.close()
    token = []
    for i in result :
        if i[0] :
            token += [[i[0] , i[1]]]
    
    return token

async def del_token(token):

    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM bots WHERE token=?" , (token ,))
    conn.commit()
    cursor.close()

async def add_token(token , ID , time):

    cursor = conn.cursor()
    result = [token , ID , time]
    cursor.execute(f"INSERT INTO bots VALUES(? , ? , ?);", result)
    cursor.close()
    conn.commit()

app.run()