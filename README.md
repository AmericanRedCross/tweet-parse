# tweet-parse

## This is the current-state of tweet-parse. 

It is designed to run on a desktop within jupyter notebooks for now. This script periodically queries Twitter
for key words, as well as the tweets of specified users, then stores the relevant results in a google sheet
for later manual review.

The inputs (query terms and users) also come from a google sheet. Those can be changed at any time if one has
the proer permissions.

The code still writes 'backup' copies of search results to local disk and will continue to do so until Q1 2023.


## Description of folder structure needed to support execution

### Wherever you choose to place the jupyter notebookds
{root folder} 

### folder where tweets are just saved to disk based on search criteria. Non-deduped
{root folder}/twitter_data/staged_tweets/

### location where, before running the consolidate_weekly_tweets, one must manually copy to.
### this should just be automated away.
{root folder}/twitter_data/{dateFolder}/

### file that caches author information. Is it referred to and expanded by consolidate_weekly_tweets
{root folder}/twitter_data/saved_mappings/authors.json

### location where consolidated and deduped weekly files are placed
{root folder}/twitter_data/weekly_files/

### location where a pipe-delimited file is placed containing the output of all that came before. This is then manually pasted into a running
### Excel file for final review and dispositioning.
{root folder}/twitter_data/weekly_summaries/



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

