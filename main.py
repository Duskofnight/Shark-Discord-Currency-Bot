from replit import db
from discord.ext import commands
import discord
import os
import requests
import json
import random
import schedule
import time
import asyncio


for key in db.keys():
  print(key)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(intents=intents, command_prefix='/')


@bot.event
async def send_fee_message(message):
  await bot.wait_until_ready()
  for channel in bot.get_all_channels():
    if isinstance(channel, discord.TextChannel):
      await channel.send(message)
      break


async def pet_fee():
  userid = db.keys()
  while True:
    await asyncio.sleep(900)
    choices = ["Pay Fee", "Decline"]
    view = discord.ui.View()

    async def button_callback(interaction, view=view):
      if interaction.data['custom_id'] == choices[0]:
        for id in userid:
          if id.isdigit():
            if db[id]['pets']:
              for pet in db[id]['pets']:
                fee = int(
                  (db['pets'][pet]['cost']) * 0.35) * int(db[id]['pets'][pet])
                db[id]['wallet'] -= round(fee, 2)

            user = await bot.fetch_user(id)
            await user.send(
              f"`You have been charged a pet maintenance fee of ${fee}!`")
            await send_fee_message(
              f"<@{id}> has been charged a pet maintenance fee of ${fee}!")

      elif interaction.data['custom_id'] == choices[1]:
        for id in userid:
          if id.isdigit():
            if db[id]['pets']:
              for pet in db[id]['pets']:
                del db[id]['pets'][pet]
                print(db[id]['items'][pet])
                del db[id]['items'][pet]

            user = await bot.fetch_user(id)
            await user.send("`Your pet has disappeared from your inventory`!")
            await send_fee_message(
              f"<@{id}>'s pets have succumbed to illness due to unpaid maintenance fees!"
            )

      await interaction.message.delete()

    for i in range(2):
      button = discord.ui.Button(label=choices[i],
                                 style=discord.ButtonStyle.green,
                                 custom_id=choices[i])

      button.callback = button_callback

      view.add_item(button)

    for id in db.keys():
      if id.isdigit() and 'pets' in db[id] and db[id]['pets']:
        for pet in db[id]['pets']:
          fee = int(
            (db['pets'][pet]['cost']) * 0.35) * int(db[id]['pets'][pet])
        user = await bot.fetch_user(id)
        if user:
          await user.send(
            f"Your pet is feeling ill and you must pay a fee of ${round(fee,2)}!\n\n`Pay or Decline?`",
            view=view)


async def property_income():
  userid = db.keys()
  while True:
    await asyncio.sleep(600)
    for id in userid:
      if id.isdigit():
        if db[id]['property']:
          total = 0
          if 'property' not in db[id]:
            db[id]['property'] = {}

          for property in db[id]['property']:
            income = int((db['property'][property]['cost'] * 0.10) *
                         int(db[id]['property'][property]))
            total += round(income, 2)
          user = await bot.fetch_user(id)
          if user:
            db[id]['wallet'] += total
            await user.send(f"`You have earned ${total} from your properties!`"
                            )
            await user.send(
              f"`{user}`\n`Balance: ${db[str(user.id)]['wallet']}`\n`Bank: ${db[str(user.id)]['bank']}`"
            )
            await send_fee_message(
              f"<@{id}> has earned ${total} from their properties!")


async def business_income():
  userid = db.keys()
  while True:
    await asyncio.sleep(300)
    for id in userid:
      if id.isdigit():
        if db[id]['business']:
          total = 0
          if 'business' not in db[id]:
            db[id]['business'] = {}

          for business in db[id]['business']:
            income = int((db['business'][business]['cost'] * 0.30) *
                         int(db[id]['business'][business]))
            total += round(income, 2)
          user = await bot.fetch_user(id)
          if user:
            db[id]['wallet'] += total
            await user.send(f"`You have earned ${total} from your businesses!`"
                            )
            await user.send(
              f"`{user}`\n`Balance: ${db[str(user.id)]['wallet']}`\n`Bank: ${db[str(user.id)]['bank']}`"
            )
            await send_fee_message(
              f"<@{id}> has earned ${total} from their businesses!")


async def background_tasks():
  await bot.wait_until_ready()
  bot.loop.create_task(pet_fee())
  bot.loop.create_task(property_income())
  bot.loop.create_task(business_income())


@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  await background_tasks()
  #instanciateItems() [only used for testing purposes]



def check_user(id):
  keys = db.keys()
  if id in keys:
    return True
  else:
    return False


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  if message.content.startswith("$hello"):
    await message.channel.send("Hello!")

  knownUser = False
  keys = db.keys()
  if str(message.author.id) in keys:
    knownUser = True
  else:
    db[str(message.author.id)] = {
      "wallet": 1000,
      "bank": 5000,
      "items": {},
      "pets": {},
      "property": {},
      "business": {}
    }

    names = db.keys()
    for name in names:
      if name.isdigit():
        user = await bot.fetch_user(name)
        if user and not db.get(f"welcomed_{name}", False):
          await user.send(f"Welcome to the server, <@{user.id}>! To read the commands of this currency game, please type `/commands.`")
          for channel in bot.get_all_channels():
            if isinstance(channel, discord.TextChannel):
              await channel.send(f"Hey, it's **Shark**! Welcome to the server, <@{user.id}>! To get started on the currency game, please type `/commands.`")
              break
          db[f"welcomed_{name}"] = True


  await bot.process_commands(message)



@bot.command()
async def commands(ctx):
  user = await bot.fetch_user(ctx.author.id)
  await user.send("`Here are the commands of this currency game:`")
  await user.send("```/commands - Displays the command list.\n\n/bank - Stores your entire wallet amount into your bank.\n\n/withdraw - Withdraws money from your bank into your wallet.\n\n/balance - Shows your current balance and items owned.\nbalance [user] - Shows the balance of the mentioned user.\n\n/buy - Lists available items to buy from the shop.\n/buy [item] [quantity] - Buy a specified item from the shop.\n* Note: You do not have to specify a quantity if you are only buying one item.\n\n/work - Earn some money for a living\n\n/invest - Lists available methods of investing.\n/invest [method] [amount] - Invest a specified amount of money into a specified method of investing.\n\n/rob [user] - An attempt to rob a specified user's wallet.\n/sell [item] [quantity] - Sell a specified item from your inventory.\n\n/business - Lists available businesses to start up. \n/business [business] - Start up a business of choice.\n\n/rank - A leaderboard that shows the amount of money and item value of every user in the server.\n\n/bankrob -  An attempt to rob every user's bank account with a small success rate.\n\n/trade [user] [item] [price] [quantity] - Trade an item for a specified price to any user of choice.\n* Note: You do not have to specify a quantity if you are only trading one item.\n\n/pets - Lists available pets to buy.\n/pets [pet] [quantity] - Buy a specified amount of pets from the shop.\n* Note: You do not have to specify a quantity if you are only buying one pet.```")

@bot.command()
async def bank(ctx):
  userid = str(ctx.author.id)
  if check_user(userid):
    db[userid]['bank'] += db[userid]['wallet']
    db[userid]['wallet'] = 0
  await balance(ctx)


@bot.command()
async def withdraw(ctx, amount: int = 0):
  userid = str(ctx.author.id)
  if check_user(userid):
    if db[userid]['bank'] < amount:
      await ctx.send('`You do not have enough money to withdraw.`')
      return
    if amount < 0:
      await ctx.send('`You cannot withdraw a negative amount.`')
      return
    db[userid]['bank'] -= amount
    db[userid]['wallet'] += amount
  await balance(ctx)


@bot.command()
async def balance(ctx, user: discord.Member = None):
  if user is not None:
    userid = str(user.id)
    if check_user(userid):
      await ctx.send(
        f"`{user}`\n`Balance: ${db[str(user.id)]['wallet']}`\n`Bank: ${db[str(user.id)]['bank']}`"
      )

  else:
    if db[str(ctx.author.id)]['items'] is None:
      db[str(ctx.author.id)]['items'] = {}
    my_items = "***Items***:\n`"
    for name in db[str(ctx.author.id)]['items'].keys():
      my_items += (f"{name}\t[{db[str(ctx.author.id)]['items'][name]}]\n")
    my_items += "`"
    if "``" in my_items:
      my_items = my_items.replace("``", "`None`")
    await ctx.reply(
      f"***Balance:***\n`Wallet: ${db[str(ctx.author.id)]['wallet']}`\n`Bank: ${db[str(ctx.author.id)]['bank']}`\n\n{my_items}"
    )


def instanciateItems():
  if 'business' in db.keys():
    del db['business']
  db['business'] = {
    "Clothing-Company": {
      "cost": 5000
    },
    "Restaurant-Chain": {
      "cost": 7500
    },
    "Construction-Company": {
      "cost": 12000
    },
    "Banking-Company": {
      "cost": 18000
    },
    "Tech-Company": {
      "cost": 25000
    }
  }

  if 'property' in db.keys():
    del db['property']
  db['property'] = {
    "Single-Family-Home": {
      "cost": 5000
    },
    "Luxury-Condo": {
      "cost": 10000
    },
    "Office-Compartment": {
      "cost": 15000
    },
    "Commercial-Skyscraper": {
      "cost": 30000
    }
  }

  if 'pets' in db.keys():
    del db['pets']
  db['pets'] = {
    "Goldfish": {
      "cost": 50,
      "stock": 85
    },
    "Syrian-Hamster": {
      "cost": 120,
      "stock": 69
    },
    "Hedgehog": {
      "cost": 300,
      "stock": 45
    },
    "Pug": {
      "cost": 450,
      "stock": 38
    },
    "Golden-Retriever": {
      "cost": 500,
      "stock": 24
    },
    "Siberian-Husky": {
      "cost": 600,
      "stock": 24
    },
    "British-Shorthair": {
      "cost": 650,
      "stock": 18
    },
    "Bengal-Cat": {
      "cost": 780,
      "stock": 15
    },
    "Siberian-Tiger": {
      "cost": 8000,
      "stock": 3
    }
  }

  if 'items' in db.keys():
    del db['items']
  db['items'] = {
    "Watch": {
      "icon": "watch.png",
      "cost": 25,
      'stock': 50
    },
    "Glasses": {
      "icon": "glasses.png",
      "cost": 50,
      'stock': 40
    },
    "Shoes": {
      "icon": "shoes.png",
      "cost": 75,
      'stock': 30
    },
    "Shirt": {
      "icon": "shirt.png",
      "cost": 100,
      'stock': 20
    },
    "Pants": {
      "icon": "pants.png",
      "cost": 150,
      'stock': 15
    },
    "Hat": {
      "icon": "hat.png",
      "cost": 200,
      'stock': 10
    },
    "Chair": {
      "icon": "chair.png",
      "cost": 300,
      'stock': 15
    },
    "Phone": {
      "icon": "iphone.png",
      "cost": 450,
      'stock': 18
    },
    "Desk": {
      "icon": "desk.png",
      "cost": 500,
      'stock': 12
    },
    "Computer": {
      "icon": "computer.png",
      "cost": 1000,
      'stock': 15
    },
    "Honda-Civic": {
      "icon": "car.png",
      "cost": 3000,
      "stock": 45
    },
    "Audi-S4": {
      "icon": "car.png",
      "cost": 5000,
      'stock': 13
    },
    "Mazda-Rx7": {
      "icon": "car.png",
      "cost": 8000,
      'stock': 3
    },
    "Audi-R8": {
      "icon": "car.png",
      "cost": 10000,
      'stock': 7
    },
    "Lamborghini-Aventador": {
      "icon": "car.png",
      "cost": 15000,
      'stock': 8
    },
    "House": {
      "icon": "house.png",
      "cost": 15000,
      'stock': 5
    },
    "Rolls-Royce-Phantom": {
      "icon": "car.png",
      "cost": 21000,
      'stock': 2
    },
    "Bugatti-Chiron": {
      "icon": "car.png",
      "cost": 30000,
      'stock': 1
    },
    "Lamborghini-Veneno": {
      "icon": "car.png",
      "cost": 42000,
      'stock': 1
    },
    "Pagani-Zonda": {
      "icon": "car.png",
      "cost": 45000,
      'stock': 1
    },
    "Mansion": {
      "icon": "mansion.png",
      "cost": 50000,
      'stock': 3
    }
  }


@bot.command()
async def buy(ctx, item: str = None, quantity: int = None):
  if item is None:
    await ctx.send("`Here are the items available to buy:`")
    forSale = "```"
    for name, object in db['items'].items():
      forSale += (f"{name}\t${object['cost']}\t[{object['stock']} remaining]\n")
    forSale += "```"
    await ctx.send(forSale)

  elif quantity is None:
    print(item)
    item = item.title()
    if item not in db['items'].keys():
      await ctx.send("`That item is not available`")
      return
    userid = str(ctx.author.id)
    if not check_user(userid):
      await ctx.send("`You do not have an account with this server.`")
      return
    if db['items'][item]['stock'] <= 0:
      await ctx.send("`That item is not in stock.`")
      return
    item_details = db['items'][item]
    if db[userid]['wallet'] < item_details['cost']:
      await ctx.send("`You do not have enough money to buy that item.`")
      return
    db[userid]['wallet'] -= item_details['cost']
    db['items'][item]['stock'] -= 1
    if db[userid]['items'] == None:
      db[userid]['items'] = {}
    if item not in db[userid]['items'].keys():
      db[userid]['items'][item] = 1
    else:
      db[userid]['items'][item] += 1
    await ctx.send(f"`You bought {item} for ${item_details['cost']}`")

  elif quantity is not None:
    print(item)
    item = item.title()
    if item not in db['items'].keys():
      await ctx.send("`That item is not available`")
      return
    userid = str(ctx.author.id)
    if not check_user(userid):
      await ctx.send("`You do not have an account with this server.`")
      return
    if db['items'][item]['stock'] <= 0:
      await ctx.send("`That item is not in stock.`")
      return
    if db['items'][item]['stock'] < quantity:
      await ctx.send("`There is not enough of that item in stock to buy.`")
      return
    item_details = db['items'][item]
    total_cost = item_details['cost'] * quantity
    if db[userid]['wallet'] < total_cost:
      await ctx.send("`You do not have enough money to buy that item.`")
      return
    db[userid]['wallet'] -= total_cost
    db['items'][item]['stock'] -= quantity
    if db[userid]['items'] == None:
      db[userid]['items'] = {}
    if item not in db[userid]['items'].keys():
      db[userid]['items'][item] = quantity
    else:
      db[userid]['items'][item] += quantity
    await ctx.send(f"`You bought {quantity} {item} for ${total_cost}`")


@bot.command()
async def work(ctx):
  result = requests.get("https://the-trivia-api.com/api/questions/")
  questions = result.json()
  question = questions[0]['question']
  correct_answer = questions[0]['correctAnswer']
  incorrect_answer = questions[0]['incorrectAnswers']
  print(question)
  print(correct_answer)
  print(incorrect_answer)

  answers = incorrect_answer
  answers.append(correct_answer)
  random.shuffle(answers)

  view = discord.ui.View()

  async def button_callback(interaction, view=view):
    paycheck = 300
    print(interaction.data['custom_id'])
    if interaction.data['custom_id'] == correct_answer:
      await interaction.response.send_message(
        "`Correct, you have earned $300!`")
    else:
      await interaction.response.send_message(
        "`Wrong, you have earned $1 for trying.`")
      paycheck = 1

    await interaction.message.delete()

    userid = str(interaction.user.id)
    if check_user(userid):
      db[userid]['wallet'] += paycheck

  for i in range(4):
    button = discord.ui.Button(label=answers[i],
                               style=discord.ButtonStyle.blurple,
                               custom_id=answers[i])

    button.callback = button_callback

    view.add_item(button)

  user = await bot.fetch_user(ctx.author.id)
  await user.send(f"`{question}`", view=view)


@bot.command()
async def invest(ctx, method: str = None, amount: int = None):
  user = await bot.fetch_user(ctx.author.id)
  if method == None:
    await ctx.send("`Please specify a method of investment: `")
    await ctx.send(
      "```- Stocks (Minimum $500): Invest in stocks and experience the excitement of the market. While there's a chance to make substantial gains, there's also the risk of losing some of your investment.\n\n- Crypto (Minimum $1500): Dive into the world of crypto, where high risk meets high reward. The potential for significant returns is great, but so is the potential for loss.\n\n- Real-Estate: Invest in real estate for a more stable opportunity to earn passive income, though it comes with high initial costs. This option generally offers a better chance for returns with a manageable level of risk.\n* Note: Do not specify an amount of money to invest into real-estate.```"
    )
    return
  method = method.strip().lower()
  if method not in ["stocks", "crypto", "real-estate"]:
    await ctx.send("`Please specify a valid method of investment.`")
    return
  if amount == None:
    if method.strip().lower() != "real-estate":
      await ctx.send("`Please specify an amount of money to invest with.`")
      return
    else:
      choices = [
        "Single-Family Home ($5000)", "Luxury Condo ($10000)",
        "Office Compartment ($15000)", "Commercial Skyscraper ($30000)"
      ]
      view = discord.ui.View()

      async def button_callback(interaction, view=view):
        userid = str(ctx.author.id)
        if interaction.data['custom_id'] == choices[0]:
          if db[userid]['wallet'] < 5000:
            await user.send(
              "`You do not have enough money to purchase this property.`")
            await interaction.message.delete()
            return
          await user.send("`You have bought a Single-Family Home for $5000.`")
          await ctx.send(
            f"<@{userid}> has bought a Single-Family Home for $5000.")
          db[userid]['wallet'] -= 5000
        elif interaction.data['custom_id'] == choices[1]:
          if db[userid]['wallet'] < 10000:
            await user.send(
              "`You do not have enough money to purchase this property.`")
            await interaction.message.delete()
            return
          await user.send("`You have bought a Luxury Condo for $10000.`")
          await ctx.send(f"<@{userid}> has bought a Luxury Condo for $10000.")
          db[userid]['wallet'] -= 10000
        elif interaction.data['custom_id'] == choices[2]:
          if db[userid]['wallet'] < 15000:
            await user.send(
              "`You do not have enough money to purchase this property.`")
            await interaction.message.delete()
            return
          await user.send("`You have bought an Office Compartment for $15000.`")
          await ctx.send(
            f"<@{userid}> has bought an Office Compartment for $15000.")
          db[userid]['wallet'] -= 15000
        elif interaction.data['custom_id'] == choices[3]:
          if db[userid]['wallet'] < 30000:
            await user.send("`You do not have enough money to purchase this property.`")
            await interaction.message.delete()
            return
          await user.send("`You have bought a Commercial Skyscraper for $30000.`")
          await ctx.send(
            f"<@{userid}> has bought a Commercial Skyscraper for $30000.")
          db[userid]['wallet'] -= 30000

        property_name = interaction.data['custom_id'].split(
          " ")[0] + "-" + interaction.data['custom_id'].split(" ")[1]
        print(property_name)
        userid = str(ctx.author.id)
        if property_name not in db[userid]['items']:
          db[userid]['items'][property_name] = 1
          db[userid]['property'][property_name] = 1
        else:
          db[userid]['items'][property_name] += 1
          db[userid]['property'][property_name] += 1
        await balance(ctx)

        await interaction.message.delete()

      for i in range(4):
        button = discord.ui.Button(label=choices[i],
                                   style=discord.ButtonStyle.blurple,
                                   custom_id=choices[i])

        button.callback = button_callback

        view.add_item(button)

      await user.send(
        "`Which real-estate property would you like to invest in?`\n",
        view=view)

  method = method.strip().lower()
  if amount is not None:
    if db[str(ctx.author.id)]['wallet'] < amount:
      await ctx.send("`You do not have enough money to invest that amount.`")
      return
    if method == "stocks":
      if amount < 500:
        await ctx.send("`You cannot invest less than $500 into stocks.`")
        return
    elif method == "crypto":
      if amount < 1500:
        await ctx.send("`You cannot invest less than $1500 into crypto.`")
        return
    elif method == "real-estate":
      await ctx.send(
        "`Do not specify an amount of money to invest in real-estate.`")
      return

    choices = ["Yes", "No"]
    view = discord.ui.View()

    async def button_callback(interaction, view=view):

      if interaction.data['custom_id'] == choices[0]:
        if method.strip().lower() == "stocks":
          roll = random.randint(1, 20)
          if roll < 4:
            roll = random.randint(1, 30)
            if roll < 11:
              amount_made = amount * 3
              db[str(ctx.author.id)]['wallet'] += round(amount_made, 0)
              await user.send(
                f"`You have earned ${round(amount_made,0)} from your stock investment!`"
              )
            else:
              amount_made = amount * 2
              db[str(ctx.author.id)]['wallet'] += round(amount_made, 0)
              await user.send(
                f"`You have earned ${round(amount_made,0)} from your stock investment!`"
              )
          else:
            amount_lost = amount * 0.7
            db[str(ctx.author.id)]['wallet'] -= round(amount_lost, 0)
            await user.send(
              f"`You have lost ${round(amount_lost,0)} from your stock investment.`"
            )
        elif method.strip().lower() == "crypto":
          roll = random.randint(1, 50)
          if roll == 14:
            amount_made = amount * 10.5
            db[str(ctx.author.id)]['wallet'] += round(amount_made, 0)
            await user.send(
              f"`You have earned ${round(amount_made,0)} from your crypto investment!`"
            )
          else:
            amount_lost = amount * 1
            await user.send(
              f"`You have lost ${round(amount_lost,0)} from your crypto investment.`"
            )
            db[str(ctx.author.id)]['wallet'] -= round(amount_lost, 0)

      elif interaction.data['custom_id'] == choices[1]:
        await user.send(f"`You have backed out of your {method} investment.`")
      await interaction.message.delete()

    for i in range(2):
      button = discord.ui.Button(label=choices[i],
                                 style=discord.ButtonStyle.blurple,
                                 custom_id=choices[i])

      button.callback = button_callback

      view.add_item(button)

    await user.send(
      f"`Are you sure you want to invest ${amount} in {method}?`", view=view)


@bot.command()
async def rob(ctx, user: discord.Member = None):
  if user == None:
    await ctx.send("`You must include a username of someone to rob.`")
    return
  userid = str(ctx.author.id)
  if not check_user(userid):
    await ctx.send("`You do not have an account with us.`")
  victim_id = str(user.id)
  if not check_user(victim_id):
    await ctx.send("`That user has no wallet!`")
    return
  roll = random.randint(1, 100)

  if roll < 20:
    if db[victim_id]['wallet'] < 1:
      await ctx.send("`That user has no money!`")
      return

    choices = ["Defend", "Ignore"]
    view = discord.ui.View()

    async def button_callback(interaction, view=view):
      userid = str(ctx.author.id)
      roll = random.randint(1, 150)
      print(interaction.data['custom_id'])

      if interaction.data['custom_id'] == choices[
          0] and roll < 20 and db[victim_id]['wallet'] > 0:
        robber_amount = db[userid]['wallet']
        db[userid]['wallet'] = 0
        db[victim_id]['wallet'] += robber_amount
        await ctx.send(
          f"<@{user.id}> has successfully defended against the robber, and took ${robber_amount} from {ctx.author.mention}"
        )
        await user.send(
          f"You have successfully defended against the robber, and took ${robber_amount} from {ctx.author.mention}"
        )
      elif db[victim_id]['wallet'] < 1:
        await ctx.send("`That user has no money!`")
        await user.send("`You have no money!`")
        await interaction.message.delete()

      elif interaction.data['custom_id'] == choices[
          1] or interaction.data['custom_id'] == choices[0] and roll >= 20:
        await ctx.send(
          f"<@{user.id}> has unsuccessfully defended from {ctx.author.mention}!\n{ctx.author.mention} is a robber!"
        )
        await user.send(
          f"You have unsuccessfully defended from {ctx.author.mention}")
        amount = db[victim_id]['wallet']
        db[victim_id]['wallet'] = 0
        db[userid]['wallet'] += amount
        await ctx.send(
          f"{ctx.author.mention} has stolen ${amount} from <@{user.id}>!")
        await user.send(
          f'{ctx.author.mention} has stolen ${amount} from your purse!')

      await interaction.message.delete()

    for i in range(2):
      button = discord.ui.Button(label=choices[i],
                                 style=discord.ButtonStyle.blurple,
                                 custom_id=choices[i])

      button.callback = button_callback

      view.add_item(button)

    await ctx.send(f"<@{user.id}> is being robbed by {ctx.author.mention}!")
    await user.send(
      f"{ctx.author.mention} has attempted to rob you!\n\n`Defend OR Ignore?`",
      view=view)

  else:
    await ctx.send(
      f"{ctx.author.mention} has failed to rob <@{user.id}>, was arrested, and has to pay bail of $500!"
    )
    db[userid]['wallet'] -= 500


@bot.command()
async def sell(ctx, item: str = None, quantity: int = None):
  userid = str(ctx.author.id)
  user = await bot.fetch_user(ctx.author.id)
  if not check_user(userid):
    await ctx.send("`You do not have an account with us.`")
    return
  if item == None:
    await ctx.send("`You must include an item to sell.`")
    return
  item = item.title()
  if item.title() not in db[userid]['items']:
    await ctx.send("`You do not own that item!`")
    return
  if quantity == None:
    quantity = 1
  if quantity > db[userid]['items'][item.title()]:
    await ctx.send("`You do not own that much amount of items to sell!`")
    return

  choices = ["Yes", "No"]
  view = discord.ui.View()

  async def button_callback(interaction, view=view):
    userid = str(ctx.author.id)
    if interaction.data['custom_id'] == choices[0]:
      db[userid]['items'][item.title()] -= quantity
      if db[userid]['items'][item] == 0:
        del db[userid]['items'][item]
      if item.title() in db['items']:
        db['items'][item.title()]['stock'] += quantity

      elif item in db['property']:
        amount = db['property'][item]['cost'] * quantity
        amount = amount * 0.7
        db[userid]['wallet'] += amount
        db[userid]['property'][item] -= quantity
        if db[userid]['property'][item] == 0:
          del db[userid]['property'][item]
      elif item in db['pets']:
        amount = db['pets'][item]['cost'] * quantity
        amount = amount * 0.7
        db[userid]['pets'][item] -= quantity
        if db[userid]['pets'][item] == 0:
          del db[userid]['pets'][item]
        db[userid]['wallet'] += amount
        db['pets'][item]['stock'] += quantity
      elif item in db['business']:
        amount = db['business'][item]['cost'] * quantity
        amount = amount * 0.7
        db[userid]['business'][item] -= quantity
        if db[userid]['business'][item] == 0:
          del db[userid]['business'][item]
      else:
        amount = db['items'][item]['cost'] * quantity
        amount = amount * 0.7
        print(amount)
        db[userid]['wallet'] += amount

      await ctx.send(
        f"<@{userid}> has sold `{quantity}x {item}` for ${round(amount,1)}!")
      await user.send(
        f"`You have sold {quantity}x {item} for ${round(amount,1)}!`")

    elif interaction.data['custom_id'] == choices[1]:
      await user.send("`You have chosen not to sell your item.`")

    await interaction.message.delete()

  for i in range(2):
    button = discord.ui.Button(label=choices[i],
                               style=discord.ButtonStyle.green,
                               custom_id=choices[i])

    button.callback = button_callback

    view.add_item(button)

  await user.send(
    f"```Are you sure you want to sell {quantity}x {item.title()}?\n\n* Note: You will only gain 70% of your item's original value.```",
    view=view)


@bot.command()
async def business(ctx, type=None):
  user = await bot.fetch_user(ctx.author.id)
  if type == None:
    await ctx.send("`Please specify the type of business you want to start up:`"
                   )
    await ctx.send(
      "```- Clothing-Company ($5000)\n- Restaurant-Chain ($7500)\n- Construction-Company ($12000)\n- Banking-Company ($18000)\n- Tech-Company ($25000)```"
    )
  if type is not None:
    type = type.strip().title()
    if type not in db['business']:
      await ctx.send(
        "`Please specify a valid type of business you want to start up.`")
    elif type in db['business']:
      if db[str(ctx.author.id)]['wallet'] < db['business'][type]['cost']:
        await ctx.send(
          f"`You do not have enough money to start up a {type} business.`")
        return
      else:
        choices = ["Yes", "No"]
        view = discord.ui.View()

        async def button_callback(interaction, view=view):
          userid = str(ctx.author.id)
          if interaction.data['custom_id'] == choices[0]:
            if db[userid]['wallet'] < db['business'][type]['cost']:
              await user.send("`You do not have enough money to start a business.")
              return
            await user.send(
              f"`You have started a {type} for ${db['business'][type]['cost']}.`"
            )
            await ctx.send(
              f"<@{userid}> has started a {type} for ${db['business'][type]['cost']}."
            )
            db[userid]['wallet'] -= db['business'][type]['cost']

            userid = str(ctx.author.id)
            if type not in db[userid]['items']:
              db[userid]['items'][type] = 1
              db[userid]['business'][type] = 1
            else:
              db[userid]['items'][type] += 1
              db[userid]['business'][type] += 1
            await balance(ctx)

          elif interaction.data['custom_id'] == choices[1]:
            await user.send(
              f"`You have chosen not to start up a {type} business.`")
            await ctx.send(
              f"<@{userid}> has chosen not to start up a {type} business.")

          await interaction.message.delete()

        for i in range(2):
          button = discord.ui.Button(label=choices[i],
                                     style=discord.ButtonStyle.green,
                                     custom_id=choices[i])

          button.callback = button_callback

          view.add_item(button)

        await user.send(f"`Are you sure you want to start a {type}?.`",
                        view=view)


@bot.command()
async def rank(ctx):
  keys = db.keys()
  counter = 1
  for key in keys:
    compare = {}
    if key == "items" or key == "pets" or key == "property" or key == "business":
      continue
    wealth = 0
    items = db[key]["items"]
    property = db[key]["property"]
    business = db[key]["business"]
    print(business)
    print(property)
    print(items)
    try:
      for business_type, quantity in business.items():
        print(business_type)
        business_type = db['business'][business_type]['cost']
        wealth += business_type * quantity
      
      for property_name, quantity in property.items():
        print(property_name)
        property_cost = db['property'][property_name]['cost']
        wealth += property_cost * quantity

      for item_name, quantity in items.items():
        print(item_name)
        print(key)
        item_cost = db['items'][item_name]['cost']
        wealth += item_cost * quantity

      wealth += db[key]['wallet'] + db[key]['bank']
    except:
      wealth += db[key]['wallet'] + db[key]['bank']
    compare[wealth] = key
    print()
    print(compare)
    
    amount = sorted(compare.items(), reverse=True)

    for wealth, user_id in amount:
      await ctx.send(f"{counter}. <@{user_id}> - Wealth: ${wealth}")
      counter += 1


@bot.command()
async def bankrob(ctx):
  roll = random.randint(1, 115)
  if roll == 1:
    amount = 0
    await ctx.send(
      f"{ctx.author.mention} has successfully robbed 50% of every user's bank account!"
    )
    print(ctx.author.id)
    keys = db.keys()
    for key in keys:
      if key == "items" or key == "" or key == "item" or key == "pets" or key == "property" or key == "business" or key == str(ctx.author.id):
        continue
      bank = db[key]['bank']
      reward = round(0.5 * bank, 0)
      db[key]['bank'] -= round(reward, 0)
      print(reward)
      amount += reward
      db[str(ctx.author.id)]['wallet'] += round(reward, 0)
      print(type(ctx.author.id))
    await ctx.send(f"{ctx.author.mention} has stolen ${int(round(amount,2))}!")

  else:
    await ctx.send(
      f"{ctx.author.mention} has failed to rob everyone's bank account, was arrested, and has to pay bail of $2000!"
    )
    db[str(ctx.author.id)]['wallet'] -= 2000


@bot.command()
async def trade(ctx,
                user: discord.Member = None,
                item: str = None,
                price: int = None,
                quantity: int = None):
  if user == None:
    await ctx.send("`You must include a username of someone to trade with.`")
    return
  userid = str(ctx.author.id)
  receiver = str(user.id)
  
  if item == None:
    await ctx.send("`You must include an item to trade.`")
    return
  if item.title() not in db[userid]['items']:
    await ctx.send("`You do not own that item!`")
    return
  if price == None:
    await ctx.send("`You must include a price of the item you want to trade.`")
    return
  if price < 0:
    await ctx.send("`You cannot trade for a negative price!`")
    return
  if quantity == None:
    quantity = 1
  if quantity > db[userid]['items'][item.title()]:
    await ctx.send("`You do not own that much amount of items to trade!`")
    return

  choices = ["Accept", "Decline"]
  view = discord.ui.View()

  async def button_callback(interaction, view=view):

    if interaction.data['custom_id'] == choices[0]:
      items = item.title()
      if db[receiver]['wallet'] >= price:
        if items in db['property']:
          db[userid]['property'][items] -= quantity
          if db[userid]['property'][items] == 0:
            del db[userid]['property'][items]
          if items not in db[receiver]['property'].keys():
            db[receiver]['property'][items] = quantity
          else:
            db[receiver]['property'][items] += quantity

        if items in db['business']:
          db[userid]['business'][items] -= quantity
          if db[userid]['business'][items] == 0:
            del db[userid]['business'][items]
          if items not in db[receiver]['business'].keys():
            db[receiver]['business'][items] = quantity
          else:
            db[receiver]['business'][items] += quantity

        if items in db['pets']:
          db[userid]['pets'][items] -= quantity
          if db[userid]['pets'][items] == 0:
            del db[userid]['pets'][items]
          if items not in db[receiver]['pets'].keys():
            db[receiver]['pets'][items] = quantity
          else:
            db[receiver]['property'][items] += quantity

        if db[receiver]['items'] == None:
          db[receiver]['items'] = {}
        db[receiver]['wallet'] -= price
        db[userid]['wallet'] += price
        db[userid]['items'][items] -= quantity
        if db[userid]['items'][items] == 0:
          del db[userid]['items'][items]
        if items not in db[receiver]['items'].keys():
          db[receiver]['items'][items] = quantity
        else:
          db[receiver]['items'][items] += quantity

        await ctx.send(
          f"<@{userid}> has successfully completed the trade with <@{receiver}>!"
        )
        print(user)
        await ctx.author.send(
          f"You have successfully completed the trade with <@{receiver}>!")
        await user.send(
          f"You have successfully completed the trade with <@{userid}>!")
      else:
        await ctx.send(
          f"<@{receiver}> does not have enough money to accept the trade!")
        await user.send("You do not have enough money to accept the trade!")

    elif interaction.data['custom_id'] == choices[1]:
      await ctx.send(f"<@{user.id}> has declined <@{ctx.author.id}>'s trade!")
      await user.send(f"You have declined <@{user.id}>'s trade!")
      await ctx.author.send(f"<@{receiver}> has declined your trade!")

    await interaction.message.delete()

  for i in range(2):
    button = discord.ui.Button(label=choices[i],
                               style=discord.ButtonStyle.red,
                               custom_id=choices[i])

    button.callback = button_callback

    view.add_item(button)

  await ctx.send(
    f"<@{ctx.author.id}> is trading <@{user.id}>:\n\n`{quantity}x {item.title()}` for ${price}!"
  )
  await user.send(
    f"{ctx.author.mention} is trading you:\n\n`{quantity}x {item.title()}` for ${price}\n\n`Accept or Decline?`",
    view=view)


@bot.command()
async def pets(ctx, item_name: str = None, quantity: int = None):
  if item_name == None:
    await ctx.send("`Here are the pets available to buy:`")
    forSale = "```"
    for name, item in db['pets'].items():
      forSale += (f"{name}\t${item['cost']}\t[{item['stock']} remaining]\n")
    forSale += "```"
    await ctx.send(forSale)
    return

  if quantity is None:
    print(item_name)
    item_name = item_name.title()
    if item_name not in db['pets'].keys():
      await ctx.send("`That pet is not available`")
      return
    userid = str(ctx.author.id)
    if not check_user(userid):
      await ctx.send("`You do not have an account with this server.`")
      return
    if db['pets'][item_name]['stock'] <= 0:
      await ctx.send("`That pet is not in stock.`")
      return
    item_details = db['pets'][item_name]
    if db[userid]['wallet'] < item_details['cost']:
      await ctx.send("`You do not have enough money to buy that pet.`")
      return
    db[userid]['wallet'] -= item_details['cost']
    db['pets'][item_name]['stock'] -= 1
    if db[userid]['pets'] == None:
      db[userid]['pets'] = {}
    if db[userid]['items'] is None:
      db[userid]['items'] = {}
    if item_name not in db[userid]['pets'].keys(
    ) or item_name not in db[userid]['items']:
      db[userid]['pets'][item_name] = 1
      db[userid]['items'][item_name] = 1
    else:
      db[userid]['items'][item_name] + -1
      db[userid]['pets'][item_name] += 1
    await ctx.send(f"`You bought {item_name} for ${item_details['cost']}`")

  if quantity is not None:
    item_name = item_name.title()
    if item_name not in db['pets'].keys():
      await ctx.send("`That pet is not available`")
      return
    userid = str(ctx.author.id)
    if not check_user(userid):
      await ctx.send("`You do not have an account with this server.`")
      return
    if db['pets'][item_name]['stock'] <= 0:
      await ctx.send("`That item is not in stock.`")
      return
    item_details = db['pets'][item_name]
    all_costs = item_details['cost'] * quantity
    if db[userid]['wallet'] < all_costs:
      await ctx.send("`You do not have enough money to buy that pet.`")
      return
    db[userid]['wallet'] -= all_costs
    db['pets'][item_name]['stock'] -= quantity
    if db[userid]['pets'] == None:
      db[userid]['pets'] = {}
    if item_name not in db[userid]['pets'].keys():
      db[userid]['pets'][item_name] = quantity
    else:
      db[userid]['pets'][item_name] += quantity

    if db[userid]['items'] is None:
      db[userid]['items'] = {}
    if item_name not in db[userid]['items'].keys():
      db[userid]['items'][item_name] = quantity
    else:
      db[userid]['items'][item_name] += quantity

    await ctx.send(f"`You bought {quantity} {item_name} for ${all_costs}`")


try:
  bot.run(os.getenv('TOKEN'))
except Exception as err:
  raise err
