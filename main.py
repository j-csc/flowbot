import discord
from discord.ext import commands
import aiohttp
import asyncio
import json
import time
import traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Init -------------------------------------------------------
load_dotenv()
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
flowUser = os.environ.get("FLOWUSERNAME")
flowPw = os.environ.get("FLOWPASSWORD")
all_flow = []
flow_check = set()
update_count = 0
channel_id = 772196146180259880
# TOKEN = 'NzYwNDM3NTU5MTAwMTc4NDcy.X3MCqg.h1qky3bcccGoiUkbXIZ9RgQdjdY'
TOKEN = os.environ.get("TOKEN")
# -----------------------------------------------------------------------------

client = commands.Bot(command_prefix='.')

class Flow:
  def __init__(self, ticker, sentiment, det, expiry, strike, cp, order_type):
    self.ticker = ticker
    self.sentiment = sentiment
    self.det = det
    self.expiry = expiry
    self.strike = strike
    self.cp = cp
    self.order_type = order_type
    
  def __str__(self):
    return (f"{self.order_type}\n{self.ticker} {self.strike} {self.cp}\n{self.det}\n")

  def key(self):
    return (f"{self.order_type}{self.ticker}{self.strike}{self.cp}{self.det}{self.expiry}")
  
  def obj(self):
    dic = {
      'ticker': self.ticker,
      'strike': self.strike,
      'cp': self.cp,
      'details': self.det,
      'order_type': self.order_type, 
      'expiry': self.expiry, 
      'sentiment': self.sentiment
    }
    return dic
  
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
  global console, alreadyFetched, refreshTime, loadTime, flowPw, flowUser, all_flow, flow_check, update_count
  
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
    past_len = len(all_flow)
    num_added = 0
    # Brute force fetch html
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")
    # with open("output1.html", "w") as file:
    #   file.write(html)
    option_flows = (soup.find_all('div',  attrs={'class': ['option-flow']}))
    for flow in option_flows:
      ticker = flow['data-ticker']
      sentiment = flow['data-sentiment']
      order_type = flow['data-ordertype']
      cp = ("CALLS" if flow['data-sentiment'] == "bullish" else "PUTS")
      strike = str(flow.find('div', class_="strike").text)
      strike = strike[6:]
      expiry = str(flow.find('div', class_="expiry").text)
      expiry = expiry[6:]
      det =  str(flow.find('div', class_="details").text)
      det = (det[21:])
      
      temp_obj = Flow(ticker, sentiment, det, expiry, strike, cp, order_type)
      obj_check = temp_obj.key()
        
      if obj_check not in flow_check:
        flow_check.add(obj_check)
        all_flow.append(temp_obj.obj())
        num_added += 1
    
    # No change at this point if initializing or no change, else add
    if past_len == 0:
      pass
    elif num_added == 0:
      pass
    else:
      await showFlow(num_added)
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
    clientReady = True
    activity = discord.Activity(name='wolftradingllc.com', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)
    print(f'{client.user} has connected to Discord!')
  
  @client.event
  async def on_message(message):
    if message.author == client.user:
      return
    
    if message.content.startswith("Block"):
      await message.channel.send("Start")
    
    if message.content.startswith('.'):
      await client.process_commands(message)

  @client.command(pass_context=True)
  async def flow(ctx):
    global channel_id
    channel = client.get_channel(channel_id)
    for flow in all_flow[:5]:
      ticker = flow['ticker']
      cp = flow['cp']
      details = flow['details']
      strike = flow['strike']
      
      exp = flow['expiry']
      order_type = flow['order_type']
      embed = discord.Embed(title=f'{order_type} {cp}', description=f'{details} {ticker} ${strike} {cp} {exp} Expiry', colour=discord.Colour.red())
      embed.set_footer(text='Powered By Guh')
      await channel.send(channel, embed=embed)
  
  client.run(TOKEN)
  
async def showFlow(added_flow_n):
  global client, clientReady, all_flow, channel_id

  if (clientReady):
    channel = client.get_channel(channel_id)
    print("New flow incoming...")
    for flow in all_flow[-added_flow_n:]:
      ticker = flow['ticker']
      cp = flow['cp']
      details = flow['details']
      strike = flow['strike']
      exp = flow['expiry']
      embed = discord.Embed(title=f'{ticker} {cp}', description=f'{details} ${strike} Calls {exp}', colour=discord.Colour.red())
      embed.set_footer(text='Powered By Guh')
      await channel.send(channel, embed=embed)

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