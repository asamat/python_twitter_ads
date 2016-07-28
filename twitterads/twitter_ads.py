from twython import Twython
import urllib
from wsgiref.handlers import format_date_time
import datetime
import sys, json 
from time import mktime
from twitterads.helper.ton_api import TwitterTon


class TwitterAds:

    twitter_consumer_key = None
    twitter_consumer_secret = None
    access_token = None
    access_token_secret = None
    base_twitter_ads_url = 'https://ads-api.twitter.com/0/'
    base_twitter_ton_url = 'https:/ton.twitter.com/1.1/ton/bucket/'
    twitter_ads = None
    ads_account_id = None

    

    def __init__(self, twitter_consumer_key, twitter_consumer_secret,
                      access_token, access_token_secret):
        
        assert twitter_consumer_key is not None, "Provide twitter_consumer_key"
        assert twitter_consumer_secret is not None, "Provide twitter_consumer_secret"
        assert access_token is not None, "Provide access_token"
        assert access_token_secret is not None, "Provide, access_token_secret"
        self.twitter_consumer_key = twitter_consumer_key
        self.twitter_consumer_secret = twitter_consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.twitter_ads = Twython(self.twitter_consumer_key, self.twitter_consumer_secret,
                                   self.access_token, self.access_token_secret)

    def get_adds_account_id_from_name(self, account_name):
        ads_account_details = self.get_ads_accounts(account_name=account_name)
        if not ads_account_details:
            print("Account permissions for {" + account_name + "} Not granted")
            return None
        return ads_account_details['id']    
       
    def verify_ads_account_id(self, ads_account_id):
        ads_account_details = self.get_ads_accounts(ads_account_id=ads_account_id)
        if not ads_account_details:
            print("Account permissions for {" + ads_account_id + "} Not granted")
            return False
        return True  

    def get_ads_accounts(self, account_name=None, ads_account_id=None):
        assert account_name is not None or ads_account_id is not None, "Provide either account_name or ads_account_id"
        all_ads_accounts =  self.twitter_ads.request( self.base_twitter_ads_url + 'accounts')
        if 'data' in all_ads_accounts:
            for data in all_ads_accounts['data']:
                if account_name and data['name'].lower() == account_name.lower() or\
                     ads_account_id and str(data['id']) == ads_account_id:
                    return data
        return None            


    def get_all_ads_accounts(self):
        all_ads_accounts =  self.twitter_ads.request( self.base_twitter_ads_url + 'accounts')
        if 'data' in all_ads_accounts:
            return all_ads_accounts['data']
        return None    
    



    '''
      Ref - https://dev.twitter.com/ads/campaigns/funding-instruments
    '''
    def get_funding_instrument(self, account_id):
        ads_funding_data = self.twitter_ads.request( self.base_twitter_ads_url +\
                                                     'accounts/' + account_id + "/funding_instruments")
        
        return ads_funding_data
      

    def get_campaigns(self, account_id):
        get_campaigns_data = self.twitter_ads.request( self.base_twitter_ads_url +\
                                                     'accounts/' + account_id + "/campaigns")
        
        return get_campaigns_data
           

    '''
      Ref - https://dev.twitter.com/ads/reference/put/accounts/%3Aaccount_id/campaigns/%3Acampaign_id
    '''
    def modify_campaign(self, account_id, campaign_id, start_time=None,
                              name=None, end_time=None, total_budget_amount_local_micro=None, 
                              daily_budget_amount_local_micro=None,
                              paused=None, standard_delivery=None):

        assert account_id is not None, 'account_id is required'
        assert campaign_id is not None, 'campaign_id is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)          
     
        modify_campaign_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                             'accounts/' + account_id + '/campaigns/' + campaign_id,
                                                              params=params,
                                                              method='PUT')


        
        assert 'data' in modify_campaign_response and 'id' in modify_campaign_response['data']
        return modify_campaign_response
    

    '''
      Ref https://dev.twitter.com/ads/reference/post/accounts/%3Aaccount_id/campaigns
    '''

    def create_campaign(self, account_id, start_time,
                              funding_instrument_id, name,
                              end_time=None, total_budget_amount_local_micro=None, 
                              daily_budget_amount_local_micro=None,
                              paused=None, standard_delivery=None):
        
        assert account_id is not None, 'account_id is required'
        assert name is not None, 'name is required'
        assert funding_instrument_id is not None, 'funding_instrument_id is required'
        assert start_time is not None, 'start_time is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)          
     
        launch_campaign_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                             'accounts/' + account_id + '/campaigns',
                                                              params=params,
                                                              method='POST')


        
        assert 'data' in launch_campaign_response and 'id' in launch_campaign_response['data']
        return launch_campaign_response
      


    '''
      Ref - https://dev.twitter.com/ads/reference/post/accounts/%3Aaccount_id/line_items
    '''
    def create_line_item(self, account_id, campaign_id, bid_amount_local_micro,
                                product_type, placements, paused=None, objective=None,
                                name=None, bid_type=None, automatically_select_bid=None,
                                include_sentiment=None, total_budget_amount_local_micro=None,
                                primary_web_event_tag=None, optimization=None,
                                bid_unit=None, charge_by=None, advertiser_domain=None,
                                categories=None):

        assert account_id is not None, 'account_id is required'
        assert campaign_id is not None, 'campaign_id is required'
        assert bid_type is None or bid_type is 'MAX' or bid_type is 'AUTO' and \
               bid_amount_local_micro is not None, 'bid_amount_local_micro is required when bid_type is MAX(Default) or AUTO'
        assert product_type is not None, 'product_type is required'
        assert placements is not None, 'placements is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)

        create_line_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                             'accounts/' + account_id + '/line_items',
                                                              params=params,
                                                             method='POST')

        assert 'data' in create_line_response and 'id' in create_line_response['data']
        return create_line_response
        
    '''
      Ref - https://dev.twitter.com/ads/reference/put/accounts/%3Aaccount_id/line_items/%3Aline_item_id
    '''    
    def edit_line_item(self, account_id, line_item_id, paused='false',
                                      bid_amount_local_micro=None, name=None,
                                      bid_type=None, total_budget_amount_local_micro=None,
                                      optimization=None):
        assert account_id is not None, 'account_id is required'
        assert line_item_id is not None, 'line_item_id is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        del tmp_params['line_item_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)

        edit_line_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                               'accounts/' + account_id + '/line_items/' + line_item_id,
                                                               params=params,
                                                               method='PUT')
        return edit_line_response



    '''
      Ref - https://dev.twitter.com/ads/reference/post/accounts/%3Aaccount_id/targeting_criteria
    '''
    def create_targeting_criteria(self, account_id, line_item_id, targeting_type,
                                      targeting_value, tailored_audience_type=None, tailored_audience_expansion=None):

        assert account_id is not None, 'account_id is required'
        assert line_item_id is not None, 'line_item_id is required'
        assert targeting_type is not None, 'targeting_type is required'
        assert targeting_value is not None, 'targeting_value is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)

        create_targeting_criteria_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                                        'accounts/' + account_id + '/targeting_criteria',
                                                                        params=params,
                                                                        method='POST')

       
        assert 'data' in create_targeting_criteria_response and 'id' in create_targeting_criteria_response['data']
        return create_targeting_criteria_response
        

    def get_targeting_criteria_location(self, location_type, country_code):
        tmp_params = locals()
        del tmp_params['self']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)
        get_targeting_criteria_location_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                                        'targeting_criteria/locations',
                                                                        params=params,
                                                                        method='GET')
        print get_targeting_criteria_location_response


    '''
      Ref - https://dev.twitter.com/ads/reference/put/accounts/%3Aaccount_id/targeting_criteria
    '''
    def edit_targeting_criteria(self, account_id, line_item_id, tailored_audiences=None, broad_keywords=None, exact_keywords=None,
                                phrase_keywords=None, negative_exact_keywords=None, negative_unordered_keywords=None,
                                negative_phrase_keywords=None, locations=None, interests=None, gender=None,
                                age_buckets=None, followers_of_users=None, similar_to_followers_of_users=None,
                                platforms=None, platform_versions=None, devices=None,
                                wifi_only=None, tv_channels=None, tv_genres=None, tv_shows=None,
                                tailored_audiences_expanded=None, tailored_audiences_excluded=None,
                                behaviors=None, behaviors_expanded=None, negative_behaviors=None,
                                languages=None, network_operators=None, network_activation_duration_lt=None,
                                network_activation_duration_gte=None, app_store_categories=None,
                                app_store_categories_lookalike=None, campaign_engagement=None,
                                user_engagement=None, engagement_type=None, exclude_app_list=None):

        assert account_id is not None, 'account_id is required'
        assert line_item_id is not None, 'line_item_id is required'
        assert tailored_audiences is not None, 'tailored_audiences is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)

        create_targeting_criteria_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                                        'accounts/' + account_id + '/targeting_criteria',
                                                                        params=params,
                                                                        method='PUT')

       
        return create_targeting_criteria_response
        

    '''
      Ref - https://dev.twitter.com/ads/reference/post/accounts/%3Aaccount_id/tailored_audiences
    '''
    def create_tailored_audience(self, account_id, name, list_type):    

        assert account_id is not None, 'account_id is required'
        assert name is not None, 'name is required'
        assert list_type is not None, 'list_type is required'

        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)

        create_tailored_audience_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                    'accounts/' + account_id + '/tailored_audiences',
                                                     params=params,
                                                     method='POST')


        return create_tailored_audience_response


    '''
      Ref - https://dev.twitter.com/ads/reference/post/accounts/%3Aaccount_id/tailored_audience_change
    '''
    def tailored_audience_change(self, account_id, tailored_audience_id,
                                       input_file_path, operation='ADD'):
        
        assert account_id is not None, 'account_id is required'
        assert tailored_audience_id is not None, 'tailored_audience_id is required'
        assert input_file_path is not None, 'input_file_path is required'
        assert operation is not None, 'operation is required'

        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)
  
        tailored_audience_change_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                    'accounts/' + account_id + '/tailored_audience_changes',
                                                     params=params,
                                                     method='POST')
        
        return tailored_audience_change_response


    '''
      Ref - https://dev.twitter.com/ads/reference/get/accounts/%3Aaccount_id/tailored_audiences
    '''
    def get_tailored_audience(self, account_id):
        assert account_id is not None, 'account_id is required'

        get_tailored_audience_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                    'accounts/' + account_id + '/tailored_audiences')
                                                                    
        return get_tailored_audience_response


    def get_tailored_audience_id(self, account_id, tailored_audience_id):
        assert account_id is not None, 'account_id is required'
        assert tailored_audience_id is not None, 'tailored_audience_id is required'
        

        get_tailored_audience_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                    'accounts/' + account_id + '/tailored_audiences/' + tailored_audience_id)
                                                                    
        return get_tailored_audience_response
    


    '''
      Upload Using TON API - https://dev.twitter.com/rest/ton/single-chunk
      see file libs/ton_api.py 
      NON API HELPER METHOD
    '''       
    def upload_primary_tailored_audience(self, account_id, list_name, list_type, file_path):
        '''
         Upload File to twitter
        '''
        ton_response = TwitterTon(twitter_consumer_key=self.twitter_consumer_key, twitter_consumer_secret=self.twitter_consumer_secret,
                                   access_token=self.access_token, access_token_secret=self.access_token_secret).upload_data(file_path) 
        assert('location' in ton_response)
        '''
         Create an Audience List
        '''
        audience_create_response = self.create_tailored_audience(account_id=account_id, name=list_name, list_type=list_type)
        assert('data' in audience_create_response and 'id' in audience_create_response['data'])
        '''
         Add uploaded data to audience list
        '''
        audience_change_response = self.tailored_audience_change(account_id=account_id, tailored_audience_id=audience_create_response['data']['id'],
                                                                 input_file_path=ton_response['location'])

        assert('data' in audience_change_response and 'id' in audience_change_response['data'])
        return audience_change_response


    '''
      Edit an Audience List using ton API
      NON API HELPER METHOD
    '''
    def edit_tailored_audience(self, account_id, tailored_audience_id, file_path, operation='ADD'):
        '''
         Upload File to twitter
        '''
        ton_response = TwitterTon().upload_data(file_path) 
        assert('location' in ton_response)
        '''
         Add uploaded data to audience list
        '''
        audience_change_response = self.tailored_audience_change(account_id=account_id, tailored_audience_id=tailored_audience_id,
                                                                  input_file_path=ton_response['location'], operation=operation)
        
        return audience_change_response


    '''
      Ref - https://dev.twitter.com/ads/reference/post/accounts/%3Aaccount_id/cards/website
    '''
    def create_website_tweet_card(self, account_id, card_name, website_title, website_url, website_cta, img_path_list=[]):
        
        assert account_id is not None, 'account_id is required'
        
        media_ids = []
        for img_path in img_path_list: 
          photo = open(img_path, 'rb')
          response = self.twitter_ads.upload_media(media=photo)
          assert 'media_id' in response
          media_ids.append(response['media_id_string'])
        
        params = {
                  'name' : card_name,
                  'website_title' : website_title,
                  'website_url' : website_url,
                  'website_cta' : website_cta
               }
        if len(media_ids) > 0:
            params['image_media_id'] = ",".join(media_ids)
                 
        tweet_website_card_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                            'accounts/' + account_id + '/cards/website',
                                                             params=params,
                                                             method='POST')
        return tweet_website_card_response


    '''
      Ref - https://dev.twitter.com/ads/reference/post/accounts/%3Aaccount_id/tweet
    '''
    def create_promoted_tweet(self, account_id, status, screen_name, img_path_list=[]):
        assert account_id is not None, 'account_id is required'
        assert screen_name is not None, 'screen_name is required'

        twitter_user = self.twitter_ads.show_user(screen_name=screen_name)
        as_user_id = twitter_user['id']
        media_ids = []
        for img_path in img_path_list: 
          photo = open(img_path, 'rb')
          response = self.twitter_ads.upload_media(media=photo,additional_owners=as_user_id)
          assert 'media_id' in response
          media_ids.append(response['media_id_string'])
        
        params = {
                  'status' : status,
                  'as_user_id' : as_user_id,
               }
        if len(media_ids) > 0:
            params['media_ids'] = ",".join(media_ids)
                 
        promoted_tweets_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                            'accounts/' + account_id + '/tweet',
                                                             params=params,
                                                             method='POST')
        return promoted_tweets_response


    '''
      Ref - https://dev.twitter.com/ads/reference/post/accounts/%3Aaccount_id/promoted_tweets
    '''
    def add_promoted_tweets_to_campaign(self, account_id, line_item_id, tweet_ids=[]):
        assert account_id is not None, 'account_id is required'
        assert line_item_id is not None, 'line_item_id is required'
        assert len(tweet_ids) > 0, 'tweet_ids is required'
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']

        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)

        params['tweet_ids'] = ",".join(tweet_ids)

        add_promoted_tweets_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                            'accounts/' + account_id + '/promoted_tweets',
                                                            params=params,
                                                            method='POST')
        return add_promoted_tweets_response


    def get_promoted_tweets(self, account_id, line_item_id):
        assert account_id is not None, 'account_id is required'
        assert line_item_id is not None, 'line_item_id is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']

        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)

         
        get_promoted_tweets_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                            'accounts/' + account_id + '/promoted_tweets',
                                                            params=params,
                                                            method='GET')
        return get_promoted_tweets_response


    def delete_camapign(self, account_id, campaign_id):
        assert account_id is not None, 'account_id is required'
        assert campaign_id is not None, 'campaign_id is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)          
     
        delete_campaign_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                             'accounts/' + account_id + '/campaigns/' + campaign_id,
                                                              params=params,
                                                              method='DELETE')
        return delete_campaign_response

    def delete_line_item(self, account_id, line_item_id):
        assert account_id is not None, 'account_id is required'
        assert line_item_id is not None, 'line_item_id is required'
        
        tmp_params = locals()
        del tmp_params['self']
        del tmp_params['account_id']
        params =  dict((k, v) for k, v in tmp_params.iteritems() if v)          
     
        delete_line_item_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                             'accounts/' + account_id + '/line_items/' + line_item_id,
                                                              params=params,
                                                              method='DELETE')
        return delete_line_item_response
    


           








