"""TEST ME"""
from setWallpapper2 import Wallpapper

if __name__ == '__main__':

    w = Wallpapper()
    w.image_containers_extract_data()
    img = w._random_image()
    local_path = w._download_image(img)
    print(local_path)
    body = '{} by {} | pexels.com{}'.format(img['title'], img['name'], img['profile'])
    w.write_img_info(local_path, body)
    w.set_as_wallpapper(local_path)
