#  colorforms/__main__.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Command-line color conversion tool.

This tool will read a color in rgb or hex format piped from stdin, and convert
to the opposite format (rgb -> hex, hex -> rgb).

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

"""
from sys import stdin, stdout
from re import match, IGNORECASE


def main():
	arg = stdin.read().strip()
	if m := match('^#?([a-f0-9])([a-f0-9])([a-f0-9])$', arg, IGNORECASE):
		d = { i:int(m[i], 16) for i in range(1, 4) }
		print(f'rgb({d[1] * 16 + d[1]}, {d[2] * 16 + d[2]}, {d[3] * 16 + d[3]})')
	elif m := match('^#?([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])$', arg, IGNORECASE):
		d = { i:int(m[i], 16) for i in range(1, 5) }
		print(f'rgb({d[1] * 16 + d[1]}, {d[2] * 16 + d[2]}, {d[3] * 16 + d[3]}, {d[4] * 16 + d[4]})')
	elif m := match('^#?([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])$', arg, IGNORECASE):
		d = { i:int(m[i], 16) for i in range(1, 7) }
		print(f'rgb({d[1] * 16 + d[2]}, {d[3] * 16 + d[4]}, {d[5] * 16 + d[6]})')
	elif m := match('^#?([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])([a-f0-9])$', arg, IGNORECASE):
		d = { i:int(m[i], 16) for i in range(1, 9) }
		print(f'rgba({d[1] * 16 + d[2]}, {d[3] * 16 + d[4]}, {d[5] * 16 + d[6]}, {d[7] * 16 + d[8]})')
	elif m := match('rgb\(\s*([0-9]{1,3}),\s*([0-9]{1,3}),\s*([0-9]{1,3})\s*\)', arg):
		l = [ int(m[i]) for i in range(1, 4) ]
		hv = [ v // 16 for v in l ]
		lv = [ v % 16 for v in l ]
		print('#' + ''.join(f'{h:x}{l:x}' for h,l in zip(hv, lv)))
	elif m := match('rgba?\(\s*([0-9]{1,3}),\s*([0-9]{1,3}),\s*([0-9]{1,3}),\s*([0-9]{1,3})\s*\)', arg):
		l = [ int(m[i]) for i in range(1, 5) ]
		hv = [ v // 16 for v in l ]
		lv = [ v % 16 for v in l ]
		print('#' + ''.join(f'{h:x}{l:x}' for h,l in zip(hv, lv)))
	else:
		print(arg)

if __name__ == '__main__':
	main()


#  end colorforms/__main__.py
