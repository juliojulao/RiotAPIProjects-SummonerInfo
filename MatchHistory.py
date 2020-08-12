from riotwatcher import LolWatcher, ApiError
import pandas as pd
import json
import sys

regions = {
    "na1" :  {"north america", "na", "na1"},
    "euw1" : {"europe west", "eu", "euw1"},
}

def getRegion():
    # Get summoner region
    while True:
        region = input("Enter region: ")
        if region.lower() in regions["na1"]:
            return "na1"
        elif region.lower() in regions["euw1"]:
            return "euw1"
        else:
            print("Invalid region")
            continue

def getSummoner(watcher, region):
    while True:
        try:
            summoner = input("Enter summoner name (leave blank to exit): ")
            if summoner == '':
                break
            return watcher.summoner.by_name(region,summoner)
        except ApiError:
            print("Summoner does not exist in this region")
            continue

def itemName(watcher, item_id):
    if item_id == 0:
        return ""
    return watcher.data_dragon.items('10.16.1')["data"][str(item_id)]["name"]

def ssName(watcher, summs_dict, ss_id):
    for k,v in summs_dict.items():
        if v["key"] == str(ss_id):
            return v["name"]

def championName(watcher, champ_dict, champ_id):
    for k,v in champ_dict.items():
        if v["key"] == str(champ_id):
            return v["name"]

if __name__ == "__main__":
    # global variables
    API_KEY = 'RGAPI-135617b9-af84-4a3c-9dfa-779cce9d25a2'
    watcher = LolWatcher(API_KEY)
    region = getRegion()
    me = getSummoner(watcher, region)
    champ_dict = watcher.data_dragon.champions('10.16.1')["data"]
    summs_dict = watcher.data_dragon.summoner_spells('10.16.1')["data"]

    if me == None:
        sys.exit()

    while True:
        try:
            print("Get information from summoner \"{}\"".format(me["name"]))
            task = int(input(
            "Options: \n" +
            "   1. Get summoner's ranked stats\n" +
            "   2. Get summoner's current match details\n" +
            "   3. Get summoner's last match details\n" +
            "Enter number to perform task (Input 0 to exit): "))
            if task == 1:
                # Return ranked stats
                try:
                    ranked_stats = watcher.league.by_summoner(region, me['id'])[0]
                    print("   Rank: {} {} at {} LP\n".format(ranked_stats["tier"], ranked_stats["rank"], ranked_stats["leaguePoints"]) +
                        "   Wins: {}\n".format(ranked_stats["wins"]) +
                        " Losses: {}".format(ranked_stats["losses"]))
                except IndexError:
                    print("No ranked stats available for this summoner.")
            
            elif task == 2:
                # Return current match details
                try:
                    current_match = watcher.spectator.by_summoner(region,me['id'])
                    json_obj = json.dumps(current_match, indent=4)
                    print(json_obj)
                except ApiError:
                    print("Summoner currently not in a match.")

            elif task == 3:
                # Return last match detail
                my_matches = watcher.match.matchlist_by_account(region, me['accountId'])
                last_match = my_matches['matches'][0]
                match_detail = watcher.match.by_id(region, last_match['gameId'])
                # print(match_detail['participants'])

                participants = []
                for row in match_detail['participants']:
                    participants_row = {}
                    participants_row['SummonerName'] = match_detail[row['participantId']]
                    participants_row['Champion'] = championName(watcher, champ_dict, row['championId'])
                    participants_row['SS1'] = ssName(watcher, summs_dict, row['spell1Id'])
                    participants_row['SS2'] = ssName(watcher, summs_dict, row['spell2Id'])
                    participants_row['Win'] = row['stats']['win']
                    participants_row['K'] = row['stats']['kills']
                    participants_row['D'] = row['stats']['deaths']
                    participants_row['A'] = row['stats']['assists']
                    participants_row['DamageDealt'] = row['stats']['totalDamageDealt']
                    participants_row['Gold'] = row['stats']['goldEarned']
                    participants_row['ChampLvl'] = row['stats']['champLevel']
                    participants_row['CS'] = row['stats']['totalMinionsKilled']
                    participants_row['item0'] = itemName(watcher, row['stats']['item0'])
                    participants_row['item1'] = itemName(watcher, row['stats']['item1'])
                    participants_row['item2'] = itemName(watcher, row['stats']['item2'])
                    participants_row['item3'] = itemName(watcher, row['stats']['item3'])
                    participants_row['item4'] = itemName(watcher, row['stats']['item4'])
                    participants_row['item5'] = itemName(watcher, row['stats']['item5'])
                    participants.append(participants_row)
                df = pd.DataFrame(participants)
                print('\n')
                print(df)
                print('\n')
            
            elif task == 0:
                break
            
            else:
                print("Invalid input.")
        except ValueError:
            print("Please enter a number")