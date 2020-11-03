import discord
from discord.ext import commands
import aiohttp
import asyncio
import json
import time
import traceback
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Init -------------------------------------------------------
url = "https://flowalgo.com"
hideChrome = True

refreshTime = 25		# WARNING - Setting below 15 seconds could violate Discord API ToS
loadTime = 5

dataDirectory = "./data"
alreadyFetched = False
console = ""
driver = None
client = None
clientReady = False
flowUser = "lalalander"
flowPw = "flowalgo2020"

# TOKEN = 'NzYwNDM3NTU5MTAwMTc4NDcy.X3MCqg.h1qky3bcccGoiUkbXIZ9RgQdjdY'
TOKEN = "NzcyMTk0MDMwNjI4MzcyNDgx.X53Huw.o7kun9cjscwxFCbr_6HfrdZeFVQ"
# -----------------------------------------------------------------------------

client = commands.Bot(command_prefix='.')

def chromeSetup():
	global driver, dataDirectory, hideChrome
	# Set up Chrome options
	chrome_opts = Options()
	# chrome_opts.set_headless(headless=hideChrome)								# Set up headless
	chrome_opts.add_argument('no-sandbox')										# --
	chrome_opts.add_argument("proxy-server=direct://")							# Make headless not unbearably slow
	chrome_opts.add_argument("proxy-bypass-list=*")								# --
	chrome_opts.add_argument("disable-extensions")								# --
	chrome_opts.add_argument("hide-scrollbars")									# --
	chrome_opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36")
	chrome_opts.add_argument("log-level=3")										# Hide console messages

	print("Setting up web driver...")
	driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_opts)
	print("Web driver set up")
	driver.get("http://google.com/")

async def refreshThread():
	global refreshTime

	while True:
		await fetchPage()
		await asyncio.sleep(refreshTime)		# Wait between page fetches

async def fetchPage():
  global console, alreadyFetched, refreshTime, loadTime, flowPw, flowUser
  
  # If not logged in
  if (not alreadyFetched):
    driver.get("https://app.flowalgo.com/")
    _form = driver.find_elements_by_xpath('//form[@name="login"]')
    _inputs = driver.find_elements_by_xpath('//form[@name="login"]//input')
    for input in _inputs:
      n = (input.get_attribute('name'))
      if n == "amember_login":
        input.send_keys(flowUser)
        pass
      elif n == "amember_pass":
        input.send_keys(flowPw)
        pass
    _form[0].submit()
    alreadyFetched = True
  else:
    driver.refresh()
    print("Page Refreshing " + time.strftime("%I:%M:%S", time.localtime()))
  
  # Fetch flow
  try:
    flowCheck = WebDriverWait(driver, loadTime).until(EC.presence_of_element_located((By.CLASS_NAME, 'option-flow')))
    # Brute force fetch html
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")
    with open("output1.html", "w") as file:
      file.write(html)
    # for div in (soup.find("div", class_= "data-body")):
    #   print(div.text)
    pass
  except TimeoutException:
    print("Page timeout")
  except AttributeError:
    traceback.print_exc()
  except NoSuchElementException:
    print("Elements not found, or page has not loaded properly")
  
  pass

def run(client):
  global TOKEN
  
  @client.event
  async def on_ready():
    global clientReady
    activity = discord.Activity(name='wolftradingllc.com', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)
    print(f'{client.user} has connected to Discord!')
  
  @client.event
  async def on_message(message):
    if message.author == client.user:
      return
    
    if message.content.startswith("Block"):
      await message.channel.send("Start")
      
    # if message.content.startswith("!flow"):
    #   embed = discord.Embed(title='Guh Calls', description='$333 Calls 10-9 Expiration', colour=discord.Colour.red())
    #   embed.set_footer(text='Powered By Guh')
    #   await message.channel.send(message.channel, embed=embed)
    
    if message.content.startswith('.'):
      await client.process_commands(message)

  @client.command(pass_context=True)
  async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

  @client.command(pass_context=True)
  async def bitcoin(ctx):
    url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        await ctx.send("Bitcoin price is: $" + response['bpi']['USD']['rate'])

  @client.command(pass_context=True)
  async def flow(ctx):
    pass
  
  client.run(TOKEN)

def main():
  global client
  # Set up chrome
  chromeSetup()
  
  # Set up async fetch
  loop = asyncio.get_event_loop()
  loop.create_task(refreshThread())
 
  # Set up Discord
  client = commands.Bot(command_prefix=".")
  run(client)

if __name__ == "__main__":
  main()