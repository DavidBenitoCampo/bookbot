#!/usr/bin/env python3
def main():
    book_path = "books/frankenstein.txt"
    text = get_book_text(book_path)
    num_words = get_num_words(text)
    counting_characters = count_characters(text)
    print(f"{num_words} words found in the document")
    print(f"{counting_characters} characters found")

def get_num_words(text):
    words = text.split()
    return len(words)


def get_book_text(path):
    with open(path) as f:
        return f.read()

def count_characters(text):
    text = text.lower()
    spliting = text.split()
    char_count = {}

    for char in spliting:
        if char in char_count:
            char_count[char] += 1
        else:
            char_count[char] = 1

    return char_count

    
main()

