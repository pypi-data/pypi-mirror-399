# Easy TTUI Menus

## About

Write simple UI for your code in seconds using Easy TTUI Menus

## Roadmap (For when I get around to it)

- Function name overhaul to make more sense (because `list_menu` really is just a multiple-choice selection...)

## Changelog

### 1.0.3

- Changed the typing hints on multiple_choice_menu() and list_menu() to support `Any` instead of just `str`
- Added stub files
- Added Roadmap header to README

### 1.0.2

- Fixed issue where multiple_choice_menu() returns a list of strings instead of ints
- Added stubs
- More annotations

### 1.0.0

- Started a changelog
- Changes the function signature of `int_menu()`. It now takes a string and two integers instead of a string and a list containing two integers. Legacy systems should use version 0.1.5
- Added `multiple_choice_menu()`
- Removed "Usage" section of readme as I dread maintaining it

## Installation

Run `pip install easyttuimenus` from your preferred environment.

