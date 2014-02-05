#!/usr/bin/env python

import schedule
import time
import praw
import urllib2
import sys
import json

# Bot to update ladder and streams in Scrolls subreddit sidebar
# Usage: python r_scrolls.py reddit_user reddit_pass

reddit = None
subreddit_name = "scrolls"

sentinel = "[~s~](/s)"
username = ""
password = ""

def login():

    global reddit
    global username
    global password

    reddit = praw.Reddit(user_agent='sidebar ladder updater for rscrolls [praw]')
    reddit.login(username, password)

def get_description():

    global reddit
    global subreddit_name

    return reddit.get_subreddit(subreddit_name).get_settings()['description']

def update_description(new_description):

    global reddit
    global subreddit_name

    print(new_description)
    print("==================================================")
    print("==================================================")
    print("==================================================")
    print("==================================================")
    print("==================================================")

    reddit.get_subreddit(subreddit_name).update_settings(description=new_description)


def streams():
    # between 1. and 2. sentinel

    login()
    old_description = get_description()

    parts = old_description.split(sentinel)

    try:
        f = urllib2.urlopen("https://api.twitch.tv/kraken/streams?game=Scrolls&limit=10")
        twitch_api = f.read()
        f.close()
        res = json.loads(twitch_api)

        # we want to get: res->streams-> EACH -> display_name
        #                                     -> url

        if len(res["streams"]) > 0:
            streams = "\n\n**Live streams**\n\n"
            for stream in res["streams"]:
                viewers = stream["viewers"]
                channel = stream["channel"]
                name = channel["display_name"]
                url  = channel["url"]
                streams += " * [%s (%s)](%s)\n" % (name,viewers,url)
        else:
            streams = ""

        parts[1] = streams

        # -------------------------------------------------------

        new_description = sentinel.join(parts)

        update_description(new_description)
    except URLError, e:
        print("Error loading streams: HTTP " + e.code)




def ladder():
    # between 3. and 4. sentinel

    login()
    old_description = get_description()

    parts = old_description.split(sentinel)

    # -------------------------------------------------------
    # edit part 3

    # a.scrollsguide.com doesn't like urllib, so apparently we're Google Chrome!
    request = urllib2.Request("http://a.scrollsguide.com/ranking?limit=10&fields=name,rating,rank")
    request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36")
    try:
        f = urllib2.urlopen(request)
        sg_api = f.read()
        f.close()

        res = json.loads(sg_api)
        top10 = ""

        if res['msg'] == 'success':
            i = 0
            for player in res['data']:
                i += 1
                top10 = "%s %d. %s (%d) \n" % (top10, i, player['name'], player['rating'])

            top10 = '\n\n**Ladder (top 10)**\n\n' + top10 + '\n\n[More at SG/ranking](http://scrollsguide.com/ranking)\n\n' + "[Last updated at %s](/smallText)" % time.strftime('%H:%M:%S UTC', time.gmtime())

        parts[3] = top10

        # -------------------------------------------------------

        new_description = sentinel.join(parts)

        update_description(new_description)
    except URLError, e:
        print("Error loading ladder: HTTP " + e.code)




def main():

    global username
    global password

    username = sys.argv[1]
    password = sys.argv[2]

    schedule.every(5).minutes.do(streams)
    schedule.every().hour.do(ladder)

    # on the startup do them both and THEN start counting time
    streams()
    print("--- Waiting 30s for Reddit to update its description")
    time.sleep(30)
    ladder()

    while True:
        schedule.run_pending()
        time.sleep(1)




if __name__ == '__main__':
    main()
