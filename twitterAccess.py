import json
import configparser
from requests_oauthlib import OAuth1Session


def auth():
    config = configparser.ConfigParser()
    config.read('./config.ini')
    CK = config['twitter']['CONSUMER_KEY']
    CS = config['twitter']['CONSUMER_SECRET']
    AT = config['twitter']['ACCESS_TOKEN']
    ATS = config['twitter']['ACCESS_TOKEN_SECRET']

    return OAuth1Session(CK, CS, AT, ATS)


def getTimeLine():
    twitter = auth()
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"  # タイムライン取得エンドポイント

    params = {'count': 5}  # 取得数
    res = twitter.get(url, params=params)

    if res.status_code == 200:  # 正常通信出来た場合
        timelines = json.loads(res.text)  # レスポンスからタイムラインリストを取得
        for line in timelines:  # タイムラインリストをループ処理
            print(line['user']['name']+'::'+line['text'])
            print(line['created_at'])
            print('*******************************************')
    else:  # 正常通信出来なかった場合
        print("Failed: %d" % res.status_code)
    return


def getListTimeLine(list_id, max_id, since_id):
    twitter = auth()
    url = "https://api.twitter.com/1.1/lists/statuses.json"  # タイムライン取得エンドポイント

    count = 100
    if not max_id and not since_id:
        params = {'list_id': list_id, 'count': count,
                  'include_entities': 'true', 'include_rts': 'true'}  # 取得数
    elif max_id:
        params = {'list_id': list_id, 'max_id': max_id, 'count': count,
                  'include_entities': 'true', 'include_rts': 'true'}  # 取得数
    elif since_id:
        params = {'list_id': list_id, 'since_id': since_id, 'count': count,
                  'include_entities': 'true', 'include_rts': 'true'}  # 取得数
    return twitter.get(url, params=params)
