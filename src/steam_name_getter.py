import requests

def get_steam_game_name(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    try:
        resp = requests.get(url).json()
        if resp[str(appid)]["success"]:
            return resp[str(appid)]["data"]["name"]
    except Exception as e:
        print("Error fetching app name:", e)
    return "Unknown application"
