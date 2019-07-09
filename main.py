import aiohttp
import asyncio
import re
from aiohttp import ClientSession
from dataclasses import dataclass
from lxml.html import document_fromstring
from pprint import pprint
from typing import List


@dataclass(frozen=True)
class SizePhoneNumber:
    MAX_LENGTH: int = 11  # 7 495 111 22 33
    WITHOUT_FIRST_NUMBER: int = 10  # 495 111 22 33
    MIN_LENGTH: int = 7  # 111 22 33

    valid_length_phone_number = [MIN_LENGTH, WITHOUT_FIRST_NUMBER, MAX_LENGTH]


class FindPhoneNumber:
    regular_phone_number_pattern = re.compile(r'(\s*)?((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}')

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    async def find_phone_numbers_from_urls(self, urls: List[str]):
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*[self.find_phone_numbers_from_url(session, url) for url in urls])

    async def find_phone_numbers_from_url(self, session: ClientSession, url: str):
        async with session.get(url) as response:
            if response.status == 200:
                texts = self._get_text_from_page(await
                response.text())

                phones = self.get_phone_numbers_from_texts(texts)

                return url, self._delete_not_unique_phone_number(phones)

        return url, 'Error'

    @staticmethod
    def _delete_not_unique_phone_number(phones):
        copy_phones = phones.copy()

        if len(phones) != 1:
            moscow_phone_numbers = [phone for phone in phones if phone[1] == '']
            for phone in moscow_phone_numbers:
                phones.remove(phone)

            if moscow_phone_numbers and phones:
                for moscow_phone in moscow_phone_numbers:
                    for phone in phones:
                        if moscow_phone[2] == phone[2]:
                            copy_phones.remove(moscow_phone)

        phones = []
        for phone in copy_phones:
            if phone[1] == '':
                phones.append(phone[2])
            else:
                phones.append(''.join(phone))

        return phones

    @staticmethod
    def _get_text_from_page(text: str):
        page = document_fromstring(text)
        return page.xpath('//body//*[not(self::script)]/text()')

    def get_phone_numbers_from_texts(self, texts: List[str]):
        phones = set()
        for text in texts:
            text = str(text)  # Для нормальной работы text.isalnum()
            if len(text) < SizePhoneNumber.MIN_LENGTH or text.isalnum():
                continue

            phone_numbers_found = self.get_phone_numbers_from_text(text)
            if phone_numbers_found:
                phones.update(phone_numbers_found)

        old_phones = phones.copy()
        phones.clear()

        for phone in old_phones:
            phones.add(self.transformation_phone_number(phone))

        return phones

    def get_phone_numbers_from_text(self, text: str):
        phones = set()
        for phone_number in self.regular_phone_number_pattern.finditer(text):
            phone_number = phone_number.group()

            phone_number = self._clean_phone_number(phone_number)

            if len(phone_number) in SizePhoneNumber.valid_length_phone_number:
                phones.add(phone_number)

        return phones or None

    @staticmethod
    def _clean_phone_number(phone_number: str):
        phone_number = phone_number.replace('(', '')
        phone_number = phone_number.replace(')', '')
        phone_number = phone_number.replace('-', '')
        phone_number = phone_number.replace(' ', '')
        phone_number = phone_number.replace('+', '')
        phone_number = phone_number.replace('\t', '')
        phone_number = phone_number.replace('\r', '')

        return phone_number

    @staticmethod
    def transformation_phone_number(phone_number: str):
        if len(phone_number) == SizePhoneNumber.MAX_LENGTH:
            return '8', phone_number[1:4], f'{phone_number[4:7]}{phone_number[7:9]}{phone_number[9:]}'

        if len(phone_number) == SizePhoneNumber.WITHOUT_FIRST_NUMBER:
            return '8', phone_number[0:3], f'{phone_number[3:6]}{phone_number[6:8]}{phone_number[8:]}'

        if len(phone_number) == SizePhoneNumber.MIN_LENGTH:
            return '8', '', f'{phone_number[0:3]}{phone_number[3:5]}{phone_number[5:]}'

        raise Exception('Wrong number format')


if __name__ == '__main__':
    service = FindPhoneNumber()

    r = asyncio.run(service.find_phone_numbers_from_urls([
        'https://hands.ru/company/about/',
        'https://repetitors.info/',
        'https://repetitors.info/about.php',
        'https://odincovo.yaremont.ru/',
        'https://sdom-stroy.ru/remont-kvartir-v-odintsovo.html',
        'https://profi.ru/remont/odincovo/',
        'https://stroyday.ru/remont-kvartiry/remont-kvartiry-svoimi-rukami-s-chego-nachinat.html',
        'https://odincovo.service-centers.ru/categories',
        'https://www.avtogermes.ru/sale/lada/vesta/?utm_phone=1360317&utm_source=yandex&utm_medium=cpc&utm_term=---autotargeting&utm_content=lada&utm_campaign=lada_vesta_avtotargeting_moscow_search&yclid=3847349872086506718',
        'https://www.avtogermes.ru/contacts/',
        'https://www.motosfera.ru/catalog/scooter/',
        'https://www.motosfera.ru/contact/',
        'http://www.team.ru/comp/model_office.php?yclid=3859639126891724622',
        'https://robotcomp.ru/category/igrovye-kompyutery/'
    ]))

    pprint(r)
