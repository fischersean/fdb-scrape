import os
import requests as rq
import time


def download_season(season: int) -> str:
    # cookies = {
    # "fsbotchecked": "true"
    # }
    print(f"Downloading data for {season} season...")
    url = f"https://www.footballdb.com/games/index.html?lg=NFL&yr={season}"
    print("\t\t" + url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15"
    }
    res = rq.get(url, headers=headers)
    print(f"Download complete with code {res.status_code}")
    if res.status_code != 200:
        raise ValueError("Error downloading data")
    return res.text


def save_download(name: str, text: str, path: str):
    with open(os.path.join(path, name + ".html"), "w") as f:
        f.write(text)


if __name__ == "__main__":
    fdir = os.path.dirname(__file__)
    for season in range(1978, 2020):
        stime = time.time()
        txt = download_season(season)
        save_download(str(season), txt, os.path.join(fdir, "downloads"))
        if stime - time.time() < 1:
            time.sleep(0.1)
