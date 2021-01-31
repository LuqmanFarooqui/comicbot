import discord
import os
from datetime import date
import datetime
from replit import db
from discord.ext import tasks, commands
from keep_alive import keep_alive


client = discord.Client()

if "sending" not in db.keys():
  db["sending"] = True

today = date.today()
day = today.strftime("%d")
month = today.strftime("%m")
year = today.strftime("%Y")
d1 = datetime.datetime(int(year), int(month), int(day))

def sarcasm(text):
  text_lower = text.lower()
  text_upper = text.upper()
  text_sarcasm = ""
  for i in range(len(text)):
    if i%2!=0:
      text_sarcasm += text_upper[i]
    else:
      text_sarcasm += text_lower[i]
  return text_sarcasm

def show_comic(strip, day = day, month = month, year = year):
  if "strips" in db.keys():
    strips = db['strips']
    href = strips.get(strip)
    if href is None:
      return "clash"
    d2 = datetime.datetime(int(year), int(month), int(day))
    if d2 > d1:
      return "big"
    show_date = year + "/" + month + "/" + day
    link = href + show_date
    return link

def update_comics(comic, link):
  if "strips" in db.keys():
    strips = db['strips']
    strips[comic] = link
    db['strips'] = strips
  else:
    strips = {comic: link}
    db['strips'] = strips

def update_send(comic):
  if "strips" in db.keys():
    strips = db['strips']
    if comic in strips.keys():
      if "sendcs" in db.keys():
        sendcs = db['sendcs']
        if comic in sendcs:
          return "already"
        sendcs.append(comic)
        db['sendcs'] = sendcs
      else:
        db['sendcs'] = [comic]
    else:
      return "no comic"
  else:
    return "no exist"
  return "sent"

@client.event
async def on_ready():
  change_status.start()
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  # if message.author == client.user:
  #   return
  
  msg = message.content
  msg_split = msg.split()

  if msg.startswith('$new'):
    if len(msg.split(" ")) > 2:
      comic = msg.split(" ", 3)[1]
      link = msg.split(" ", 3)[2]
      res = update_comics(comic, link)
      await message.channel.send("Yay! You have added a new comic: {}".format(comic))
    else:
      await message.channel.send("Now _thats_ a comical request. You gotta put the link after the comic name")

  if msg.startswith('$send '):
    comic = msg.split(" ", 2)[1]
    res = update_send(comic)
    if res == "sent":
      await message.channel.send("Send {} every day ? As you wish!".format(comic))
    elif res == "no comic":
      await message.channel.send("You havent stored this comic")
    elif res == "no exist":
      await message.channel.send("dude. there are no comics stored at all. You need to add some.")     
    elif res == "already":
      await message.channel.send("Already sending you that. Remember?")


  if msg.startswith('$cs'):
    msg_split = msg.split(" ")
    strip = msg_split[1]
    today = date.today()
    day = today.strftime("%d")
    month = today.strftime("%m")
    year = today.strftime("%Y")
    for i in range(len(msg_split)):
      if i == 2:
        day = msg_split[i]
      if i == 3:
        month = msg_split[i]
      if i == 4:
        year = msg_split[i]
    res = show_comic(strip, day, month, year)
    if res == 'clash':
      await message.channel.send("You havent stored this comic")
    elif res == 'big':
      await message.channel.send("Fact: I cannot send links from the future. Ok ?")
    elif res is not None:
      await message.channel.send(res)
    else:
      await message.channel.send("You havent stored this comic")


  if msg.startswith('$list'):
    flag = 0
    if "strips" in db.keys():
      strips = db['strips']
      if len(strips)>0:
        txt = '\n'. join(strips)
        await message.channel.send("The Chosen Comics:\n{}".format(txt))
      else:
        flag = 1
    else:
      flag = 1
    if flag == 1:
      await message.channel.send("List of all stored comics :\nNone, Brutus, none.")
    flag = 0
    if "sendcs" in db.keys():
      sendcs = db['sendcs']
      if len(sendcs)>0:
        txt = '\n'. join(sendcs)
        await message.channel.send("You are having me send these ones daily:\n{}".format(txt))
      else:
        flag = 1
    else:
      flag = 1
    if flag == 1:
      await message.channel.send("List of comics that are sent daily:\nNada. Zilch.")
      

  if msg.startswith('$sarc'):
    msg_split = msg.split(" ")
    msg_split.pop(0)
    text = ' '.join(msg_split)
    sarcd = sarcasm(text)
    og = message.author
    await message.channel.purge(limit=1)
    await message.channel.send("{} says: {}".format(og, sarcd))

  if msg.startswith('$del'):
    flag = 0
    if "strips" in db.keys():
      strips = db['strips']
    else:
      await message.channel.send("dude. there are no comics stored _at all_. You need to add some.")
    if "sendcs" in db.keys():
      flag = 1
      sendcs = db['sendcs']
    msg_split = msg.split(" ")
    lent = len(msg_split)
    del_arg = msg_split[1]
    if del_arg == 'all':
      strips.clear()
      if flag == 1:
        sendcs.clear()
      await message.channel.send("sed. you have deleted all your comics.")
    else:
      if del_arg in strips.keys():
        if lent == 2:
          strips.pop(del_arg)
          if flag == 1 and del_arg in sendcs:
            sendcs.remove(del_arg)
          await message.channel.send("{} has been sent to the Great Beyond ...".format(del_arg))
        elif lent > 2 and flag == 1 and del_arg in sendcs:
          sendcs.remove(del_arg)
          await message.channel.send("{} will now not visit you".format(del_arg))
      else:
        await message.channel.send("You havent stored this comic, ergo, I cant delete it.")
    db['sendcs'] = sendcs
    db['strips'] = strips
  
  if msg.startswith("$sending"):
    value = msg.split("$sending ",1)[1]

    if value.lower() == "true":
      db["sending"] = True
      await message.channel.send("sending is on")
    else:
      db["sending"] = False
      await message.channel.send("sending is off")

  if msg.startswith('$help'):
    await message.channel.send("Hello!\nHere's a list of commands:\n`$new $cs $list $send $sending $del $sarc`\n\nTo store new comic strips, or modify old ones, enter:\n`$new <comic_name> <gocomics_link with `/` at end>`\nExample:\n`$new calvobes https://www.gocomics.com/calvinandhobbes/`\nThe above command will now allow me to access the Calvin and Cobbes comic strips using the pseudo-name, `calvobes`\n\nTo view all stored comics, enter: `$list`\n\nTo view comic strips, enter:\n`$cs <stored pseudo_name> [ <dd> <mm> <yyyy>]`\nExamples:\n`$cs calvobes` : This gives today's strip\n`$cs calvobes 08` : This gives the strip published on the 08th of the current month\n`$cs calvobes 21 05` : This gives the strip published on the 21st of May of the current year\n`$cs calvobes 21 05 2020` : This gives the strip published on the 21st of May of 2020\n\nTo have a stored comic be sent every 24 hours, enter:\n`$send <stored pseudo_name>`\nExample: `$send calvobes`\n\nTo switch on or switch off automatic sending of comics everyday, enter:\n`$sending true` to switch on and\n `$sending false` to switch off\n\nTo delete stored comics, enter:\n`$del <pseudo_name / all> [send]`\nExample: `$del calvobes` will remove the calvobes entry from the bot's database\nEnter `$del all` to remove all comics at once\nEnter `$del <pseudo_name> stop` to stop that comic from being sent everyday\nExample: `$del calvobes stop`\n\nBonus command!\nEnter `$sarc <text>` to get your text back in sarcasm mode!\nExample: `$sarc Gold` gives `gOlD`\nEnjoy!")

@tasks.loop(minutes=1440)
async def change_status():
  if db["sending"]:
    channel = client.get_channel(761646441302458388)
    if "sendcs" in db.keys():
      sendcs = db['sendcs']
      if len(sendcs)>0:
        for strip in sendcs:
          res = show_comic(strip, day, month, year)
          # if res != 'clash':
          await channel.send(res)
      else:
        return 0
    else:
      return 0

# db.clear()
keep_alive()
client.run(os.getenv('TOKEN'))
