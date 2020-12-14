import os
import sys
import requests
import time
import urllib.parse
import webbrowser
from tqdm import tqdm


FOLDER='docs'
CLIENT_ID = '7697172'
AUTH_URL = f'https://oauth.vk.com/authorize?client_id={CLIENT_ID}&redirect_uri=https://vk.com&scope=docs&response_type=token'
METHOD_URL = 'https://api.vk.com/method/docs.get'
DELETE_URL = 'https://api.vk.com/method/docs.delete'


def download(url, filename, total):
    try:
        os.mkdir(FOLDER)
    except:
        pass
    try:
        r = requests.get(url, stream=True)
        with open(os.path.join(FOLDER, filename), 'bw') as file:
            for chunk in tqdm(r.iter_content(1024), desc=filename, unit='KB', total=int(total/1024)):
                file.write(chunk)
    except Exception as e:
        print(e)
        sys.exit()
            

def main():
    print('vk_docs_dl\nАвтор: Макс Рокицкий\nhttps://github.com/exenzi/vk_docs_dl\n')
    print('Этот скрипт скачивает все Ваши документы(файлы) из Вконтакте.')
    print('Если Ваш браузер не открылся, введите эту ссылку в браузере:\n', AUTH_URL, sep='')
    webbrowser.open_new_tab(AUTH_URL)
    auth_link = input('\nКопировать: Ctrl+Shift+C\nВставить: Ctrl+Shift+V\nПредоставьте приложению доступ к файлам, после чего, скопируйте ссылку из адресной строки браузера после авторизации сюда: ')
    fragment = urllib.parse.urlparse(auth_link).fragment
    url_params = dict(urllib.parse.parse_qsl(fragment))
    

    r = requests.get(METHOD_URL, params={
                     'client_id': CLIENT_ID, 'access_token': url_params['access_token'], 'v': '5.52', 'count': 2000})
    docs = r.json()['response']['items']
    
    print(f'Найдено {len(docs)} документов.')
    ask_to_delete = input('Удалять скаченные файлы? (д/Н)')
    
    delete_docs = False
    if ask_to_delete.strip().lower() in ['д', 'да', 'y', 'yes']:
        delete_docs = True

    start_time = time.time()
    for doc in docs:
        filename = doc['title']
        filename = filename.replace('https://', '').replace('http://',
                                                            '').replace('/', '.').replace('\\', '.').replace(':', '.')
        if not filename.endswith(doc['ext']):
            filename = f'{filename}.{doc["ext"]}'
        try:
            download(doc['url'], filename, doc['size'])
        except KeyboardInterrupt:
            print('Exit...')
            sys.exit()
        if delete_docs:
            requests.get(DELETE_URL, params={
                'client_id': CLIENT_ID, 'access_token': url_params['access_token'], 'v': '5.52', 'owner_id': url_params['user_id'], 'doc_id': doc['id']})
    print('Time:', int(time.time() - start_time), 'sec')
    

if __name__ == '__main__':
    main()

