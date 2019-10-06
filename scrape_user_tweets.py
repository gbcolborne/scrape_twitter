import os, sys, json, datetime, time, argparse
import tweepy
from tweepy import OAuthHandler
import utils
 
"""
Scrape a Twitter user's timeline.

Go back n days (to the morning of the day which is n days prior to
today).
 
Write tweets in JSON format.
"""

def scrape_user_timeline(api, user_name, max_past, verbose=True):
    timeline = tweepy.Cursor(api.user_timeline, screen_name=user_name)
    HIT_THEN = False
    statuses = []
    try:
        for status in timeline.items():
            status = status._json
            # Check date and time to see if we have gone back far enough in the past
            timestamp = status["created_at"]
            then = utils.twitter_timestamp_to_datetime(timestamp)
            if then < max_past:
                HIT_THEN = True
                break
            statuses.append(status)
            # Print progress
            if verbose:
                now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
                now = utils.datetime_to_short_timestamp(now)
                then = utils.datetime_to_short_timestamp(then)
                print("{}: got status from {}.".format(now, then))
    except tweepy.error.TweepError as e:
        print(e)
        print("Scraping interrupted")
    if not HIT_THEN:
        msg = "WARNING: scraper can not reach all the way back to target date."
        msg += " Maybe this is due to rate limiting of the user_timeline API," 
        msg += " or the max number of tweets accessible throught that API."
        print(msg)
    return statuses

 
parser = argparse.ArgumentParser()
parser.add_argument("--nb_days", type=int, default=1)
parser.add_argument("user_names", type=str, help="Path of text file containing Twitter user screen names (start with '@'), one per line")
parser.add_argument("path_credentials", type=str, help="Path of config file containing Twitter API credentials")
parser.add_argument("path_output", type=str, help="Path of output file")
args = parser.parse_args()
 
# Check args
if args.nb_days < 1:
    raise ValueError("nb_days must be positive")
 
# Load credentials
cred = utils.load_credentials(args.path_credentials)
 
# Set date and time where we stop (morning of the day args.nb_days
# prior to today, which I will arbitrarilty set to 12:00 PM UTC, which
# is 7:00 AM EST). 
now = datetime.datetime.now()
delta = datetime.timedelta(days=args.nb_days)
then = now - delta
that_morning = datetime.datetime(then.year, then.month, then.day, hour=12, tzinfo=datetime.timezone.utc)
 
# Get API instance. Make the API wait when it hits rate limits.
auth = OAuthHandler(cred["consumer_key"], cred["consumer_secret"])
auth.set_access_token(cred["access_token"], cred["access_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Get user names
user_names = []
with open(args.user_names) as f:
    for line in f:
        name = line.strip()
        if len(name):
            if name[0] == "@":
                name = name[1:]
            user_names.append(name)

print("Preparing to scrape timelines going back to {} for following users: {}".format(that_morning, ", ".join(user_names)))
 
# Scrape timelines
name_to_tweets = {}
for user_name in user_names:
    name_to_tweets[user_name] = scrape_user_timeline(api, user_name, that_morning, verbose=True)

for name, tweets in name_to_tweets.items():
    print("Nb tweets collected from {}: {}".format(name, len(tweets)))
print("\nTotal nb tweets collected: {}".format(sum(len(t) for n,t in name_to_tweets.items())))
 
# Write (pretty)
with open(args.path_output, "w") as f:
    for user_name, tweets in name_to_tweets.items():
        if len(tweets):
            json.dump(tweets, f, sort_keys=True, indent=2)
    
print("Wrote tweets --> {}".format(args.path_output))
