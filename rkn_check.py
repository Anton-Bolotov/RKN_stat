from bs4 import BeautifulSoup
from threading import Thread

import threading
import time
import requests


class Download_rkn_base(Thread):

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        r = requests.get(url=self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        result = str(soup.find('pre'))
        with open(file='rkn_base.txt', mode='a', encoding='utf-8') as file:
            file.write(result)


class Rkn_check:

    def __init__(self):
        self.file_in = 'input.txt'
        self.temporary_blocking = {}
        self.permanent_blocking = {}
        self.result_dict = {}
        self.domains_set = set()

    def creation_set_domains(self):
        with open(file=self.file_in, mode='r', encoding='utf-8') as file_for_filtration:
            for domain in file_for_filtration:
                domain = domain.replace('\n', '')
                if '/' in domain:
                    domain = domain.split('/')[2].replace('www.', '')
                    self.domains_set.add(domain)
                else:
                    domain = domain.replace('www.', '')
                    self.domains_set.add(domain)

    def _status_check(self, record_rkn, domain_name):
        record_rkn = record_rkn.split(';')
        if record_rkn[3] == 'Роспотребнадзор':
            self.temporary_blocking.update({domain_name: 'Временная'})
        elif record_rkn[3] == 'Минкомсвязь':
            self.permanent_blocking.update({domain_name: 'Вечная'})
        elif record_rkn[3] == 'ФНС':
            self.temporary_blocking.update({domain_name: 'Временная'})
        elif record_rkn[3] == 'суд':
            self.temporary_blocking.update({domain_name: 'Временная'})
        elif record_rkn[3] == 'Роскомнадзор':
            self.temporary_blocking.update({domain_name: 'Временная'})
        elif record_rkn[3] == 'Генпрокуратура':
            self.permanent_blocking.update({domain_name: 'Вечная'})
        elif record_rkn[3] == 'Мосгорсуд':
            if 'решение суда по делу № 3' in record_rkn[4]:
                self.permanent_blocking.update({domain_name: 'Вечная'})
            elif 'определение о предварительном обеспечении по заявлению № 2' in record_rkn[4]:
                self.temporary_blocking.update({domain_name: 'Временная'})
        elif record_rkn[3] == 'МВД':
            self.temporary_blocking.update({domain_name: 'Временная'})
        elif record_rkn[3] == 'ФСКН':
            self.temporary_blocking.update({domain_name: 'Временная'})
        elif record_rkn[3] == 'Росалкогольрегулирование':
            self.temporary_blocking.update({domain_name: 'Временная'})
        elif record_rkn[3] == 'Росмолодежь':
            self.temporary_blocking.update({domain_name: 'Временная'})

    def domain_check(self, domain, search_line):
        try:
            need_domain = search_line.split(';')[1]
            new_domain = 'www.' + domain
            new_domain2 = '*.' + str(domain.split('.')[1:]).replace('[', '').replace(
                ']', '').replace(', ', '.').replace("'", '')
            if domain == need_domain:
                self._status_check(record_rkn=search_line, domain_name=domain)
            elif new_domain == need_domain:
                self._status_check(record_rkn=search_line, domain_name=domain)
            elif new_domain2 == need_domain:
                self._status_check(record_rkn=search_line, domain_name=domain)
            else:
                self.result_dict.update({domain: 'Нету в базе'})
        except IndexError:
            pass

    def result_dict_create(self):
        if 'Вечная' in self.permanent_blocking.values():
            for key, value in self.permanent_blocking.items():
                if key in self.temporary_blocking.keys():
                    self.result_dict.update({key: value + self.temporary_blocking[key]})
                else:
                    self.result_dict.update({key: value})
            for key2, value2 in self.temporary_blocking.items():
                try:
                    if self.result_dict[key2] != 'ВечнаяВременная':
                        self.result_dict.update({key2: value2})
                except KeyError:
                    self.result_dict.update({key2: value2})
        else:
            for keys, values in self.temporary_blocking.items():
                self.result_dict.update({keys: values})

    def result_dict_sort(self):
        print(self.result_dict)
        for key, values in self.result_dict.items():
            if self.result_dict[key] == 'ВечнаяВременная':
                self.result_dict.update({key: 'Вечная'})

    def run(self):
        with open(file='rkn_base.txt', mode='r', encoding='utf-8') as file_for_filtration:
            for search_line in file_for_filtration:
                for domain in self.domains_set:
                    self.domain_check(domain=domain, search_line=search_line)


base_rkn = [
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-00.csv',
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-01.csv',
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-02.csv',
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-03.csv',
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-04.csv',
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-05.csv',
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-06.csv',
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-07.csv',
    'https://sourceforge.net/p/z-i/code-0/HEAD/tree/dump-08.csv',
]

if __name__ == '__main__':
    start_time = time.time()
    threads_domains = []
    for urls in base_rkn:
        thread = Download_rkn_base(url=urls)
        thread.start()
        threads_domains.append(thread)
        if threading.active_count() >= 350:
            for t in threads_domains:
                t.join()
    for t in threads_domains:
        t.join()

    end_time = time.time()
    print(f'Время затраченное на скачивание базы ркн - ', round(end_time - start_time, 2), 'секунд')

    start_time1 = time.time()
    rkn = Rkn_check()
    rkn.creation_set_domains()
    rkn.run()
    rkn.result_dict_create()
    rkn.result_dict_sort()

    end_time1 = time.time()
    print(f'Время затраченное на выполнение программы - ', round(end_time1 - start_time1, 2), 'секунд')
