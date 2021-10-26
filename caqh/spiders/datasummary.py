import scrapy
import json
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
from caqh.items import DataSummary


class DataSummarySpider(scrapy.Spider):
    name = 'datasummary'
    start_urls = ['http://proview.caqh.org/Login']


    def start_requests(self):
        request_list = []

        # Load accounts
        MY_ACCOUNTS_FILE = open(self.crawler.settings['MY_ACCOUNTS_FILE'])
        MY_ACCOUNTS_list = json.load(MY_ACCOUNTS_FILE)

        for i, account_data in enumerate(MY_ACCOUNTS_list):
            request = scrapy.Request(url='http://proview.caqh.org/Login',
                                     callback=self.login,
                                     dont_filter=True)
            request.cb_kwargs['account_data'] = account_data
            request.meta['cookiejar'] = i
            self.logger.info(f'INITIAL REQUEST for provider: {i:03d} at {request.url}')
            request_list.append(request)
        
        return request_list


    def login(self, response, account_data):

        self.logger.info(f'LOGIN REQUEST for provider: {response.meta["cookiejar"]:03d}, Account: {account_data}')
        yield FormRequest.from_response(response=response,
                                        formdata=account_data,
                                        callback=self.goto_datasummary,
                                        meta={'cookiejar':response.meta['cookiejar']},
                                        dont_filter=True)


    def goto_datasummary(self, response):
        datasummary_url = "https://proview.caqh.org/PR/Review/ReviewProviderDataSummary"
        
        self.logger.info(f'GO TO DATASUMMARY for provider: {response.meta["cookiejar"]:03d} at {datasummary_url}')

        yield scrapy.Request(url=datasummary_url, 
                             meta={'cookiejar':response.meta['cookiejar']},
                             callback=self.parse_datasummary,
                             dont_filter=True)
        



    def parse_datasummary(self,response):
        self.logger.info(f'RECIVED Data Summary for provider: {response.meta["cookiejar"]:03d}')

        data_summary = DataSummary()

        # xpaths = json.open(xpath.json)
        # for field, xpath, regex in xpath:
        #     try:
        #         field = response.xpath(xpath)
        #         if field == '':
        #             raise exception()
        #         data_summary[field]=field.re_first(regex)
        #     except:
        #         self.logger.warn(f'Field {field} does not have information')
        #         # ve y registra en un archivo field_exception.json que el provider tal no tiene la info del field

        data_summary['first_name']= response.xpath( '//div[preceding-sibling::div[./label[contains(@for,"First_Name_")]]]//text()' ).re_first('[a-zA-Z]+')
        data_summary['middle_name']= response.xpath( '//div[preceding-sibling::div[./label[contains(@for,"Middle_Name_")]]]//text()' ).re_first('[a-zA-Z]+')
        data_summary['last_name']= response.xpath( '//div[preceding-sibling::div[./label[contains(@for,"Last_Name_")]]]//text()' ).re_first('[a-zA-Z]+')
        data_summary['provider_id'] = response.xpath('//div/label[contains(@for, "CAQH_Provider_ID")]//text()').re_first('(?<=:\s).*')

        self.logger.info(f'FINISH PARSING Data Summary for provider: {response.meta["cookiejar"]:03d} \n \n {dict(data_summary)} \n')

        yield data_summary




