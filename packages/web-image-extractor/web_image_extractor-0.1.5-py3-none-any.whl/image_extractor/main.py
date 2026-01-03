"""First started Nov 1, 2023 3.50pm"""

import argparse
import json
import sys

from tkinter import Frame, Tk, NSEW
from tkinter.ttk import Frame


from image_extractor import download_images, extract_images


class ImageExtractor:
    def __init__(self):
        self.app = Tk()
        self.app.title("Image Extractor")
        # self.app.resizable(width=0, height=0)  - looks like I'll need another typeshed PR
        self.build_appframe()
        self.style()

    def build_appframe(self):
        self.appframe = Frame(self.app, padding=(10))
        self.appframe.grid(column=0, row=0, sticky=NSEW)
        self.appframe.columnconfigure(0, weight=1)

    def style(self):
        # Make it resize with the window
        self.app.columnconfigure(0, weight=1)
        self.app.rowconfigure(0, weight=1)
        self.appframe.columnconfigure(0, weight=1)

    def __getitem__(self, prop: str):
        return getattr(self.app, prop)


parser = argparse.ArgumentParser(
    prog="python main.py",
    description="Extracts images from a webpage or html file url",
    epilog="Thanks for using!",
)

parser.add_argument("url", help="The web page or html file resource link")
parser.add_argument("--fp", help="Path to storage folder on user's system")
parser.add_argument("--isfile", action="store_true", help="Option to specify a file url instead of web")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Called without arguments
        try:
            from .actions import Actions
            app = ImageExtractor()
            Actions(app)
            app.app.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            print("Exiting, thanks for using Image Extractor!")
    else:
        args = parser.parse_args()
        print(f"Sourcing images from {args.url}")
        img_sources = extract_images(args.url, args.isfile)
        max_len = len(max(img_sources["img_srcs"], key=len))
        print(
            f"\nImage urls, SVG texts: {json.dumps({
                k: [x if len(x) <= max_len else f"{x[:max_len]}..." for x in v] for k, v in img_sources.items()}, indent=4
                )}"
        )
        if args.fp is not None:
            print(f"\nSaving to {args.fp}")
            download_images(args.url, args.fp, **img_sources)

        print("\nDone!")
