import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import csv
import time
from bs4 import BeautifulSoup

def scrape_player(soup):
    """
    Scrape data for an individual player given the html
    soup of the player's career page.
    Parameters:
        soup (BeautifulSoup): A BeautifulSoup object with
            the page source for the career of the player
            to scrape.
    Returns:
        data (list): A list of lists containing one list
            for each season of the players career, and
            each list contains data corresponding to the
            player's stats for that season.
    """
    data = []
    tag = soup.td.parent           # Get to first line of table
    while tag is not None:
        line = []
        for i, item in enumerate(list(tag.children)[1::2]):
            if i == 0:
                line.append(item.a.string)
            elif i == 1:
                line.append(item.span.string)
            else:
                line.append(item.string)
        data.append(line)
        for _ in range(2):
            tag = tag.next_sibling # Get to next line
        if tag == '\n':
            break
    return data

def write_to_csv(player, lines):
    """
    Write headers, then lines to csv file.

    Parameters:
        player (str): Player name and position, used to name csv file.
            Formatted as: 'Kobe Bryant, F'.
        lines (list): List of lines of player data to put in csv
    """
    headers = ["SEASON","TEAM","AGE","GP","GS","MIN", # Headers for all players
               "PTS","FGM","FGA","FG%","3PM","3PA",
               "3P%","FTM","FTA","FT%","OREB","DREB",
               "REB","AST","STL","BLK","TOV","PF"]
    with open('csvs/'+player+'.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(headers)
        for line in lines:
            writer.writerow(line)

def scrape_data(seasons, num_per_season):
    """
    Scrape the following data from randomly selected players
    from each season in seasons:
    - Player Name
    - Player Position
    - Player Career Stats

    Parameters:
        seasons (list): list of seasons in format ['1990-91', '1991-92']
        num_per_season (int): number of players per season to scrape
    Returns:
        players_scraped (list): list of players scraped and their positions
            in this format ['Kobe Bryant, F', 'Steph Curry, G']
    """
    players_scraped = []

    base_url = 'http://stats.nba.com'
    browser = webdriver.Chrome()
    for season in seasons:
        browser.get(base_url + '/leaders/?Season={}&SeasonType=Regular%20Season'.format(season))

        # Gets all players from that season
        time.sleep(2)
        drop_down_bar = browser.find_element_by_class_name("stats-table-pagination__select")
        drop_down_bar.click()
        drop_down_bar.send_keys("All")

        soup = BeautifulSoup(browser.page_source, 'html.parser')
        for _ in range(num_per_season):
            invalid = True # Validate selected player
            while invalid:
                index = np.random.randint(1, 300)
                tags = soup.find_all(string=index)
                if len(tags) == 0:
                    continue
                else:
                    invalid = False
                i = 0
                while i < len(tags):
                    player_tag = tags[i].parent.parent.a
                    if player_tag is not None:
                        invalid = False
                        break
                    i+=1

            player_link = player_tag.attrs['href']
            player_link = player_link.replace('traditional', 'career')
            player_name = player_tag.string
            browser.get(base_url + player_link)

            player_soup = BeautifulSoup(browser.page_source, 'html.parser')
            position_tag = player_soup.find(class_="player-summary__player-pos")
            position = position_tag.string

            if position is not None: # Only scrape players with a position
                scraped_data = scrape_player(player_soup)
                write_to_csv(player_name + ', ' + position, scraped_data)
                players_scraped.append(player_name + ', ' + position)
    return players_scraped
