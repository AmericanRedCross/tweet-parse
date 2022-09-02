# tweet-parse

## This is the current-state of tweet-parse. 

It is designed to run on a desktop within jupyter notebooks, requiring a folder structure to be created to house temp files.
Because I plan to convert this to run in google cloud, for now I won't spend a lot of energy documenting things.


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



## Sequence of script execution
Daily

Note the scripts all expect a .ENV file to exist with a valid API_KEY, API_KEY_SECRET, and BEARER_TOKEN env variable.

1) 'GetTweetsByKeyword' -- downloads tweets meeting certain pre-established search criteria
Weekly

1) 'GetTweetsByUser' -- downloads tweets from specific pre-identified users

2) Manual Step: Copy all tweets to a folder containing today's date [TODO: Make this an automated step]

3) run 'consolidate_weekly_tweets' -- searches and updates the local store of user information, does hard dedupes and writes out unique tweets to a single file. NOTE: This script can take a while because it throttles twitter requests to once every 5 seconds to stay under the 900 per 15 minute cap. [TODO: Test changing this to once every 2 seconds. 1 second should be enough but for some reason in practice this hasn't worked]

4) run 'procss_weekly_tweets' -- actually this might be the new version of consolidate...
