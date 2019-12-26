"""TEST ME"""
from setWallpapper2 import Wallpapper

if __name__ == '__main__':

    w = Wallpapper()
    screen = w.screen_size()
    print(round(screen['width'] / screen['height'], 2))
    
    w.image_containers_extract_data()
    img, not_used = w._random_image()
    body = '{} by {} | pexels.com{}'.format(img['title'],
                                            img['name'],
                                            img['profile'])
    print(img)
    if not_used:
        print('Not Used')
        w._download_image(img)
        w.processor(img['local_path'], body)
       
    w.set_as_wallpapper(img)
