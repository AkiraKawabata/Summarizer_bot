import re
import time
import requests

from bs4 import BeautifulSoup


def news_crawl(url):
    news_dic = dict()
    dic_idx = 0

    # ヤフーニュースのトップページ情報を取得する
    
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    data_list = soup.find_all(href=re.compile("news.yahoo.co.jp/pickup"))

    headline_link_list = [data.attrs["href"] for data in data_list]

    news_textl = []
    #print('linls: ', headline_link_list)
    for headline_link in headline_link_list:
        #ex. https://news.yahoo.co.jp/byline/nishidamasaki/20210905-00256411'だとhtmlがうまくparseできない


        exist_text = True
        #time.sleep(5)

        summary = requests.get(headline_link)
        summary_soup = BeautifulSoup(summary.text, "html.parser")
        summary_soup_a = summary_soup.select("a:contains('続きを読む')")[0]

        news_body_link = summary_soup_a.attrs["href"]
        if 'https://news.yahoo.co.jp/articles/' not in news_body_link:
            continue
        news_body = requests.get(news_body_link)
        news_soup = BeautifulSoup(news_body.text, "html.parser")

        soupl = [news_soup]
        while True:
            parent = news_soup.find('li', class_ = 'pagination_item pagination_item-next')
            if parent is None:
                break
            else:
                next_page = parent.contents[0].attrs['href']
                next_url = 'https://news.yahoo.co.jp' + next_page
                #print('next_url: ', next_url)
                next_body = requests.get(next_url)
                news_soup = BeautifulSoup(next_body.text, "html.parser")
                soupl.append(news_soup)

        #print(news_soup.title.text)
        #print(news_body_link)

        texts = []
        for soup in soupl:
            details = soup.find_all(class_=re.compile('Direct'))
            for detail in details:
                if hasattr(detail, 'text'):
                    texts.append(detail.text)
                else:
                    exist_text = False
        
        if exist_text == False: #本文が取得できない時
            continue

        joined_text = ''.join(texts)
        kakko_pattern = '（.+?）|(【.+】.+)|\s'

        subed = re.sub(kakko_pattern, '', joined_text)

        #news_textl.append(subed)
        news_dic[dic_idx] = {}
        news_dic[dic_idx]['URL'] = news_body_link
        news_dic[dic_idx]['title'] = news_soup.title.text
        news_dic[dic_idx]['text'] = subed
        dic_idx += 1
    return news_dic

'''
if __name__ == '__main__':
    URL = "https://news.yahoo.co.jp/"
    dic = news_crawl(URL)
    for i in range(5):
        print('URL:', dic[i]['URL'])
        print('title:', dic[i]['title'])
        print('text:', dic[i]['text'])
'''