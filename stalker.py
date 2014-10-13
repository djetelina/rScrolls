#!/usr/bin/env python

#Config Here:
subreddit_name = "Scrolls"
subreddit_id = "t5_2scq0"
page = "stalker"
usernames = ["MansOlson","carnalizer","BomuBoi","jonkagstrom","poipoichen", "SeeMeScrollin", "Atmaz", "jeb_", "aronnie"]
newcontent = ""

import json
import datetime
import urllib2
import time
import praw
import schedule
import sys
from ago import human
 
posts = []
username = ""
password = ""
reddit = None

def login():

    global reddit
    global username
    global password

    reddit = praw.Reddit(user_agent='Mojang stalker for /r/scrolls [praw]')
    reddit.login(username, password)
 
def stalk():
	try:
		login()
		for username in usernames:
			time.sleep(10)
			hdr = { 'User-Agent' : 'Mojang stalker bot for /r/scrolls' }
			req = urllib2.Request("http://www.reddit.com/user/%s/comments.json?limit=10"%username, headers=hdr)
			h = urllib2.urlopen(req)
			d = json.loads(h.read())
			for p in d["data"]["children"]:
				#Filter only a specific subreddit
				if p["data"]["subreddit_id"] == subreddit_id:
					posts.append(p)
		 
		#Sort by the time the post was created
		posts.sort(key=lambda p: p["data"]["created"],reverse=True)
		
		newcontent = ""
		for post in posts[0:20]:
			print("Author: %s" % post["data"]["author"])
			timestamp = human(datetime.datetime.fromtimestamp(post["data"]["created"]) - datetime.timedelta(hours=8))
			print ("Timestamp: %s" % timestamp)
			thread_id = post["data"]["link_id"][3:]
			comment_id = post["data"]["id"]
			url = "http://www.reddit.com/r/%s/comments/%s//%s?context=3" % (subreddit_name,thread_id,comment_id)
			print ("Url to comment: %s" % url)
			print ("%s by /u/%s") % (post["data"]["link_title"], post["data"]["link_author"])
			print ("---------------")
			newcontent += "/u/%s (%s) [%s](%s) by /u/%s \n\n>%s\n\n****\n\n" % (post["data"]["author"], timestamp, post["data"]["link_title"], url, post["data"]["link_author"], post["data"]["body"].replace("\n","\n> "))

		del posts[:]
		reddit.edit_wiki_page(subreddit=subreddit_name, page=page, content=newcontent, reason='')
	except Exception as e:
		print("Error stalking: " + str(e))

def main():

    global username
    global password

    username = sys.argv[1]
    password = sys.argv[2]

    schedule.every().hour.do(stalk)

    # on the startup do them both and THEN start counting time
    stalk()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
