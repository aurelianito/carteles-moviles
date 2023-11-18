import sys
import re
from argparse import ArgumentParser

from bs4 import BeautifulSoup

def arg_parser():
    p = ArgumentParser("Carteles Moviles generator")
    p.add_argument("--step-seconds", "-s", default="1", help="Seconds between steps (default=%(default)s)")
    p.add_argument("--overflow", "-o", default="hidden", help="Generated webpage CSS overflow (default=%(default)s)")
    p.add_argument("--disable-scrolling", "-d", action='store_true', help="Disable auto scrolling in generated web page")
    p.add_argument("files", nargs='+', help="Source .htm files to be used")

    return p

def make_soup(path):
    with open(path, "rb") as f:
        buf = f.read()

    raw_text = buf.decode("cp1252")
    return BeautifulSoup(
        raw_text,
        features="html.parser"
    )

START=r"(^|;)\s*"
END=r"\s*($|;)"
REMOVAL_REGEXES = [re.compile(START + r + END, re.DOTALL) for r in (
    r"background:\s*white",
    r"color:\s*black",
    r"background:\s*#\d+",
    r"color:\s*#\d+",
    r"[^;]*font-family[^;]*"
)]

def remove_unwanted_style(bs):
    for e in bs.body.find_all(recursive=True):
        if hasattr(e, "get"):
            style = e.get("style")
            if not style is None:
                for regex in REMOVAL_REGEXES:
                    style = regex.sub(";", style)
                e["style"] = style

def main(argv):
    args = arg_parser().parse_args(argv[1:])
    
    print("""\
<html>
<head>
<meta charset="UTF-8">
<style>
    body {
        overflow: """ + args.overflow + """;
        background:black;
        margin:0px;
        writing-mode: vertical-rl;
        font-family: sans-serif;
    }
</style>
</head>
<body>
<div id=\"viewport\">
""")
    
    for fname in (args.files):

        bs = make_soup(fname)
        remove_unwanted_style(bs)

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
const step_millis = 1000 * """ + args.step_seconds + """
var on_tick = function() {
    var viewport_width = document.getElementById("viewport").getBoundingClientRect().width
    var window_width = window.innerWidth
    var millis = Date.now()
    var position = (millis / step_millis) % (viewport_width - window_width)
    window.scroll(-position,0)
}
""")
    if not args.disable_scrolling:
        print("""\
on_tick()
setInterval( on_tick, 1000 );
""")
    print("""
</script>
</body>
</html>
""")

if __name__ == "__main__":
    main(sys.argv)