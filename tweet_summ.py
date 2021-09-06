# coding: utf-8
import re
import time
import torch
import tweepy

from yahoo_crawl import news_crawl
from shorten_url import shorten_url
from normalizer import normalize_text, remove_brackets
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM


# 取得した各種キーを格納-----------------------------------------------------
consumer_key =""
consumer_secret =""
access_token=""
access_token_secret =""
 
# Twitterオブジェクトの生成
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
#-------------------------------------------------------------------------

# モデルとトークナイザーの準備
model = AutoModelForSeq2SeqLM.from_pretrained('t5_model/')    
tokenizer = AutoTokenizer.from_pretrained('sonoisa/t5-base-japanese') 

if __name__ == '__main__':
    news_category = ['domestic', 'world', 'business', 'entertainment', 'sports', 'it', 'science', 'local']
    tweeted_title = []
    for category in news_category:
        url = 'https://news.yahoo.co.jp/categories/' + category
        #url = "https://news.yahoo.co.jp/"
        news_dic = news_crawl(url)

        for idx in news_dic:
            time.sleep(30) #30秒ごとにツイート
            url = shorten_url(news_dic[idx]['URL'])
            title = news_dic[idx]['title']
            text = news_dic[idx]['text']
            if title in tweeted_title: #重複投稿回避
                continue
            text = normalize_text(remove_brackets(text))
            inputs = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)

            # 推論
            model.eval()
            with torch.no_grad():
                summary_ids = model.generate(inputs, max_length=512, min_length=5, length_penalty=1.0, repetition_penalty=2.5, num_beams=10) #, max_length=512, min_length=5, length_penalty=5., num_beams=2)
                summary = tokenizer.decode(summary_ids[0])
            summary = re.sub(r'<[^>]*?>', '', summary) #<pad>などを削除する
            text = ('{url}\n要約するぶー！\n{summary}'.format(url = url, summary = summary))
            print('この記事をツイート') #確認のため
            print(text)
            #api.update_status(text)
            tweeted_title.append(title)
