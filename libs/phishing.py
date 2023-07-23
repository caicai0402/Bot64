import requests
import os

class Phishing:
    tiananmenSquareList = []

    def __init__(self):
        if len(Phishing.tiananmenSquareList) == 0:
            Phishing.fetch()
        
    @staticmethod
    def fetch():
        url = 'https://raw.githubusercontent.com/Dogino/Discord-Phishing-URLs/main/scam-urls.txt'
        r = requests.get(url)
        Phishing.tiananmenSquareList = r.text.split('\n')
        print('Successfully fetched latest phishing links at ' + url)

        directory = os.path.dirname(__file__)
        blackListFilePath2 = os.path.join(directory, 'link.txt')
        f = open(blackListFilePath2, 'r', encoding = 'utf-8')
        origin_TAMSlist = f.read().split('\n')
        f.close()

        TAMS_set1 = set(Phishing.tiananmenSquareList + origin_TAMSlist)
        TAMS_list = list(TAMS_set1)
        TAMS_list.sort()
        TAMS_str = '\n'.join(TAMS_list)
        f1 = open(blackListFilePath2, 'w', encoding = 'utf-8')
        f1.write(TAMS_str)
        print('Successfully updated latest phishing links in ' + blackListFilePath2)
