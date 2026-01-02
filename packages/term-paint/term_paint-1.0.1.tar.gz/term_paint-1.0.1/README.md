# term-paint

## Description

This is a CLI tool for drawing images in your terminal with keyboard controls. For wide compatibility, only 8 terminal colors are used - an image that uses different colors will round them to the nearest supported color when loaded and saved.

## Usage

- E to toggle drawing mode (`X` in infobar means drawing is disabled; `%` in infobar means it is enabled)
- W,A,S,D to move around the image
- 1...7 for switching colors (indicated on the left of the infobar)
- 0 to switch to black (default fill color)
- B to show a view of the image in your default image viewer
- X to save the image under the filename provided (nameless files are saved as `unnamed.png`)
- Q to exit the program without saving any changes

## CLI options

- `-n NAME`/`--filename NAME`: provides a filename to save or load the image
- `-l`/`--load`: try to load the specified image (fails if the name was not provided or the image doesn't exist)
- `-x`/`--width`: specify the width in pixels when creating a new image (default 88)
- `-y`/`--height`: specify the height in pixels when creating a new image (default 31 for 88x31 images)
- `-p`/`--pos`: display cursor position in infobar (recommended)
- `-c`/`--change-color`: tries to use the brighter versions of terminal colors (visible colors are dependent on your theme)

## Installation

From [PyPI](https://pypi.org/project/term-paint/):

- `pip install term-paint` or `pipx install term-paint` or `uvx install term-paint`
- `term-paint [OPTIONS]`

From wheel files:

- Download the wheel files from the release and place them into a new directory
- `uv install .`
- `term-paint [OPTIONS]`

From the repo:

- `git clone https://github.com/strawberry-p/term-paint.git`
- `cd term-paint`
- `py paint.py [OPTIONS]`
