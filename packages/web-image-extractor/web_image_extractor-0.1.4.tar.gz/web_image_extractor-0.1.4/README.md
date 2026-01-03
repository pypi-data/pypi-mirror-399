Made By Daniel Enesi.

## Python Web Image Extractor
This Python project extracts images from a website url
- It can access many image formats including SVG.
- It works using only Python Standard Library modules.

### Usage
1. Run `python main.py`
- A tkinter window should pop up providing a textbox.
- Enter the URL into the textbox and click "Get Images"
- When it is done, click the download button to download the images
- Select the folder you want to store the images
- Wait for the images from the website or html file path to download
- When the images download, the folder is automatically opened for you to view the images.

2. Run `python main.py <url> --fp <destination_path> --isfile`
- Prints the image sources to console
- `<url>`: The link to html webpage
- - If `--isfile` is specified, `<url>` maps to a file in the runner's system
- `<destination_path>` is the path to store the images
- - If it is omitted, the images will not be stored

### Notes
- To avoid overwriting files already present in your file system, choose an empty folder while using
- `--isfile` and `--fp` are undergoing testing and development
- The application might not work for some websites
- The tkinter interface might appear unresponsive sometimes, but it's probably just in an loop
- That said, I'll work to make it asynchronous so the UI doesn't freeze
- Would it be nice if I have an executable in this repo? So people don't need to code to use this.

Feel free to create a detailed issue if you find one.
Enjoy using it.