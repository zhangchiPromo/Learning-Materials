import urllib.request
import re
import pandas as pd
import os
import time
import requests

# 设置表头，这里需要注意的是，搜狗会根据爬取频率进行反爬，如果抓不到网页时需要更新cookie和uuid
headers = {
    'Cache-Control': "no-cache",
    'Cookie': 'SUV=00C555450E17380E59E0BA849208F883; SUID=0438170E3765860A5A0E5B44000D181F; IPLOC=CN4403; ABTEST=6|1544784185|v1; weixinIndexVisited=1; ppinf=5|1544968129|1546177729|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyNzolRTYlOUUlOTclRTYlQTUlOUElRTYlQjUlQjd8Y3J0OjEwOjE1NDQ5NjgxMjl8cmVmbmljazoyNzolRTYlOUUlOTclRTYlQTUlOUElRTYlQjUlQjd8dXNlcmlkOjQ0Om85dDJsdVBMVkU4eVUxc0c0TlhGLUI3RFNhX2tAd2VpeGluLnNvaHUuY29tfA; pprdig=hDc_xZlQrc3H4aXVf_8GT98xI-BGt-n1ZuBx9uT3xeUHlaMxlUZgj8oFKqOEWaLurQh_Fr5A5KOjBwsbz7zhsFwYogGBE6vXf8tBSOt0eu-jOFv65Gtw2mmUP44WjwW_uKI7zaiHVohLEuqaiNQkBedKYK2_12JHnjTiTie8lQk; sgid=23-38371477-AVwWV8H4ibb8zCtzQVFJEsns; SUIR=78A01EA612146DEB0989880A12788972; SNUID=F4ECC5F0EBEF96CE9225D53EEBE8FB92; sct=11; ld=Tlllllllll2tV16UlllllVZgvSylllllHZMeYlllll9lllll9ylll5@@@@@@@@@@; LSTMV=246%2C72; LCLKINT=3156; ppmdig=154502991200000021dde46c3f50c25b028f60b868f299c6; JSESSIONID=aaaoA200iNipMaOiCa7Cw',
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    'UUID': "3aa12688-86c7-49c1-aa06-89f76ceed15a",
}


def replace_url_char(url):
    """
    替换url中因转义产生的特殊字符，如&amp;
    :param url: 爬取到的url链接
    :return:
    """
    url = re.sub('&amp;', '&', url)
    return url


def filter_html_label(text):
    """
    过滤掉文本中的html标签
    :param text:
    :return:
    """
    text = re.sub('font-family: .*?[,|;|]', '', text)
    text = re.sub('[^\\u4e00-\\u9fa5]|后台回复', '', text)
    return text


def get_all_url(keyword='咪蒙', page=100, headers=headers):
    """
    获取指定公众号文章的所有链接
    :param keyword: 公众号名称. [str]
    :param page: 获取多少个页面的链接. [int]
    :param headers: 请求表头. [dict]
    :return:
    """
    # 获取文章链接
    all_url_list = []
    for i in range(page):
        url = "https://weixin.sogou.com/weixin"
        querystring = {"query": keyword, "_sug_type_": "", "s_from": "input", "_sug_": "n", "type": "2", "page": str(i), "ie": "utf8"}
        search_data = requests.request("GET", url, headers=headers, params=querystring)
        url_pattern = 'data-z="art" target="_blank".*href="(.*?)"'
        url_list = re.compile(url_pattern).findall(search_data.text)
        url_list = [replace_url_char(i) for i in url_list]
        all_url_list.extend(url_list)
        print("finished page：%d" % (i + 1))
        print('url length: %d' % len(all_url_list))
        time.sleep(50)
    return all_url_list


def get_content(text_url, keyword):
    """
    获取给定链接的文章内容
    :param text_url: 链接. [url]
    :param keyword: 公众号名称. [str]
    :param headers: 表头信息. [dict]
    :return:
    """
    text_data = urllib.request.urlopen(text_url).read().decode('UTF-8', 'ignore')
    author_pattern = '<strong class="profile_nickname">(.*?)</strong>'
    try:
        author = re.compile(author_pattern, re.S).findall(text_data)[0]
    except:
        author = ''
    text_pattern = '<p style=(.*?)</p>'
    text_list = re.compile(text_pattern, re.S).findall(text_data)
    text = ''.join(text_list)
    text = filter_html_label(text)
    title_pattern = '<title>(.*?)</title>'
    title = re.compile(title_pattern, re.S).findall(text_data)
    title = re.sub('\n', '', title[0])
    print("finished content:《%s》" % (title))
    # opener.close()
    time.sleep(50)
    return [title, author, text]


def save_as_csv(content_list, keyword):
    """
    将爬虫结果保存到本地data文件夹路径下，保存格式为csv格式
    :param content_list: 爬取到的文章内容. [list]
    :param keyword: 文件名称. [str]
    :return:
    """
    content_list = pd.DataFrame(content_list, columns=['title', 'author', 'content'])
    content_list.to_csv(os.path.join('./data', keyword + '_文章.csv'), index=False)


if __name__ == '__main__':
    # 设定公众号名称和爬取的页数
    keyword = '咪蒙'
    page = 100

    # # 获取所有的文章链接
    # all_url_list = get_all_url(keyword, page)
    # if not os.path.exists('./data'):
    #     os.mkdir('./data')
    #
    # f = open('./data/%s_链接.txt' % keyword, 'w', encoding='utf-8')
    # for i in all_url_list:
    #     f.writelines(str(i)+'\n')
    # f.close()

    # 获取所有的文章
    with open('./data/%s_链接.txt' % keyword, 'r', encoding='utf-8') as f:
        all_url_list = f.read()
    all_url_list = all_url_list.split('\n')
    all_url_list = all_url_list[:-1]
    all_content = []
    for url in all_url_list:
        all_content.append(get_content(url, keyword))

    # 保存到本地csv文件
    save_as_csv(all_content, keyword)
