import os
import pprint
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import adafruit_ssd1306
import board
import psutil as ps
import statsapi
from PIL import Image, ImageDraw, ImageFont

WIDTH = 128
HEIGHT = 64
FONTSIZE = 16
pp = pprint.PrettyPrinter(indent=4)
date = datetime.now().strftime("%m/%d/%Y")

games = statsapi.schedule(start_date=date, end_date=date)

HITS = 108
RUNS = 84


def stats_status(status=True):
    commands = ["sudo", "systemctl", "start", "stats"]
    if not status:
        commands.remove("start")
        commands.insert(2, "stop")
    return subprocess.run(
        commands,
        check=False,
    )


def display_game(game):
    stats_status(False)
    i2c = board.I2C()
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)
    oled.fill(0)
    oled.show()
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    padding = -2
    top = padding
    bottom = oled.height - padding
    x = 0

    # font = ImageFont.load_default()
    font = ImageFont.truetype(
        f"{Path(__file__).parent / 'fonts' / 'PixelOperator.ttf'}", FONTSIZE
    )
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    draw.text((RUNS, top), "R", font=font, fill=255)
    draw.text((HITS, top), "H", font=font, fill=255)

    draw.text((x, top + 10 + FONTSIZE), game.get("away_team", ""), font=font, fill=255)
    draw.text(
        (x, top + 10 + 2 * FONTSIZE), game.get("home_team", ""), font=font, fill=255
    )
    draw.text(
        (RUNS, top + 10 + FONTSIZE), str(game.get("away_runs", "")), font=font, fill=255
    )
    draw.text(
        (RUNS, top + 10 + 2 * FONTSIZE),
        str(game.get("home_runs", "")),
        font=font,
        fill=255,
    )
    draw.text(
        (HITS, top + 10 + FONTSIZE), str(game.get("away_hits", "")), font=font, fill=255
    )
    draw.text(
        (HITS, top + 10 + 2 * FONTSIZE),
        str(game.get("home_hits", "")),
        font=font,
        fill=255,
    )
    draw.text((x, top), game.get("status"), font=font, fill=255)
    oled.image(image)
    oled.show()


while 1:
    for game in games:
        game_time = datetime.fromisoformat(game.get("game_datetime")).replace(
            tzinfo=timezone.utc
        )
        local_tz = ZoneInfo("America/Chicago")
        local_dt = game_time.astimezone(local_tz)
        if game.get("status") == "In Progress":
            status = f"{game.get('inning_state', '')} {game.get('current_inning', '')}"
        elif game.get("status") in ["Scheduled", "Pre-Game"]:
            status = local_dt.strftime("%-I:%M")
        else:
            status = game.get("status", "")
        box_score = statsapi.boxscore_data(gamePk=game.get("game_id"))
        team_info = box_score.get("teamInfo")

        game_details = {
            "away_team": team_info["away"]["teamName"],
            "home_team": team_info["home"]["teamName"],
            "away_runs": box_score["away"]["teamStats"]["batting"]["runs"],
            "home_runs": box_score["home"]["teamStats"]["batting"]["runs"],
            "away_hits": box_score["away"]["teamStats"]["batting"]["hits"],
            "home_hits": box_score["home"]["teamStats"]["batting"]["hits"],
            "status": status,
            "game_datetime": game.get("game_datetime"),
            # "away_runs": box_score["away"]["teamStats"]["batting"]["errors"],
            # "home_errors": box_score["home"]["teamStats"]["batting"]["runs"],
        }
        # pp.pprint(details)
        display_game(game_details)
        time.sleep(5)
