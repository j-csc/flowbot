from bs4 import BeautifulSoup

soup = BeautifulSoup(open("./output1.html"), "html.parser")

arr = [1,2,3,4]

arr.append(45)
print(arr[-2:])

# class Flow:
#   def __init__(self, ticker, sentiment, det, expiry, strike, cp, order_type, prem, gsweep, sizelot, unusual):
#     self.ticker = ticker
#     self.sentiment = sentiment
#     self.det = det
#     self.expiry = expiry
#     self.strike = strike
#     self.cp = cp
#     self.order_type = order_type
#     self.prem = prem
#     self.gsweep = gsweep
#     self.sizelot = sizelot
#     self.unusual = unusual
    

#   def key(self):
#     return (f"{self.order_type}{self.ticker}{self.strike}{self.cp}{self.det}{self.expiry}{self.prem}")
  
#   def obj(self):
#     dic = {
#       'ticker': self.ticker,
#       'strike': self.strike,
#       'cp': self.cp,
#       'details': self.det,
#       'order_type': self.order_type, 
#       'expiry': self.expiry, 
#       'sentiment': self.sentiment,
#       'premium': self.prem,
#       'gsweep': self.gsweep,
#       'sizelot': self.sizelot,
#       'unusual': self.unusual
#     }
#     return dic
  

# flow = (soup.find('div',  attrs={'class': ['option-flow']}))
# attr_dict = flow.attrs
# prem =  str(flow.find('div', class_="premium").text)
# print(flow)

# option_flows = (soup.find_all('div',  attrs={'class': ['option-flow']}))
# # print(option_flows.prettify())
# for flow in option_flows:
#   attr_dict = flow.attrs
#   print(attr_dict)
#   print(flow['data-unusual']=='')
  
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
  
#   temp_obj = Flow(ticker, sentiment, det, expiry, strike, cp, order_type)
#   print(flow)
# TOKEN="NzcyMTk0MDMwNjI4MzcyNDgx.X53Huw.yF53leoWQjPkpxXFGsgqSUu_OmQ"
  
"""
{'class': ['item', 'option-flow', 'bullflow', 'animated', 'fadeInUp'], 
'data-ticker': 'GNUS', 'data-sentiment': 'bullish', 
'data-flowid': '833838', 'data-premiumpaid': '23490', 
'data-ordertype': 'BLOCK', 'data-qty': '783', 'data-score': '25.45725891911', 
'data-days-to-expiry': '164.01', 'data-sector': 'CONDI', 'data-lev': 'false', '
data-unusual': '', 'data-agsweep': '', 'data-sizelot': '', 'data-er': 'false', 
'data-np': 'false', 'data-weekly': 'false', 'data-lc': 'true'}
"""
