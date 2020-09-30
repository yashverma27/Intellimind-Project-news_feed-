#!/usr/bin/env python
# coding: utf-8

# # OBJECTIVE
# ####       To scrap news from different news sites and store them in json file

# In[1]:


## importing Libraries
import feedparser as fp
import json
import newspaper
from newspaper import Article
from time import mktime
from datetime import datetime



# In[2]:


LIMIT = 5   ## Set the limit for number of articles to download

data = {}
data['newspapers'] = {}

## Loads the JSON files with news sites
with open('newspaper.json') as data_file:
    companies = json.load(data_file)

count = 1

# Iterate through each news company present in the above file
for company, value in companies.items():
    # If a RSS link is provided in the JSON file, this will be the first choice.
    # Reason for this is that, RSS feeds often give more consistent and correct data.
    # If we do not want to scrape from the RSS-feed,so, just leave the RSS attr empty in the JSON file.
    if 'rss' in value:
        d = fp.parse(value['rss'])
        print("Downloading articles from ", company)
        newsPaper = {
            "rss": value['rss'],
            "link": value['link'],
            "articles": []
        }
        for entry in d.entries:
            # Check if publish date is provided, if no the article is skipped.
            # This is done to keep consistency in the data and to keep the script from crashing.
            if hasattr(entry, 'published'):
                if count > LIMIT:
                    break
                article = {}
                article['link'] = entry.link
                date = entry.published_parsed
                ##date is printed in ISO format
                article['published'] = datetime.fromtimestamp(mktime(date)).isoformat()
                try:
                    content = Article(entry.link)
                    content.download()
                    content.parse()
                except Exception as e:
                    # If the download for some reason fails (ex. 404) the script will continue downloading
                    # the next article.
                    print(e)
                    print("continuing...")
                    continue
                article['title'] = content.title
                article['text'] = content.text
                newsPaper['articles'].append(article)
                print(count, "articles downloaded from", company, ", url: ", entry.link)
                count = count + 1
    else:
        # This if a RSS-feed link is not provided then this block will execute.
        # It uses the python newspaper library to extract articles
        print("Building site for ", company)
        paper = newspaper.build(value['link'], memoize_articles=False)
        newsPaper = {
            "link": value['link'],
            "articles": []
        }
        noneTypeCount = 0
        for content in paper.articles:
            if count > LIMIT:
                break
            try:
                content.download()    ##downloading the content
                content.parse()       ## parsing 
            except Exception as e:
                print(e)
                print("continuing...")
                continue
            ## if there is no found publish date the article will be skipped.
            ## After 10 downloaded articles from the same newspaper without publish date, the company will be skipped.
            if content.publish_date is None:
                print(count, " Article has date of type None...")
                noneTypeCount = noneTypeCount + 1
                if noneTypeCount > 10:
                    print("Too many noneType dates, aborting...")
                    noneTypeCount = 0
                    break
                count = count + 1
                continue
            article = {}
            article['title'] = content.title
            article['text'] = content.text
            article['link'] = content.url
            article['published'] = content.publish_date.isoformat()
            newsPaper['articles'].append(article)
            print(count, "articles downloaded from", company, " using newspaper, url: ", content.url)
            count = count + 1
            noneTypeCount = 0
    count = 1
    data['newspapers'][company] = newsPaper

## Finally it saves the articles as a JSON-file.
try:
    with open('scraped_articles.json', 'w') as outfile:
        json.dump(data, outfile)
except Exception as e: print(e)


# # Observation
# #### 1) newspaper.json file contain sites from which we will extract the data.
# #### 2) Output of extracted news is stored in scraped_articles.json file.

# In[ ]:




