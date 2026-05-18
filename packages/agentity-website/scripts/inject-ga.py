"""Inject Google Analytics snippet into all static HTML files after build."""

import os
import sys

GA_SCRIPT = (
    '<script async src="https://www.googletagmanager.com/gtag/js?id=G-WKVSFZQEXZ"></script>\n'
    '<script>window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag("js", new Date()); gtag("config", "G-WKVSFZQEXZ");</script>'
)


def main(out_dir: str) -> None:
    for root, _dirs, files in os.walk(out_dir):
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            with open(path) as f:
                html = f.read()
            if "G-WKVSFZQEXZ" in html:
                print(f"  already injected GA into {path}")
                continue
            html = html.replace("</head>", GA_SCRIPT + "</head>")
            with open(path, "w") as f:
                f.write(html)
            print(f"  injected GA into {path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
