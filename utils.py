import datetime
from configparser import ConfigParser


MONTH_STR2INT = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
TWITTER_TIMESTAMP_STRF = '%a %b %d %H:%M:%S %z %Y'
 
def twitter_timestamp_to_datetime(timestamp):
    """ Convert string representation of timestamps used by Twitter to a datetime object. """
    then = datetime.datetime.strptime(timestamp, TWITTER_TIMESTAMP_STRF)
    return then
 
def datetime_to_twitter_timestamp(then):
    """ Convert datetime object to string representation of timestamps used by Twitter. """
    timestamp = datetime.datetime.strftime(then, TWITTER_TIMESTAMP_STRF)
    return timestamp
 
def datetime_to_short_timestamp(then):
    """ Convert datetime object to short string representation. """
    short = then.replace(microsecond=0).replace(tzinfo=None).isoformat(sep="-")
    return short

def load_credentials(path): 
    # Load Twitter API credentials
    config = ConfigParser()
    config.read(path)
    cred = {}
    cred["consumer_key"] = config["credentials"]["consumer_key"]
    cred["consumer_secret"] = config["credentials"]["consumer_secret"]
    cred["access_token"] = config["credentials"]["access_token"]
    cred["access_secret"] = config["credentials"]["access_secret"]
    return cred
