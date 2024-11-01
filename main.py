#!/usr/bin/env python3

def main():
    # Define the path to the file
    path_to_file = "books/frankenstein.txt"
    
    # Open the file and read the contents
    with open(path_to_file) as f:
        file_contents = f.read()
    
    words_counts = count_words(file_contents)

    print(f"The book contains {words_counts} words.")

def count_words(text):
    words = text.split()
    
    return len(words)

    print(file_contents)
    
if __name__ == "__main__":
    main()
