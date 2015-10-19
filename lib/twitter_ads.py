from twython import Twython
import urllib
from wsgiref.handlers import format_date_time
import datetime
import sys, json 
from time import mktime
from libs.ton_api import TwitterTon


class TwitterAds:

    APP_KEY = '<APP key>'
    APP_SECRET = '<APP Secret>'
    OAUTH_TOKEN = '<OAUTH_TOKEN>'
    OAUTH_TOKEN_SECRET = '<OAUTH Secret>'
    base_twitter_ads_url = 'https://ads-api.twitter.com/0/'
    base_twitter_ton_url = 'https:/ton.twitter.com/1.1/ton/bucket/'
    twitter_ads = None
    ads_account_id  = None
    ads_funding_id = None
    campaign_id = None
   

    def __init__(self, account_name='Mariana'):
        self.twitter_ads = Twython(self.APP_KEY, self.APP_SECRET,
                          self.OAUTH_TOKEN, self.OAUTH_TOKEN_SECRET)
        ads_account_details = self.__get_ads_accounts(account_name=account_name)
        if not ads_account_details:
            print("Account permissions for {" + account_name + "} Not granted")
            exit(0)
        self.ads_account_id = ads_account_details['id']
        self.ads_funding_id = self.__get_funding_id(self.ads_account_id)
    
    
    def __get_ads_accounts(self, account_name='Mariana'):
        all_ads_accounts =  self.twitter_ads.request( self.base_twitter_ads_url + 'accounts')
        if 'data' in all_ads_accounts:
            for data in all_ads_accounts['data']:
                if data['name'].lower() == account_name.lower():
                    return data
        return None            

    def __get_funding_id(self, account_id):
        ads_funding_data = self.twitter_ads.request( self.base_twitter_ads_url +\
                                                     'accounts/' + account_id + "/funding_instruments")
        
        print(ads_funding_data['data'])
        if 'data' in ads_funding_data:
            for data in ads_funding_data['data']:
                if 'id' in data:
                    return data['id']
        return None 


    def create_campaign(self, account_id, start_time, end_time,
                              funding_instrument_id, campaign_name,
                              total_budget_amount_local_micro, 
                              daily_budget_amount_local_micro):
        launch_campaign_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                             'accounts/' + account_id + '/campaigns?' +\
                                                             'start_time=' + start_time + '&funding_instrument_id=' + funding_instrument_id +\
                                                             '&name=' + campaign_name + '&total_budget_amount_local_micro=' + total_budget_amount_local_micro +\
                                                             '&daily_budget_amount_local_micro=' +  daily_budget_amount_local_micro,
                                                              method='POST')


        
        self.campaign_id = launch_campaign_response['data']['id']
      

    def create_line_item(self, account_id, campaign_id, bid_amount_local_micro,
                                product_type, placements, automatically_select_tweets,
                                paused):
        create_line_response =  self.twitter_ads.request(self.base_twitter_ads_url +\
                                                             'accounts/' + account_id + '/line_items?' +\
                                                             'campaign_id=' + campaign_id + '&bid_amount_local_micro=' + bid_amount_local_micro +\
                                                             '&product_type=' + product_type + '&placements=' + placements +\
                                                             '&automatically_select_tweets' + automatically_select_tweets,
                                                             method='POST')

        self.line_item_id = create_line_response['data']['id']

    

    
    def upload_tailored_audience(self, account_id, name, list_type):    
        create_tailored_audience_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                    'accounts/' + account_id + '/tailored_audiences?' +\
                                                    'name=' + name + '&list_type=' + list_type,
                                                     method='POST')


        return create_tailored_audience_response


    def tailored_audience_change(self, account_id, tailored_audience_id,
                                       input_file_path, operation='ADD'):
        
        params = {
                    'tailored_audience_id' : tailored_audience_id,
                    'input_file_path' : input_file_path,
                    'operation' : operation
                 }
        tailored_audience_change_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                    'accounts/' + account_id + '/tailored_audience_changes',
                                                     params=params,
                                                     method='POST'
                                                     )
        
        return tailored_audience_change_response


    def get_tailored_audience(self, account_id):
        get_tailored_audience_response = self.twitter_ads.request(self.base_twitter_ads_url +\
                                                    'accounts/' + account_id + '/tailored_audiences')
                                                                    
        print(get_tailored_audience_response)

       
    def upload_primary_tailored_audience(self, account_id, list_name, list_type, file_path):
        '''
         Upload File to twitter
        '''
        ton_response = TwitterTon().upload_data(file_path) 
        assert('location' in ton_response)
        '''
         Create an Audience List
        '''
        audience_create_response = self.upload_tailored_audience(account_id=account_id, name=list_name, list_type=list_type)
        assert('data' in audience_create_response and 'id' in audience_create_response['data'])
        '''
         Add uploaded data to audience list
        '''
        audience_change_response = self.tailored_audience_change(account_id=account_id, tailored_audience_id=audience_create_response['data']['id'],
                                                                 input_file_path=ton_response['location'])

        assert('data' in audience_change_response and 'id' in audience_change_response['data'])
        return audience_create_response['data']['id']


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


