# Using oxttools

makeoxt is a tool for creating a LibreOffice extension.
You will need to choose a language tag to associate with your writing system.
LibreOffice 5.3 or later is needed if you are adding a language that is not in the list
of languages that ships with LibreOffice.

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
  - PARATEXT_WORDLIST.xml : file containing the output of Paratext's Wordlist-File-Export to XML (see note below)
  - DICT.aff : looks for Hunspell dictionary files DICT.dic and DICT.aff
- "Name of Language" = the name of the language enclosed in quotes (for example "Ankave" or "Albanian")
- SCRIPTTYPE =
  - west (Latin, Greek, Cyrillic, etc.), this is the default
  - asian (Chinese, Japanese, Korean)
  - rtl (complex right-to-left scripts, Arabic, etc.)
  - ctl (complex left-to-right scripts, Devanagri, etc.)
- LANGTAG = the language tag (for example aak or aae-Latn)
- OUTPUT.oxt = name of the LibreOffice extension to be created

For the Paratext wordlist option, you may need the additional parameter `--dicttype=xxx` where `xxx` is:
- pt = (default) Paratext 8 format: `<item word="abcd" spelling="Correct"/>
- ptall = Paratext 8 format (as above), but ignore the `spelling` status
- pt9 = Paratext 9 format: `<Status Word="abcd" State="R"/>
- Pt9all = Paratext 9 format (as above), but ignore the `State` status

Note that, for `pt9` and `pt9all`, the `<SpecificCase>` indication is not considered.

You are encouraged to use the `-v` option to include a version number and increment it each time you create a new version. 
If omitted, the version number defaults to `0.1`.
Often version numbers less than `1.0` are used during initial development and the first general release is `1.0`.

To see a list of additional options, use the command:
```
makeoxt --help
```

Examples
```
makeoxt -l "Hypothetical Language" -d SpellingStatus.xml --dicttype=pt9 -v 0.3 xyz xyzHunspellDictionary.oxt
```
Uses the `SpellingStatus.xml` file from a Paratext 9 project and therefore needs to specify `--dicttype=pt9` 
so that the XML file is properly treated.
Version number is set to 0.3.
The language tag is `xyz` and the output is written to `xyzHunspellDictionary.oxt`.


```
makeoxt -l Sango -d sg-CF.aff -n None -v 0.2 sg-CF sg.oxt
```
Uses the `sg-CF.aff` and `sg-CF.dic` Hunspell dictionary files. 
The `-n None` overrides the default NFC normalization. 
The version number is set to 0.2.
The language tag for Sango is normally `sg`, but LibreOffice requires the region code `CF`, so the `sg-CF` language tag is used.



NB: LibreOffice may require a region as part of the language tag.

## Using the .oxt file
### Installing the .oxt file in LibreOffice
- Tools menu, Extension Manager... menu item brings up a dialog
- Click Add
- Navigate to the folder with the .oxt file and double-click on it
- Accept the license
- Close the Extension Manager dialog
- At this point you may need to close and reopen LibreOffice

### Initial use of the language in a LibreOffice document
- Format menu, Character menu item, brings up a dialog, then select the Font tab
  - Use "Western Text Font" for Latin, Greek, Cyrillic fonts
  - Use "CTL Font" otherwise
- In the `Language` field, select the language name from the list. (This will be the value that was used for "Name of Language" during the creation process).
- Use the `OK` button to exit the dialog.
- The language name should then be available from the Tools menu, Language menu item. You can, for example, select the entire text and apply the 
