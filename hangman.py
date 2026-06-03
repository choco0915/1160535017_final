#!/usr/bin/env python3
import random
import os
import sys
import tkinter as tk
from tkinter import messagebox

HANGMAN_PICS = [
"""

         |
         |
         |
         |
         |
    =========""",
"""
     +---+
         |
         |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========""",
]

DEFAULT_WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt')


def load_words(path=DEFAULT_WORDS_FILE):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            words = [w.strip().lower() for w in f if w.strip()]
        return words
    except FileNotFoundError:
        return []


class HangmanGUI:
    def __init__(self, words, demo_word=None):
        self.words = words
        self.demo_word = demo_word
        self.root = tk.Tk()
        self.root.title('Hangman')

        self.max_wrong = len(HANGMAN_PICS) - 1

        # Top: hangman ASCII
        self.hangman_label = tk.Label(self.root, text='', font=('Courier', 12), justify='left')
        self.hangman_label.pack(padx=10, pady=5)

        # Word display (per-letter labels to allow colored hint letters)
        self.word_frame = tk.Frame(self.root)
        self.word_frame.pack(padx=10, pady=5)

        # Frame for letter buttons
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(padx=10, pady=5)

        # Create A-Z buttons
        self.letter_buttons = {}
        for index, ch in enumerate('abcdefghijklmnopqrstuvwxyz'):
            btn = tk.Button(self.buttons_frame, text=ch.upper(), width=3, command=lambda c=ch: self.on_letter(c))
            btn.grid(row=index // 13, column=index % 13, padx=1, pady=1)
            self.letter_buttons[ch] = btn

        # Guessed letters label
        self.guessed_var = tk.StringVar()
        self.guessed_label = tk.Label(self.root, textvariable=self.guessed_var)
        self.guessed_label.pack(padx=10, pady=5)

        # (Removed whole-word guess entry per user request)

        # Bottom controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(padx=10, pady=5)
        new_btn = tk.Button(control_frame, text='New Game', command=self.new_game)
        new_btn.pack(side='left')
        self.difficulty_var = tk.StringVar(value='Normal')
        diff_menu = tk.OptionMenu(control_frame, self.difficulty_var, 'Easy', 'Normal', 'Hard')
        diff_menu.pack(side='left', padx=5)
        # Hint button (max 2 per round)
        self.hints_left = 2
        self.hinted_letters = set()
        self.hint_btn = tk.Button(control_frame, text=f'Hint ({self.hints_left})', command=self.use_hint)
        self.hint_btn.pack(side='left', padx=5)

        # initialize state
        self.secret = ''
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.hints_left = 2
        self.hinted_letters = set()
        self.initial_hint = None

        self.new_game()

    def pick_secret(self):
        if self.demo_word:
            return self.demo_word.lower()
        difficulty = self.difficulty_var.get()
        if difficulty == 'Easy':
            pool = [w for w in self.words if len(w) <= 5]
        elif difficulty == 'Hard':
            pool = [w for w in self.words if len(w) > 8]
        else:  # Normal
            pool = [w for w in self.words if len(w) <= 8 and len(w) > 5]
        if not pool:
            pool = self.words
        return random.choice(pool) if pool else ''

    def new_game(self):
        self.secret = self.pick_secret()
        self.guessed_letters = set()
        self.wrong_guesses = 0
        for btn in self.letter_buttons.values():
            btn.config(state='normal')
        # reset hints
        self.hints_left = 2
        self.hinted_letters = set()
        self.hint_btn.config(text=f'Hint ({self.hints_left})', state='normal')
        # initial orange hint: reveal one random letter at start
        self.initial_hint = None
        unique_letters = [c for c in sorted(set(self.secret)) if c.isalpha()]
        if unique_letters:
            self.initial_hint = random.choice(unique_letters)
            self.guessed_letters.add(self.initial_hint)
            if self.initial_hint in self.letter_buttons:
                self.letter_buttons[self.initial_hint].config(state='disabled')
        self.update_display()

    def on_letter(self, ch):
        ch = ch.lower()
        if ch in self.guessed_letters:
            return
        self.guessed_letters.add(ch)
        self.letter_buttons[ch].config(state='disabled')
        if ch in self.secret:
            pass
        else:
            self.wrong_guesses += 1
        self.update_display()

    def on_guess_word(self):
        # removed whole-word guessing per user request
        return

    def use_hint(self):
        if self.hints_left <= 0:
            return
        # choose an unguessed letter from the secret
        candidates = [c for c in sorted(set(self.secret)) if c not in self.guessed_letters]
        if not candidates:
            messagebox.showinfo('Hint', 'No letters left to reveal.')
            return
        pick = random.choice(candidates)
        self.guessed_letters.add(pick)
        self.hinted_letters.add(pick)
        # disable button for that letter
        if pick in self.letter_buttons:
            self.letter_buttons[pick].config(state='disabled')
        self.hints_left -= 1
        if self.hints_left <= 0:
            self.hint_btn.config(text=f'Hint (0)', state='disabled')
        else:
            self.hint_btn.config(text=f'Hint ({self.hints_left})')
        self.update_display()

    def update_display(self):
        # update hangman ascii
        stage = min(self.wrong_guesses, self.max_wrong)
        self.hangman_label.config(text=HANGMAN_PICS[stage])
        # update word display: rebuild per-letter labels so we can color hinted letters
        for w in self.word_frame.winfo_children():
            w.destroy()
        for ch in self.secret:
            if ch in self.guessed_letters:
                if ch in self.hinted_letters:
                    color = 'red'
                elif self.initial_hint and ch == self.initial_hint:
                    color = 'orange'
                else:
                    color = 'black'
                lbl = tk.Label(self.word_frame, text=ch.upper(), font=('Helvetica', 20), fg=color)
            else:
                lbl = tk.Label(self.word_frame, text='_', font=('Helvetica', 20), fg='black')
            lbl.pack(side='left', padx=3)

        # update guessed letters text
        guessed_display = 'Guessed: ' + ', '.join(sorted(self.guessed_letters)) if self.guessed_letters else 'Guessed: (none)'
        self.guessed_var.set(guessed_display)

        # check win/lose
        if self.secret and all(c in self.guessed_letters for c in self.secret):
            messagebox.showinfo('Hangman', f'Congratulations! You guessed the word: {self.secret}')
            for btn in self.letter_buttons.values():
                btn.config(state='disabled')
            self.hint_btn.config(state='disabled')
        elif self.wrong_guesses >= self.max_wrong:
            messagebox.showinfo('Hangman', f'Game over. The word was: {self.secret}')
            for btn in self.letter_buttons.values():
                btn.config(state='disabled')
            self.hint_btn.config(state='disabled')

    def run(self):
        self.root.mainloop()


def main():
    words = load_words()
    if not words:
        message = 'Please create a `words.txt` file next to this script with one word per line.'
        print(message)
        return

    demo_word = None
    if '--demo' in sys.argv:
        try:
            idx = sys.argv.index('--demo')
            if idx + 1 < len(sys.argv):
                candidate = sys.argv[idx + 1].strip().lower()
                if candidate.isalpha():
                    demo_word = candidate
        except Exception:
            demo_word = None

    gui = HangmanGUI(words, demo_word=demo_word)
    gui.run()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        sys.exit(1)
