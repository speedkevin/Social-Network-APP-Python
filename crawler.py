# encoding:utf-8

import urllib2
import re
from bs4 import BeautifulSoup

print('==== 大同 ====')
quote_page = 'http://taipeidt.com/tc/iwlink.php'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')
gym_box = soup.find('table', attrs={'bordercolor': '#006666'})
gym = gym_box.text.strip().split()
#print gym[1] + "/100"
swim_box = soup.find('table', attrs={'bordercolor': '#CC0000'})
swim = swim_box.text.strip().split()
#print swim[1] + "/250"
result ="{\"gym\":[\"" + gym[1] + "\",\"100\"],\"swim\":[\"" + swim[1] + "\",\"250\"]}"
print result
# return jsonify(result)

print('==== 中正 ====')
quote_page = 'http://www.tpejjsports.com.tw/zh-TW/onsitenum'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')
gym_box = soup.find('h3', attrs={'class': 'flow gym_flow'})
gym = gym_box.text.strip()
gym = gym.split()
#print gym[0][3:]
swim_box = soup.find('h3', attrs={'class': 'flow swimming_flow'})
swim = swim_box.text.strip()
swim = swim.split()
#print swim[0][3:]
result ="{\"gym\":[\"" + gym[0][3:] + "\",\"120\"],\"swim\":[\"" + swim[0][3:] + "\",\"300\"]}"
print result

print('==== 萬華 ====')
quote_page = 'http://whsc.com.tw/'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')
name_box = soup.find_all(re.compile("^script"))
target = str(name_box[8])
for item in target.split("\n"):
    if "this.venueInfo" in item:
        target = item
result = ""
for myitem in target.split("\\r\\n"):
    if "UseQty" in myitem:
        a = myitem.split(" ")
        result = result + a[5] + " "
result = result.split(" ")
result ="{\"gym\":[\"" + result[1] + "\",\"150\"],\"swim\":[\"" + result[0] + "\",\"400\"]}"
print result

print('==== 北投 ====')
quote_page = 'http://www.btsport.org.tw/zh-TW/onsitenum'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')
gym_box = soup.find('h3', attrs={'class': 'flow gym_flow'})
gym = gym_box.find('span', attrs={'class': 'flow_number'})
gym = gym.text.strip()
gym = gym[:len(gym)-1]

swim_box = soup.find('h3', attrs={'class': 'flow swimming_flow'})
swim = swim_box.find('span', attrs={'class': 'flow_number'})
swim = swim.text.strip()
swim = swim[:len(swim)-1]

result ="{\"gym\":[\"" + gym + "\",\"80\"],\"swim\":[\"" + swim + "\",\"200\"]}"
print result

print('==== 士林 ====')
quote_page = 'http://www.slsc-taipei.org/'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')
gym_box = soup.find('li', attrs={'id': 'data1'})
gym = gym_box.find('span', attrs={'class': 'number'})
gym = gym.text.strip()
print gym
swim_box = soup.find('li', attrs={'id': 'data2'})
swim = swim_box.find('span', attrs={'class': 'number'})
swim = swim.text.strip()
result ="{\"gym\":[\"" + gym + "\",\"100\"],\"swim\":[\"" + swim + "\",\"200\"]}"
print result

print('==== 松山 ====')
quote_page = 'http://sssc.com.tw/'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')
name_box = soup.find_all(re.compile("^script"))
target = str(name_box[8])
for item in target.split("\n"):
    if "this.venueInfo" in item:
        target = item
result = ""
for myitem in target.split("\\r\\n"):
    if "UseQty" in myitem:
        a = myitem.split(" ")
        result = result + a[5] + " "
result = result.split(" ")
#print result[0]
#print result[1]
result ="{\"gym\":[\"" + result[1] + "\",\"150\"],\"swim\":[\"" + result[0] + "\",\"400\"]}"
print result

print('==== 板橋 ====')
quote_page = 'http://www.bqsports.com.tw/zh-TW/onsitenum'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')
gym_box = soup.find('h3', attrs={'class': 'flow gym_flow'})
gym = gym_box.text.strip()
gym = gym.split()
gym = gym[0][3:]
#print gym
swim_box = soup.find('h3', attrs={'class': 'flow swimming_flow'})
swim = swim_box.text.strip()
swim = swim.split()
swim = swim[0][3:]
#print swim
result ="{\"gym\":[\"" + gym + "\",\"80\"],\"swim\":[\"" + swim + "\",\"400\"]}"
print result
