from bs4 import BeautifulSoup

soup = BeautifulSoup(open("./output1.html"), "html.parser")

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
    return(f"{self.order_type}\n{self.ticker} {self.strike} {self.cp}\n{self.det}\n")
  
  def obj(self):
    dic = {
      'ticker': self.ticker,
      'strike': self.strike,
      'cp': self.cp,
      'details': self.det,
      'order_type': self.order_type,
      'expiry': self.expiry
    }
    return dic
  

# flow = (soup.find('div',  attrs={'class': ['option-flow']}))
# attr_dict = flow.attrs
# ticker = flow['data-ticker']
# sentiment = flow['data-sentiment']
# order_type = flow['data-ordertype']
# cp = ("CALLS" if flow['data-sentiment'] == "bullish" else "PUTS")
# strike = str(flow.find('div', class_="strike").text)
# strike = strike[6:]
# expiry = str(flow.find('div', class_="expiry").text)
# expiry = expiry[6:]
# det =  str(flow.find('div', class_="details").text)
# det = (det[21:])

option_flows = (soup.find_all('div',  attrs={'class': ['option-flow']}))
# print(option_flows.prettify())
for flow in option_flows:
  attr_dict = flow.attrs
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
  print(temp_obj)

  
"""
{'class': ['item', 'option-flow', 'bullflow', 'animated', 'fadeInUp'], 
'data-ticker': 'GNUS', 'data-sentiment': 'bullish', 
'data-flowid': '833838', 'data-premiumpaid': '23490', 
'data-ordertype': 'BLOCK', 'data-qty': '783', 'data-score': '25.45725891911', 
'data-days-to-expiry': '164.01', 'data-sector': 'CONDI', 'data-lev': 'false', '
data-unusual': '', 'data-agsweep': '', 'data-sizelot': '', 'data-er': 'false', 
'data-np': 'false', 'data-weekly': 'false', 'data-lc': 'true'}
"""
