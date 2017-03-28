# Using oxttools

makeoxt is the tool for creating a LibreOffice extension.
You will need to choose a language tag to associate with your writing system.
LibreOffice 5.3 or later is needed if you are adding a language.

## Windows installation (using packaged version)
Copy makeoxt.exe to the working folder

## Linux installation
Use setup.py to install the makeoxt python script.

## Usage
- Copy DICT.txt to the working folder
- From command prompt enter the command:
```
makeoxt -d DICT.txt -l "Name of Language" -t SCRIPTTYPE LANGTAG OUTPUT.oxt
```
- OUTPUT.oxt will be created

where
- DICT.txt = name of a file containing a list of words (one per line)
- "Name of Language" = the name of the language enclosed in quotes (for example "Ankave" or "Albanian")
- SCRIPTTYPE =
  - west (Latin, Greek, Cyrillic, etc.)
  - asian (Chinese, Japanese, Korean)
  - rtl (complex right-to-left scripts, Arabic, etc.)
  - ctl (complex left-to-right scripts, Devanagri, etc.)
- LANGTAG = the language tag (for example aak or aae-Latn)
- OUTPUT.oxt = name of the LibreOffice extension to be created
