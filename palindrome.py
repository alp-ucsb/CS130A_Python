#!/usr/bin/env python3

__doc__ = "Program to check if a sentence is a palindrome"

import sys

def strip_non_letters(word):
   letters = [
      c.lower() for c in word if 'a' <= c.lower() and c.lower() <= 'z']
   return ''.join(letters)

def reverse(word):
   return ''.join(word[i] for i in range(len(word) - 1, -1, -1))

def check_palindrome(words):
   letters = strip_non_letters(''.join(words))
   palindrome = letters == reverse(letters)
   print('The phrase "{}" reduces to "{}"'.format(' '.join(words), letters))
   print('and is{} a palindrome'.format('' if palindrome else ' not'))
   
if __name__ == '__main__':
   check_palindrome(sys.argv[1:])
    
