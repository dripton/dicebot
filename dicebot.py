#!/usr/bin/env python3

import random
import sys
from typing import List, Tuple

import discord
from discord.ext import commands

description = "Dice rolling bot"""

bot = commands.Bot(command_prefix="/", description=description)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


def d(dice: int, sides: int) -> List[int]:
    rolls = [random.randint(1, sides) for r in range(dice)]
    return rolls


def is_number(st: str) -> bool:
    if not st:
        return False
    for ch in st:
        if ch != "." and not ch.isdigit():
            return False
    return True


def gen_tokens(cmd: str):
    """Yield tokens."""
    in_whitespace = False
    in_number = False
    in_alpha = False
    partial = ""
    for ii, ch in enumerate(cmd):
        if ch.isspace():
            if in_whitespace:
                partial += ch
            else:
                if partial:
                    yield partial
                in_whitespace = True
                in_number = False
                in_alpha = False
                partial = ch
        elif is_number(ch):
            if in_number:
                partial += ch
            else:
                if partial:
                    yield partial
                in_number = True
                in_whitespace = False
                in_alpha = False
                partial = ch
        elif ch.isalpha():
            if in_alpha:
                partial += ch
            else:
                if partial:
                    yield partial
                in_alpha = True
                in_whitespace = False
                in_number = False
                partial = ch
        else:
            if partial:
                yield partial
                partial = ""
            in_alpha = False
            in_whitespace = False
            in_number = False
            yield ch
    if partial:
        yield partial


def strip_whitespace(tokens: List[str]) -> List[str]:
    return [token for token in tokens if not token.isspace()]


def add_missing_numbers(tokens: List[str]) -> List[str]:
    """Add extra numbers before and after "d" tokens, if missing.

    If no number before "d", add a "1"
    If no number after "d", add a "6"
    """
    result = []
    for ii, token in enumerate(tokens):
        if token == "d" or token == "D":
            if ii == 0 or not is_number(tokens[ii - 1]):
                result.append("1")
            result.append("d")
            if ii == len(tokens) - 1 or not is_number(tokens[ii + 1]):
                result.append("6")
        else:
            result.append(token)
    return result


operators = {
    "*": 3,
    "/": 3,
    "+": 2,
    "-": 2,
}


def to_postfix(tokens: List[str]) -> List[str]:
    """ https://en.wikipedia.org/wiki/Shunting-yard_algorithm """
    output_queue = []
    operator_stack = []
    for token in tokens:
        if token[0].isspace():
            pass
        elif is_number(token):
            output_queue.append(token)
        elif token[0].isalpha():
            operator_stack.append(token)
        elif token[0] in operators:
            precedence = operators[token[0]]
            while operator_stack and (
                    operator_stack[-1][0].isalpha() or
                    operators.get(operator_stack[-1], 0) >= precedence):
                operator = operator_stack.pop()
                output_queue.append(operator)
            operator_stack.append(token)
        elif token == "(":
            operator_stack.append(token)
        elif token == ")":
            while operator_stack and operator_stack[-1] != "(":
                operator = operator_stack.pop()
                output_queue.append(operator)
            if operator_stack and operator_stack[-1] == "(":
                operator_stack.pop()
                # else mismatched parentheses
    while operator_stack:
        operator = operator_stack.pop()
        output_queue.append(operator)
    return output_queue


def to_number(arg):
    if isinstance(arg, str):
        if "." in arg:
            return float(arg)
        else:
            return int(arg)
    return arg


def rpn_evaluate(output_queue: List[str]) -> Tuple[List[List[int]], float]:
    eval_stack = []
    details = []
    for token in output_queue:
        if is_number(token):
            eval_stack.append(to_number(token))
        elif token[0].isalpha():
            if token[0].lower() == "d":
                arg2 = eval_stack.pop()
                sides = int(arg2)
                arg1 = eval_stack.pop()
                dice = int(arg1)
                rolls = d(dice, sides)
                details.append(rolls)
                eval_stack.append(sum(rolls))
            else:
                raise Exception("bogus function")
        elif token in operators:
            arg2 = to_number(eval_stack.pop())
            arg1 = to_number(eval_stack.pop())
            if token == "+":
                total = arg1 + arg2
            elif token == "-":
                total = arg1 - arg2
            elif token == "*":
                total = arg1 * arg2
            elif token == "/":
                total = arg1 / arg2
            eval_stack.append(total)
    return (details, eval_stack[0])


def roll_inner(cmd: str) -> Tuple[List[List[int]], float]:
    tokens = list(gen_tokens(cmd))
    tokens = strip_whitespace(tokens)
    tokens = add_missing_numbers(tokens)
    output_queue = to_postfix(tokens)
    result = rpn_evaluate(output_queue)
    return result


@bot.command()
async def roll(cmd: str):
    """Rolls dice in roll20 format.  Example: /roll 3d6+2"""
    print("roll(%s)" % cmd)
    try:
        roll_lists, total = roll_inner(cmd)
    except Exception:
        await bot.say("invalid format")
        return
    roll_strs = []
    for roll_list in roll_lists:
        roll_strs.append("+".join(map(str, roll_list)))
    result = ",".join(roll_strs) + " = " + str(total)
    print("result", result)
    await bot.say(result)


# Give token on command line
# https://discordapp.com/developers/applications/me to find it
if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot.run(sys.argv[1])
    else:
        print("Must give Discord bot token on command line")
