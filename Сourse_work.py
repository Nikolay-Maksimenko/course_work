import requests
import json

class Vk_user:
    def __init__(self, vk_token, vk_id):
        self.vk_token = vk_token
        self.vk_id = vk_id

    def get_user_id(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.vk_id, 'access_token': self.vk_token, 'v': '5.131'}
        result = requests.get(url, params=params)
        return result.json()['response'][0]['id']

    def get_albums(self, vk_id):
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {'owner_id': vk_id, 'need_system': 1, 'access_token': self.vk_token, 'v': '5.131'}
        result = requests.get(url, params=params)
        list_of_albums = result.json()['response']['items']
        id_albums = [id['id'] for id in list_of_albums]
        # print(id_albums)
        return id_albums

    def get_list_photos(self, number_of_photos, album_id='profile'):
        vk_id = self.get_user_id()
        list_of_albums = self.get_albums(vk_id)
        if album_id != 'profile' and album_id not in list_of_albums:
            raise Exception('неверный id альбома')
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id' : vk_id, 'album_id': album_id, 'extended' : 1, 'count': number_of_photos, 'access_token' : self.vk_token, 'v' : '5.131'}
        result = requests.get(url, params=params)
        list_of_photos = result.json()['response']['items']
        return list_of_photos

    def get_max_size_photos(self, list_of_photos):
        max_size_photos = []
        for photo in list_of_photos:
            max_size_photos.append({'url': photo['sizes'][-1]['url'], 'likes_count': photo['likes']['count'], 'date': photo['date'], 'size_type': photo['sizes'][-1]['type']})
        return max_size_photos

    def get_photos_names(self, list_of_photos):
        photo_names = []
        for photo in list_of_photos:
            name = str(photo['likes_count']) + '.jpg'
            if name in photo_names:
                name = str(photo['date']) + name
            photo_names.append(name)
        return photo_names

class Yandex_disk:
    def __init__(self, yd_token):
        self.yd_token = yd_token
        self.yd_headers = {'Authorization': 'OAuth ' + self.yd_token}

    def create_folder(self, folder_name='VK_photos'):
        url = "https://cloud-api.yandex.net:443/v1/disk/resources/"
        params = {'path': folder_name}
        result = requests.put(url, headers=self.yd_headers, params=params)
        return folder_name

    def write_log(self, log):
        with open('log.json', 'a') as file:
            json.dump(log, file, indent=2)

    def upload(self):
        log = []
        with open('VK_token.txt') as file_object:
            vk_token = file_object.read().strip()
        user_id = input("Введите id или username пользователя: ")
        list_photo = Vk_user(vk_token, user_id)
        number_of_photos = input("Введите количество загружаемых фотографий: ")
        all_photos = list_photo.get_list_photos(int(number_of_photos))
        folder_name = self.create_folder()
        max_size_photos = list_photo.get_max_size_photos(all_photos)
        photo_names = list_photo.get_photos_names(max_size_photos)
        photos_url = [photo['url'] for photo in max_size_photos]
        photos_size = [photo['size_type'] for photo in max_size_photos]
        number = 0
        for photo in photos_url:
            url = "https://cloud-api.yandex.net:443/v1/disk/resources/upload"
            params = {'path': folder_name + '/' + photo_names[number], 'url': photos_url[number]}
            r = requests.post(url, headers=self.yd_headers, params=params)
            log.append({"file_name": photo_names[number], "size": photos_size[number]})
            number += 1
        result = self.write_log(log)



upload_photos = Yandex_disk('token')
result = upload_photos.upload()

