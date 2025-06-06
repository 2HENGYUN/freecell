from colorama import Fore


class Suit:
    def __init__(self, symbol, color, cls):
        self.symbol = symbol
        self.color = color
        self.cls = cls

    def __str__(self):
        return f"{self.color}{self.symbol}{Fore.RESET}"


Spades = Suit('♠', Fore.BLUE, 0)  # 黑桃 - 黑色
Hearts = Suit('♥', Fore.RED, 1)  # 红心 - 红色
Clubs = Suit('♣', Fore.BLUE, 0)  # 梅花 - 黑色
Diamonds = Suit('♦', Fore.RED, 1)  # 方块 - 红色


class Card:
    def __init__(self, suit: Suit, rank, h=0):
        self.suit = suit
        self.rank = rank
        self.h = h

    def __str__(self):
        rank = self.rank
        if rank == 1:
            rank = 'A'
        elif rank == 11:
            rank = 'J'
        elif rank == 12:
            rank = 'Q'
        elif rank == 13:
            rank = 'K'
        elif 2 <= rank <= 10:
            rank = f'{rank}'
        else:
            rank = ' '

        symbol = self.suit.symbol if self.suit else ' '

        lines = [
            f"┌───────┐",
            f"│ {rank:<4}{symbol} │",
            f"│   {symbol}   │",
            f"│ {symbol}{rank:>4} │",
            f"└───────┘"
        ]
        if self.suit:
            color = self.suit.color
            lines = [f"{color}{line}{Fore.RESET}" for line in lines]

        if self.h == 1:
            lines = [f"\033[7m{line}\033[0m" for line in lines]
        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()

    def highlight(self):
        return Card(self.suit, self.rank, 1)

def edge_col(text):
    return f"\033[38;5;240m{text}\033[0m"