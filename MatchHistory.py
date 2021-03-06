from riotwatcher import LolWatcher, ApiError
from tabulate import tabulate
import pandas as pd
import json, requests
import sys



class Summoner:
    def __init__(self, region, summoner):
        self.region = region
        self.summoner = summoner
        self.ranked_stats = None
        self.current_match = None
        self.recent_matches = None

    def showRank(self):
        if self.ranked_stats == None:
            print("Unranked")
        else:
            print("   Rank: {} {} at {} LP\n".format(self.ranked_stats["tier"], self.ranked_stats["rank"], self.ranked_stats["leaguePoints"]) +
                  "   Wins: {}\n".format(self.ranked_stats["wins"]) +
                  " Losses: {}\n".format(self.ranked_stats["losses"]) +
                  "Winrate: {:.0%}\n".format(self.ranked_stats["wins"] / (self.ranked_stats["wins"] + self.ranked_stats["losses"])))

    def showCurrentMatch(self):
        if self.current_match == None:
            print("Summoner currently not in a match.\n")
        else:
            participants = []
            for row in self.current_match['participants']:
                parts_row = {}
                parts_row['Summoner Name'] = row['summonerName']
                try:
                    rank = getSummonerRank(watcher, region, watcher.summoner.by_name(region,row['summonerName']))
                    parts_row['Rank'] = rank['tier'] + ' ' + rank['rank']
                except TypeError:
                    parts_row['Rank'] = 'Unkranked'
                parts_row['Champion'] = championName(watcher, champ_dict, row['championId'])
                parts_row['Summs 1'] = ssName(watcher, summs_dict, row['spell1Id'])
                parts_row['Summs 2'] = ssName(watcher, summs_dict, row['spell2Id'])
                if row['teamId'] == 100:
                    parts_row['Team'] = 'Blue'
                else:
                    parts_row['Team'] = 'Red'
                participants.append(parts_row)
            df = pd.DataFrame(participants)
            print()
            print(tabulate(df, showindex=False, headers=df.columns))
            print('\n')

    def showLastMatch(self):
        last_match = self.recent_matches['matches'][0]
        match_detail = watcher.match.by_id(region, last_match['gameId'])

        participants = []
        for i,row in enumerate(match_detail['participants']):
            participants_row = {}
            participants_row['Summoner Name'] = match_detail["participantIdentities"][int(row['participantId']-1)]['player']['summonerName']
            participants_row['Champion'] = championName(watcher, champ_dict, row['championId'])
            participants_row['Summ 1'] = ssName(watcher, summs_dict, row['spell1Id'])
            participants_row['Summ 2'] = ssName(watcher, summs_dict, row['spell2Id'])
            if row['stats']['win'] == True:
                participants_row['Win'] = 'Win'
            else:
                participants_row['Win'] = 'Loss'
            participants_row['K'] = row['stats']['kills']
            participants_row['D'] = row['stats']['deaths']
            participants_row['A'] = row['stats']['assists']
            participants_row['Damage Dealt'] = row['stats']['totalDamageDealt']
            participants_row['Gold'] = row['stats']['goldEarned']
            participants_row['Champ Lvl'] = row['stats']['champLevel']
            participants_row['CS'] = row['stats']['totalMinionsKilled']
            participants_row['Item 1'] = itemName(watcher, items_dict, row['stats']['item0'])
            participants_row['Item 2'] = itemName(watcher, items_dict, row['stats']['item1'])
            participants_row['Item 3'] = itemName(watcher, items_dict, row['stats']['item2'])
            participants_row['Item 4'] = itemName(watcher, items_dict, row['stats']['item3'])
            participants_row['Item 5'] = itemName(watcher, items_dict, row['stats']['item4'])
            participants_row['Item 6'] = itemName(watcher, items_dict, row['stats']['item5'])
            participants_row['Trinket'] = itemName(watcher, items_dict, row['stats']['item6'])
            participants.append(participants_row)
        df = pd.DataFrame(participants)
        print()
        print(tabulate(df, showindex=False, headers=df.columns))
        print('\n')

    def showRecentMatches(self):
        last_match = mySummoner.recent_matches['matches'][:3]
        for i in last_match:
            match_detail = watcher.match.by_id(region, i['gameId'])

            participants = []
            for i,row in enumerate(match_detail['participants']):
                participants_row = {}
                # print(row['participantId'], match_detail["participantIdentities"][int(row['participantId']-1)]['participantId'])
                # if int(row['participantId']) ==  match_detail["participantIdentities"][int(row['participantId']-1)]['participantId']:
                participants_row['Summoner Name'] = match_detail["participantIdentities"][int(row['participantId']-1)]['player']['summonerName']
                participants_row['Champion'] = championName(watcher, champ_dict, row['championId'])
                participants_row['Summ 1'] = ssName(watcher, summs_dict, row['spell1Id'])
                participants_row['Summ 2'] = ssName(watcher, summs_dict, row['spell2Id'])
                if row['stats']['win'] == True:
                    participants_row['Win'] = 'Win'
                else:
                    participants_row['Win'] = 'Loss'
                participants_row['K'] = row['stats']['kills']
                participants_row['D'] = row['stats']['deaths']
                participants_row['A'] = row['stats']['assists']
                participants_row['Damage Dealt'] = row['stats']['totalDamageDealt']
                participants_row['Gold'] = row['stats']['goldEarned']
                participants_row['Champ Lvl'] = row['stats']['champLevel']
                participants_row['CS'] = row['stats']['totalMinionsKilled']
                participants_row['Item 1'] = itemName(watcher, items_dict, row['stats']['item0'])
                participants_row['Item 2'] = itemName(watcher, items_dict, row['stats']['item1'])
                participants_row['Item 3'] = itemName(watcher, items_dict, row['stats']['item2'])
                participants_row['Item 4'] = itemName(watcher, items_dict, row['stats']['item3'])
                participants_row['Item 5'] = itemName(watcher, items_dict, row['stats']['item4'])
                participants_row['Item 6'] = itemName(watcher, items_dict, row['stats']['item5'])
                participants_row['Trinket'] = itemName(watcher, items_dict, row['stats']['item6'])
                participants.append(participants_row)
            df = pd.DataFrame(participants)
            print()
            print(tabulate(df, showindex=False, headers=df.columns))
            print('\n')

    def __str__(self):
        return f"Name: {self.summoner}\nRegion: {self.region}\nStats: {self.ranked_stats}\nCurrent Match: {self.current_match}\nRecent Matches: {self.recent_matches}\n"


def getRegion():
    # Get summoner region
    regions = {
        "na1" :  {"north america", "na", "na1"},
        "euw1" : {"europe west", "eu", "euw1"},
    }
    while True:
        region = input("Enter region (leave blank to exit): ")
        if region == '':
            break
        if region.lower() in regions["na1"]:
            return "na1"
        elif region.lower() in regions["euw1"]:
            return "euw1"
        else:
            print("Invalid region")
            continue

def getSummoner(watcher, region):
    # Get summoner name
    while True:
        try:
            summoner = input("Enter summoner name (leave blank to exit): ")
            if summoner == '':
                break
            return watcher.summoner.by_name(region,summoner)
        except ApiError as err:
            if err.response.status_code == 403:
                print("Invalid API key")
                break
            elif err.response.status_code == 404:
                print("Summoner does not exist in this region")
            continue

def getSummonerRank(watcher, region, me):
    ranks = watcher.league.by_summoner(region, me['id'])
    for rank in ranks:
        if rank['queueType'] == 'RANKED_SOLO_5x5':
            return rank
    return None

def itemName(watcher, items_dict, item_id):
    try:
        if item_id == 0:
            return ""
        return items_dict[str(item_id)]['name']
    except KeyError:
        return ""

def ssName(watcher, summs_dict, ss_id):
    for k,v in summs_dict.items():
        if v["key"] == str(ss_id):
            return v["name"]

def championName(watcher, champ_dict, champ_id):
    for k,v in champ_dict.items():
        if v["key"] == str(champ_id):
            return v["name"]

if __name__ == "__main__":
    API_KEY = input('Enter API key: ')
    watcher = LolWatcher(API_KEY)
    patch_version = json.loads(requests.get("https://ddragon.leagueoflegends.com/api/versions.json").content)[0]
    champ_dict = watcher.data_dragon.champions(patch_version)["data"]
    summs_dict = watcher.data_dragon.summoner_spells(patch_version)["data"]
    items_dict = watcher.data_dragon.items(patch_version)["data"]
    while True:
        region = getRegion()
        if region == None:
            sys.exit()
        me = getSummoner(watcher, region)
        if me == None:
            sys.exit()
        mySummoner = Summoner(region, me['name'])

        while True:
            try:
                print("Get information from summoner \"{}\"".format(me["name"]))
                task = int(input(
                "Options: \n" +
                "   1. Get summoner's ranked stats\n" +
                "   2. Get summoner's current match details\n" +
                "   3. Get summoner's last match details\n" +
                "   4. Get summoner's last 3 match details\n" +
                "Enter number to perform task (Input 0 to exit): "))
                if task == 1:
                    # Return ranked stats
                    mySummoner.ranked_stats = getSummonerRank(watcher, region, me)
                    mySummoner.showRank()
                
                elif task == 2:
                    # Return current match details
                    try:
                        mySummoner.current_match = watcher.spectator.by_summoner(region,me['id'])
                    except ApiError:
                        mySummoner.current_match = None
                    mySummoner.showCurrentMatch()

                elif task == 3:
                    # Return last match detail
                    mySummoner.recent_matches = watcher.match.matchlist_by_account(region, me['accountId'])
                    mySummoner.showLastMatch()

                elif task == 4:
                    # Return last 3 match detail
                    mySummoner.recent_matches = watcher.match.matchlist_by_account(region, me['accountId'])
                    mySummoner.showRecentMatches()

                elif task == 5:
                    # Special return for debug
                    print(mySummoner)
                
                elif task == 0:
                    break
                
                else:
                    print("Invalid input.")
            except ValueError:
                print("Please enter a number")
