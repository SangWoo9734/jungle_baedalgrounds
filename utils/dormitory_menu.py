import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient   
from datetime import datetime        

client = MongoClient('mongodb://anuhyun:dksdn@3.36.103.219',27017)
db = client.dbground    

db.dormitory_menu.drop()

r=requests.get("https://dorm.kyonggi.ac.kr:446/Khostel/mall_main.php?viewform=B0001_foodboard_list&board_no=1")
r.encoding='euc-kr'
soup= BeautifulSoup(r.text,'html.parser')

for i in range(1,8):
    lunch_menu=soup.select_one('body > table:nth-child(2) > tr > td > table > tr > td:nth-child(2) > table:nth-child(2) > tr:nth-child(2) > td > table > tr > td:nth-child(1) > table:nth-of-type(2) >tbody>tr:nth-of-type({}) >td:nth-of-type(2)'.format(i))
    lunch_menu = lunch_menu.text
    lunch_menu = lunch_menu.split()
    dinner_menu=soup.select_one('body > table:nth-child(2) > tr > td > table > tr > td:nth-child(2) > table:nth-child(2) > tr:nth-child(2) > td > table > tr > td:nth-child(1) > table:nth-of-type(2) >tbody>tr:nth-of-type({}) >td:nth-of-type(3)'.format(i))
    dinner_menu = dinner_menu.text
    dinner_menu = dinner_menu.split()
    if i==1 or 7:
        date=soup.select_one('body > table:nth-child(2) > tr > td > table > tr > td:nth-child(2) > table:nth-child(2) > tr:nth-child(2) > td > table > tr >  td:nth-child(1) > table:nth-of-type(2) >tbody>tr:nth-of-type({}) >th'.format(i))
        date = date.text
        date = date.split()
        
    else:
        date=soup.select_one('body > table:nth-child(2) > tr > td > table > tr > td:nth-child(2) > table:nth-child(2) > tr:nth-child(2) > td > table > tr >  td:nth-child(1) > table:nth-of-type(2) >tbody>tr:nth-of-type({}) >th>a'.format(i))
        date = date.text
        date = date.split()
    
    db.dormitory_menu.insert_one({'date':date[0],'day':date[1],'lunch_menu':lunch_menu,'dinner_menu':dinner_menu})
