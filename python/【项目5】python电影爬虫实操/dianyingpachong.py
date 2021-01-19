import requests
  6 from lxml import etree
  7 HEADERS = {
  8     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
  9                   'AppleWebKit/537.36 (KHTML, like Gecko)'
 10                   ' Chrome/67.0.3396.99 Safari/537.36'
 11 }
 12 BASE_DOMAIN="http://www.dytt8.net"
 13
 14
 15 def get_detail_url(url):
 16     response = requests.get(url, headers=HEADERS) #print(response.content.decode('gbk'))
 17     text = response.text.encode("utf-8")  #拿到数据，，再解码
 18     html = etree.HTML(text)
 19     detail_urls = html.xpath("//table[@class='tbspan']//a/@href")
 20     detail_urls=map(lambda url:BASE_DOMAIN+url,detail_urls)
 21     return detail_urls
 22
 23 def parse_detail_page(url):
 24     movie={}
 25     response=requests.get(url,headers=HEADERS)
 26     text=response.content.decode('gbk')  #text = response.text.encode("utf-8")
 27     html=etree.HTML(text)
 28     title=html.xpath("//div[@class='title_all']//font[@color='#07519a']/text()")[0]
 29     # for x in title:
 30     #     print(etree.tostring(x,encoding="utf-8").decode("utf-8"))
 31     #print(title)
 32     movie['title']=title
 33     Zoome=html.xpath("//div[@id='Zoom']")[0] #return list
 34     imgs=Zoome.xpath(".//img/@src")
 35     #print(cover)
 36     cover=imgs[0]
 37     # screenshot=imgs[1]
 38     movie['cover']=cover
 39     # movie['screenshot']=screenshot  not all movie has screenshot ,so discard for this moment
 40
 41     def parse_info(info,rule):
 42         return info.replace(rule,"").strip()
 43
 44     infos=Zoome.xpath(".//text()")
 45     # print(infos) each line is a element of the list
 46
 47     for index,info in enumerate(infos):
 48         if info.startswith("◎年　　代"):
 49             info=parse_info(info,"◎年　　代")
 50             # print(info)
 51             movie['year']=info
 52         elif info.startswith("◎产　　地"):
 53             info=parse_info(info,"◎产　　地")
 54             movie['country']=info
 55         elif info.startswith("◎类　　别"):
 56             info=parse_info(info,"◎类　　别")
 57             movie['category']=info
 58         elif info.startswith("◎语　　言"):
 59             info=parse_info(info,"◎语　　言")
 60             movie['language']=info
 61         elif info.startswith("◎字　　幕"):
 62             info=parse_info(info,"◎字　　幕")
 63             movie['sub_title']=info
 64         elif info.startswith("◎上映日期"):
 65             info=parse_info(info,"◎上映日期")
 66             movie['release_time']=info
 67         elif info.startswith("◎豆瓣评分"):
 68             info=parse_info(info,"◎豆瓣评分")
 69             movie['douban_score']=info
 70         elif info.startswith("◎片　　长"):
 71             info=parse_info(info,"◎片　　长")
 72             movie['length']=info
 73         elif info.startswith("◎导　　演"):
 74             info=parse_info(info,"◎导　　演")
 75             movie['director']=info
 76         elif info.startswith("◎主　　演"):
 77             info=parse_info(info,"◎主　　演")
 78             actors=[info]
 79             for x in range(index+1,len(infos)):
 80                 actor=infos[x].strip()
 81                 if actor.startswith("◎"):
 82                     break
 83                 actors.append(actor)
 84             movie['actors']=actors
 85         elif info.startswith("◎简　　介"):
 86             info=parse_info(info,"◎简　　介")
 87             profiles=[info]
 88             for x in range(index+1,len(infos)):
 89                 profile=infos[x].strip()
 90                 if profile.startswith("【下载地址】"):
 91                     break
 92                 profiles.append(profile)
 93                 movie['profiles']=profiles
 94     download_url=html.xpath("//td[@bgcolor='#fdfddf']/a/@href")[0]
 95     #print(download_url)
 96     movie['download_url']=download_url
 97     return movie
 98
 99 movies=[]
100
101 def spider():
102     base_url = 'http://www.dytt8.net/html/gndy/dyzz/list_23_{}.html'
103     for x in range(1,2):  #how much page depend on you
104         # print("==="*30)
105         # print(x)
106         url=base_url.format(x)
107         detail_urls=get_detail_url(url)
108         for detail_url in detail_urls:
109             # print(detail_url)
110             movie=parse_detail_page(detail_url)
111             movies.append(movie)
112
113 if __name__ == '__main__':
114     spider()
115     with open('movies.txt','a',encoding='utf-8') as f:
116         for movie in movies:
117             f.write("="*30)
118             f.write('\n'*2)
119             for (key,value) in movie.items():
120                 if(key=='actors'):
121                     str='actors :{}'
122                     f.write(str.format(value))
123                     f.write('\n')
124                 elif(key=='profiles'):
125                     str='profiles :{}'
126                     f.write(str.format(value))
127                     f.write('\n')
128                 else:
129                     f.write(key+":"+value)
130                     f.write('\n')
131             f.write('\n'*3)