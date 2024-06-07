# NSMBW BMG Editor
This tool allows to edit Message.arc files found in New Super Mario Bros. Wii!

## Setup
- Install Python 3
- Install PyQt5
- Install [wbmgt](https://szs.wiimm.de/wbmgt/)

## Usage
Execute the NSMBW-BMG-Editor.py script. On Windows you can also use the NSMBW-BMG-Editor.bat script to call the .py file.

## Why use this tool?
NSMBW stores BMG files within arc files. Another tool called BMG Editor can open the .bmg file, but you need to extract it from the .arc first or use SZS Explorer and open the BMG Editor from within it.

While this costs a lot of time, the main reason to use this new tool instead however is, that BMG Editor doesn't allow you to easily edit the attributes of newly added strings. When editing existing strings, the attributes remain, but when adding new strings, the default attributes actually turn the new string invisible!

While the command line tool wbmgt allows to properly edit .bmg files, it is even harder to use than the BMG Editor. Therefore this tool now provides a GUI added on top of it. There also is a convenient feature to convert string numbers to and from category + ID as used in in-game custom code!