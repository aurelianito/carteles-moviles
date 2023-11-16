import sys
import re

from bs4 import BeautifulSoup

def make_soup(path):
    with open(path, "rb") as f:
        buf = f.read()

    raw_text = buf.decode("cp1252")
    return BeautifulSoup(
        raw_text,
        features="html.parser"
    )

re_background_white = re.compile(r"background:\s*white", re.DOTALL)
re_color_black = re.compile(r"color:\s*black", re.DOTALL)

def harmonize_colors(bs):
    for e in bs.body.find_all(recursive=True):
        if hasattr(e, "get"):
            style = e.get("style")
            if not style is None:
                # no_enters = style.replace("\n"," ")
                no_white_background = re_background_white.sub("", style)
                no_black_color = re_color_black.sub("", no_white_background)
                e["style"] = no_black_color

if __name__ == "__main__":

    print("""\
<html>
<head>
<meta charset="UTF-8">
<style>
    body {
        overflow: hidden; 
        background:black;
    }
</style>
</head>
<body>
<div id=\"viewport\">
""")
    
    for fname in (sys.argv[1:]):

        bs = make_soup(fname)
        harmonize_colors(bs)

        word_section = bs.body.find("div", {"class":"WordSection1"})

        for p in word_section.find_all("p", {"class": "MsoNormal"}, recursive=False):
            for enter_thing in p.find_all("span", {"style":"mso-spacerun:yes"}):
                ns = enter_thing.find_next_sibling()
                del enter_thing["style"]
                enter_thing.string = " "
                enter_thing.append(bs.new_tag("br"))
            for c in p.children:
                align = p.get("align") or 'left'
                print(f'<p align="{align}" style="color:white">')
                print(c)
                print("</p>")

    print("""\
</div>
<script>
const step_millis = 1000 // * 60 
var on_tick = function() {
    var viewport_height = document.getElementById("viewport").getBoundingClientRect().height
    var window_height = window.innerHeight
    var millis = Date.now()
    var position = (millis / step_millis) % (window_height - viewport_height)
    window.scroll(0,position)
}
on_tick()
setInterval( on_tick, 1000 );
</script>
</body>
</html>
""")