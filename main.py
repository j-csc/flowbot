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
import undetected_chromedriver as uc
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
reg_channel_id = 795486318012268564
golden_channel_id = 795486634907926529
unusual_channel_id = 795486772050133053
TOKEN = os.environ.get("TOKEN")
# -----------------------------------------------------------------------------

client = commands.Bot(command_prefix='.')

class Flow:
  def __init__(self, ticker, sentiment, det, expiry, strike, cp, order_type, prem, gsweep, sizelot, unusual):
    self.ticker = ticker
    self.sentiment = sentiment
    self.det = det
    self.expiry = expiry
    self.strike = strike
    self.cp = cp
    self.order_type = order_type
    self.prem = prem
    self.gsweep = gsweep
    self.sizelot = sizelot
    self.unusual = unusual
  
  def key(self):
    return (f"{self.order_type}{self.ticker}{self.strike}{self.cp}{self.det}{self.expiry}{self.prem}")
  
  def obj(self):
    dic = {
      'ticker': self.ticker,
      'strike': self.strike,
      'cp': self.cp,
      'details': self.det,
      'order_type': self.order_type, 
      'expiry': self.expiry, 
      'sentiment': self.sentiment,
      'premium': self.prem,
      'gsweep': self.gsweep,
      'sizelot': self.sizelot,
      'unusual': self.unusual
    }
    return dic
  
def chromeSetup():
	global driver, dataDirectory, hideChrome
	# Set up Chrome options
	chrome_opts = webdriver.ChromeOptions()
	chrome_opts.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
	chrome_opts.set_headless(headless=hideChrome)
	chrome_opts.add_argument('--no-sandbox')
	chrome_opts.add_argument("proxy-server=direct://")
 	# chrome_opts.add_argument("--headless")
	chrome_opts.add_argument("proxy-bypass-list=*")		
	chrome_opts.add_argument("window-size=1400,920")
	chrome_opts.add_argument("--disable-dev-shm-usage")
	chrome_opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36")
	chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
 

	driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=chrome_opts)

	print("Web driver set up")
	# driver.get("http://google.com/")

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
    WebDriverWait(driver, 10)
    print("fetching page")
    # _form = WebDriverWait(driver, loadTime).until(EC.presence_of_element_located((By.XPATH, '//form[@name="login"]')))
    _form = driver.find_elements_by_xpath('//form[@name="login"]')
    # _inputs = WebDriverWait(driver, loadTime).until(EC.presence_of_element_located((By.XPATH, '//form[@name="login"]//input')))
    _inputs = driver.find_elements_by_xpath('//form[@name="login"]//input')
    for input in _inputs:
      n = (input.get_attribute('name'))
      if n == "amember_login":
        input.send_keys(flowUser)
        pass
      elif n == "amember_pass":
        input.send_keys(flowPw)
        pass
    print(driver.page_source)
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
      prem =  str(flow.find('div', class_="premium").text)
      gsweep = flow['data-agsweep']
      sizelot = flow['data-sizelot']
      unusual = flow['data-unusual']
      
      temp_obj = Flow(ticker, sentiment, det, expiry, strike, cp, order_type, prem, gsweep, sizelot, unusual)
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
  async def test(ctx):
    channel = client.get_channel(reg_channel_id)
    await channel.send("testing")

  @client.command(pass_context=True)
  async def flow(ctx):
    global reg_channel_id
    channel = client.get_channel(reg_channel_id)
    for flow in all_flow[:5]:
      ticker = flow['ticker']
      cp = flow['cp']
      details = flow['details']
      strike = flow['strike']
      prem = flow['premium']
      exp = flow['expiry']
      order_type = flow['order_type']
      gsweep = flow['gsweep']
      sizelot = flow['sizelot']
      unusual = flow['unusual']
      color = discord.Colour.gold() if gsweep != "" else discord.Colour.purple() if unusual != "" else discord.Colour.green() if sizelot != "" else discord.Colour.red()
      embed = discord.Embed(title=f'{order_type}: {ticker} {cp}', 
        description=f'Expiry\n{exp}\nStrike\n${strike}\nContract\n{cp}\nSize @ Price\n{details}\nPremium\n{prem}', colour=color)
      embed.set_footer(text='Powered By Wolf Trading LLC')
      await channel.send(channel, embed=embed)
  
  @client.command(pass_context=True)
  async def golden(ctx):
    global reg_channel_id
    channel = client.get_channel(reg_channel_id)
    for flow in all_flow:
      gsweep = flow['gsweep']
      if gsweep != "":
        ticker = flow['ticker']
        cp = flow['cp']
        details = flow['details']
        strike = flow['strike']
        prem = flow['premium']
        exp = flow['expiry']
        order_type = flow['order_type']
        sizelot = flow['sizelot']
        unusual = flow['unusual']
        gsweep = flow['gsweep']
        color = discord.Colour.gold() if gsweep != "" else discord.Colour.purple() if unusual != "" else discord.Colour.green() if sizelot != "" else discord.Colour.red()
        embed = discord.Embed(title=f'{order_type}: {ticker} {cp}', 
          description=f'Expiry\n{exp}\nStrike\n${strike}\nContract\n{cp}\nSize @ Price\n{details}\nPremium\n{prem}', colour=color)
        embed.set_footer(text='Powered By Wolf Trading LLC')
        await channel.send(channel, embed=embed)
        
  @client.command(pass_context=True)
  async def unusual(ctx):
    global unusual_channel_id
    channel = client.get_channel(unusual_channel_id)
    for flow in all_flow:
      unusual = flow['unusual']
      if unusual != "":
        ticker = flow['ticker']
        cp = flow['cp']
        details = flow['details']
        strike = flow['strike']
        prem = flow['premium']
        exp = flow['expiry']
        order_type = flow['order_type']
        sizelot = flow['sizelot']
        unusual = flow['unusual']
        gsweep = flow['gsweep']
        color = discord.Colour.gold() if gsweep != "" else discord.Colour.purple() if unusual != "" else discord.Colour.green() if sizelot != "" else discord.Colour.red()
        embed = discord.Embed(title=f'{order_type}: {ticker} {cp}', 
          description=f'Expiry\n{exp}\nStrike\n${strike}\nContract\n{cp}\nSize @ Price\n{details}\nPremium\n{prem}', colour=color)
        embed.set_footer(text='Powered By Wolf Trading LLC')
        await channel.send(channel, embed=embed)
  client.run(TOKEN)
  
async def showFlow(added_flow_n):
  global client, clientReady, all_flow, reg_channel_id

  if (clientReady):
    print("New flow incoming...")
    for flow in all_flow[-added_flow_n:]:
      ticker = flow['ticker']
      cp = flow['cp']
      details = flow['details']
      strike = flow['strike']
      prem = flow['premium']
      exp = flow['expiry']
      order_type = flow['order_type']
      gsweep = flow['gsweep']
      sizelot = flow['sizelot']
      unusual = flow['unusual']
      if gsweep != "":
        embed = discord.Embed(title=f'{order_type}: {ticker} {cp}', 
        description=f'Expiry\n{exp}\nStrike\n${strike}\nContract\n{cp}\nSize @ Price\n{details}\nPremium\n{prem}', colour=discord.Colour.gold())
        embed.set_footer(text='Powered By Wolf Trading LLC')
        channel = client.get_channel(golden_channel_id)
        await channel.send(channel, embed=embed)
      elif unusual != "":
        embed = discord.Embed(title=f'{order_type}: {ticker} {cp}', 
        description=f'Expiry\n{exp}\nStrike\n${strike}\nContract\n{cp}\nSize @ Price\n{details}\nPremium\n{prem}', colour=discord.Colour.purple())
        embed.set_footer(text='Powered By Wolf Trading LLC')
        channel = client.get_channel(unusual_channel_id)
        await channel.send(channel, embed=embed)
      else:
        if cp == "CALLS":
          color = discord.Colour.green()
        else: 
          color = discord.Colour.red()
        channel = client.get_channel(reg_channel_id)
        embed = discord.Embed(title=f'{order_type}: {ticker} {cp}', 
          description=f'Expiry\n{exp}\nStrike\n${strike}\nContract\n{cp}\nSize @ Price\n{details}\nPremium\n{prem}', colour=color)
        embed.set_footer(text='Powered By Wolf Trading LLC')
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