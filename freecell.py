import os
import random

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
Suits = [Spades, Hearts, Clubs, Diamonds]


class Card:
    def __init__(self, suit: Suit, rank, h=0, b=0):
        self.suit = suit
        self.rank = rank
        self.h = h
        self.b = b

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

        symbol = ' '
        if self.suit:
            symbol = self.suit.symbol

        if self.b:
            lines = [
                f"┏━━━━━━━┓",
                f"┃ {rank:<4}{symbol} ┃",
                f"┃   {symbol}   ┃",
                f"┃ {symbol}{rank:>4} ┃",
                f"┗━━━━━━━┛"
            ]
        else:
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
        # else:
        #     lines = [
        #         *[f"\033[38;5;240m{lines[0]}\033[0m"],
        #         *[
        #             f"\033[38;5;240m{line[:2]}\033[0m\033[7m\033[38;5;240m{line[2:-2]}\033[0m\033[0m\033[38;5;240m{line[-2:]}\033[0m"
        #             for line in lines[1:-1]],
        #         *[f"\033[38;5;240m{lines[-1]}\033[0m"],
        #     ]
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


class Stack:
    def __init__(self, cards: list[Card]):
        self.cards = cards
        self.s = 0
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
                cards += [EmptyCard().highlight()]
            elif cards:
                cards[-1] = cards[-1].highlight()
            else:
                cards = [EmptyCard().highlight()]

        r.extend(Stack.__print_cards(cards or [EmptyCard()]))
        if on_card:
            r.append("         ")
            r.append(str(on_card))
        return "\n".join(r)

    def __repr__(self):
        return self.__str__()


class Header:
    def __init__(self, A: list[Stack], B: list[Stack]):
        self.A = A
        self.B = B

    @staticmethod
    def __col(text):
        return f"\033[38;5;240m{text}\033[0m"

    def __str__(self):
        stacks = self.A + self.B
        stacks = [Stack([stack.cards[-1]] if stack.cards else []) for stack in stacks]
        stacks = [str(stack).splitlines() for stack in stacks]
        m = max([len(stack) for stack in stacks])
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
    def __init__(self, stacks: list[Stack], min_h=0):
        self.stacks = stacks
        self.min_h = min_h

    @staticmethod
    def __col(text):
        return f"\033[38;5;240m{text}\033[0m{Fore.RESET}"

    def __str__(self):
        stacks = [str(stack).splitlines() for stack in self.stacks]
        m = max([len(stack) for stack in stacks] + [self.min_h])
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


class Game:
    header: Header
    table: Table
    cursor: int = -1
    trigger: int = -1

    def __init__(self):
        all_cards = [Card(suit, i + 1) for i in range(13) for suit in Suits]
        shuffled = random.sample(all_cards, len(all_cards))
        stacks = [Stack([]) for _ in range(8)]
        self.header = Header([Stack([Card(suit, 0)]) for suit in Suits], [Stack([]) for _ in range(4)])
        self.table = Table(stacks, 25)

        i = 0
        for j in range(8):
            k = i + j + 3
            stacks[j].cards.extend(shuffled[i:k])
            i = k

        stacks[0].cards = []
        self.pt()

    def pt(self):
        os.system("clear")
        print(self.header)
        print(self.table)
        print()

    def pe(self, content):
        print("-----------> Error: " + content)
        print()

    def on(self, event):
        table = self.table
        header = self.header
        trigger = self.trigger
        cursor = self.cursor

        if event == 'w':
            if trigger < 0 or cursor < 0:
                return
            if trigger != cursor:
                s1 = table.stacks[trigger]
                s2 = table.stacks[cursor]
                if not self.__stack_to_stack(s1, s2):
                    return
                s2.cards.append(s1.cards.pop())
            if trigger >= 0:
                table.stacks[trigger].trigger = False
            self.__change_mode(False)
        elif event == 's':
            if cursor < 0:
                return
            if len(table.stacks[cursor].cards) == 0:
                return
            self.__change_mode(True)
            if trigger >= 0:
                table.stacks[trigger].trigger = False
            if cursor >= 0:
                trigger = cursor
                table.stacks[trigger].trigger = True
        elif event == 'a' or event == 'd':
            d = -1 if event == 'a' else 1
            if cursor >= 0:
                table.stacks[cursor].focus = False
            cursor += d
            if cursor < 0:
                cursor = len(table.stacks) - 1
            if cursor >= len(table.stacks):
                cursor = 0
            table.stacks[cursor].focus = True
        elif 1 <= event <= 4:
            pass
        elif 5 <= event <= 8:
            pass
        self.trigger = trigger
        self.cursor = cursor
        self.pt()

    def __change_mode(self, mode):
        for stack in self.table.stacks:
            stack.mode = mode
        for stack in self.header.A:
            stack.mode = mode
        for stack in self.header.B:
            stack.mode = mode

    @staticmethod
    def __stack_to_stack(s1, s2):
        if s2.cards:
            c1 = s1.cards[-1]
            c2 = s2.cards[-1]
            if c1.rank != c2.rank - 1:
                return False
            if c1.suit.cls == c2.suit.cls:
                return False
        return True

    @staticmethod
    def __stack_to_A(s, a):
        c1 = s.cards[-1]
        c2 = a.cards[-1]
        if c1.rank != c2.rank - 1:
            return False
        if c1.suit.cls != c2.suit.cls:
            return False
        return True


game = Game()


def on_press(event: KeyboardEvent):
    code = event.scan_code
    if 123 <= code <= 126:
        code = ['a', 'd', 's', 'w'][code - 123]
        game.on(code)


# 监听所有按键
keyboard.on_press(on_press)

# 阻塞主线程，直到按下 esc 键
keyboard.wait(7)
