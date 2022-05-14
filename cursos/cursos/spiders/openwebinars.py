import scrapy


class OpenwebinarsSpider(scrapy.Spider):
    name = 'openwebinars'
    allowed_domains = ['openwebinars.net']
    start_urls = ['https://openwebinars.net/cursos/?page=1']

    custom_settings = {
        'FEED_URI' : 'openwebinars.csv',
        'FEED_FORMAT': 'csv'
    }

    def parse_videos(self, response, **kwargs):
        title = response.xpath("//h1[contains(@class, 'title')]/text()").getall()
        title = [title.strip() for title in title if len(title.strip()) > 0][0]

        es_taller = len(response.xpath("//span[contains(@class, 'badge badge-secondary')]/text()")) > 0

        parte_entera = response.xpath("//strong[contains(@class,'rating-points' )]/text()").getall()[0]
        
        try:
            parte_decimal = response.xpath("//strong[contains(@class,'rating-points' )]/small/text()").getall()[0]
            parte_decimal = parte_decimal.replace(',', '.')
            puntuacion = float(f'{parte_entera}{parte_decimal}')
        except Exception as e:
            puntuacion = float(parte_entera)

        yield {'Titulo': title, "Es taller": es_taller, "Puntuacion": puntuacion}

    def parse(self, response):

        cursos = response.xpath('//div[contains(@class, "card-course")]//*/a/@href').getall()

        for curso in cursos:
            yield response.follow(f"https://openwebinars.net{curso}", callback=self.parse_videos)
            
        paginas = response.xpath("//a[contains(@class, 'endless_page_link page-link')]/text()").getall()
        ultima_pagina = max([*map(int, paginas)])
        current_url = response.url
        index = current_url.index("=")+1
        base_url = current_url[:index]
        current_page = int(current_url[index:])

        if current_page < ultima_pagina:
            print(f'PAGINA ACTUAL {current_page}')
            yield response.follow(f'{base_url}{current_page+1}')

