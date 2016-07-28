twitterads
==============

Python interface to twitter ads api <br />
Detailed Doc - https://dev.twitter.com/ads/overview

Installation
============

pip install twitterads

Features
========
The library, helps you create, run and modify a campaign over twitter. 
Upload Hashed email/twiiter_id/phone_number csvs as tailored audience lists using Ton API

PS-The library is not exhaustive and does not cover all the api methods but feel free to add new methods
as and when required


Using the Library
=================


```python
from twitterads.twitter_ads import TwitterAds
import sys

tads = TwitterAds(twitter_consumer_key, twitter_consumer_secret,
                  access_token, access_token_secret)

'''
  Get ads_account_id if you just have the name
'''

ads_account_id = tads.get_adds_account_id_from_name(account_name='Mariana')

'''
  Verify If you have permissions for ads_account_id
'''
assert tads.verify_ads_account_id(ads_account_id=ads_account_id), 'Should Have permssions for the ads_account_id'

'''
********Proceed if you have permissions for the ads account
'''

'''
  Get Funding funding instruments
'''
ads_funding_data = tads.get_funding_instrument(account_id=ads_account_id)

'''
  Select a Funding Instrument ID
'''
funding_instrument_id = None
if 'data' in ads_funding_data:
        for data in ads_funding_data['data']:
            if 'id' in data:
                funding_instrument_id = data['id']

'''
****Proceed if you have a valid funding instrument ID
'''

'''
  Create a campaign and get the campaign id
'''

create_campaign_response = tads.create_campaign(account_id=ads_account_id, start_time='2015-11-02', end_time='2015-11-05',
                                                 funding_instrument_id=funding_instrument_id, name='TestCampaignMARIANA OCT 26',
                                                 total_budget_amount_local_micro='500000000', 
                                                 daily_budget_amount_local_micro='50000000')
campaign_id = create_campaign_response['data']['id']

'''
  Create a paused line item and get the line item id 
'''
line_item_response = tads.create_line_item(account_id=ads_account_id, campaign_id=campaign_id, bid_amount_local_micro='1500000',
                                  product_type='PROMOTED_TWEETS', placements='ALL_ON_TWITTER',
                                  paused='true')
line_item_id = line_item_response['data']['id']

'''
  Upload Tailored Audince List(Optional) from a hashed csv and get tailored audience id
'''
tailored_audience_data = tads.upload_primary_tailored_audience(account_id=ads_account_id, list_name='SampleTestEmailList', list_type='EMAIL',
                                                               file_path=sys.argv[1])

print(tailored_audience_data)
tailored_audience_id = tailored_audience_data['data']['tailored_audience_id']

'''
  Create targetting Criteria, associated with the line item
'''   
targeting_criteria_response = tads.create_targeting_criteria(account_id=ads_account_id, line_item_id=line_item_id, targeting_type='TAILORED_AUDIENCE',
                                                            targeting_value=tailored_audience_id, tailored_audience_type='CRM', tailored_audience_expansion='true')
  
tads.create_promoted_tweet(account_id=ads_account_id, status="TEST TEST TEST", screen_name='Mariana')

'''
 Unpause Line item to make the campaign live
'''
edit_line_item_response = tads.edit_line_item(account_id=ads_account_id, line_item_id=line_item_id)
print(edit_line_item_response)
```

