import scrapy
import logging
from configparser import ConfigParser


class smartShoppersCrawler(scrapy.Spider):
    name = "smartShoppers"
    def start_requests(self):
        """
        This function call all supporting methods to create dataframe
        and convert it into csv file
            """

        # Fetch target url from config.ini file and assign it to variable url
        config = ConfigParser()
        config.read('config.ini')

        url = config.get('settings', 'input_link')

        yield scrapy.Request(url=url, callback=self.parse)



    def parse(self,response):
        """
                            1) Get HTML element where product camera lense are listed
                            2) Code executes asynchronously because of Twister Class Inherited in Scrapy
                            3) Check if next page exist, run this method recursively until
                            next page is None



                            Args:

                            pageTree (HTML ELement Object): The first parameter.

                        Returns:
                        data_dictionary (dic) : yield output row by row
                        """

        # fetch all <a /> tags where parent node id is 'products'
        listItems =  response.xpath("//*[@id='products']/div/div/div/div/div/div/a")

        for item in listItems:
            #Get href link from node.
            link = item.xpath(".//@href").get()

            yield response.follow(url=link , callback=self.itemParser)

        # fetch next page url from html element where text is '>' and parent node id is 'content'
        nextPage = response.xpath("//*[@id='content']/div[6]/div[1]/ul/li/a[text()='>']/@href").get()
        if nextPage is not None:
            newUrl = nextPage

            logging.info(newUrl)
            yield scrapy.Request(url=newUrl, callback=self.parse)


    def itemParser(self,response):
        """
        Get desired data from different nodes.

        Args:

        item (HTML ELement Object): element tree of 1 single product.

        Returns:
        (dic): The return value is a dictionary containing data 'name', 'price', 'availability',
        'brand','productCode', 'description'
                        """

        # find name of product from given xpath
        name = response.xpath("//*[@id='content']/div/div[1]/div/div[2]/h1/text()").get()
        # find price of product from given xpath
        price = response.xpath("//*[@id='content']/div/div[1]/div/div[2]/div[2]/ul/li/span[1]/text()").get()
        # find availability of product from given xpath
        availability = response.xpath("//*[@id='content']/div/div[1]/div/div[2]/div[2]/ul/li/span[1]/text()").get()
        # find brand of product from given xpath
        brand = response.xpath("//*[@id='content']/div/div[1]/div/div[2]/ul[2]/li[2]/a/text()").get()
        # find productCode of product from given xpath
        productCode = response.xpath("//*[@id='content']/div/div[1]/div/div[2]/ul[2]/li[3]/text()").get()

        # find description of product from given xpath
        # As data is present in multiple tags , fetch data from self node(id='tab-description')
        # and all child nodes
        description = response.xpath("//*[@id='tab-description']/descendant-or-self::*/text()").getall()

        yield {'name': name.strip(),
               'price': price.strip(),
               'availability': availability.strip(),
               'brand': brand.strip(),
               'productCode': productCode.strip(),
               'description':description

               }
if __name__ =='__main__':
    obj = smartShoppersCrawler()
    obj.start_requests()
