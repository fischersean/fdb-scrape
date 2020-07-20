from pprint import pprint as print
from typing import List, Tuple, Dict, Union
import json
import os
import shutil
import pandas as pd
from bs4 import BeautifulSoup as bs
import uuid

"""
My type-casting in this file is totally fucked
"""


class Game:
    def __init__(
        self,
        date: str,
        hscore: int,
        home: str,
        vscore: int,
        visitor: str,
        OT: bool,
        week: str,
    ):
        self.date = date
        self.hscore = hscore
        self.home = home
        self.vscore = vscore
        self.visitor = visitor
        self.OT = OT
        self.week = week
        self.id = str(uuid.uuid4())

    @classmethod
    def from_row(cls, row: pd.Series):
        # breakpoint()
        return cls(
            date=row["Date"],
            hscore=row["HScore"],
            home=row["Home"],
            vscore=row["VScore"],
            visitor=row["Visitor"],
            OT=row["OT"],
            week=row["Week"],
        )

    def asdict(self) -> dict:
        return {
            "Date": str(self.date),
            "HScore": int(self.hscore),
            "Home": str(self.home),
            "VScore": int(self.vscore),
            "Visitor": str(self.visitor),
            "OT": bool(self.OT),
            "id": self.id,
            "Week": str(self.week),
        }

    def to_json(self) -> str:
        return json.dumps(self.asdict())


class Season:
    def __init__(
        self,
        year: int,
        weeks: List[Dict[str, Union[str, int]]],
        games: List[Game],
    ):
        self.year = year
        self.weeks = weeks
        self.games = games

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        games = []
        year = df["Season"].iloc[0]
        weeks = []
        # breakpoint()
        for i, w in enumerate(df["Week"].unique()):
            weeks.append({"Order": i, "Label": str(w)})

        for _, gm in df.iterrows():
            games.append(Game.from_row(gm))

        return cls(year, weeks, games)

    def asdict(self) -> dict:
        glist = []
        for game in self.games:
            # breakpoint()
            glist.append(game.asdict())

        return {
            "Season": int(self.year),
            "Weeks": self.weeks,
            "Games": glist,
        }

    def to_json(self) -> str:
        return json.dumps(self.asdict())


class GameHistory:
    def __init__(self, seasons: List[Season]):
        self.seasons = seasons

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        rets = []
        uni_seasons = df["Season"].unique()
        for season in uni_seasons:
            rets.append(Season.from_df(df[df["Season"] == season]))

        return cls(seasons=rets)

    def asdict(self) -> dict:
        outlist = []
        for season in self.seasons:
            outlist.append(season.asdict())

        return outlist

    def to_json(self) -> str:
        return json.dumps(self.asdict())


def clean_dates(date):
    return date[0 : 2 + 1 + 2 + 1 + 4]


def parse_team_name(name: str):
    # breakpoint()
    for i in range(len(name) - 1, 0, -1):
        if name[i].islower():
            end_index = i + 1
            break

    return name[0:end_index] + ", " + name[end_index:]


def parse_tbl(season: int):
    fname = os.path.join("./downloads", str(season) + ".html")
    with open(fname, "r") as f:
        soup = bs(f.read(), "html.parser")

    df = pd.DataFrame()
    sdivs = soup.find_all("span", class_="divheader")
    for week, table in zip(sdivs, soup.find_all("table")):
        wkdf = pd.read_html(str(table))[0]
        wkdf["Week"] = week.text
        df = df.append(wkdf, ignore_index=True)

    nmap = {
        "Unnamed: 2": "VScore",
        "Unnamed: 4": "HScore",
        "Unnamed: 5": "Notes",
    }

    df = df.rename(nmap, axis=1)

    df["Season"] = season
    df["Date"] = df["Date"].apply(clean_dates)
    df["Home"] = df["Home"].apply(parse_team_name)
    df["Visitor"] = df["Visitor"].apply(parse_team_name)

    df["OT"] = df["Notes"] == "OT"
    df = df.drop("Notes", axis=1)
    df = df.drop("Box", axis=1)

    return df


def to_models(df: pd.DataFrame) -> GameHistory:
    return GameHistory.from_df(df)


if __name__ == "__main__":
    df = pd.DataFrame()
    for season in range(1978, 2020):
        # for season in range(2010, 2020):
        print(f"Season: {season}")
        _df = parse_tbl(season)
        df = df.append(_df, ignore_index=True)

    seasons = to_models(df)
    # print(seasons.to_json())

    df.to_csv("./exports/gamedata.csv")
    # df.to_json("./exports/combined.json", orient="records")
    with open("./exports/gamedata.json", "w") as f:
        f.write(seasons.to_json())

    # Copy json file to resources dir
