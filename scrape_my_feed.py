import sys, json, datetime, time, argparse
import tweepy
from tweepy import OAuthHandler
import utils
 
"""
Scrape my Twitter feed (timeline) using Twitter's official Search API
(which is rate-limited, but provides free and easy access to the timeline).
 
Go back n days (to the morning of the day which is n days prior to
today).
 
Write tweets in JSON format.
"""
 
 
parser = argparse.ArgumentParser()
parser.add_argument("--nb_days", type=int, default=1)
parser.add_argument("path_credentials", type=str, help="Path of config file containing Twitter API credentials")
parser.add_argument("path_output", type=str, help="Path of output file")
args = parser.parse_args()
 
# Check args
if args.nb_days < 1:
    raise ValueError("nb_days must be positive")
 
# Load credentials
cred = utils.load_credentials(args.path_credentials)
 
# Set date and time where we stop (morning of the day args.nb_days prior to today, which I will arbitrarilty set to 12:00 PM UTC, which is 7:00 AM EST). 
now = datetime.datetime.now()
delta = datetime.timedelta(days=args.nb_days)
then = now - delta
that_morning = datetime.datetime(then.year, then.month, then.day, hour=12, tzinfo=datetime.timezone.utc)
print("Preparing to scrape tweets going back to {}...".format(that_morning))
 
# Get API instance. Make the API wait when it hits rate limits.
auth = OAuthHandler(cred["consumer_key"], cred["consumer_secret"])
auth.set_access_token(cred["access_token"], cred["access_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
 
# Scrape timeline
timeline = tweepy.Cursor(api.home_timeline)
statuses = []
HIT_THEN = False
try:
    for status in timeline.items():
        status = status._json
 
        # Check date and time to see if we have gone back far enough in the past
        timestamp = status["created_at"]
        then = utils.twitter_timestamp_to_datetime(timestamp)
        if then < that_morning:
            HIT_THEN = True
            break
 
        statuses.append(status)
 
        # Print progress
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        now = utils.datetime_to_short_timestamp(now)
        then = utils.datetime_to_short_timestamp(then)
        print("{}: got status from {}. Nb collected: {}.".format(now, then, len(statuses)))
except tweepy.error.TweepError as e:
    print(e)
    print("Scraping interrupted")
 
if not HIT_THEN:
    msg = "WARNING: scraper can not reach all the way to the morning of the day {} prior to today.".format(args.nb_days)
    msg += " Maybe this is due to rate limiting of the user_timeline API, or the max number of tweets accessible throught that API."
    print(msg)
 
print("\nNb statuses collected: {}".format(len(statuses)))
 
# Write (pretty)
with open(args.path_output, "w") as f:
    json.dump(statuses, f, sort_keys=True, indent=2)
 
print("Wrote statuses --> {}".format(args.path_output))
