import os
from threading import Thread
import threading
import time
import requests


class Download_rkn_base(Thread):
    """ Загрузка базы РКН с использованием потоков
              и сохранение ее в файл. """

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        r = requests.get(url=self.url)
        with open(file='rkn_base.txt', mode='a', encoding='utf-8') as file:
            file.write(r.text)


class Rkn_check:
    """ Класс для проверки домена """

    def __init__(self):
        self.file_in = 'input.txt'
        self.temporary_blocking = {}
        self.permanent_blocking = {}
        self.result_dict = {}
        self.rkn_dict = {}
        self.domains_set = set()

    def create_rkn_dict(self):
        """ Создание словаря из базы РКН """
        with open(file='rkn_base.txt', mode='r', encoding='utf-8') as file:
            for line in file:
                line = line.replace('\n', '').split(';')
                try:
                    domain = line[1].replace('www.', '')
                    if '.' in domain:
                        if domain in self.rkn_dict.keys():
                            self.rkn_dict[domain] += ';' + line[3] + ';' + line[4] + ';' + line[5] + ';'
                        else:
                            self.rkn_dict.update({domain: ';' + line[3] + ';' + line[4] + ';' + line[5] + ';'})
                except IndexError:
                    continue

    def creation_set_domains(self):
        """ Создание множества доменов """
        with open(file=self.file_in, mode='r', encoding='utf-8') as file_for_filtration:
            for domain in file_for_filtration:
                domain = domain.replace('\n', '')
                if '/' in domain:
                    domain = domain.split('/')[2].replace('www.', '')
                    self.domains_set.add(domain)
                else:
                    domain = domain.replace('www.', '')
                    self.domains_set.add(domain)

    def _status_check(self, domain_name, true_domain):
        """ Определение статуса вечной или временной блокировки """
        record_rkn = str(self.rkn_dict[domain_name])
        if ';�����������;' in record_rkn:  # Минкомсвязь
            self.permanent_blocking.update({true_domain: 'Вечная'})
        elif ';��������������;' in record_rkn:  # Генпрокуратура
            self.permanent_blocking.update({true_domain: 'Вечная'})
        elif ';������� ���� �� ���� � 3' in record_rkn:  # Мосгорсуд
            self.permanent_blocking.update({true_domain: 'Вечная'})
        elif ';����������� � ��������������� ����������� �� ��������� � 2�' in record_rkn:  # Мосгорсуд
            self.temporary_blocking.update({true_domain: 'Временная'})
        elif ';���������������;' in record_rkn:  # Роспотребнадзор
            self.temporary_blocking.update({true_domain: 'Временная'})
        elif ';���;' in record_rkn:  # ФНС
            self.temporary_blocking.update({true_domain: 'Временная'})
        elif ';������������;' in record_rkn:  # Роскомнадзор
            self.temporary_blocking.update({true_domain: 'Временная'})
        elif ';����;' in record_rkn:  # ФСКН
            self.temporary_blocking.update({true_domain: 'Временная'})
        elif ';������������������������;' in record_rkn:  # Росалкогольрегулирование
            self.temporary_blocking.update({true_domain: 'Временная'})
        elif ';�����������;' in record_rkn:  # Росмолодежь
            self.temporary_blocking.update({true_domain: 'Временная'})

    def domain_check(self, domain):
        """ Проверка домена на блокировку """
        new_domain2 = '*.' + str(domain.split('.')[1:]).replace('[', '').replace(
            ']', '').replace(', ', '.').replace("'", '')
        new_domain3 = '*.' + str(domain)
        try:
            if self.rkn_dict[domain]:
                if domain == 'youtube.com':
                    self.result_dict.update({domain: 'Нету в базе'})
                else:
                    self._status_check(domain_name=domain, true_domain=domain)
        except KeyError:
            try:
                if self.rkn_dict[new_domain2]:
                    self._status_check(domain_name=new_domain2, true_domain=domain)
            except KeyError:
                try:
                    if self.rkn_dict[new_domain3]:
                        self._status_check(domain_name=new_domain3, true_domain=domain)
                except KeyError:
                    self.result_dict.update({domain: 'Нету в базе'})

    def result_dict_create(self):
        """ Создание словаря, где ключами являются домены,
            а значениями является статус вечная/временная """
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
        """ Рефакторинг значений финального словаря """
        for key, values in self.result_dict.items():
            if self.result_dict[key] == 'ВечнаяВременная':
                self.result_dict.update({key: 'Вечная'})

    def main(self):
        for domain in self.domains_set:
            self.domain_check(domain=domain)

    def write_to_file(self):
        with open(file='output.txt', mode='w', encoding='utf-8') as result_file:
            for key, values in self.result_dict.items():
                result_file.write(key + '\t' + values + '\n')


base_rkn = [
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-00.csv',
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-01.csv',
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-02.csv',
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-03.csv',
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-04.csv',
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-05.csv',
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-06.csv',
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-07.csv',
    'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-08.csv',
]

if __name__ == '__main__':
    start_time = time.time()
    with open(file='rkn_base.txt', mode='w', encoding='utf-8'):
        print('---> Скачивание базы данных РКН...')
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
    print(f'---> Время затраченное на скачивание базы данных РКН - ', round(end_time - start_time, 2), 'секунд')

    start_time1 = time.time()
    print('---> Подготовка данных...')
    rkn = Rkn_check()
    rkn.create_rkn_dict()
    end_time1 = time.time()
    print(f'---> Время затраченное на подготовку данных - ', round(end_time1 - start_time1, 2), 'секунд')

    rkn.creation_set_domains()
    rkn.main()
    rkn.result_dict_create()
    rkn.result_dict_sort()
    rkn.write_to_file()
    os.remove('rkn_base.txt')
    print(f'---> Готово! Результат смотри в файле output.txt !')
    input('\nДля выхода из программы нажмите ENTER')



