# helpers
from tkinter import StringVar, Frame, Label, Entry
from tkinter.ttk import Button, Frame, Label, Entry
from tkinter.filedialog import askdirectory

from main import ImageExtractor
from image_extractor import download_images, extract_images


# All the self.app stuff, maybe it should be in actions
class Actions:
    def __init__(self, app: ImageExtractor):
        self.url: str
        self.exiter: Button
        self.reseter: Button
        self.downloader: Button
        self.sources: dict[str, set[str]]
        self.app = app

        self.build()
        self.events()

    def build(self):
        self.frame = Frame(self.app.appframe, padding=(30, 0))
        self.frame.grid()
        column = 0

        for butn_prop in (
            ("downloader", "Download"),
            ("reseter", "Reset"),
            ("exiter", "Exit"),
        ):
            butn = Button(self.frame, text=butn_prop[1], width=15, state="disabled")
            butn.grid(row=0, column=column, padx=5, pady=5)
            column += 1
            setattr(self, butn_prop[0], butn)

        self.exiter.state(["!disabled"])
        # build status box
        self.status = StringVar(self.frame, "Input a web or file url and click Get Images")
        self.status_display = Label(self.frame, textvariable=self.status)
        self.status_display.grid(row=1, column=0, columnspan=3, sticky="news", pady=5)
        # build search box
        self.value = StringVar(self.frame, "https://")
        self.search_box = Entry(self.frame, textvariable=self.value)
        self.search_box.grid(row=2, column=0, columnspan=3, pady=5, sticky="news")

        self.getter = Button(self.frame, text="Get Images")
        self.getter.grid(row=3, column=0, columnspan=3, pady=5, sticky="news")

    def events(self):
        def search():
            self.status.set("Searching...")
            # disable the getter
            self.getter.state(["disabled"])

            self.url = self.value.get()
            try:
                is_file = self.url.startswith(("C:/", '/'))  # Maybe also check https
                self.sources = extract_images(self.url, is_file)
            except Exception as error:
                # Do stuff later, like resetting buttons
                raise error

            self.reseter.state(
                ["!disabled"]
            )
            self.downloader.state(
                ["!disabled"]
            )
            self.status.set(
                "Done with searching. Click the Download button to download images"
            )

        def download():
            # self.status.set("Pick a folder")
            self.status.set("Downloading...")
            self.downloader.state(
                ["disabled"]
            )
            folder = askdirectory()
            if not folder:
                return reset()

            download_images(self.url, folder, **self.sources)
            reset()

        def reset():
            self.sources["img_srcs"].clear()
            self.sources["svg_texts"].clear()
            self.value.set("https://")
            self.status.set("Input a url and click Get Images")
            self.downloader.state(
                ["disabled"]
            )
            self.getter.state(["!disabled"])
            self.reseter.state(["disabled"])

        self.getter["command"] = search
        self.downloader["command"] = download
        self.reseter["command"] = reset
        self.exiter["command"] = self.app.app.destroy
