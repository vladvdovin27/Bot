import telebot
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time
import requests
from bs4 import BeautifulSoup as bs


def get_session(proxy):
    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}
    return session


def find_proxy():
    url = "https://free-proxy-list.net/"

    soup = bs(requests.get(url).content, "html.parser")
    proxies = []
    for row in soup.find("table", attrs={"class": "table table-striped table-bordered"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies


def find_work_proxy(timeout=1.5):
    proxies = find_proxy()
    work_proxy = []

    for proxy in proxies:
        s = get_session(proxy)
        try:
            s.get("http://icanhazip.com", timeout=timeout).text.strip()
        except:
            continue
        else:
            work_proxy.append(proxy)
            return work_proxy


bot = telebot.TeleBot("5140866265:AAFCkFPr1mWiv9qsLbpGAz4SZtE8s6vyJNc")


@bot.message_handler(content_types=['text', 'document'])
def handle_text(message):
    if message.content_type == 'text':
        bot.send_message(message.chat.id, message.text)
    else:
        url_numb = 10000
        wrong_urls = []
        driver = None
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = message.document.file_name
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.send_message(message.chat.id, 'Файл сохранен, начинаю работу')
            filename = src

            file = pd.read_excel(filename)

            # proxy = find_work_proxy()

            opts = Options()
            opts.add_argument("--headless")
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')

            # if proxy:
            #     webdriver.DesiredCapabilities.CHROME['proxy'] = {
            #         "httpProxy": proxy[0],
            #         "ftpProxy": proxy[0],
            #         "sslProxy": proxy[0],
            #         "proxyType": "MANUAL",
            #     }
            #
            #     webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True

            opts.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
            service = Service(executable_path=os.environ['CHROMEDRIVER_PATH'])
            driver = webdriver.Chrome(service=service, options=opts)
            driver.set_window_size(1920, 1080)

            COLS = ['Проект', 'Текст', 'Имя', 'Почта']
            for i in range(file.shape[0] - 1, -1, -1):
                url = file[COLS[0]][i]

                dict_ = {
                    'email': file[COLS[3]][i],
                    'full_name': file[COLS[2]][i],
                    'text': file[COLS[1]][i]
                }
                check = False

                if i % 100 == 0:
                    bot.send_message(message.chat.id, str(i))
                    url_numb = i
                attempts = 0
                k = 0
                while not check:
                    try:
                        driver.get(url)

                        time.sleep(1.5)

                        driver.find_element(By.NAME, 'full_name').send_keys(dict_['full_name'])
                        driver.find_element(By.NAME, 'email').send_keys(dict_['email'])
                        driver.find_element(By.NAME, 'text').send_keys(dict_['text'])

                        time.sleep(0.5)

                        driver.find_element(By.TAG_NAME, 'button').click()
                    except Exception as ex:
                        attempts += 1
                        if attempts == 10:
                            bot.send_message(message.chat.id, f'Не удалось отправить сообщение на адрес {url}')
                            # bot.send_message(message.chat.id, ex)
                            wrong_urls.append(url)
                            check = True
                            # k += 1
                        if k == 15:
                            bot.send_message(message.chat.id, f'Подозрение на сбой работы сервера, заканчиваю работу над файлом')
                            break
                    else:
                        check = True
                        k = 0

            os.remove(filename)
        except Exception as e:
            if url_numb == 0:
                bot.send_message(message.chat.id, 'Файл успешно обработан')
                bot.send_message(message.chat.id, 'Сайты, на которые не получилось отправить сообщение:')
                bot.send_message(message.chat.id, '\n'.join(wrong_urls))
                driver.close()
            else:
                bot.send_message(message.chat.id, 'Global Error')
                bot.send_message(message.chat.id, e)
        else:
            bot.send_message(message.chat.id, 'Файл успешно обработан')
            bot.send_message(message.chat.id, 'Сайты, на которые не получилось отправить сообщение:')
            bot.send_message(message.chat.id, '\n'.join(wrong_urls))
            driver.close()


bot.infinity_polling()
