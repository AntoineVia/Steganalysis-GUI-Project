# README.md

## Folder listing

- assets: folder with graphical resources (currently just src.ico)
- imports: empty folder where the images will be imported to
- sh: folder with scripts to import pictures from Android devices (pullpics.sh)
- txt: folder where logs will be created
- ui: folder where the UI files of the project are stored

## File listing

Apart from the folders previously described, the main files of the project are:

- start.py: the starting script
- Main.py: the file containing the "main" App class declaration
- DeviceList.py: the file containing the DeviceList class declaration
- ImportFile.py: the file containing the ImportFile class declaration
- ResultsDisplay.py: the file containing the ResultsDisplay class declaration

## Potential problems and how to fix them

There may be a problem running the program for the first time with an ErrNo 13: the way to fix this is to open a terminal in the sh directory and type:

```
sudo chmod +755 pullpics.sh
```
