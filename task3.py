#INSTRUCCIONES DE SUBIDA
#To submit the solution  you need to send an e-mail
#to **p.lebedev@itransition.com** with the following:
#1. a link to a video demonstrating launch with different parameters
# (4 identical dice `1,2,3,4,5,6 1,2,3,4,5,6 1,2,3,4,5,6 1,2,3,4,5,6`
# as well as 3 dice `2,2,4,4,9,9 1,1,6,6,8,8 3,3,5,5,7,7`),
# launch with incorrect parameters
# (no dice; 2 dice; invalid number of sides; non-integer value in the dice configuration),
# help table with probabilities (on 3 dice from the example),
# whole game played with the output of results (at least 2 runs);

#2. a link to the Github public repository.

import sys
import hmac
import hashlib
import secrets
from tabulate import tabulate


class ParseoDado:
    @staticmethod
    def parse_dice(args):
        if len(args) < 3:
            raise ValueError("WRONG, you gotta throw at least 3 dice values, come on!")

        dice = []
        for arg in args:
            try:
                values = list(map(int, arg.split(',')))
                if len(values) != 6:
                    raise ValueError
                dice.append(Dice(values))
            except ValueError:
                raise ValueError(
                    f"Invalid dice configuration: {arg}. Each die needs exactly 6 numbers!"
                )
        return dice

class Dice:
    def __init__(self, values):
        self.values = values

    def roll(self):
        return secrets.choice(self.values)

class FairRandomGenerator:
    def __init__(self):
        self.key = None

    def generate_random_with_hmac(self, range_end):
        self.key = secrets.token_bytes(32)  # 256 bits
        value = secrets.randbelow(range_end)
        message = str(value).encode()
        hmac_value = hmac.new(self.key, message, hashlib.sha3_256).hexdigest()
        return value, hmac_value

    def reveal_key(self):
        return self.key.hex()

class ProbabilityCalculator:
    @staticmethod
    def calculate(dice_list):
        probabilities = []
        for i, dice_a in enumerate(dice_list):
            row = []
            for j, dice_b in enumerate(dice_list):
                if i == j:
                    row.append("-")
                else:
                    wins = 0
                    for a in dice_a.values:
                        for b in dice_b.values:
                            if a > b:
                                wins += 1
                    total = len(dice_a.values) * len(dice_b.values)
                    row.append(f"{(wins / total) * 100:.2f}%")
            probabilities.append(row)
        return probabilities

class ProbabilityTable:
    @staticmethod
    def display(dice_list):
        headers = [f"Dice {i}" for i in range(len(dice_list))]
        probabilities = ProbabilityCalculator.calculate(dice_list)
        print(tabulate(probabilities, headers=headers, showindex="always", tablefmt="grid"))

class CLIManager:
    @staticmethod
    def prompt_selection(options):
        while True:
            for idx, option in enumerate(options):
                print(f"{idx} - {option}")
            print("X - Exit the game, bye!")
            print("? - Win probabilities,!")
            selection = input("What's your pick? ").strip().lower()

            if selection == "?":
                return "help"
            elif selection == "x":
                return "exit"
            elif selection.isdigit() and 0 <= int(selection) < len(options):
                return int(selection)
            else:
                print("Yo, that ain't it. Try again.")

class DiceGame:
    def __init__(self, dice_list):
        self.dice_list = dice_list
        self.fair_random = FairRandomGenerator()

    def determine_first_move(self):
        computer_value, hmac_value = self.fair_random.generate_random_with_hmac(2)
        print(f"I picked a random value between 0 and 1 (HMAC={hmac_value}).")
        print("Now, guess what I picked!")

        user_guess = CLIManager.prompt_selection(["0", "1"])
        if user_guess == "exit":
            sys.exit("You bailed. See ya!")

        print(f"My pick: {computer_value} (KEY={self.fair_random.reveal_key()}).")
        return computer_value

    def play(self):
        print("Time to pick your dice, let's go:")

        computer_dice_index = secrets.randbelow(len(self.dice_list))
        computer_dice = self.dice_list[computer_dice_index]
        print(f"I chose the dice {computer_dice.values}.")
        self.dice_list.pop(computer_dice_index)

        user_dice_index = CLIManager.prompt_selection(
            [str(dice.values) for dice in self.dice_list]
        )
        if user_dice_index == "exit":
            sys.exit("You bailed. Later!")
        elif user_dice_index == "help":
            ProbabilityTable.display(self.dice_list)
            return self.play()

        user_dice = self.dice_list[user_dice_index]
        print(f"You picked the dice {user_dice.values}. Nice choice!")

        print("Okay, my throw's coming up!")
        computer_value, hmac_value = self.fair_random.generate_random_with_hmac(len(computer_dice.values))
        print(f"I chose a random number in the range 0..{len(computer_dice.values) - 1} (HMAC={hmac_value}).")

        user_number = CLIManager.prompt_selection([str(i) for i in range(len(computer_dice.values))])
        if user_number == "exit":
            sys.exit("You bailed. See ya!")

        result = (computer_value + user_number) % len(computer_dice.values)
        print(f"My number is {computer_value} (KEY={self.fair_random.reveal_key()}).")
        print(f"The result is {computer_value} + {user_number} = {result} (mod {len(computer_dice.values)}).")
        print(f"My roll is {computer_dice.values[result]}.")

        print("Your turn to roll now!")
        computer_value, hmac_value = self.fair_random.generate_random_with_hmac(len(user_dice.values))
        print(f"I chose a random number in the range 0..{len(user_dice.values) - 1} (HMAC={hmac_value}).")

        user_number = CLIManager.prompt_selection([str(i) for i in range(len(user_dice.values))])
        if user_number == "exit":
            sys.exit("You bailed. See ya!")

        result = (computer_value + user_number) % len(user_dice.values)
        print(f"My number is {computer_value} (KEY={self.fair_random.reveal_key()}).")
        print(f"The result is {computer_value} + {user_number} = {result} (mod {len(user_dice.values)}).")
        print(f"Your roll is {user_dice.values[result]}.")

        user_throw = user_dice.values[result]
        computer_throw = computer_dice.values[result]
        if user_throw > computer_throw:
            print(f"You win! ({user_throw} > {computer_throw})! 🎉")
        else:
            print(f"I win! ({computer_throw} > {user_throw})! Better luck next time! 😎")


if __name__ == "__main__":
    try:
        dice = ParseoDado.parse_dice(sys.argv[1:])
        game = DiceGame(dice)
        first_move = game.determine_first_move()
        if first_move == 0:
            print("Alright, I'm going first!")
        else:
            print("Looks like you're making the first move, let's go!")
        game.play()
    except ValueError as e:
        print(f"Error: {e}")
        print("Usage example: python game.py 2,2,4,4,9,9 6,8,1,1,8,6 7,5,3,7,5,3")
