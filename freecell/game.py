import os
import random
import shutil
import time
from abc import abstractmethod, ABC

from colorama import init

from animation import CongratulationAnimation
from common import Card, Suit, Spades, Hearts, Clubs, Diamonds, edge_col

init()

author = "zhengyun"
banner = f"""                                                                                                 
      _______ .______       _______  _______   ______  _______  __       __           __  _      
     |   ____||   _  \     |   ____||   ____| /      ||   ____||  |     |  |         /  \/ |     
     |  |__   |  |_)  |    |  |__   |  |__   |  ,----'|  |__   |  |     |  |        |_/\__/      
     |   __|  |      /     |   __|  |   __|  |  |     |   __|  |  |     |  |                     
     |  |     |  |\  \----.|  |____ |  |____ |  `----.|  |____ |  `----.|  `----.    By:         
     |__|     | _| `._____||_______||_______| \______||_______||_______||_______|     {author[:8]}   
                                                                                                 
                                                                                                 
            [ ↑ ↓ ← → ]: Move Cursor     [ n ]: New Game        [ u ]: Undo                      
            [ Tab ]: Grab / Place Card   [ Esc ]: Cancel Grab   [ Space ]: Auto Sort             
                                                                                                 
                                                                                                 """

conform_tip = """                               Do You Conform To Start A New Game?                               
                                                                                                 
                                                                                                 
                                 [ Esc ]: No          [ n ]: Yes                                 """


class EmptyCard(Card):
    def __init__(self, h=0):
        super().__init__(None, -1, h)

    def highlight(self):
        return EmptyCard(1)


def print_cards(cards):
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


class Stack(ABC):
    def __init__(self, cards: list[Card]):
        self.cards = cards
        self.focus = False
        self.trigger = False
        self.mode = False

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

        r.extend(print_cards(cards or [EmptyCard()]))
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
        self.dummy = Card(suit, 0)
        super().__init__([self.dummy])

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

    def __str__(self):
        cards = [self.cards[-1]]
        r = []

        on_card = None
        if self.trigger:
            if cards:
                on_card = cards[-1].highlight()
                cards = cards[:-1]

        if self.focus:
            if self.mode:
                cards = cards or [self.dummy]
                cards += [EmptyCard().highlight()]
            else:
                if cards:
                    cards[-1] = cards[-1].highlight()
                else:
                    cards = [EmptyCard().highlight()]

        r.extend(print_cards(cards or [self.dummy]))
        if on_card:
            r.append(str(on_card))
        return "\n".join(r)


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

    def __str__(self):
        stacks = self.A + self.B
        stacks = [str(stack).splitlines() for stack in stacks]
        m = max([len(stack) for stack in stacks] + [5])
        for stack in stacks:
            for _ in range(m - len(stack)):
                stack.append(" " * 9)

        lines = []
        for i in range(m):
            lines.append(edge_col(" │ ").join([stack[i] for stack in stacks]))

        up_edge = "┌" + "┬".join(["───────────" for _ in stacks]) + "┐"
        down_edge = "└" + "┴".join(["───────────" for _ in stacks]) + "┘"

        lines = [edge_col("│ ") + line + edge_col(" │") for line in lines]
        lines = [edge_col(up_edge)] + lines + [edge_col(down_edge)]
        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()


class Table:
    def __init__(self, stacks: list[Stack]):
        self.stacks = stacks

    def __str__(self):
        stacks = [str(stack).splitlines() for stack in self.stacks]
        m = max([len(stack) for stack in stacks] + [23])
        for stack in stacks:
            for _ in range(m - len(stack)):
                stack.append(" " * 9)

        lines = []
        for i in range(m):
            lines.append(edge_col(" │ ").join([stack[i] for stack in stacks]))

        up_edge = "┌" + "┬".join(["───────────" for _ in stacks]) + "┐"
        down_edge = "└" + "┴".join(["───────────" for _ in stacks]) + "┘"

        lines = [edge_col("│ ") + line + edge_col(" │") for line in lines]
        lines = [edge_col(up_edge)] + lines + [edge_col(down_edge)]
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


def print_to_screen(lines):
    lines = [edge_col(line) for line in banner.splitlines()] + lines
    up_edge = "┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐"
    down_edge = "└─────────────────────────────────────────────────────────────────────────────────────────────────────┘"
    lines = [
        edge_col(up_edge),
        *[f"{edge_col('│  ')}{line}{edge_col('  │')}" for line in lines],
        edge_col(down_edge),
    ]

    os.system("clear")

    size = shutil.get_terminal_size(fallback=(103, 24))
    columns = size.columns
    bias = (columns - 103) // 2
    print()
    print()
    print()
    print("\n".join([f"{' ' * bias}{line}" for line in lines]))
    print()


def congrats():
    time.sleep(0.5)
    an = CongratulationAnimation()
    for t in range(len(an.timeline)):
        lines = [
            *[" " * 97] * 2,
            *an.get_frame(t),
        ]

        print_to_screen(lines)
        time.sleep(0.05)


def conform_new_game():
    print_to_screen([
        *[" " * 97] * 13,
        *[edge_col(line) for line in conform_tip.splitlines()],
        *[" " * 97] * 18,
    ])


class Game:
    header: Header
    table: Table
    cursor: tuple[int, int]
    pop_card: Card | None
    pop_index: int
    history: list[tuple[int, int]]
    state: int

    def __init__(self):
        self.__restart()

    def __str__(self):
        h = str(self.header)
        t = str(self.table)
        h_title = " ┌───────────────── Foundation ────────────────┐ ┌─────────────────── Buffer ──────────────────┐ "
        t_title = " ┌────────────────────────────────────────── Tableau ──────────────────────────────────────────┐ "

        return f"""{edge_col(h_title)}
{h}
{" " * 97}
{" " * 97}
{edge_col(t_title)}
{t}
{" " * 97}"""

    def __repr__(self):
        return self.__str__()

    def refresh(self):
        print_to_screen(str(self).splitlines())
        r = min([len(a.cards) for a in self.header.A])
        if r == 14:
            self.state = 2
            congrats()

    def on(self, event):
        if self.state == 2:
            if event == Commands.RESET:
                self.__restart()
        elif self.state == 1:
            if event == Commands.RESET:
                self.__restart()
            elif event == Commands.ESC:
                self.state = 0
                self.refresh()
        else:
            if event == Commands.RESET:
                self.state = 1
                conform_new_game()
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
        self.state = 0

        i = 0
        for j in range(8):
            k = i + j + 3
            self.table.stacks[j].cards.extend(shuffled[i:k])
            i = k

        self.refresh()

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

        self.refresh()

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

        self.refresh()

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

        self.refresh()

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
                        self.refresh()
                        return
        for i, b in enumerate(self.header.B):
            card = b.peek()
            if card:
                for j, a in enumerate(self.header.A):
                    if a.push(card):
                        b.pop()
                        self.history.append((i + 12, j + 8))
                        self.refresh()
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
        self.refresh()
