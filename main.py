#!/usr/bin/env python3
import json
import sys
import os.path
import pickle
from collections import Counter
from itertools import chain
from datetime import datetime, timezone, timedelta
from operator import itemgetter

from sudachipy import tokenizer, dictionary
import jaconv

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager

TIMELINE = os.path.join(os.path.dirname(__file__), "timeline.pickle")
TIMEZONE = timezone(timedelta(hours=9), "JST")

matplotlib.rcParams["font.sans-serif"] = ["Hiragino Maru Gothic Pro", "Yu Gothic", "Meirio", "Takao", "IPAexGothic", "IPAPGothic", "VL PGothic", "Noto Sans CJK JP"]

# (ward to plot, line style, color)
RTA_EMOTES = (
    ("rtaClap", "-", "#ec7087"),
    ("rtaPray", "-", "#f7f97a"),
    ("rtaGl", "-", "#5cc200"),
    ("rtaGg", "-", "#ff381c"),
    ("rtaHatena", "-", "#ffb5a1"),
    ("rtaR", "-", "white"),
    ("rtaRedbull", "-", "#1753c8"),
    # ("rtaRedbull2", "-", "#98b0df"),

    ("rtaPog", "-.", "#f8c900"),
    ("rtaCry", "-.", "#5ec6ff"),
    ("rtaHello", "-.", "#ff3291"),
    ("rtaHmm", "-.", "#fcc7b9"),
    ("rtaOko", "-.", "#d20025"),
    # ("rtaWut", "-.", "#d97f8d"),
    # ("rtaChan", "-.", "green"),
    # ("rtaKappa", "-.", "#ffeae2"),
    ("rtaPolice", "-.", "#7891b8"),
    ("rtaKabe", "-.", "#bf927a"),
    ("rtaListen", "-.", "#5eb0ff"),

    # ("rtaPolice", "--", "#7891b8"),
    # ("rtaKabe", "--", "#bf927a"),
    # ("rtaListen", "--", "#5eb0ff"),
    # ("rtaSleep", "--", "#ff8000"),
    # ("rtaCafe", "--", "#a44242"),
    # ("rtaDot", "--", "#ff3291"),

    ("rtaIizo", ":", "#0f9619"),
    ("rtaBanana", ":", "#f3f905"),
    ("rtaShogi", ":", "#c68d46"),
    ("rtaFrameperfect", ":", "#ff7401"),
    ("rtaPixelperfect", ":", "#ffa300"),
    # ("rtaShi", ":", "#8aa0ec"),
    # ("rtaGift", ":", "white"),
    # ("rtaAnkimo", ":", "#f92218")

    ("草", "--", "green"),
    ("無敵時間", "--", "red"),
    ("ファイナル", "--", "gray"),
    ("石油王", "--", "yellow"),
    ("ホットプレート", "--", "orange")
)

# (title, movie start time as timestamp, offset hour, min, sec)
GAMES = (
    ("世界のアソビ大全51", 1609005175, 0, 13, 40),
    ("剣神ドラゴンクエスト 甦りし伝説の剣", 1609005175, 2, 0, 54),
    ("ドラゴンクエスト3", 1609005175, 4, 2, 26),
    ("ロマンシング サガ3 HDリマスター版", 1609005175, 4, 51, 46),
    ("メタルマックス", 1609005175, 7, 47, 17),
    ("メタルマックスゼノリボーン", 1609005175, 8, 47, 47),
    ("テンミリオン", 1609005175, 10, 29, 41),
    ("Terraria", 1609005175, 11, 6, 54),
    ("四字熟語Flash", 1609005175, 11, 47, 46),
    ("人生オワタの\n大冒険2", 1609005175, 12, 15, 48),
    ("ティンクルスター\nスプライツ", 1609005175, 12, 41, 43),
    ("秘封ナイトメアダイアリー 〜 Violet Detector.", 1609005175, 13, 10, 41),
    ("Tetris Effect", 1609005175, 14, 50, 9),
    ("I.Q FINAL", 1609005175, 15, 39, 51),
    ("XI JUMBO", 1609005175, 16, 23, 45),
    ("The Typing of the Dead 2004", 1609005175, 17, 45, 37),
    ("ジ・ウーズ", 1609005175, 18, 50, 33),
    ("心霊呪殺師 太郎丸", 1609005175, 19, 54, 50),
    ("マリオアーティスト\nポリゴンスタジオ", 1609005175, 20, 36, 29),
    (".hack//G.U. Last Recode", 1609005175, 21, 41, 17),
    ("ファイナルファンタジーXIII", 1609005175, 24, 40, 25),
    ("DARK SOULS REMASTERED", 1609005175, 29, 50, 48),
    ("Salt and Sanctuary", 1609115920, 0, 4, 58),
    ("マリーのアトリエplus", 1609115920, 0, 51, 6),
    ("FINAL FANTASY XV ROYAL EDITION", 1609115920, 2, 3, 51),
    ("Kingdom Hearts II Final Mix", 1609115920, 3, 3, 28),
    ("イース セルセタの樹海", 1609115920, 6, 23, 37),
    ("MOTHER2", 1609115920, 7, 32, 45),
    ("星のカービィ ウルトラスーパーデラックス", 1609115920, 11, 48, 11),
    ("カービィの\nすいこみ大作戦", 1609115920, 13, 9, 27),
    ("ファイアーエムブレム 烈火の剣", 1609115920, 13, 45, 17),
    ("ASTRAL CHAIN", 1609115920, 15, 21, 29),
    ("F-ZERO GX", 1609115920, 18, 23, 54),
    ("ロックマン バトル＆チェイス", 1609115920, 19, 2, 38),
    ("ボンバーマン'94", 1609115920, 20, 9, 25),
    ("妖怪ウォッチ", 1609115920, 21, 3, 13),
    ("おねがいマイメロディ\n夢の国の大冒険", 1609115920, 23, 55, 27),
    ("Yono and the\nCelestial Elephants", 1609115920, 24, 41, 35),
    ("キョロちゃん\nランド", 1609115920, 25, 38, 42),
    ("Gunman Clive", 1609115920, 26, 9, 38),
    ("高速廻転寿司", 1609115920, 26, 39, 58),
    ("突然！マッチョマン", 1609115920, 27, 7, 5),
    ("吉野家", 1609115920, 27, 51, 47),
    ("シャーロック\nホームズ\n伯爵令嬢誘拐事件", 1609115920, 28, 53, 31),
    ("ファイナルソード", 1609115920, 29, 31, 35),
    ("ゼルダの伝説\n時のオカリナ", 1609115920, 30, 45, 7),
    ("ルイージ\nマンション", 1609115920, 31, 33, 14),
    ("ゼルダの伝説ふしぎの木の実大地の章", 1609115920, 32, 2, 47),
    ("ポケットモンスター ブラック・ホワイト", 1609115920, 33, 19, 54),
    ("ソニック\nザ\nヘッジホッグ", 1609115920, 36, 54, 50),
    ("ソニックと暗黒の騎士", 1609115920, 37, 28, 49),
    ("テイルコンチェルト", 1609115920, 38, 23, 1),
    ("No Straight Roads", 1609115920, 40, 0, 48),
    ("神巫女 -カミコ-", 1609115920, 40, 39, 36),
    ("Warriors\nof\nFate", 1609115920, 41, 16, 49),
    ("マジックソード", 1609115920, 42, 26, 18),
    ("所さんの\nまもるも\nせめるも", 1609269995, 0, 11, 4),
    ("ジェットセットラジオ", 1609269995, 0, 41, 9),
    ("KORG Gadget\nfor Nintendo Switch", 1609269995, 2, 6, 7),
    ("PC\nBuilding\nSimulator", 1609269995, 2, 50, 8),
    ("鉄騎", 1609269995, 3, 15, 3),
    ("VAMPIRE KILLER", 1609269995, 4, 41, 57),
    ("真・女神転生", 1609289847, 0, 14, 13),
    ("LIVE A LIVE", 1609299079, 0, 0, 41),
    ("クロックタワートリロジーリレー", 1609299079, 1, 18, 11),
    ("DevilMayCry5", 1609299079, 4, 11, 32),
    ("バイオハザード3", 1609299079, 6, 3, 37),
    ("サイレントヒル2", 1609299079, 7, 29, 57),
    ("ヨッシークラフトワールド", 1609299079, 9, 4, 56),
    ("深世海 Into The Depths", 1609341724, 0, 4, 51),
    ("DARK SOULS\nREMASTERED", 1609341724, 1, 41, 1),
    ("朧村正", 1609341724, 2, 18, 2),
    ("鬼武者", 1609341724, 3, 54, 50),
    ("New\nスーパーマリオ\nブラザーズ", 1609341724, 5, 7, 8),
    ("Momodora\n月下のレクイエム", 1609341724, 5, 46, 20),
    ("がんばれゴエモン3 獅子重禄兵衛のからくり卍固め", 1609341724, 6, 22, 50),
    ("Jump King", 1609341724, 7, 58, 53),
    ("カイザーナックル", 1609341724, 8, 35, 23),
    ("スーパーマリオランドトリロジーリレー", 1609341724, 9, 24, 50),
    ("ゼルダの伝説\nブレスオブザワイルド", 1609341724, 10, 56, 55)
)
GAMES = tuple((name, datetime.fromtimestamp(t + h * 3600 + m * 60 + s)) for name, t, h, m, s in GAMES)

WINDOWSIZE = 1
WINDOW = timedelta(minutes=WINDOWSIZE)
DPI = 200
ROW = 4
PAGES = 4
YMAX = 450
WIDTH = 3840
HEIGHT = 2160

FONT_COLOR = "white"
FRAME_COLOR = "#ffff79"
BACKGROUND_COLOR = "#352319"
FACE_COLOR = "#482b1e"


class Message:
    _tokenizer = dictionary.Dictionary().create()
    _mode = tokenizer.Tokenizer.SplitMode.C
    _timezone = TIMEZONE

    # 例外処理する固有名詞
    pns = ("無敵時間", "超カッコいい", "stonec7FioGG", "stonec7Macho", "stonec7Shachi",
           "4Head", "ArgieB8", "Mau5", "MercyWing1", "MercyWing2", "Squid1",
           "Squid2", "Squid3", "Squid4", "TF2John", "rtaRedbull2",
           "石油王", "納期のテーマ", "キョロちゃん", "タイガー先生")

    # 含まれていたら処理しない
    sub = (" gifted a Tier ", " is gifting ", " subscribed at ", " shared rewards to ",
           " subscribed with Prime", "converted from a Prime sub to")

    @classmethod
    def _tokenize(cls, text):
        return cls._tokenizer.tokenize(text, cls._mode)

    def __init__(self, author, message, time_in_seconds, time_text, timestamp):
        self.msg = set()
        self.datetime = datetime.fromtimestamp(timestamp // 1000000).replace(tzinfo=self._timezone)

        message = jaconv.h2z(message)

        for t in self.sub:
            if t in message:
                return

        for pn in self.pns:
            if pn in message:
                self.msg.add(pn)
                message = message.replace(pn, '')

        message = ' '.join(m for m in message.split() if not m.startswith("http"))

        # (名詞 or 動詞) (+助動詞)を取り出す
        parts = []
        currentpart = None
        for m in self._tokenize(message):
            part = m.part_of_speech()[0]

            if currentpart:
                if part == "助動詞":
                    parts.append(m.surface())
                else:
                    self.msg.add(''.join(parts))
                    parts = []
                    if part in ("名詞", "動詞"):
                        currentpart = part
                        parts.append(m.surface())
                    else:
                        currentpart = None
            else:
                if part in ("名詞", "動詞"):
                    currentpart = part
                    parts.append(m.surface())

        if parts:
            self.msg.add(''.join(parts))

    def __len__(self):
        return len(self.msg)


def _parse_chat(paths):
    messages = []
    for p in paths:
        with open(p) as f:
            for d in json.load(f):
                messages.append(Message(**d))

    timeline = []
    currentwindow = messages[0].datetime.replace(second=0) + WINDOW
    _messages = []
    for m in messages:
        if m.datetime <= currentwindow:
            _messages.append(m)
        else:
            timeline.append((currentwindow, Counter(_ for _ in chain(*(m.msg for m in _messages)))))
            currentwindow = m.datetime.replace(second=0) + WINDOW
            _messages = [m]
    if _messages:
        timeline.append((currentwindow, Counter(_ for _ in chain(*(m.msg for m in _messages)))))

    return timeline


def _load_timeline(paths):
    if os.path.exists(TIMELINE):
        with open(TIMELINE, "rb") as f:
            timeline = pickle.load(f)
    else:
        timeline = _parse_chat(paths)
        with open(TIMELINE, "wb") as f:
            pickle.dump(timeline, f)

    return timeline


def _save_counts(timeline):
    _, counters = zip(*timeline)

    counter = Counter()
    for c in counters:
        counter.update(c)

    with open("words.tab", 'w') as f:
        for w, c in sorted(counter.items(), key=itemgetter(1), reverse=True):
            print(w, c, sep='\t', file=f)


def _plot(timeline):
    for npage in range(1, 1 + PAGES):
        chunklen = int(len(timeline) / PAGES / ROW)

        fig = plt.figure(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)
        fig.patch.set_facecolor(BACKGROUND_COLOR)
        plt.rcParams["savefig.facecolor"] = BACKGROUND_COLOR
        plt.subplots_adjust(left=0.07, bottom=0.05, top=0.92)

        for i in range(1, 1 + ROW):
            nrow = i + ROW * (npage - 1)
            f, t = chunklen * (nrow - 1), chunklen * nrow
            x, y = zip(*timeline[f:t])
            _x = tuple(t.replace(tzinfo=None) for t in x)

            ax = fig.add_subplot(ROW, 1, i)
            _plot_row(ax, _x, y, i == 1)

        fig.suptitle(f"RTA in Japan 2020 チャット頻出スタンプ・単語 ({npage}/{PAGES})",
                     color=FONT_COLOR, size="x-large")
        fig.text(0.03, 0.5, "単語 / 分 （同一メッセージ内の重複単語は除外）",
                 ha="center", va="center", rotation="vertical", color=FONT_COLOR, size="large")
        fig.savefig(f"{npage}.png", dpi=DPI)
        plt.close()


def _plot_row(ax, x, y, add_legend):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M", tz=TIMEZONE))
    ax.set_facecolor(FACE_COLOR)
    for axis in ("top", "bottom", "left", "right"):
        ax.spines[axis].set_color(FRAME_COLOR)

    ax.tick_params(colors=FONT_COLOR)
    ax.set_ylim(0, YMAX)

    for name, point in GAMES:
        if x[0] <= point <= x[-1]:
            ax.axvline(x=point, color=FRAME_COLOR, linestyle=":")
            ax.annotate(name, xy=(point, YMAX), xytext=(point, YMAX * 0.9), verticalalignment="top",
                        color=FONT_COLOR, arrowprops=dict(facecolor=FRAME_COLOR, shrink=0.05))

    for e, style, color in RTA_EMOTES:
        _y = tuple(c[e] / WINDOWSIZE for c in y)
        if not sum(_y):
            continue
        ax.plot(x, _y, label=e, linestyle=style, color=(color if color else None))

    if add_legend:
        leg = ax.legend(facecolor="None", frameon=False, bbox_to_anchor=(1.015, 1), loc="upper left")
        for text in leg.get_texts():
            text.set_color(FONT_COLOR)


def _main():
    timeline = _load_timeline(sys.argv[1:])
    _save_counts(timeline)
    _plot(timeline)


if __name__ == "__main__":
    _main()
