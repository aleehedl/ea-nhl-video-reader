#!/usr/local/bin/python
import csv
import os
import sys

import PIL.ImageOps
from PIL import Image
import pytesseract

OUT_DIR = 'out'
TMP_DIR = 'tmp'

# Expects 1920 x 1080 image
AWAY_STAT_X = 990
HOME_STAT_X = 1585
STAT_Y_OFFSET = 340
STAT_WIDTH = 115
STAT_HEIGHT = 56
STAT_Y_OUTER_HEIGHT = 68

AWAY_TEAM_CROP = (1070, 258, 1240, 326)
AWAY_GOALS_CROP = (1261, 254, 1328, 320)

HOME_TEAM_CROP = (1450, 258, 1615, 326)
HOME_GOALS_CROP = (1360, 254, 1425, 320)

STAT_ORDER = [
    'shots',
    'hits',
    'time on attack',
    'passing',
    'faceoffs won',
    'penalty minutes',
    'powerplays',
    'powerplay minutes',
    'shorthanded goals',
]

STAT_POSITIONS = {
    'goals': {
        'away': (AWAY_STAT_X, STAT_Y_OFFSET + 0 * STAT_Y_OFFSET),
        'home': (HOME_STAT_X, STAT_Y_OFFSET),
    }
},


def scale_crop_pos(image, crop):
    normal_width = 1920
    normal_height = 1080
    width, height = image.size
    width_factor = width / normal_width
    height_factor = height / normal_height
    return (
        crop[0] * width_factor,
        crop[1] * height_factor,
        crop[2] * width_factor,
        crop[3] * height_factor,
    )


def get_stat_bounding_box(away_or_home, index):
    if away_or_home not in ('away', 'home'):
        raise Exception('away_or_home value must be `away` or `home`')
    is_away = away_or_home == 'away'
    pos_1 = (
        AWAY_STAT_X if is_away else HOME_STAT_X,
        STAT_Y_OFFSET + index * STAT_Y_OUTER_HEIGHT
    )

    pos_2 = (
        pos_1[0] + STAT_WIDTH,
        pos_1[1] + STAT_HEIGHT
    )
    return (pos_1, pos_2)


def read_value_from_image(
    image, crop=None, invert=False, convert=True, save_path=None,
    prefer_digits=False,
):
    if crop:
        image = image.crop(scale_crop_pos(image, crop))

    if convert:
        image = image.convert('L')

    if invert:
        image = PIL.ImageOps.invert(image)

    value = pytesseract.image_to_string(image, config=f'--psm 6')

    if save_path:
        image.save(save_path)
    if prefer_digits:
        # Trial and error
        value = value \
            .replace('v', '/') \
            .replace('!', '1') \
            .replace('|', '1') \
            .replace('o', '0') \
            .replace('a', '0') \
            .replace('g', '9') \
            .replace('n', '11') \
            .replace('z', '2') \
            .replace('O', '0') \
            .replace('O', '0') \
            .replace('s', '/')
    return value


def get_stat_from_image(image, away_or_home, i, prefer_digits=False):
    pos_1, pos_2 = get_stat_bounding_box(away_or_home, i)
    crop = (*pos_1, *pos_2)
    save_path = os.path.join(TMP_DIR, f'{away_or_home}_{i}.png')
    return read_value_from_image(
        image, crop=crop, invert=True, save_path=save_path,
        prefer_digits=prefer_digits,
    )


def get_stats(image_path):
    image = Image.open(image_path)

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    if not os.path.exists(TMP_DIR):
        os.makedirs(OUT_DIR)

    out_filename = os.path.splitext(os.path.basename(image_path))[0]
    out_filepath = os.path.join(OUT_DIR, f'{out_filename}.csv')
    with open(out_filepath, mode='w') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        away_team = read_value_from_image(
            image, crop=AWAY_TEAM_CROP, invert=True,
            save_path=os.path.join(TMP_DIR, 'away_team.png'),
        )
        home_team = read_value_from_image(
            image, crop=HOME_TEAM_CROP, invert=True,
            save_path=os.path.join(TMP_DIR, 'home_team.png'),
        )
        away_goals = read_value_from_image(
            image, crop=AWAY_GOALS_CROP,
            save_path=os.path.join(TMP_DIR, 'away_goals.png'),
            prefer_digits=True,
        )
        home_goals = read_value_from_image(
            image, crop=HOME_GOALS_CROP,
            save_path=os.path.join(TMP_DIR, 'home_goals.png'),
            prefer_digits=True,
        )
        writer.writerow(['Stat', 'Away', 'Home'])
        writer.writerow(['Team', away_team, home_team])
        writer.writerow(['Goals', away_goals, home_goals])
        for i, stat in enumerate(STAT_ORDER):
            away_value = get_stat_from_image(image, 'away', i, prefer_digits=True)
            home_value = get_stat_from_image(image, 'home', i, prefer_digits=True)
            writer.writerow([stat.capitalize(), away_value, home_value])


if __name__ == '__main__':
    get_stats(sys.argv[1])
