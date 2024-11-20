# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 14:35:31 2023

@author: kalya
"""

import time
import tkinter as tk
from tkinter import messagebox
ALPHABET_SIZE = 36

def char_to_index(c):
    if 'a' <= c <= 'z':
        return ord(c) - ord('a')
    elif '0' <= c <= '9':
        return ord(c) - ord('0') + 26
    else:
        return None

class TrieNode:
    def __init__(self):
        self.children = [None] * ALPHABET_SIZE
        self.isWordEnd = False

def get_node():
    return TrieNode()

class User:
    def __init__(self):
        self.history = []

def insert_user_history(user, query, suggestions):
    user.history.append((query, suggestions))

def insert(root, key):
    pCrawl = root
    key = key.lower()  # Convert to lowercase for case insensitivity
    for level in range(len(key)):
        index = char_to_index(key[level])
        if index is not None:
            if not pCrawl.children[index]:
                pCrawl.children[index] = get_node()
            pCrawl = pCrawl.children[index]
    pCrawl.isWordEnd = True

def print_auto_suggestions(root, query, limit=None):
    pCrawl = root
    original_query = query
    query = query.lower()  # Convert the query to lowercase for case insensitivity

    results = []
    for c in query:
        index = char_to_index(c)
        if index is not None and pCrawl.children[index]:
            pCrawl = pCrawl.children[index]
        else:
            return 0  # Return 0 if an invalid character is encountered

    suggestions_rec(pCrawl, original_query, limit, results)

    unique_results = list(set(results))
    for i, suggestion in enumerate(unique_results):
        if limit is not None and i >= limit:
            break
        print(suggestion)

    return len(unique_results)

def is_last_node(root):
    return all(child is None for child in root.children)

def suggestions_rec(root, curr_prefix, limit, results):
    if root.isWordEnd:
        results.append(curr_prefix)

    if limit is not None and len(results) >= limit:
        return

    for i in range(ALPHABET_SIZE):
        if root.children[i]:
            if i < 26:
                child = chr(ord('a') + i)
            else:
                child = str(i - 26)
            suggestions_rec(root.children[i], curr_prefix + child, limit, results)

def save_search_history_to_file(user):
    with open("search_history.txt", "a") as file:
        for query, suggestions in user.history:
            file.write(f"Query: {query}, Suggestions: {suggestions}\n")

def view_search_history_from_file():
    with open("search_history.txt", "r") as file:
        search_history = file.read()
        print("Search History:")
        print(search_history)

def clear_search_history():
    with open("search_history.txt", "w") as file:
        file.truncate(0)  # This empties the file, effectively clearing the search history

def main():
    root = tk.Tk()
    root.title("Search Engine")
    while True:
        print("WELCOME TO THE SEARCH ENGINE")
        print("You can use it to see the available movies, music, departments")

        root = get_node()
        user = User()

        print("Please enter the respective number to go to the respective searching")
        num = int(input())
        if num == 1:
            search_file = "words.txt"
        elif num == 2:
            search_file = "music.txt"
        with open(search_file, "r") as inputFile:
            for word in inputFile:
                insert(root, word.strip())

        print("Enter text to search")
        query = input()
        start_time = time.time()
        print("Enter the maximum number of suggestions (or press Enter for unlimited):")
        limit_input = input()
        limit = int(limit_input) if limit_input.isdigit() else None
        comp = print_auto_suggestions(root, query, limit)
        end_time = time.time()

        if comp == -1:
            print("No other strings found with this prefix")
        elif comp == 0:
            print("No string found with this prefix")

        search_time = end_time - start_time
        print(f"Search took {search_time:.4f} seconds")

        insert_user_history(user, query, comp)
        save_search_history_to_file(user)

        print("Do you want to search again or quit? (search/quit)")
        search_again = input().strip().lower()
        if search_again == 'quit':
            break

    # Prompt to view search history
    print("Do you want to see the search history or clear it? (view/clear/none)")
    see_or_clear = input().strip().lower()
    if see_or_clear == 'view':
        view_search_history_from_file()
    elif see_or_clear == 'clear':
        clear_search_history()
        print("Search history has been cleared.")
    else:
        print("Search history remains unchanged")


if __name__ == "__main__":
    main()