# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.http import TextResponse
import json

import re

class JSProcessingPipeline:
    def process_item(self, item, spider):
        if item['url'].endswith('.js'):
            js_code = item['body']
            variables = self.extract_variables(js_code)
            functions = self.extract_functions(js_code)
            item['js_variables'] = variables
            item['js_functions'] = functions
        return item

    def extract_variables(self, js_code):
        pattern = r'[var|let|const]\s+(\w+)\s*='
        variables = re.findall(pattern, js_code)
        variables = list(set(variables))
        return variables

    def extract_functions(self, js_code):
        pattern = r'function\s+(\w+)\s*\('
        functions = re.findall(pattern, js_code)
        functions = list(set(functions))
        return functions



class JSONPipeline:
    def process_item(self, item, spider):
        body_binary = item['body'].encode()
        response = TextResponse(item['url'], body=body_binary)
        extracted_jsons = []
        for text in response.xpath('//text()').extract():
            try:
                json_data = json.loads(text)
                extracted_jsons.append(json_data)
            except json.JSONDecodeError:
                pass
        item['extracted_jsons'] = extracted_jsons
        return item