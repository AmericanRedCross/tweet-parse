# tweet-parse

## This is the current-state of tweet-parse. 

This script periodically queries Twitter for key words, as well as the tweets of specified users, 
then stores the relevant results in a google sheet for later manual review.

The inputs (query terms and users) also come from a google sheet. Those can be changed at any time if one has
the proper permissions.


## High Level Design is as follows:

3 main classes

### twitter_scanner
An instantion of this class polls the input sheet (defined below) for the things to search for
and periodically performs said search (periodicity hard coded in the code itself, currently set for every 10 hours)

### tweet_formatter
This object performs various cleanup operations.. stripping out emojis, translates to English, removes tweets with
duplicate urls, etc

### tweet_screener
This object compares the resultant list of tweets against what's already stored on google sheets and saves
everything that is net new.


## Input Sheet (how you control the script)
The input sheet is the way you control what keywords and users to search for.
The format of the sheet is as follows:

4 columns (3 required)
record_type: put 'search_term' for keywords, or 'twitter_user' for an account name
key_words: put any search terms if the record type is 'search_term', or a user account name if 'twitter_user'
status: active or inactive 
status_reason: put any contextual info you want, this has no effect on the functionality of the script.

NOTE: this tab can be called whatever you want, but for now it MUST be the first sheet in the workbook.

## Output Sheet (results capture)
When the script runs, it saves tweets to a tab "staged_tweets" and author info to "twitter_authors"
those two tabs must be the 2nd and 3rd tab respectively




## General Configuration Requirements
To run this, one must have:
1) a Twitter dev account
2) a Google sheets account (with permissions to the relevant google sheets)

The API Key and service account info must be put in a .ENV file with the following entries

		API_KEY=
		API_KEY_SECRET=
		BEARER_TOKEN=
		GOOGLE_SERVICE_ACCOUNT_FILE=


GOOGLE_SERVICE_ACCOUNT_FILE must point to a JSON file you get from google with the same basic key content

