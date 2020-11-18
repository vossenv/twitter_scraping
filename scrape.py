import datetime
from time import sleep

import yaml
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# edit these three variables
user = 'realdonaldtrump'
start = datetime.datetime(2020, 11, 1)  # year, month, day
end = datetime.datetime(2020, 11, 2)  # year, month, day

# only edit these if you're having problems
delay = 5  # time to wait on each page load before reading the page
driver = webdriver.Chrome()  # options are Chrome() Firefox() Safari()

# don't mess with this stuff
twitter_ids_filename = 'all_tweets.yaml'
days = (end - start).days + 1
# id_selector = '.time a.tweet-timestamp'
id_selector = 'time'
# tweet_selector = 'li.js-stream-item'
tweet_selector = 'article'
user = user.lower()
ids = []

all_tweets = []

def format_day(date):
    day = '0' + str(date.day) if len(str(date.day)) == 1 else str(date.day)
    month = '0' + str(date.month) if len(str(date.month)) == 1 else str(date.month)
    year = str(date.year)
    return '-'.join([year, month, day])


def form_url(since, until):
    p1 = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A'
    p2 = user + '%20since%3A' + since + '%20until%3A' + until + 'include%3Aretweets&src=typd'
    return p1 + p2


def increment_day(date, i):
    return date + datetime.timedelta(days=i)


def extract_tweet(data, date):
    tweet = {}
    tweet['id'] = data.id
    tweet['text'] = data.text
    tweet['date'] = date
    return tweet


for day in range(days):
    d1 = format_day(increment_day(start, 0))
    d2 = format_day(increment_day(start, 1))
    url = form_url(d1, d2)
    print(url)
    print(d1)
    driver.get(url)
    sleep(delay)

    try:

        found_tweets = driver.find_elements_by_css_selector(tweet_selector)
        increment = 10
        while len(found_tweets) >= increment:
            print('scrolling down to load more tweets')
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(delay)
            found_tweets = driver.find_elements_by_css_selector(tweet_selector)
            increment += 10
        print('{} tweets found, {} total'.format(len(found_tweets), len(all_tweets)))
        all_tweets.extend([extract_tweet(t, d1) for t in found_tweets])

    except NoSuchElementException:
        print('no tweets on this day')
    start = increment_day(start, 1)

with open(twitter_ids_filename, 'w') as outfile:
    yaml.safe_dump(all_tweets, outfile)

print('all done here')
driver.close()
