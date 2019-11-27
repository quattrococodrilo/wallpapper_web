import requests
from bs4 import BeautifulSoup
import subprocess
from os import path, system


def run(dir_wallpappers):
    wallpapers_dir = dir_wallpappers
    command_terminal_get_screen_size = "xdpyinfo | awk '/dimensions/{print $2}'"
    screen_size = subprocess.check_output(
        command_terminal_get_screen_size, shell=True).decode("utf-8").split('x')
    screen_width = int(screen_size[0])
    screen_height = int(screen_size[1])

    # url = 'https://www.pexels.com/search/landscape/'
    url = 'https://www.pexels.com'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    image_container = soup.find_all(
        'article', {
            'class': 'photo-item',
        })

    image_pool = []
    image_selected = {
        'author': '',
        'title': '',
        'size': '',
        'url': ''
    }

    for image in image_container:
        try:
            image_size = image['data-photo-modal-download-value-original'].\
                split('x')
            image_url = image['data-photo-modal-image-grid-item-srcset']\
                .split('?')[0]
            image_width = int(image_size[0])
            image_height = int(image_size[1])

            if image_width == screen_width and image_height == screen_height:
                image_selected['author'] = image['data-photo-modal-user-profile-full-name']
                image_selected['title'] = image['data-meta-title']
                image_selected['size'] = image['data-photo-modal-download-value-original']
                image_selected['url'] = image_url

            elif image_width >= screen_width\
                    and image_height >= screen_height\
                    and image_width > image_height:

                image_pool.append((image_width, image_height, image))

        except KeyError:
            pass

    if not image_selected['url']:
        image_pool.sort(key=lambda x: x[0])
        image_selected['author'] = image_pool[0][2]['data-photo-modal-user-profile-full-name']
        image_selected['title'] = image_pool[0][2]['data-meta-title']
        image_selected['size'] = image_pool[0][2]['data-photo-modal-download-value-original']
        image_selected['url'] = image_pool[0][2]['data-photo-modal-image-grid-item-srcset']\
            .split('?')[0]

    img_file_name = '{}__{}'.format(
        image_selected['title'], image_selected['author'])

    img_file_name = img_file_name.replace('·', '').replace(' ', '_')

    img_full_path = path.join(wallpapers_dir, img_file_name)

    with open(img_full_path, 'wb') as img:
        img.write(requests.get(image_selected['url']).content)

    system('gsettings set org.gnome.desktop.background picture-uri file://{}'.format(
        img_full_path
    ))

    print(img_full_path)


'''
    name: data-photo-modal-user-profile-full-name
    profile: data-photo-modal-user-profile-link
    title: data-meta-title
    size: data-photo-modal-download-value-original
    url: data-photo-modal-image-grid-item-src
    '''

# /usr/share/backgrounds/warty-final-ubuntu.png'
# file:///usr/share/backgrounds/warty-final-ubuntu.png

# print(image_selected['data-photo-modal-download-url'])


if __name__ == '__main__':
    run('/home/quattro/Imágenes/wallpapers')
