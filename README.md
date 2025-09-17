markdown
# kextan's XML Cropper

**Description:**  
`kextan's XML Cropper` is a Python-based tool for creating XML-based sprite maps from images. Originally developed for *The Lost Crew Files*, it is now available as a standalone, fully functional tool. Users can crop parts of an image, assign names, and export them as XML, ready for use in game development or other projects.

---

## Features

- **Image Cropping:** Select parts of an image and name them.  
- **XML Export:** Save all cropped parts as an XML spritesheet.  
- **Preview Bar:** See all added parts in a horizontal preview bar with names.  
- **Right-Click Deletion:** Remove any selected part immediately.  
- **Cached Image Handling:** Original images remain untouched; all edits are done on cached copies.  
- **Open XML:** Load previously saved XML files and continue editing.  
- **Auto Cleanup:** Temporary cache stored in `%AppData%\XMLCIMGTemp\cache` is automatically cleared on exit.  

---

## Requirements

- Python 3.8+  
- Pillow (`pip install pillow`)  
- Tkinter (usually included with Python on Windows)  

---

## Installation

1. Clone or download the repository.  
2. Install dependencies:

```bash
pip install pillow
````

3. Run the script:

```bash
python sprite_mapper.py
```

> Optional: Use PyInstaller to build a standalone executable (Windows only).

---

## Usage

1. **Open Image:** `File → Open Image` → select a PNG/JPG.
2. **Select Sprite:** Click and drag to select a part of the image.
3. **Name Sprite:** Enter a name for the selected part.
4. **Preview:** Cropped part appears in the bottom preview bar.
5. **Delete Sprite:** Right-click on the rectangle or preview and choose Delete.
6. **Save XML:** `File → Save XML` to export all parts.
7. **Open XML:** `File → Open XML` to continue editing a previous project.
8. **Cancel Selection:** Right-click while drawing a rectangle cancels the selection.

---

## Notes

* Crops and previews are saved in `%AppData%\XMLCIMGTemp\cache` to protect original images.
* Closing the app automatically cleans the cache folder.
* Designed for ease of use and quick sprite mapping for games or applications.

---

## Building an EXE (Windows)

To build a standalone Windows executable with a custom icon:

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Prepare an `.ico` file for your icon.

3. Build the EXE:

```bash
pyinstaller --onefile --windowed --icon=icon.ico kextxmlcrop.py
```

* `--onefile` → creates a single EXE
* `--windowed` → hides the console window
* `--icon=icon.ico` → sets the EXE icon

The output EXE will be located in the `dist` folder.

---

## License

Free for personal use. Attribution appreciated if used in projects.
