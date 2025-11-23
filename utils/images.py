from PIL import Image, ImageDraw, ImageFont
from typing import List
import requests
from io import BytesIO
from valaw import objects

# Note to self.
# Align = Vertical Alignment
# Anchor = (Horizontal, Vertical)

def open_image_from_url(url):
    # Send a HTTP request to the URL
    response = requests.get(url)

    # Raise an exception if the request was unsuccessful
    response.raise_for_status()

    # Open the image from the response content
    image = Image.open(BytesIO(response.content))

    return image
    
def create_overview_statistics_image(riotID, stats: dict, filename):
    template = Image.open("assets/VALcord_assets/statistics_assets/overview_template.png")
    draw = ImageDraw.Draw(template)
    font_96px_bold = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf",96)
    font_96px_bold.set_variation_by_name(b"Bold")
    font_64px_bold = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf", 64)
    font_64px_bold.set_variation_by_name(b"Bold")
    font_48px_bold = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf", 48)
    font_48px_bold.set_variation_by_name(b"Bold")
    font_82px_bold = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf", 82)
    font_82px_bold.set_variation_by_name(b"Bold")

    # Riot ID
    draw.text((1280, 156), riotID, (255, 255, 255), font=font_96px_bold, align='center', anchor="mm")
    # Rank
    draw.text((318, 185), stats["rank"], (255, 255, 255), font=font_64px_bold, align='middle', anchor="lm")
    rank_image = Image.open(f"assets/VALORANT_assets/Ranks/{stats['rank'].replace(' ', '_')}.png")
    if stats["rank"] == "Unranked":
        size = (189, 189)
        rank_image = rank_image.resize(size)
        rank_y = (156+22) - rank_image.height // 2
    else:
        size = (140, 140)
        rank_image = rank_image.resize(size)
        rank_y = 156 - (rank_image.height // 2)
    template.paste(rank_image, (227 - rank_image.width // 2, rank_y), rank_image)
    # Level
    draw.text((2315, 185), str(stats["level"]), (255, 255, 255), font=font_64px_bold, align='middle', anchor="mm")
    # Act
    draw.text((198, 542), stats["season_display_name"], (181, 181, 181), font=font_48px_bold, align='middle', anchor="lm")
    # KD
    draw.text((416, 773), str(stats["kd_ratio"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Win Percent
    draw.text((992, 773), str(stats["win_percentage"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # ACS
    draw.text((1570, 773), str(stats["average_combat_score"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Headshot Percent
    draw.text((2147, 773), str(stats["headshot_percentage"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Kills
    draw.text((358, 1025), str(stats["kills"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Deaths
    draw.text((818, 1025), str(stats["deaths"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Assists
    draw.text((1280, 1025), str(stats["assists"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # KDA
    draw.text((1742, 1025), str(stats["kda_ratio"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Damage Per Round
    draw.text((2204, 1025), str(stats["damage_per_round"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Wins
    draw.text((358, 1276), str(stats["wins"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Losses
    draw.text((818, 1276), str(stats["losses"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # First Bloods
    draw.text((1280, 1276), str(stats["first_bloods"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Aces
    draw.text((1742, 1276), str(stats["aces"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")
    # Most Kills
    draw.text((2204, 1276), str(stats["most_kills"]), (255, 255, 255), font=font_82px_bold, align='middle', anchor="mm")

    template.save("statistics_images/overview/" + str(filename) + ".png")

def create_matches_statistics_image(riotID, rank, level, act, matchlist: List[dict], filename):
    template = Image.open("assets/VALcord_assets/statistics_assets/matches_template.png")
    draw = ImageDraw.Draw(template)
    font_96px_bold = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf", 96)
    font_96px_bold.set_variation_by_name(b"Bold")
    font_64px_bold = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf", 64)
    font_64px_bold.set_variation_by_name(b"Bold")
    font_48px_bold = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf", 48)
    font_48px_bold.set_variation_by_name(b"Bold")
    font_82px_bold = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf", 82)
    font_82px_bold.set_variation_by_name(b"Bold")
    font_46px_semi = ImageFont.truetype("assets/VALcord_assets/statistics_assets/Rubik-VariableFont_wght.ttf", 46)
    font_46px_semi.set_variation_by_name(b"SemiBold")

    # Riot ID
    draw.text((1280, 156), riotID, (255, 255, 255), font=font_96px_bold, align='center', anchor="mm")
    # Rank
    draw.text((298, 185), rank, (255, 255, 255), font=font_64px_bold, align='middle', anchor="lm")
    rank_image = Image.open(f"assets/VALORANT_assets/Ranks/{rank.replace(' ', '_')}.png")
    if rank == "Unranked":
        size = (189, 189)
        rank_image = rank_image.resize(size)
        rank_y = (156 + 22) - rank_image.height // 2
        template.paste(rank_image, (205 - rank_image.width // 2, rank_y), rank_image)
    else:
        size = (140, 140)
        rank_image = rank_image.resize(size)
        template.paste(rank_image, (138, 87), rank_image)
    # Level
    draw.text((2315, 185), str(level), (255, 255, 255), font=font_64px_bold, align='middle', anchor="mm")
    # Act
    draw.text((198, 542), act, (181, 181, 181), font=font_48px_bold, align='middle', anchor="lm")

    for index, match in enumerate(matchlist):
        match_background = Image.open(f"assets/VALcord_assets/statistics_assets/{match['data']['outcome']}_background.png").convert("RGBA")
        match_background = match_background.resize((2260, 136))
        y_position = 668 + (index * 136)
        template.paste(match_background, (150, y_position), match_background)
        agent_image = open_image_from_url(f"https://media.valorant-api.com/agents/{match['data']['agent_uuid']}/displayicon.png").convert("RGBA")
        agent_image = agent_image.resize((136, 136))
        template.paste(agent_image, (160, y_position), agent_image)
        map_image = Image.open(f"assets/VALcord_assets/statistics_assets/{match['data']['map']}.png").convert("RGBA")
        map_image = map_image.resize((704,136))
        template.paste(map_image, (1703, y_position), map_image)
        
        rank_image = Image.open(f"assets/VALORANT_assets/Ranks/{match['data']['rank'].replace(' ', '_')}.png").convert("RGBA")
        rank_image = rank_image.resize((110,110))
        if match['data']['rank'] == "Unranked":
            rank_y_position = 695 + (index * 136)
        else:
            rank_y_position = 681 + (index * 136)
        template.paste(rank_image, (314, rank_y_position), rank_image)
        draw.text((719, 715 + (index * 136)), str(match['data']['kda']), (255, 255, 255), font=font_46px_semi, align="middle", anchor="lm")
        draw.text((719, 766 + (index * 136)), str(match['data']['user-score']), (181, 181, 181), font=font_46px_semi, align="middle", anchor="lm")
        draw.text((1280,736 + (index * 136)), str(match['data']['game-score']), (255, 255, 255), font=font_96px_bold, align="middle", anchor="mm")


    template.save("statistics_images/matches/" + str(filename) + ".png")