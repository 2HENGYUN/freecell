import os
import random
from abc import abstractmethod, ABC

import keyboard
from colorama import init, Fore
from keyboard import KeyboardEvent

init()


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


class EmptyCard(Card):
    def __init__(self, h=0):
        super().__init__(None, -1, h)

    def highlight(self):
        return EmptyCard(1)


class Stack(ABC):
    def __init__(self, cards: list[Card]):
        self.cards = cards
        self.focus = False
        self.trigger = False
        self.mode = False

    @staticmethod
    def __print_cards(cards):
        r = []
        cards = cards or [EmptyCard()]
        for i, card in enumerate(cards):
            if i == len(cards) - 1:
                r.append(str(card))
            else:
                lines = str(card).splitlines()
                for line in lines[:2]:
                    r.append(line)

        return r

    def __str__(self):
        cards = self.cards.copy()
        r = []

        on_card = None
        if self.trigger:
            if cards:
                on_card = cards[-1].highlight()
                cards = cards[:-1]

        if self.focus:
            if self.mode:
                cards = cards or [EmptyCard()]
                cards += [EmptyCard().highlight()]
            else:
                if cards:
                    cards[-1] = cards[-1].highlight()
                else:
                    cards = [EmptyCard().highlight()]

        r.extend(Stack.__print_cards(cards or [EmptyCard()]))
        if on_card:
            r.append(str(on_card))
        return "\n".join(r)

    def __repr__(self):
        return self.__str__()

    def append(self, card: Card):
        self.cards.append(card)

    @abstractmethod
    def peek(self) -> Card:
        pass

    @abstractmethod
    def pop(self) -> Card:
        pass

    @abstractmethod
    def push(self, card: Card) -> bool:
        pass


class TableStack(Stack):
    def __init__(self):
        super().__init__([])

    def peek(self) -> Card:
        return self.cards[-1] if self.cards else None

    def pop(self) -> Card:
        return self.cards.pop() if self.cards else None

    def push(self, card: Card) -> bool:
        if self.cards:
            last = self.cards[-1]
            if last.rank != card.rank + 1:
                return False
            if last.suit.cls == card.suit.cls:
                return False
        self.append(card)
        return True


class AStack(Stack):
    def __init__(self, suit: Suit):
        super().__init__([Card(suit, 0)])

    def peek(self) -> Card:
        return self.cards[-1] if len(self.cards) > 1 else None

    def pop(self) -> Card:
        return self.cards.pop() if len(self.cards) > 1 else None

    def push(self, card: Card) -> bool:
        last = self.cards[-1]
        if last.rank != card.rank - 1:
            return False
        if last.suit != card.suit:
            return False
        self.cards.append(card)
        return True


class BStack(Stack):
    def __init__(self):
        super().__init__([])

    def peek(self) -> Card:
        return self.cards[-1] if self.cards else None

    def pop(self) -> Card:
        return self.cards.pop() if self.cards else None

    def push(self, card: Card) -> bool:
        if self.cards:
            return False
        self.cards.append(card)
        return True


class Header:
    def __init__(self, A: list[Stack], B: list[Stack]):
        self.A = A
        self.B = B

    @staticmethod
    def __col(text):
        return f"\033[38;5;240m{text}\033[0m"

    def __str__(self):
        stacks = self.A + self.B
        stacks = [str(stack).splitlines() for stack in stacks]
        m = max([len(stack) for stack in stacks] + [5])
        for stack in stacks:
            for _ in range(m - len(stack)):
                stack.append("         ")

        lines = []
        for i in range(m):
            lines.append(Header.__col(" │ ").join([stack[i] for stack in stacks]))

        up_edge = "┌" + "┬".join(["───────────" for _ in stacks]) + "┐"
        down_edge = "└" + "┴".join(["───────────" for _ in stacks]) + "┘"

        lines = [Header.__col("│ ") + line + Header.__col(" │") for line in lines]
        lines = [Header.__col(up_edge)] + lines + [Header.__col(down_edge)]
        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()


class Table:
    def __init__(self, stacks: list[Stack]):
        self.stacks = stacks

    @staticmethod
    def __col(text):
        return f"\033[38;5;240m{text}\033[0m{Fore.RESET}"

    def __str__(self):
        stacks = [str(stack).splitlines() for stack in self.stacks]
        m = max([len(stack) for stack in stacks] + [23])
        for stack in stacks:
            for _ in range(m - len(stack)):
                stack.append("         ")

        lines = []
        for i in range(m):
            lines.append(Table.__col(" │ ").join([stack[i] for stack in stacks]))

        up_edge = "┌" + "┬".join(["───────────" for _ in stacks]) + "┐"
        down_edge = "└" + "┴".join(["───────────" for _ in stacks]) + "┘"

        lines = [Table.__col("│ ") + line + Table.__col(" │") for line in lines]
        lines = [Table.__col(up_edge)] + lines + [Table.__col(down_edge)]
        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()


class Commands:
    ARROW_UP = 0
    ARROW_DOWN = 1
    ARROW_LEFT = 2
    ARROW_RIGHT = 3
    RESET = 4
    TAB = 5
    ESC = 6
    SPACE = 7
    UNDO = 8


class Game:
    header: Header
    table: Table
    cursor: tuple[int, int]
    pop_card: Card | None
    pop_index: int
    history: list[tuple[int, int]]

    def __init__(self):
        self.__restart()

    def pt(self):
        os.system("clear")
        print()
        print(self.header)
        print(self.table)
        print()

    def pe(self, content):
        print("-----------> Error: " + content)
        print()

    def on(self, event):
        if event == Commands.RESET:
            self.__restart()
        elif event == Commands.TAB:
            self.__handle_tab()
        elif event == Commands.ESC:
            self.__handle_esc()
        elif event in {Commands.ARROW_UP, Commands.ARROW_DOWN, Commands.ARROW_LEFT, Commands.ARROW_RIGHT}:
            self.__handle_arrow(event)
        elif event == Commands.SPACE:
            self.__handle_space()
        elif event == Commands.UNDO:
            self.__handle_undo()

    def __restart(self):
        suits = [Spades, Hearts, Clubs, Diamonds]
        cards = [Card(suit, i + 1) for i in range(13) for suit in suits]
        shuffled = random.sample(cards, len(cards))

        self.header = Header([AStack(suit) for suit in suits], [BStack() for _ in range(4)])
        self.table = Table([TableStack() for _ in range(8)])
        self.cursor = -1, -1
        self.pop_card = None
        self.pop_index = -1
        self.history = []

        i = 0
        for j in range(8):
            k = i + j + 3
            self.table.stacks[j].cards.extend(shuffled[i:k])
            i = k

        self.pt()

    def __get_stacks(self):
        return self.table.stacks + self.header.A + self.header.B

    def __handle_tab(self):
        x, y = self.cursor
        if x < 0 or y < 0:
            return

        cursor = y * 8 + x
        pop_card = self.pop_card
        pop_index = self.pop_index
        stacks = self.__get_stacks()

        if pop_card:
            if pop_index != cursor:
                if not stacks[cursor].push(pop_card):
                    return
                stacks[pop_index].pop()
                self.history.append((pop_index, cursor))
            stacks[pop_index].trigger = False
            self.pop_card = None
            self.pop_index = -1
            for stack in stacks:
                stack.mode = False
        else:
            pop_card = stacks[cursor].peek()
            if not pop_card:
                return
            stacks[pop_index].trigger = False
            self.pop_card = pop_card
            self.pop_index = cursor
            stacks[cursor].trigger = True
            for stack in stacks:
                stack.mode = True

        self.pt()

    def __handle_esc(self):
        pop_card = self.pop_card
        pop_index = self.pop_index
        stacks = self.__get_stacks()

        if not pop_card:
            return
        stacks[pop_index].trigger = False
        self.pop_card = None
        self.pop_index = -1
        for stack in stacks:
            stack.mode = False

        self.pt()

    def __handle_arrow(self, event):
        x, y = self.cursor
        stacks = self.__get_stacks()
        if x >= 0 and y >= 0:
            stacks[y * 8 + x].focus = False
            if event == Commands.ARROW_LEFT:
                x -= 1
            elif event == Commands.ARROW_RIGHT:
                x += 1
            elif event == Commands.ARROW_UP:
                y += 1
            else:
                y -= 1
            if x < 0:
                x = 7
            elif x > 7:
                x = 0
            if y < 0:
                y = 1
            elif y > 1:
                y = 0
        else:
            if event == Commands.ARROW_LEFT:
                x, y = 7, 0
            elif event == Commands.ARROW_RIGHT:
                x, y = 0, 0
            elif event == Commands.ARROW_UP:
                x, y = 0, 0
            else:
                x, y = 0, 1

        stacks[y * 8 + x].focus = True
        self.cursor = x, y

        self.pt()

    def __handle_space(self):
        if self.pop_card:
            return
        for i, b in enumerate(self.table.stacks):
            card = b.peek()
            if card:
                for j, a in enumerate(self.header.A):
                    if a.push(card):
                        b.pop()
                        self.history.append((i, j + 8))
                        self.pt()
                        return
        for i, b in enumerate(self.header.B):
            card = b.peek()
            if card:
                for j, a in enumerate(self.header.A):
                    if a.push(card):
                        b.pop()
                        self.history.append((i + 12, j + 8))
                        self.pt()
                        return

    def __handle_undo(self):
        if self.pop_card:
            return
        if not self.history:
            return
        f, t = self.history.pop()
        stacks = self.__get_stacks()
        card = stacks[t].pop()
        stacks[f].append(card)
        self.pt()


game = Game()

key_map = {
    123: Commands.ARROW_LEFT,
    124: Commands.ARROW_RIGHT,
    125: Commands.ARROW_DOWN,
    126: Commands.ARROW_UP,
    15: Commands.RESET,
    32: Commands.UNDO,
    48: Commands.TAB,
    49: Commands.SPACE,
    53: Commands.ESC,
}


def on_press(event: KeyboardEvent):
    code = event.scan_code
    if code in key_map:
        game.on(key_map.get(code))


keyboard.on_press(on_press)

while True:
    pass
