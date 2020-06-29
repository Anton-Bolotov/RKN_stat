import os
import sys
import requests
import time

list_rkn = ['https://raw.githubusercontent.com/zapret-info/z-i/master/dump-00.csv',
            'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-01.csv',
            'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-02.csv',
            'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-03.csv',
            'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-04.csv',
            'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-05.csv',
            'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-06.csv',
            'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-07.csv',
            'https://raw.githubusercontent.com/zapret-info/z-i/master/dump-08.csv',
            # 'https://raw.githubusercontent.com/zapret-info/z-i/master/dump.csv',
            ]


def file_write(rkn):
    print('Копирование базы данных РКН...')
    with open('dump_base_rkn.txt', 'w', encoding='utf-8') as file:
        for dump in rkn:
            r = requests.get(dump)
            file.write(r.text)
    print('База данных РКН скопированна...')


def create_list_of_search(file_name):
    some_list = []
    count = 4
    check = os.stat(file_name).st_size == 0
    if check:
        print('\nФайл пустой!')
        for _ in range(4):
            count -= 1
            sys.stdout.write('\r' + 'Завершение программы через - ' + str(count) + ' секунд(ы)')
            time.sleep(1)
            sys.stdout.flush()
        sys.exit()
    else:
        with open(file_name, 'r', encoding='utf-8') as file:
            ff = [i.strip() for i in file]
            for urls in ff:
                if '//' in urls:
                    a = urls.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
                    some_list.append(a)
                else:
                    b = urls
                    some_list.append(b)
    return some_list


def check_domain(block, good_dict, bad_dict, domain, line):
    if block == '1':
        good_dict.update({domain: 'Вечная'})
    elif block == '2':
        bad_dict.update({domain: 'Временная'})
    elif block == '3':
        good_dict.update({domain: 'Вечная'})
    else:
        blocked = line.split(';')[4].replace('�', '').replace(' ', '').split('-')[1]
        if blocked == '17':
            good_dict.update({domain: 'Вечная'})
        elif line.split(';')[3] == '�' * 14:
            good_dict.update({domain: 'Вечная'})
        else:
            if line.split(';')[3] == '���':
                bad_dict.update({domain: 'Временная'})
            else:
                print(f'{domain} c этим доменом что-то не так, не могу обработать')


def count_rkn():
    count = 0
    with open('dump_base_rkn.txt', 'r', encoding='utf-8') as file:
        for _ in file:
            count += 1
    return count


def file_read(file_name, file_out):
    print('Проверка записей...')
    good_dict = {}
    bad_dict = {}
    final_dict = {}
    count = count_rkn()
    count2 = 0
    with open('dump_base_rkn.txt', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.replace('\n', '')
            count2 += 1
            sys.stdout.write('\r' + 'Проверенно записей РКН - ' + str(count2) + ' из ' + str(count) +
                             ' (' + str(round(count2 / count * 100, 4)) + ' %)')
            sys.stdout.flush()
            for domain in create_list_of_search(file_name):
                try:
                    if domain.replace('www.', '') in line:
                        block = line.split(';')[4].replace('�', '').replace(' ', '').split('-')[0]
                        need_domain = line.split(';')[1].replace('www.', '')
                        if domain.replace('www.', '') == need_domain:
                            check_domain(block=block, good_dict=good_dict, bad_dict=bad_dict, domain=domain, line=line)
                        else:
                            new_domain = '*.' + str(domain.replace('www.', ''))
                            if new_domain == need_domain:
                                check_domain(block=block, good_dict=good_dict, bad_dict=bad_dict, domain=domain, line=line)
                    else:
                        final_dict.update({domain: 'Нет в базе РКН / домен на русском'})
                except:
                    final_dict.update({domain: 'Не могу обработать'})
        if 'Вечная' in good_dict.values():
            for key, value in good_dict.items():
                if key in bad_dict.keys():
                    final_dict.update({key: value + bad_dict[key]})
                else:
                    final_dict.update({key: value})
            for key2, value2 in bad_dict.items():
                if final_dict[key2] != 'ВечнаяВременная':
                    final_dict.update({key2: value2})
        else:
            for keys, values in bad_dict.items():
                final_dict.update({keys: values})

        print('\nЗапись данных в файл... output.txt')
        with open(file_out, 'w', encoding='utf-8') as files:
            for keys, values in final_dict.items():
                if 'ВечнаяВременная' == values:
                    files.write(str(keys) + '\t' + str(values).replace('ВечнаяВременная', 'Вечная') + '\n')
                else:
                    files.write(str(keys) + '\t' + str(values) + '\n')


first_time = time.time()
file_write(list_rkn)
file_read('input.txt', 'output.txt')
print('Удаление базы данных РКН с ПК...')
time.sleep(0.5)
os.remove('dump_base_rkn.txt')
last_time = time.time()
program_time = round(last_time - first_time, 1)
if program_time >= 60:
    print('Время затраченное на поиск -', round(program_time // 60), 'минут(ы)', round(program_time % 60), 'секунд(а)')
else:
    print('Время затраченное на поиск -', program_time, 'секунд(а)')
input('Для выхода из программы нажмите Enter')
