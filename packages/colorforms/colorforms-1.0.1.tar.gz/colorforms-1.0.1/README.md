# colorforms

Convert colors from one format to another.

This tool will read a color in rgb or hex format piped from stdin, and convert
to the opposite format (rgb -> hex, hex -> rgb).

### Example:

	$ echo "#FFEE00" | colorforms
	rgb(255, 238, 0)

### Usage notes:

The following patterns are valid:

    hhh           (rgb)
    #hhh          (rgb)
    hhhh          (rgba)
    #hhhh         (rgba)
    hhhhhh        (rgb)
    #hhhhhh       (rgb)
    hhhhhhhh      (rgba)
    #hhhhhhhh     (rgba)
    rgb(n,n,n)    (rgb)
    rgb(n,n,n,n)  (rgba)
    rgba(n,n,n,n) (rgba)

### Installation

From [PyPi](https://pypi.org/project/colorforms/):

	pip install colorforms

...or...

	python -m pip install colorforms

### Geany integration

I use this tool inside [Geany](https://www.geany.org/), to quickly convert
colors back and forth with a keyboard shortcut.

2. From the Geany menu, select "Edit -> Format -> Send selection to -> Set custom commands"
3. In the popup dialog, choose an empty Command / Label line. In the "Command"
field, type "colorforms". Add an appropriate label, such as "Convert color format".

Now this tool will be available from the Edit menu.

1. Select the string you want to convert.
2. From the Geany menu, select "Edit -> Format -> Send selection to -> Convert color format"

If you put this tool in one of the first three lines, you automatically get a
keyboard shortcut you can use to invoke it. For example, entering colorforms on
line 2 will make it possible to select a color value, and simply press "CTRL-2"
to convert to the opposite format.
