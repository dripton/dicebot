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


def d(dice: int, sides: int) -> Tuple[str, List[int], int]:
    rolls = [random.randint(1, sides) for r in range(dice)]
    total = sum(rolls)
    if rolls:
        result = " + ".join(map(str, rolls)) + " = %d" % total
    else:
        result = ""
    return (result, rolls, total)


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
        elif ch.isdigit() or ch == ".":
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
        elif token[0].isdigit() or token[0] == ".":
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


def rpn_evaluate(output_queue: List[str]) -> float:
    eval_stack = []
    for token in output_queue:
        if token[0].isdigit() or token[0] == ".":
            eval_stack.append(token)
        elif token[0].isalpha():
            # TODO 1-arg vs. 2-arg vs. "d" function  d vs. d6 vs. 3d6 or 4d
            if token[0].lower() == "d":
                arg2 = eval_stack.pop()
                sides = int(arg2)
                arg1 = eval_stack.pop()
                dice = int(arg1)
                result, rolls, total = d(dice, sides)
                # TODO show result
                eval_stack.append(total)
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
            # TODO bogus operator
            eval_stack.append(total)
    return eval_stack[0]


def roll_inner(cmd: str) -> float:
    tokens = list(gen_tokens(cmd))
    output_queue = to_postfix(tokens)
    result = rpn_evaluate(output_queue)
    return result


@bot.command()
async def roll(cmd: str):
    """Rolls dice in roll20 format."""
    print("roll(%s)" % cmd)
    try:
        result = roll_inner(cmd)
    except Exception:
        await bot.say("invalid format")
        return
    print("result", result)
    await bot.say(result)


# Give token on command line
# https://discordapp.com/developers/applications/me to find it
if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot.run(sys.argv[1])
    else:
        print("Must give Discord bot token on command line")
