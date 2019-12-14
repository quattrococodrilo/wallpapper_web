from bs4 import BeautifulSoup
from crud_yaml.crud import CRUD
from random import choice
import datetime
import requests
import subprocess
import yaml
from os import path, system


class Wallpapper():
    image_info = {
        'name': 'data-photo-modal-user-profile-full-name',
        'profile': 'data-photo-modal-user-profile-link',
        'title': 'data-meta-title',
        'size': 'data-photo-modal-download-value-original',
        'url': 'data-photo-modal-image-grid-item-src',
    }

    settings = None
    db_path = 'db.yaml'
    db = None

    def __init__(self):
        self.get_settings()
        self.db = CRUD(self.db_path)
        self.settings = CRUD('settings.yaml')

    def get_settings(self):
        """Get settings from settings.yaml"""
        with open('settings.yaml', 'r') as f:
            self.settings = yaml.full_load(f)

    def screen_size(self):
        """Get local screen size"""
        command = "xdpyinfo | awk '/dimensions/{print $2}'"
        screen_size = subprocess.check_output(command, shell=True)
        screen_size = screen_size.decode("utf-8").split('x')
        return self.width_height(screen_size)

    def width_height(self, screen_size):
        """Return a dict with width and height"""
        if len(screen_size) == 2:
            return {'width': int(screen_size[0]),
                    'height': int(screen_size[1])}
        else:
            return ''

    def image_containers_extract_data(self):
        """Extract images from web."""
        if self._compare_date():
            screen_size = self.screen_size()
            screen_ratio = self.calculate_aspect(
                screen_size['width'], screen_size['height'])
            response = requests.get(self.settings.datas[0]['url'])
            soup = BeautifulSoup(response.content, 'html.parser')
            datas = soup.find_all(
                'article', {
                    'class': 'photo-item',
                })

            for data in datas:
                info = {}
                info['name'] = data.get(self.image_info['name'], '')
                info['profile'] = data.get(self.image_info['profile'], '')
                info['title'] = data.get(self.image_info['title'], '')
                info['size'] = self.width_height(
                    data.get(self.image_info['size'], '').split('x'))
                info['url'] = data.get(self.image_info['url'], '')
                info['ratio'] = ''
                info['used'] = False
                info['downloaded'] = False
                info['local_path'] = None
                info['created'] = None

                if info['size'] and info['size']['width'] > info['size']['height']:
                    if 'video' not in info['title'].lower():
                        info['ratio'] = self.calculate_aspect(
                            info['size']['width'], info['size']['height'])
                        if not self.db.get(title=info['title']):
                            self.db.datas.append(info)

            self._update_date()
            self.db._save()

    def used_images(self):
        """
        ----------------------NOT USED-----------------------------------
        """
        images_not_used = []

    def calculate_aspect(self, width, height):
        """Caculate de aspect ratio.
        Code taken from: https://gist.github.com/Integralist/4ca9ff94ea82b0e407f540540f1d8c6c"""
        temp = 0

        def gcd(a, b):
            """The GCD (greatest common divisor) is the highest number that evenly divides both width and height."""
            return a if b == 0 else gcd(b, a % b)

        if width == height:
            return "1:1"

        if width < height:
            temp = width
            width = height
            height = temp

        divisor = gcd(width, height)

        x = int(width / divisor) if not temp else int(height / divisor)
        y = int(height / divisor) if not temp else int(width / divisor)

        return "{x}:{y}".format(x=x, y=y)

    def _string_binary(self, param):
        return str(bin(param))

    def _get_date_today(self):
        return datetime.date.today()

    def _update_date(self):
        self.settings.datas[0]['last_update'] = self._get_date_today()
        self.settings._save()

    def _compare_date(self):
        if not self.settings.datas[0]['last_update']:
            return True

        previus_date = self.settings.datas[0]['last_update']
        update_frecuency = datetime.timedelta(
            days=self.settings.datas[0]['update_frecuency'])

        date_to_compare = previus_date + update_frecuency
        if date_to_compare <= self._get_date_today():
            return True
        else:
            return False

    def _random_image(self):
        not_used_images = self.db.filter(used=False)
        while True:
            image_info = choice(not_used_images)
            if not image_info['used']:
                return image_info
    #

    def _download_image(self, image):
        """Downloads image"""
        try:
            if not image['downloaded'] and not image['local_path']:
                url = image['url'].split('?')[0]
                name = '{}-{}'.format(image['id'], url.split('/')[-1])
                image_path = path.join(
                    self.settings.datas[0]['images_dir'], name)
                print(url)
                with open(image_path, 'wb') as img:
                    img.write(requests.get(url).content)
                image['local_path'] = image_path
                image['downloaded'] = True
                self.db.datas[image['idx']] = image
                self.db._save()
                return image_path
        except Exception as e:
            print(e)
            return False

    def set_as_wallpapper(self, path):
        """Set image as Wallpapper"""
        if path:
            system(
                'gsettings set org.gnome.desktop.background picture-uri file://{}'.format(path))
