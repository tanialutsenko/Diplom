from random import randrange
from pprint import pprint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from io import BytesIO
from datetime import datetime

from Table import create_tables, session, Course


with open("access_token.txt", "r") as file_object:  # access_token
    token_vk = file_object.read().strip()

with open("token_community.txt", "r") as file:  # ключ сообщества
    token_community = file.read().strip()

with open("password_base.txt", "r") as file_object:  # access_token
    password = file_object.read().strip()

list_base = password.split(",")

login= list_base[0]
password = list_base[1]
database = list_base[2]

create_tables(login,password,database)

class VKApi():
    def __init__(self, base_url: str = "https://api.vk.com/"):
        self.token_vk = token_vk
        self.base_url = base_url
        self.params = {
            'access_token': self.token_vk,
            'v': '5.131'
        }

    def users_get_name(self, user_id):
        params = {
            "user_ids": user_id,
            "fields": "sex, city, bdate,is_closed"
        }
        response = requests.get(f"{self.base_url}/method/users.get", params={**self.params, **params})
        user_json = response.json()

        return (user_json)

    def users_search(self, age_go, age_from, s_1, city):
        params = {
            "count": 10,
            "offset": randrange(100),
            "fields": "city,sex",
            "sex": s_1,
            "age_from": age_from,
            "age_go": age_go,
            "has_photo": 1,
            "status": 1
        }
        response = requests.get(f"{self.base_url}/method/users.search", params={**self.params, **params})
        user_search= response.json()
        list_id = []
        black_list_id = []
        list_name = []
        for user in user_search['response']['items']:
            id = user['id']
            for key,value in user.items():
                if user['is_closed'] == True:
                    black_list_id.append(id)
                if user['is_closed'] == False:
                    if key == 'city':
                        for key, value in value.items():
                            if key == 'title' and value == city:
                                list_id.append(id)
                                first_name = user['first_name']
                                last_name = user['last_name']
                                full_name = f'{first_name} {last_name}'
                                list_name.append(full_name)
        dict_name_id = {list_id[i]: list_name[i] for i in range(len(list_id))}
        return (dict_name_id)

    def photos_get(self, id):
        params = {
            "owner_id": id,
            "album_id": "profile",
            "extended": "1"}
        response = requests.get(f"{self.base_url}/method/photos.get", params={**self.params, **params})
        photo_json = response.json()
        return (photo_json)


def get_age(response_user):
    currentYear = int(datetime.now().year)
    print(currentYear)
    date = 20
    for r in response_user['response']:
        if 'bdate' in r:
            date_date = r['bdate']
            year = int(date_date[-4:])
            date = currentYear - year
        if 'bdate' not in r:
            write_msg(event.user_id, "Введите ваш возраст")
            date = listen_user()
    return (date)


def get_city(response_user):
    for r in response_user['response']:
        city = "Теткино"
        if 'city' in r:
            city = r['city']['title']
        if 'city' not in r:
            write_msg(event.user_id, "Введите ваш город")
            city = listen_user()
    return (city)


def get_sex(response_user):
    for r in response_user['response']:
        sex_faind = 0
        sex = r['sex']
        if sex == 1:
            sex_faind = 2
        if sex == 2:
            sex_faind = 1
    return (sex_faind)

def upload_photo(best_photo_link):
    three_link = []
    for link in best_photo_link:
        list_value = []
        list_key = ['owner_id', 'id', 'access_key']
        upload = vk_api.VkUpload(vk)
        img = requests.get(link).content
        img_bate = BytesIO(img)

        response = upload.photo_messages(img_bate)[0]

        owner_id = response['owner_id']
        id = response['id']
        access_key = response['access_key']

        list_value.append(owner_id)
        list_value.append(id)
        list_value.append(access_key)
        dict_for_send = {list_key[i]: list_value[i] for i in range(len(list_key))}
        three_link.append(dict_for_send)

    return three_link

def main(id_people_search):

    for key, value in id_people_search.items():
        response_photo = user_vk_name.photos_get(key)
        id = key
        name = value
        id_profile_link = f'https://vk.com/id{id}'
        id_photo = []
        likes = []
        for photo in response_photo['response']['items']:
            id_photo.append(photo['id'])
            for key, value in photo['likes'].items():
                if key == 'count':
                    likes.append(value)

        dict_photo_link = {id_photo[i]: likes[i] for i in range(len(id_photo))}
        photos_best = sorted(dict_photo_link, key=dict_photo_link.get, reverse=True)[:3]
        best_photo_link = []
        for photo in photos_best:
            for key in response_photo['response']['items']:
                if key['id'] == photo:
                    all_photo_link = []
                    for sizes in key['sizes']:  # берем ссылки для разных качеств фото
                        f = sizes['url']
                        all_photo_link.append(f)

                    best_photo_link.append(all_photo_link[-1])  # последняя ссылка самого лучшего качества

        write_msg(event.user_id,f'{name} {id_profile_link}')

        three_link = upload_photo(best_photo_link)

        for link in three_link:
            list_photo = []
            for key, value in link.items():
                list_photo.append(value)
            owner_id = list_photo[0]
            photo_id = list_photo[1]
            access_key = list_photo[2]

            send_photo(event.user_id, f'photo{owner_id}_{photo_id}_{access_key}')

def write_msg(user_id, message):
    vk.method('messages.send',
              {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

def send_photo(user_id, attachment):
    vk.method('messages.send',
              {'user_id': user_id, 'attachment': attachment, 'random_id': randrange(10 ** 7)})


def listen_user():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            age = event.text
            break
    return (age)

vk = vk_api.VkApi(token=token_community)
longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        response = event.text
        reesponse_lower = response.lower()
        user_vk_name = VKApi()  #  экземпляр класса
        name_user = user_vk_name.users_get_name(event.user_id)
        for r in name_user['response']:
            name = r['first_name']
        write_msg(event.user_id, f"Привет, {name} ! Я могу найти вам пару.Хотите начать  поиск?")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                response_1 = event.text
                response_1_lower = response_1.lower()
                if response_1_lower == "да":
                    user_id = event.user_id
                    currentYear = int(datetime.now().year)
                    date = get_age(name_user)
                    age_go = str(date)
                    age_from = str(date)
                    city = get_city(name_user)
                    sex = get_sex(name_user)
                    id_people_search = user_vk_name.users_search(age_go, age_from, sex, city)
                    # session(user_id, id_people_search)
                    session(user_id, id_people_search, login, password, database)
                    main(id_people_search)
                    write_msg(event.user_id, "Хотите продолжить поиск?")
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            response_2 = event.text
                            response_2_lower = response_2.lower()
                            if response_2_lower == "да":
                                people_search_new = user_vk_name.users_search(age_go, age_from, sex, city)
                                # session(user_id, people_search_new)
                                session(user_id, people_search_new, login, password, database)
                                main(people_search_new)
                                write_msg(event.user_id, "Хотите продолжить поиск?")
                                continue
                            if response_2_lower == "нет":
                                write_msg(event.user_id, "Пока((")
                                break
                            else:
                                write_msg(event.user_id, "Не понял вашего ответа...Вы хотите продолжить поиск?")

                if response_1_lower == "нет":
                    write_msg(event.user_id, "Пока((")

                break
