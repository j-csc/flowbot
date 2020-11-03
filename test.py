from bs4 import BeautifulSoup

soup = BeautifulSoup(open("./output1.html"), "html.parser")

divs = (soup.find_all('div', class_="option-flow"))

for div in divs:
  print(div.contents.string)