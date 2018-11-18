from django.shortcuts import render
from itertools import chain
import twitterAccess
import json
import datetime
import os
import codecs
import urllib.error
import urllib.request
import configUtils


def hasPhoto(tweet):
    extends_entities = tweet.get('extended_entities')
    if extends_entities:
        if extends_entities.get('media'):
            return True
    return False


def getImageTweetInfo(tweet):
    tweet_text = tweet['text']
    tweet_date = tweet['created_at']
    imageUrlList = [media['media_url_https']
                    for media in tweet['extended_entities']['media']]
    return (tweet_text, imageUrlList, tweet_date)


def writeTweetInfo(tweetInfo, filePath, fileName):

    if not tweetInfo:
        return
    with open(filePath + 'tweetInfo\\' + fileName, 'ab') as file:
        separator = '----------------------------\n\n'.encode(
            'cp932', 'ignore')
        lf = '\n'.encode('cp932', 'ignore')
        file.write(separator)

        for tweet in tweetInfo:
            file.write(tweet[2].encode('cp932', 'ignore'))
            file.write(lf)
            file.write(tweet[0].encode('cp932', 'ignore'))
            file.write(lf)
            file.write('\n'.join(tweet[1]).encode('cp932', 'ignore'))
            file.write(lf + lf + separator)
    return


def downloadImages(imageUrlList, downloadPath):
    for url in imageUrlList:
        downloadImage(url, downloadPath)
    return


def downloadImage(url, downloadPath):
    fileName = appendSuf(url.split('/')[-1], '-orig')
    try:
        image = urllib.request.urlopen(url + ':orig').read()
        with open(downloadPath + fileName, mode="wb") as file:
            file.write(image)

    except urllib.error.URLError as e:
        print(e)
    return


def appendSuf(name, suffix):
    array = name.split('.')
    array[0] += suffix
    return '.'.join(array)


def existsConfig(section, option):
    return config.has_section(section) and config.has_option(section, option)


def getTweets(res):

    if res.status_code == 200:

        tweets = json.loads(res.text)

        imageTweets = [tweet for tweet in tweets if hasPhoto(tweet)]
        imageTweets = [getImageTweetInfo(tweet) for tweet in imageTweets]

        imageUrlList = list(chain.from_iterable(
            [tweet[1] for tweet in imageTweets]))

        sysDate = datetime.datetime.now()
        filePath = 'H:\\picture\\自動収集\\'

        writeTweetInfo(imageTweets, filePath,
                       sysDate.strftime('tweetInfo_%Y%m%d.txt'))
        downloadImages(imageUrlList, filePath)

        if tweets:
            since_id = tweets[0].get('id') + 1
            max_id = tweets[-1].get('id') - 1
        else:
            since_id = -1
            max_id = -1
        return (since_id, max_id)
    else:
        print('error!')
        print(res.status_code)
        return


def getTimeLine(section, option, func):
    if existsConfig(section, option):
        param = config.get(section, option)
        return func(param)
    return twitterAccess.getListTimeLine(
        list_id=_list_id, max_id='', since_id='')


def getOldTimeLine(param):
    return twitterAccess.getListTimeLine(
        list_id=_list_id, max_id=param, since_id='')


def getNewTimeLine(param):
    return twitterAccess.getListTimeLine(
        list_id=_list_id, max_id='', since_id=param)


os.chdir(os.path.dirname(__file__))

confFile = './config.ini'
config = configUtils.getConfigParser(confFile)
_list_id = 965107604148989952
section = 'list-' + str(_list_id)
_max_id = 'max_id'
_since_id = 'since_id'

max_id = 0
since_id = 0
# とりあえず1回の実行で5回繰り返す
for i in range(5):
    if max_id != -1:
        oldTweetsRes = getTimeLine(section, _max_id, getOldTimeLine)
        max_id = getTweets(oldTweetsRes)[1]

    if since_id != -1:
        newTweetsRes = getTimeLine(section, _since_id, getNewTimeLine)
        since_id = getTweets(newTweetsRes)[0]

    if max_id != -1:
        configUtils.writeOption(
            confFile, config, section, _max_id, str(max_id))

    if since_id != -1:
        configUtils.writeOption(
            confFile, config, section, 'since_id', str(since_id))
