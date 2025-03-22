import sys
import time
import json
import os
import pyautogui
import random
from humancursor import SystemCursor

cursor = SystemCursor()
json_file_path = "play_data.json"
with open("limit.txt", "r") as f:
    numbers = [float(line.strip()) for line in f]
if numbers:
    limit = numbers[0]
else:
    print("No limit")
    sys.exit()

print("Limit:",limit)
dealing = True

def optimal_blackjack_action(dealer_value, hard_value, soft_value, can_double, can_split):
    # --- 1. Handle Splitting ---
    if can_split:
        # Define optimal splitting strategy based on dealer up-card
        split_rules = {
            1: "split",  # Always split Aces
            8: "split",   # Always split 8s
            10: "stand",  # Never split 10s (e.g., 10 + 10)
            9: "split" if dealer_value not in [7, 10, 11] else "stand",
            7: "split" if dealer_value <= 7 else "hit",
            6: "split" if dealer_value <= 6 else "hit",
            5: "double",  # Treat a pair of 5s like a hard 10
            4: "split" if dealer_value in [5, 6] else "hit",
            3: "split" if dealer_value <= 7 else "hit",
            2: "split" if dealer_value <= 7 else "hit"
        }

        pair_value = soft_value // 2  # Pair value, assuming player has a pair (e.g., 8 + 8 = 16)
        return split_rules[pair_value]

    # --- 2. Handle Soft Hands ---
    if soft_value < hard_value:
        soft_value = hard_value
        # Soft hand strategy (Ace counted as 11)
        if soft_value >= 20:
            return "stand"
        elif soft_value == 19:
            if dealer_value == 6 and can_double:
                return "double"
            else:
                return "stand"
        elif soft_value == 18:
            if 2 <= dealer_value <= 6:
                return "double" if can_double else "stand"
            elif dealer_value in [9, 10, 11]:
                return "hit"
            else:
                return "stand"
        elif soft_value == 17:
            return "double" if 3 <= dealer_value <= 6 and can_double else "hit"
        elif soft_value == 16 or soft_value == 15:
            return "double" if 4 <= dealer_value <= 6 and can_double else "hit"
        else:
            return "double" if 5 <= dealer_value <= 6 and can_double else "hit"

    # --- 3. Handle Hard Hands ---
    if hard_value >= 17:
        return "stand"
    elif hard_value >= 13 and dealer_value <= 6:
        return "stand"
    elif hard_value == 12:
        if 4 <= dealer_value <= 6:
            return "stand"
        else:
            return "hit"
    elif hard_value == 11:
        return "double" if can_double else "hit"
    elif hard_value == 10:
        return "double" if dealer_value <= 9 and can_double else "hit"
    elif hard_value == 9:
        return "double" if 3 <= dealer_value <= 6 and can_double else "hit"
    else:
        return "hit"


def process_hand_response(data):
    """ Processes a single hand and determines the best move. """
    global spent
    global earned
    global dealing
    action = None
    dealer_value = data["spin"]["dealer"]["total_value"]
    hands = data["spin"]["hands"]
    for i in ["0","1","2"]:
        if i in hands:
            if type(hands[i]["split"]) != int and hands[i]["split"]["active"]:
                hard_value = hands[i]["split"]["hard_value"]
                soft_value = hands[i]["split"]["soft_value"]
                can_double = "DOUBLE" in data["spin"]["steps"].values()
                can_split = "SPLIT" in data["spin"]["steps"].values()
                action = optimal_blackjack_action(dealer_value, hard_value, soft_value, can_double, can_split)
                break
            elif hands[i]["active"]:
                hard_value = hands[i]["hard_value"]
                soft_value = hands[i]["soft_value"]
                can_double = "DOUBLE" in data["spin"]["steps"].values()
                can_split = "SPLIT" in data["spin"]["steps"].values()
                action = optimal_blackjack_action(dealer_value, hard_value, soft_value, can_double, can_split)
                break
    if dealing:
        time.sleep(random.uniform(4, 4.7))
    else:
        time.sleep(random.uniform(0.4, 0.6))
    dealing = False
    if "EVENMONEY" in data["spin"]["steps"].values():
        reject_even_money()
    elif "INSURE" in data["spin"]["steps"].values():
        reject_insurance()
    elif action == "hit":
        hit()
    elif action == "stand":
        stand()
    elif action == "double":
        double()
    elif action == "split":
        split()
    else:
        spent += data["spin"]["total_bet"]
        earned += data["spin"]["total_win"]
        print("Spent:", spent)
        print("Earned:", earned,"\n")
        time.sleep(random.uniform(0.8, 0.9))
        reset()


def hit():
    print("Hit.\n")
    human_action(875,930)

def stand():
    print("Stand.\n")
    human_action(1300,930)

def double():
    print("Double.\n")
    human_action(1000,930)

def split():
    print("Split.\n")
    human_action(1150,930)

def reject_insurance():
    print("Reject insurance.\n")
    human_action(1150, 930)

def reject_even_money():
    print("Reject even money.\n")
    human_action(1150, 930)

def reset():
    global dealing
    if spent >= limit:
        return
    human_action(1000, 930)
    dealing = True

def human_action(x,y):
    human_like_mouse_move(x, y)
    human_like_click()

def human_like_mouse_move(x, y):
    x += random.randint(-10,-5)
    y += random.randint(-10,-5)
    cursor.move_to([x,y])

def human_like_click():
    time.sleep(random.uniform(0.1, 0.15))
    pyautogui.mouseDown()
    time.sleep(random.uniform(0.2, 0.3))
    pyautogui.mouseUp()

def refresh_page():
    print("Something went wrong. Refreshing page...\n")
    pyautogui.press("f5")


def read_and_process_json():
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            process_hand_response(data)
    except FileNotFoundError:
        print("The file play_data.json was not found.")
    except json.JSONDecodeError:
        print("Error: The file does not contain valid JSON.")

spent = 0
earned = 0

def main():
    try:
        initial_modified_time = os.path.getmtime(json_file_path)
    except FileNotFoundError:
        initial_modified_time = None
    tries = 0
    refreshes = 0
    while spent<limit:
        if refreshes > 7:
            print("Fatal error. Killing bot.")
            break
        if tries > random.randint(130,150):
            tries = 0
            refreshes += 1
            refresh_page()
        tries += 1
        try:
            current_modified_time = os.path.getmtime(json_file_path)
            if initial_modified_time is None or current_modified_time > initial_modified_time:
                tries = 0
                refreshes = 0
                read_and_process_json()
                initial_modified_time = current_modified_time
        except FileNotFoundError:
            print("Waiting for the JSON file to be created...")
        time.sleep(0.2)

if __name__ == "__main__":
    main()
