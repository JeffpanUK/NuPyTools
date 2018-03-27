import os
import sys
import re
import io
import time
import socket
import gzip
import random
import urllib
from urllib import error, request
from bs4 import BeautifulSoup 
agents = []
with open("agent.list", 'r', encoding='utf-8') as fi:
    for line in fi:
        line = line.strip()
        if line != "":
            agents.append(line)
i=6835
count=0
while(i<9999):
    try:

        f = open('results_2018_2.txt','a+',encoding='utf-8')
        url = 'http://wx.triman.com.cn/rkbyw/hksp/queryInfo/0?SPWH=%s00180%s&SFZHM='% (r"%E4%BA%BA",i)    
        request = urllib.request.Request(url)
        agent_index = random.randint(0, 9811 - 1)
        user_agent = agents[agent_index]
        request.add_header('User-Agent', user_agent)
        request.add_header('connection','keep-alive')
        request.add_header('Accept-Encoding', 'gzip')
        response = urllib.request.urlopen(request)
        html = response.read()
        if(response.headers.get('content-encoding', None) == 'gzip'):
            html = gzip.GzipFile(fileobj=io.BytesIO(html)).read()
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', {'class':'rediv'})
        if div is not None:
            top = div.find('ul')
            if top == None:
                i+=1
                continue
            link = top.findAll('td')
            if link == None or len(link)<5:
                i+=1
                continue
    #         name = link[5].renderContents()
    #         if name.decode() == "叶剑豪":
    #             print(url)
    #         print(link[0].renderContents())
            count+=1
            print("got %d people."%count)
            for j in range(len(link)//2):
                f.write("%s: %s\n"%(link[2*j].renderContents().decode(),link[2*j+1].renderContents().decode()))
            f.write("%s\n"%(link[-1].renderContents().decode()))
            f.write("\n")
        f.close()
        i+=1
        time.sleep(1)
        if i%100==0:
            time.sleep(59)
    except:
        print("meet err when fetching %d."%i)
        time.sleep(300)

print(count)