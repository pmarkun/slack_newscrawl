from newsapi import NewsApiClient
import datetime
import requests
import json
from settings import *


class Trobador:
    def __init__(self, newsapi, slack_token, slack_channel):
        self.newsapi = NewsApiClient(api_key=newsapi)
        self.slack = {
            'token' : slack_token,
            'channel' : slack_channel
        }

    def cry(self, keyword, days=0):
        today = datetime.datetime.now()-datetime.timedelta(days)
        today = today.strftime('%Y-%d-%M')
        news = self.newsapi.get_everything(q=keyword, language='pt', sort_by='publishedAt', from_param=today)

        for article in news['articles']:
            noticia = Noticia(article['title'],article['description'],article['url'],article['urlToImage'],article['source']['name'], article['publishedAt'], keyword)
            payload={
                  "blocks" : noticia.toJSON(),
                  "token": self.slack['token'],
                  "channel" : self.slack['channel'],
                }
            r = requests.post("https://slack.com/api/chat.postMessage", params=payload)


class Noticia:
    def __init__(self, title, description, url, image, source, date, keyword):
        self.title = title
        self.description = description
        self.url = url
        self.image = image
        self.source = source
        self.date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        self.keyword = keyword

    def toJSON(self):
        self.msg = [{
        		"type": "section",
        		"text": {
        			"type": "mrkdwn",
        			"text": "*<{}|{}>* \n{}".format(self.url,self.title, self.description)
        		},
        		"accessory": {
        			"type": "image",
        			"image_url": self.image,
        			"alt_text": "+"
        		}
        	},
        	{
        		"type": "context",
        		"elements": [
        			{
        				"type": "mrkdwn",
        				"text": "*#{}* {} - {}".format(self.keyword, self.source, self.date.strftime("%d/%m %H:%M"))
        			}
        		]
        	}]
        return json.dumps(self.msg)


if __name__ == "__main__":
    boy = Trobador(SETTINGS['newsapi'], SETTINGS['token'], SETTINGS['channel'])
    for word in SETTINGS['keywords']:
        boy.cry(word, 3)
