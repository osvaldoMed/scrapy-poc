# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DataSummary(scrapy.Item):
    # define the fields for your item here like:
    first_name = scrapy.Field()
    middle_name = scrapy.Field()
    last_name = scrapy.Field()
    provider_id = scrapy.Field()

    pass
