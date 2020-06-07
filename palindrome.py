#!/usr/bin/env python3

__doc__ = "Program to check if a sentence is a palindrome"

import sys

def strip_non_letters(word):
   letters = [
      c.lower() for c in word if 'a' <= c.lower() and c.lower() <= 'z']
   return ''.join(letters)

def reverse(word):
   return ''.join(word[i] for i in range(len(word) - 1, -1, -1))

def is_palindrome(words):
   letters = strip_non_letters(''.join(words))
   return letters == reverse(letters)
   
if __name__ == '__main__':
   single_word = strip_non_letters(''.join(sys.argv[1:]))
   print('The phrase "{}" reduces to "{}"'.format(
      ' '.join(sys.argv[1:]), single_word))
   print('and is{} a palindrome'.format(
      '' if is_palindrome(single_word) else ' not'))
    
