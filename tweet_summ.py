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

'''
#text = '9月2日15時すぎ、東京・霞ヶ関の司法記者クラブで開かれた会見。  松永真菜さんの夫、松永拓也さんは「判決を聞いて、すごく複雑な感情になりました。やっぱり、本心を言ってしまえば、命は戻らないという虚しさを感じる。でも、この判決は私達が前を向いて生きていくきっかけになると思います。やってきてよかった」と語った。  その上で飯塚被告については、「何よりも、2人の命と罪に向き合って欲しかった」と口にした。  「これはラストチャンスです。判決で客観的事実が認定された。まずこれを受け入れるラストチャンスです。そして過ちを認めた上で謝罪をする、これもラストチャンスなのだと思います」   真菜さんの父・上原義教さん  会見には真菜さんの父、上原義教さんも出席した。「（量刑が）5年でも何年でも、2人は戻ってきませんので、その点が一番残念ではあります」「親としては楽しいこと、辛いこと、色々な思いがあります。禁錮5年は短いと思う」とコメント。  「自分は過ちをおかしたと、それを受け止めていただいて、心からの謝罪をしてほしい」と強調しつつ、次のように語った。  「これで少し前を向いて歩んでいけるのかな。心に大きな穴が空いてしまっている、埋めることは一生できないかもしれないけど、少しだけ前を向いていける気がしました」  2人の命と向き合って生きてきた2年4ヶ月 事故からここまでの歩みを振り返り、松永さんは「悲しみと苦しみと絶望と、死んだ方が良いんじゃないかというところから始まった。多くの人に支えられて、なんとか生きようと、2人の命と向き合って生きてきた2年4ヶ月だった」とつぶやいた。  「悲しみと苦しみが襲ってくるタイミングはこれからもある。波は穏やかになっていくと思いますが、悲しみや苦しみは一生続くだろうと感じています」  「でも、ひとつの区切りには間違いなくなった。波が穏やかになるためにも、大きな1日、大きな判決だったと思います」  松永さんは、事故直後から報道陣の取材に応じ、交通事故の再発防止を訴えてきた。  この日の会見でも、この事故だけが注目されるのでだめだと何度も繰り返し、交通事故を減らすため、社会全体で議論していく必要があるのではないかと問題提起した。  「池袋暴走事故は大きな注目を集めた事故であることは確かです。ただ、交通事故は年間40万件近く起きる、死亡者は年間3000人近く。だからこそ、実は誰しもが当事者になり得る。私は皆さんに当時者になってほしくない。交通事故をひとつでも無くしていくために活動をしたいと考えています」'
#text = normalize_text(remove_brackets(text))

inputs = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)

# 推論
model.eval()
with torch.no_grad():
    summary_ids = model.generate(inputs, max_length=512, min_length=5, length_penalty=1.0, repetition_penalty=2.5, num_beams=2) #, max_length=512, min_length=5, length_penalty=5., num_beams=2)
    summary = tokenizer.decode(summary_ids[0])
    print(summary)
'''

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
            print('この記事をツイート')
            print(text)
            #api.update_status(text)
            tweeted_title.append(title)
