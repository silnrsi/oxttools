# Using oxttools

makeoxt is a tool for creating a LibreOffice extension.
You will need to choose a language tag to associate with your writing system.
LibreOffice 5.3 or later is needed if you are adding a language.

## Windows installation (using packaged version)
Download makeoxt.zip from the https://github.com/silnrsi/oxttools/releases page.
Extract the makeoxt.exe file and copy it to working folder.

## Linux installation
Use setup.py to install the makeoxt python script:
```
python setup.py build
sudo python setup.py install
```

Note: makeoxt requires Python 3. If you need to type 'python3' (rather than 'python') to run Python 3, then substitute 'python3' for 'python' in the above command.

Note: The installation process uses setuptools. If it is not installed, you'll need `sudo apt-get install python3-setuptools`. 

Note: makeoxt uses lxml. If it is not installed, you'll need to install python3-lxml.

## Usage
- Copy WORDLIST (.txt, .dic/.aff, .xml) to the working folder (see below for details on format)
- From command prompt enter the command:
```
makeoxt -d WORDLIST -l "Name of Language" -t SCRIPTTYPE LANGTAG OUTPUT.oxt
```
- OUTPUT.oxt will be created

where
- WORDLIST (which processes differently based on the file extension) =
  - DICT.txt : plain text file containing a list of words (one per line)
  - PARATEXT_WORDLIST.xml : file containing the output of Paratext's Wordlist-File-Export to XML
  - DICT.aff : (experimental) hunspell .dic/.aff dictionary files
- "Name of Language" = the name of the language enclosed in quotes (for example "Ankave" or "Albanian")
- SCRIPTTYPE =
  - west (Latin, Greek, Cyrillic, etc.)
  - asian (Chinese, Japanese, Korean)
  - rtl (complex right-to-left scripts, Arabic, etc.)
  - ctl (complex left-to-right scripts, Devanagri, etc.)
- LANGTAG = the language tag (for example aak or aae-Latn)
- OUTPUT.oxt = name of the LibreOffice extension to be created

To see a list of additiona options, use the command:
```
makeoxt --help
```

NB: LibreOffice may require a region as part of the language tag.

## Using the .oxt file
### Installing the .oxt file in LibreOffice
- Tools menu, Extension Manager... menu item brings up a dialog
- Click Add
- Navigate to the folder with the .oxt file and double-click on it
- Accept the license
- Close the Extension Manager dialog

### Initial use of the language in a LibreOffice document
- Format menu, Character menu item, brings up a dialog, then select the Font tab
- Select the language name (value of "Name of Language" in the creation process) from the list
  - Use "Western Text Font" for Latin, Greek, Cyrillic fonts
  - Use "CTL Font" otherwise
- The language name should then be available from the Tools menu, Language menu item
