# scrape_twitter

A couple scripts to scrape Twitter using the official APIs

Note: you must obtain your own Twitter developer credentials (consumer keys and access tokens). See [https://developer.twitter.com](https://developer.twitter.com). 

## Contents 

* `scrape_user_tweets.py`: scrape tweets of specific users for the past _n_ days. Note: this script exploits the `home_timeline` API, which can only access roughly 800 tweets. 

* `scrape_my_feed.py`: scrape my feed, including the tweets of users I follow, for the past _n_ days. 



## Requirements

* Python 3
* Tweepy