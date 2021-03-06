from bs4 import BeautifulSoup
from crud_yaml.crud import CRUD
from random import choice
from os import path, system, makedirs
from wand.image import Image
from wand.drawing import Drawing
import datetime
import requests
import subprocess
import yaml


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
        if self._compare_date() or len(self.db.datas) == 0:
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
                info['created'] = datetime.datetime.now()

                if info['size'] and info['size']['width'] > info['size']['height']:
                    if 'video' not in info['title'].lower():
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
        Code taken from: 
        https://gist.github.com/Integralist/4ca9ff94ea82b0e407f540540f1d8c6c"""
        temp = 0

        def gcd(a, b):
            """The GCD (greatest common divisor) is the highest number 
            that evenly divides both width and height."""
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
        """Return a random image"""
        not_used_images = self.db.filter(used=False)
        if not_used_images:
            return (choice(not_used_images), True)
        return (choice(self.db.datas), False)
        

    def _download_image(self, image):
        """Downloads image"""
        dir_photos = self.settings.datas[0]['images_dir']
        self.check_if_dir_exist(dir_photos)
        try:
            if not image['downloaded'] and not image['local_path']:
                url = image['url'].split('?')[0]
                name = '{}.{}'.format(image['id'], url.split('.')[-1])
                image_path = path.join(dir_photos, name)
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

    def processor(self, img_path, body):
        """Write info (author, photo, profile) in the photo and
        crop image to screen size"""
        lscreen = self.screen_size()
        
        with Image(filename=img_path) as img:
            
            proportion = 0
            height = 0
            width = 0
            if lscreen['height'] > lscreen['width']:
                proportion = round(lscreen['height'] / lscreen['width'], 2)
                height = img.height
                width_calculated = int(img.height / proportion)
                width = width_calculated if width_calculated else img.width
            else:
                proportion = round(lscreen['width'] / lscreen['height'], 2)
                height_calculated = int(img.width / proportion)
                height = height_calculated if height_calculated else img.height
                width = img.width
            
            img.crop(
            width= width,
            height= height,
            gravity='center')
            
            with Drawing() as draw:
                draw.font = self.settings.datas[0]['font']
                draw.font_size = int(img.height * 0.02)
                draw.fill_color = 'WHITE'
                draw.text(30, img.height - 30, body)
                draw(img)
                img.save(filename=img_path)
    
    def check_if_dir_exist(self, dir_photos):
        """Check if directory existis, if not exist, 
        creates a tree directory"""
        if not path.isdir(dir_photos):
            makedirs(dir_photos)

    def set_as_wallpapper(self, img):
        """Set image as Wallpapper"""
        if img['local_path']:
            system(
                'gsettings set org.gnome.desktop.background picture-uri file://{}'\
                    .format(img['local_path'])
            )
            img['used'] = True
            self.db._save()

    
