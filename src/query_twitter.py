#Test or Prod
env = 'prod'  #'prod'

if env == 'test':
    RESULTS_WORKBOOK = {'sheet_id' : '1HAqjdiUgvDK-0sQjsg-TYEIxJf2q0WD7X8XUs_pPOx0',
                     'range_names': ['staged_tweets','twitter_authors']}   
    stop_after = 1
    sleeptime = 1
    search_languages = ['en']
    control_input = 'googlesheets'
elif env == 'prod':
    RESULTS_WORKBOOK = {'sheet_id' : '1_6-O1D7UtbA4PiDNr71Fm-kA_OJk8S7RBctkGjZRIVk',
                     'range_names': ['tweet_list','staged_tweets','twitter_authors']}
    stop_after = -1
    sleeptime = 36000 #10 hour sleep time
    search_languages = ['es']
    control_input = 'googlesheets'
else:
    print("""'valid env values are 'prod' or 'test'""")
    
    
import re
import json
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import urllib.parse
#https://www.thepythoncode.com/article/translate-text-in-python
from googletrans import Translator
from google.oauth2 import service_account
import pygsheets
import pandas as pd
import time
import jmespath
import urlexpander

query_twitter_version = 'v2022-12-07'
runDate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

load_dotenv()

#twitter variables
API_Key = os.environ.get("API_KEY")
API_Key_Secret = os.environ.get("API_KEY_SECRET")
Bearer_Token = os.environ.get("BEARER_TOKEN")
bearer = 'bearer ' + Bearer_Token


#google variables
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")


# Google Sheets Variables
# variables that shouldn't change by person

SEARCH_WORKBOOK = {'sheet_id' : '1QjvZOnkCJM-BcRvMlP0XsN0hJeanKPiK7_e37uJiKek',
                    'range_names': ['twitter_keywords','stop_phrases']}


def instantiate_google_sheets_connector():
    # Set up Google Credentials
    #SERVICE_ACCOUNT_FILE = google_service_account_file

    SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # connect
    gc = pygsheets.authorize(credentials=service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, 
        scopes=SCOPES))
    
    return gc

gc = instantiate_google_sheets_connector()

#load to workbook objects
search_workbook = gc.open_by_key(SEARCH_WORKBOOK['sheet_id'])
results_workbook = gc.open_by_key(RESULTS_WORKBOOK['sheet_id'])

#generate read-only dataframes
keywords = search_workbook[0]
#df_r_keywords = pd.DataFrame(keywords.get_all_records())

stops = search_workbook[1]
#df_r_stop_phrases = pd.DataFrame(stop_phrases.get_all_records())

#generate updatable dataframes
tweet_list = results_workbook[0]
#df_u_tweet_list = pd.DataFrame(tweet_list.get_all_records())

staged_tweets = results_workbook[1]
#df_u_staged_tweets = pd.DataFrame(staged_tweets.get_all_records())

twitter_authors = results_workbook[2]
global DF_AUTHORS
DF_AUTHORS = pd.DataFrame(twitter_authors.get_all_records())


class twitter_scanner:
    def __init__(self, bearer, keywords):
        self.bearer = bearer
        self.base_api_url = 'https://api.twitter.com/2/tweets/search/recent?query='
        self.fixed_args = '-is:retweet  has:links '
        self.query_arg_suffix = '&max_results=100&tweet.fields=attachments,author_id,context_annotations,\
created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,\
referenced_tweets,source,text,withheld&expansions=referenced_tweets.id,geo.place_id'
        self.refresh_scan_terms()


        
    def __str__(self):
        return f'{self.query_arg_suffix}'

    def scan_for_search_terms(self,keywords):
        print(f'scanning for {keywords}')
        query_arg_prefix = self.fixed_args + keywords
        query_arg_prefix = urllib.parse.quote(query_arg_prefix)
        query = self.base_api_url + query_arg_prefix + self.query_arg_suffix
        
        response = requests.get(query, headers={"Authorization":bearer})
        return(json.loads(response.text))
        
    
    def scan_for_author(self,author):
        print(f'scanning for {author}')
        query_arg_prefix = urllib.parse.quote(f'-is:retweet  has:links from:{author}')   
        query = self.base_api_url + query_arg_prefix + self.query_arg_suffix

        
        response = requests.get(query, headers={"Authorization":bearer})
        return(json.loads(response.text))
    
    def refresh_scan_terms(self):
        self.keywords = pd.DataFrame(keywords.get_all_records())
        self.keywords.status = self.keywords.status.str.lower()
        self.keywords = self.keywords[self.keywords.status == 'active']

    
    def scan_all_active_terms(self,num,sleep_time):
        i = 0
        while i != num:
            i+=1
            self.refresh_scan_terms()
            key_terms = self.keywords.key_words[self.keywords.record_type == 'search_term'].tolist()
            authors = self.keywords.key_words[self.keywords.record_type == 'twitter_user'].tolist()
            
            for t in key_terms:
                res = self.scan_for_search_terms(t)
                df = tf.tweets_to_df(res)
                df['query_twitter_version'] = query_twitter_version
                df['search_term'] = f'search_string:{t}'
                ts.screen_tweets(df)

            for a in authors:
                res = self.scan_for_author(a)
                df = tf.tweets_to_df(res)
                df['query_twitter_version'] = query_twitter_version
                df['search_term'] = f'author:{a}'               
                ts.screen_tweets(df)            
    
            print(f'about to sleep for {sleep_time}, i is {i}')
            time.sleep(sleep_time)
            runDate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            print(f'waking up and running at {runDate}')
                  
    
tscanner = twitter_scanner(bearer, keywords)


class tweet_screener:
    def __init__(self, stops, staged_tweets):

        self.staged_tweets = pd.DataFrame(staged_tweets.get_all_records())
        self.stops = pd.DataFrame(stops.get_all_records())

    def __str__(self):
        return f'{self.stops}'

    
    def refresh_stops(self):
        #print('refreshing critera')
        self.stops = pd.DataFrame(stops.get_all_records())
        self.stops = self.stops[self.stops.type == 'text']
        print(self.stops)
        
    def refresh_saved_tweets(self):
        #print('refreshing saved tweets')
        self.staged_tweets = pd.DataFrame(staged_tweets.get_all_records())
        
    def screen_tweets(self, df_tweets):
        self.refresh_saved_tweets()
        #self.df_tweets = df_tweets
        
        #check to see if tweets have already been saved
         
        
        #print(f'before checking for dupes {df_tweets.shape}')
        df_tweets = df_tweets.assign(tweet_already_staged=df_tweets.tweet_id.isin(self.staged_tweets.tweet_id).astype(int))
        df_x = df_tweets[df_tweets['tweet_already_staged'] == 0]
        #print(f'after checking for dupes {df_x.shape}')
        self.stage_tweets(df_x)
        
        return df_tweets
    
    def stage_tweets(self, df_tweets):
        self.df_tweets = df_tweets
        
        #if anything remains, write to the tweet_list sheet
        if len(df_tweets) > 0:
            staged_tweets.append_table(df_tweets.values.tolist(), start='A1', end=None, dimension='ROWS', overwrite=False)
   
        #else:
            #print('No new content to add')
            
    def get_staged_tweets(self):
        return self.staged_tweets

    
ts = tweet_screener(stops, staged_tweets)


class tweet_formatter:
    def __init__(self):
        self
        # init the Google API translator
        self.translator = Translator()
    
    def tweets_to_df(self,json):

        
        cols = ['create_date','create_time','tweet_url','tweet_id','author_username',\
                'reference_url','text','orig_lang','orig_text']
        df_tweets = pd.DataFrame(columns=cols)
        
        if json['meta']['result_count'] == 0:
            #print('no results')
            return df_tweets # return an empty df
        
        
        for tweet in json['data']:
            
            tweet_id_pure = str(jmespath.search("id", tweet))
            tweet_id = f'tweet_id:{tweet_id_pure}'
            #print(tweet_id)
            urls = jmespath.search("entities.urls[*].expanded_url", tweet)
            primary_url = self.screen_urls(urls)
            
            ## if there's no primary url, don't bother with the rest
            if primary_url == 'none found':
                continue
                
                
            
            text = jmespath.search("text", tweet)
            orig_text = text
            text = self.scrub_text(text)
            original_lang = jmespath.search("lang", tweet)
            
            #don't translate english or twitter pseudo-codes
            #list found here: https://twittercommunity.com/t/unkown-language-code-qht-returned-by-api/172819
            stop_lang_codes = ['en','qam','qct','qht','qme','qst','zxx']
            if original_lang not in stop_lang_codes:
                try:
                    #print(f'translating from {original_lang} -- {text}')
                    translation = self.translator.translate(text, src=original_lang, dest='en')
                    text = translation.text
                    print(f'translated from {original_lang}')
                except Exception as e:
                    print(f'translation issue {original_lang}\n\n{e}')
                    print(f'{tweet_id} ')
                    print(f'text: {text} ')
                    #print('tweet')
                    
                    
            
            created_date = jmespath.search("created_at", tweet)
            create_date, create_time = created_date.split('T')
            create_time = create_time[:8]
            
            author_id = jmespath.search("author_id", tweet)
            author_username = self.get_author_info(author_id)
            
            tweet_url = f'https://twitter.com/{author_username}/status/{tweet_id_pure}'
            
            tweet_info = [create_date, create_time, tweet_url, tweet_id, author_username, primary_url, text, original_lang, orig_text ]

            df_tweets.loc[len(df_tweets)] = tweet_info
            
            df_tweets = df_tweets.drop_duplicates(subset='reference_url')
            
            
        return df_tweets
            
    def scrub_text(self,t):
    
        if isinstance(t, str):
            #remove newlines
            t = re.sub('\n', ' ', t)
            #remove amp
            t = re.sub('&amp;', ' and ', t)
            #remove pipes because I use them as delimiters
            t = t.replace('|', ' ')  
            #remove unicode special chars
            string_encode = t.encode("ascii", "ignore")
            t = string_encode.decode()

        return t
    
    def screen_urls(self,urls):
        #capture urls
        patterns = [re.compile("pic\.twitter\.com"), 
                    re.compile("twitter\.com"),
                    re.compile("amzn\."),
                    re.compile("youtube\."),
                    re.compile("linkedin\."),
                   ]
        returnUrls = []

        for url in urls:
            include = 'Y'
            for pattern in patterns:
                if pattern.search(url) != None:
                    include = 'N'
            if include == 'Y':
                returnUrls.append(url)
                
        main_url = 'none found'      
        if len(returnUrls) > 0:
            main_url = returnUrls[0]

        return main_url
    
    
    def get_author_info(self,author_id):
        global DF_AUTHORS
        global runDate
        #add the "TID"
        internal_author_id = 'TID' + author_id

        auth_list = DF_AUTHORS[DF_AUTHORS['author_id'] == internal_author_id].values.tolist()
        if len(auth_list) == 1:
            where = 'locally'
            author_username = auth_list[0][3]

        elif len(auth_list) > 1:
            author_username = 'UNKN_MultipleResultsReturned'

        else:
            print(f'no individual author match on {author_id} ... trying twitter')

            userFields = 'location,url,description,entities'
            api_getAuthor = f'https://api.twitter.com/2/users?ids={author_id}&user.fields={userFields}'
            response = requests.get(api_getAuthor, headers={"Authorization":bearer})
            author_from_twitter = json.loads(response.text)
            time.sleep(1) #throttle volume
            #print(f' found {author_from_twitter}')

            if 'data' in author_from_twitter:
                
                author_name = author_from_twitter['data'][0]['name']
                author_username = author_from_twitter['data'][0]['username']
                try:
                    author_description = author_from_twitter['data'][0]['description']
                except:
                    author_description = ''
                try:
                    author_url = author_from_twitter['data'][0]['url']
                except:
                    author_url = ''

            elif 'errors' in   author_from_twitter:
                author_name = author_from_twitter['errors'][0]['title']
                author_username = author_from_twitter['errors'][0]['title']
                author_description = author_from_twitter['errors'][0]['detail']
                author_url = author_from_twitter['errors'][0]['type']

            else:
                author_username = 'UNKNN_NoResultsReturned'



            # add values to google sheets
            vals= [runDate, internal_author_id, author_name, author_username, author_description, author_url]

            #print(f'before cleanup of {vals}')
            #clean up text 
            for i, item in enumerate(vals):
                vals[i] = self.scrub_text(item)
            #print(f'after cleanup of {vals}')

            twitter_authors.append_table(vals, start='A1', end=None, dimension='ROWS', overwrite=False)

            # add values to DF_AUTHORS
            r = pd.Series(vals, index = DF_AUTHORS.columns)
            DF_AUTHORS = DF_AUTHORS.append(r, ignore_index=True)


        return author_username

    

#assert get_author_info('2576444334') == 'TheMissingMaps' #positive use-case
#assert get_author_info('1477759062884421631') == 'Not Found Error' #negative use-case


#assert scrub_text('asdfa|sdf &amp; dsdfgsdfg') == 'asdfa sdf  and  dsdfgsdfg'
tf = tweet_formatter()


tscanner.scan_all_active_terms(stop_after,sleeptime)






