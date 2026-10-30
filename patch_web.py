"""Apply the phone-first, full-screen canvas layout to pygbag's generated page."""

import re
from pathlib import Path


INDEX = Path("build/web/index.html")
MARKER = "<!-- DRIVEX MOBILE CANVAS -->"
STYLES = """<!-- DRIVEX MOBILE CANVAS -->
<style>
html, body {
    width: 100%;
    height: 100%;
    margin: 0;
    overflow: hidden;
    background: #183022;
}
#canvas.emscripten {
    position: fixed !important;
    left: 50% !important;
    top: 50% !important;
    right: auto !important;
    bottom: auto !important;
    transform: translate(-50%, -50%) !important;
    width: min(100vw, 46vh) !important;
    height: min(100vh, 217.4vw) !important;
}
@supports (height: 100dvh) {
    #canvas.emscripten {
        width: min(100vw, 46dvh) !important;
        height: min(100dvh, 217.4vw) !important;
    }
}
@media (orientation: portrait) {
    #canvas.emscripten {
        width: 100vw !important;
        height: 100vh !important;
    }
}
@supports (height: 100dvh) {
    @media (orientation: portrait) {
        #canvas.emscripten {
            height: 100dvh !important;
        }
    }
}
</style>"""


def main():
    if not INDEX.is_file():
        raise SystemExit(f"pygbag output was not found: {INDEX}")

    html = INDEX.read_text()
    html = re.sub(r"fb_ar\s*:\s*[-+]?\d*\.?\d+\s*,", "fb_ar : 0.4600,", html, count=1)
    if MARKER in html:
        start = html.index(MARKER)
        end = html.index("</style>", start) + len("</style>")
        html = html[:start] + STYLES + html[end:]
    elif "</head>" in html:
        html = html.replace("</head>", f"{STYLES}\n</head>", 1)
    else:
        raise SystemExit("Generated pygbag page has no </head> insertion point")

    INDEX.write_text(html)
    print(f"Applied full-screen 9:16 mobile canvas styles to {INDEX}.")


if __name__ == "__main__":
    main()
