import datetime
import json

import scrapy
from scrapy.exceptions import CloseSpider

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import AkbankItem
from itemloaders.processors import TakeFirst

base = 'https://www.akbank.com/_vti_bin/AkbankServicesSecure/FrontEndServiceSecure.svc/GetPressRelease/{}?locale=en-us'

class AkbankSpider(scrapy.Spider):
	name = 'akbank'
	year = datetime.datetime.now().year
	start_urls = [base.format(year)]

	def parse(self, response):
		data = json.loads(response.text)
		if data['GetPressReleaseResult'] != 'null':
			self.year -= 1
		else:
			raise CloseSpider('No more pages')

		raw_data = json.loads(data['GetPressReleaseResult'])

		for post in raw_data:
			title = post['Title']
			date = post['Date']
			description = remove_tags(post['Body'])

			item = ItemLoader(item=AkbankItem(), response=response)
			item.default_output_processor = TakeFirst()
			item.add_value('title', title)
			item.add_value('description', description)
			item.add_value('date', date)

			yield item.load_item()

		yield response.follow(base.format(self.year), self.parse)
