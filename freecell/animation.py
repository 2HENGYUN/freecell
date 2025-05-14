from common import Spades, Card, Suit, Hearts, Clubs, Diamonds, edge_col

congrats = """                                                                                                 
                                                                                                 
                                                                                                 
                                                                                                 
   ______   ______   .__   __.   _______ .______          ___   .___________.    _______.    __  
  /      | /  __  \  |  \ |  |  /  _____||   _  \        /   \  |           |   /       |   |  | 
 |  ,----'|  |  |  | |   \|  | |  |  __  |  |_)  |      /  ^  \ `---|  |----`  |   (----`   |  | 
 |  |     |  |  |  | |  . `  | |  | |_ | |      /      /  /_\  \    |  |        \   \       |  | 
 |  `----.|  `--'  | |  |\   | |  |__| | |  |\  \----./  _____  \   |  |    .----)   |      |__| 
  \______| \______/  |__| \__|  \______| | _| `._____/__/     \__\  |__|    |_______/       (__) 
                                                                                                 
                                                                                                 
                                                                                                 
                                                                                                 
       ____    ____  ______    __    __     ____    __    ____  ______   .__   __.     __        
       \   \  /   / /  __  \  |  |  |  |    \   \  /  \  /   / /  __  \  |  \ |  |    |  |       
        \   \/   / |  |  |  | |  |  |  |     \   \/    \/   / |  |  |  | |   \|  |    |  |       
         \_    _/  |  |  |  | |  |  |  |      \            /  |  |  |  | |  . `  |    |  |       
           |  |    |  `--'  | |  `--'  |       \    /\    /   |  `--'  | |  |\   |    |__|       
           |__|     \______/   \______/         \__/  \__/     \______/  |__| \__|    (__)       
                                                                                                 
                                                                                                 
                                                                                                 
                                                                                                 
                                                                                                 """

tip = "                                Press [ n ] To Start New Game ...                                "


def get_frame_index(timeline, t):
    l = len(timeline)
    i = t if 0 <= t < l else 0 if t < 0 else l - 1
    return timeline[i]


class StackSparkleAnimation:
    def __init__(self, suit: Suit):
        card = Card(suit, 13)
        self.last = str(card).splitlines()
        self.last_h = str(card.highlight()).splitlines()

    def get_frame(self, t) -> list[str]:
        return self.last_h if t % 2 == 0 else self.last


class StacksSparkleAnimation:
    def __init__(self, suits: list[Suit], offset=0):
        self.ssas = [StackSparkleAnimation(suit) for suit in suits]
        self.offset = offset

    def get_frame(self, t) -> list[str]:
        frames = [ssa.get_frame(t) for ssa in self.ssas]
        m = max([len(frame) for frame in frames])

        lines = []
        for i in range(m):
            line = []
            for frame in frames:
                if len(frame) > i:
                    line.append(frame[i])
                else:
                    line.append(" " * 9)
            lines.append("   ".join(line))
        offset = self.offset
        lines = [" " * (26 - offset) + line + " " * (26 + offset) for line in lines]
        return lines


class StacksTranslateAnimation:
    def __init__(self, suits: list[Suit]):
        cards = [Card(suit, 13) for suit in suits]
        cards = [str(card.highlight()).splitlines() for card in cards]
        m = max([len(card) for card in cards])

        self.lines = []
        for i in range(m):
            line = []
            for card in cards:
                if len(card) > i:
                    line.append(card[i])
                else:
                    line.append(" " * 9)
            self.lines.append("   ".join(line))
        self.timeline = [i for i in range(9)]

    def get_frame(self, t) -> list[str]:
        return self.__get_frame(get_frame_index(self.timeline, t))

    def __get_frame(self, frame_index) -> list[str]:
        offset = (8 - frame_index) * 3
        return [" " * (26 - offset) + line + " " * (26 + offset) for line in self.lines]


class StackUnfoldAnimation:
    def __init__(self, suit: Suit):
        self.cards = [Card(suit, i + 1) for i in range(13)]
        self.last = str(self.cards[-1]).splitlines()
        self.last_h = str(self.cards[-1].highlight()).splitlines()
        self.timeline = [t for t in range(26)] + [25 - t for t in range(26)]

    def get_frame(self, t) -> list[str]:
        return self.__get_frame(get_frame_index(self.timeline, t))

    def __get_frame(self, frame_index) -> list[str]:
        card_strs = [str(card).splitlines() for card in self.cards[:-1]]

        i = frame_index // 2
        j = frame_index % 2

        if i < 0:
            return []
        else:
            lines = []
            for k, card in enumerate(card_strs):
                if k < i:
                    lines.extend(card[:2])
                elif k == i:
                    lines.extend(card[:j])

            if i < 13:
                lines.extend(self.last_h)
            else:
                lines.extend(self.last)
            return lines


class StacksUnfoldAnimation:
    def __init__(self, suits: list[Suit]):
        self.suas = [StackUnfoldAnimation(suit) for suit in suits]
        self.base = [i for i in range(61)] + [(60 - i) for i in range(61)]
        self.timeline = []
        t = 0
        for i in range(23):
            t += i // 2
            self.timeline.append(t)

    def get_frame(self, t) -> list[str]:
        return self.__get_frame(get_frame_index(self.base, t))

    def __get_frame(self, frame_index) -> list[str]:
        frames = []
        for i, sua in enumerate(self.suas):
            s_t = frame_index - (3 - i) * 4
            frames.append(sua.get_frame(s_t))

        m = max([len(frame) for frame in frames])

        lines = []
        for i in range(m):
            line = []
            for frame in frames:
                if len(frame) > i:
                    line.append(frame[i])
                else:
                    line.append(" " * 9)
            lines.append("   ".join(line))
        lines = [" " * 26 + line + " " * 26 for line in lines]
        return lines


class CongratulationAnimation:
    def __init__(self):
        suits = [Spades, Hearts, Clubs, Diamonds]
        self.ssa1 = StacksSparkleAnimation(suits, 24)
        self.ssa2 = StacksSparkleAnimation(suits)
        self.sua = StacksUnfoldAnimation(suits)
        self.sta = StacksTranslateAnimation(suits)
        self.timeline = [
            *([-1] * 3),
            *([-1, -1, -1, -2, -2, -2] * 3),
            *[i - 20000 for i in self.sta.timeline],
            *([10002] * 6),
            *self.sua.timeline,
            *[10002, 10002, 10002, 10001, 10001, 10001],
            99999999999,
        ]

    def get_frame(self, t) -> list[str]:
        return self.__get_frame(get_frame_index(self.timeline, t))

    def __get_frame(self, frame_index) -> list[str]:
        if frame_index < 0:
            if frame_index < -10000:
                lines = self.sta.get_frame(frame_index + 20000)
            else:
                lines = self.ssa1.get_frame(frame_index)
        else:
            if frame_index > 10000:
                lines = self.ssa2.get_frame(frame_index)
            else:
                lines = self.sua.get_frame(frame_index)
            lines.extend([edge_col(line) for line in congrats.splitlines()])
            if frame_index == 99999999999:
                lines.append(edge_col(tip))
        delta = 35 - len(lines)
        if delta > 0:
            lines += [" " * 97] * delta
        elif delta < 0:
            lines = lines[:delta]
        return lines
