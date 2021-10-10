import requests
import json
import typing

class VKUser:
    VK_API_BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, token: str, user_id: str, api_version: str):
        self.token = token
        self.user_id = user_id
        self.api_version = api_version
        self.user_id = self.get_user_id()

    def get_user_id(self) -> int:
        url = self.VK_API_BASE_URL + 'users.get'
        params = {'user_ids': self.user_id, 'access_token': self.token, 'v': self.api_version}
        result = requests.get(url, params=params)
        return result.json()['response'][0]['id']

    def get_albums(self) -> typing.List[str]:
        url = self.VK_API_BASE_URL + 'photos.getAlbums'
        params = {'owner_id': self.user_id, 'need_system': 1, 'access_token': self.token, 'v': self.api_version}
        result = requests.get(url, params=params)
        albums_list = result.json()['response']['items']
        return [album['id'] for album in albums_list]

    def get_photos(self, count: int, album_id: str ='profile') -> typing.List[typing.Dict]:
        albums = self.get_albums()
        if album_id != 'profile' and album_id not in albums:
            raise Exception('неверный id альбома')
        url = self.VK_API_BASE_URL + 'photos.get'
        params = {'owner_id': self.user_id, 'album_id': album_id, 'extended': 1, 'count': count, 'access_token': self.token, 'v': self.api_version}
        result = requests.get(url, params=params)
        return result.json()['response']['items']

    def get_max_size_photos(self, photos: typing.List[typing.Dict]) -> typing.List[typing.Dict]:
        max_size_photos = []
        for photo in photos:
            max_size_photos.append({'url': photo['sizes'][-1]['url'], 'likes_count': photo['likes']['count'], 'date': photo['date'], 'size_type': photo['sizes'][-1]['type']})
        return max_size_photos

    def get_photos_names(self, photos: typing.List[typing.Dict]) -> typing.List[str]:
        photo_names = []
        for photo in photos:
            name = str(photo['likes']['count']) + '.jpg'
            if name in photo_names:
                name = str(photo['date']) + name
            photo_names.append(name)
        return photo_names

    def get_photos_for_upload(self, count: int = 5) -> typing.Dict:
        number = 0
        list_photos = []
        photos = self.get_photos(count)
        names = self.get_photos_names(photos)
        max_size_photos = self.get_max_size_photos(photos)
        for photo in max_size_photos:
            list_photos.append({'url': photo['url'], 'name': names[number], 'size_type': photo['size_type']})
            number+=1
        return list_photos

class YandexDiscClient:
    YANDEX_DISC_BASE_URL = 'https://cloud-api.yandex.net:443/v1/disk/resources/'

    def __init__(self, token: str):
        self.yd_token = token
        self.headers = {'Authorization': 'OAuth ' + self.yd_token}

    def create_folder(self, folder_name: str ='VK_photos'):
        url = "https://cloud-api.yandex.net:443/v1/disk/resources/"
        params = {'path': folder_name}
        requests.put(self.YANDEX_DISC_BASE_URL, headers=self.headers, params=params)
        return folder_name

    def write_log(self, log: typing.List[typing.Dict]):
        with open('log.json', 'a') as file:
            json.dump(log, file, indent=2)

    def upload(self, photos: typing.Dict):
        log = []
        url = self.YANDEX_DISC_BASE_URL + "upload"
        folder = self.create_folder()
        for photo in photos:
            params = {'path': folder + '/' + photo['name'], 'url': photo['url']}
            requests.post(url, headers=self.headers, params=params)
            log.append({"file_name": photo['name'], "size": photo['size_type']})
        self.write_log(log)

if __name__ == '__main__':
    user_id = input("Введите id или username пользователя: ")
    count = int(input("Введите количество загружаемых фотографий: "))
    with open('VK_token.txt') as file_object:
        vk_token = file_object.read().strip()
    vk = VKUser(vk_token, user_id, '5.131')
    photos = vk.get_photos_for_upload(count)
    yandex = YandexDiscClient('Token')
    yandex.upload(photos)