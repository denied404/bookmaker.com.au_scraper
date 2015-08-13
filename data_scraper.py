#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from time import strptime, strftime
from bs4 import BeautifulSoup
import urllib.request
import re

root_url = "https://www.bookmaker.com.au"


def remove_suffix_from_date(date_str):
    """Removes day suffixes from date"""
    res = date_str
    for ch in ["st", "nd", "rd", "th"]:
        res = res.replace(ch, "")
    return res


def make_soup(url):
    """Makes soup from URL"""
    content = urllib.request.urlopen(url).read()
    return BeautifulSoup(content, "html.parser")


def get_racing_divs(soup):
    """Returns Horse racing table div"""
    return soup.find("div", id="racesToday").findAll("div", class_="fullbox")


def get_racing_rel_urls(divs):
    """Returns a list of url's with racings to parse"""
    urls = [a['href'] for div in divs for a in div.find_all("a", class_=re.compile("subpage"))]
    return [x for x in filter(lambda x: "/next/" not in x, urls)]


if __name__ == '__main__':

    # Result header
    result = [["Rcdate", "Track", "Rcno", "Rctime", "Horse", "Tab"]]

    # Ok, let's make a soup and retrieve all racing URLs
    soup = make_soup(root_url + "/racing/horses/")
    racing_divs = get_racing_divs(soup)
    racing_rel_urls = get_racing_rel_urls(racing_divs)

    # Traversing by racing URLs
    for racing_rel_url in racing_rel_urls:
        race_soup = make_soup(root_url + racing_rel_url)

        # Fetch all needed info
        title_container = race_soup.find("div", id="col-2-2") \
            .find("div", id=re.compile("event-"))
        race_number = title_container \
            .find("span", class_="race-number") \
            .string
        track = title_container.h1.get_text().split(" Race")[0]
        race_date = race_soup.find("div", id=re.compile("event-")).find("span", class_="race-date").string
        race_date = strptime(remove_suffix_from_date(race_date), "%a %d %b %Y")
        race_time = race_soup.find("div", class_=re.compile("racedescription"), recursive=True) \
            .find("span", id=re.compile("outcome_ts")).string

        horses_trs = race_soup.find_all("tr", id=re.compile("competitor"), recursive=True)
        for tr in horses_trs:
            horse_name = tr.find("span", class_="competitor-name", recursive=True).string
            horse_slot_txt = tr.find("span", class_="barrier-number", recursive=True).string
            horse_slot = re.search("\((.*)\)", horse_slot_txt).group(1)
            result.append([strftime("%d.%m.%Y", race_date), track, race_number, race_time, horse_name, horse_slot])

    # Write results to output.csv
    with open('output.csv', 'w', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(result)
