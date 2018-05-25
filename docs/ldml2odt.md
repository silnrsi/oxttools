# Using ldml2odt

ldml2odt takes an LDML file and a template and generates a report from it.

An example usage is:

```
scripts/ldml2odt -l pcm-Latn-NI -t reports/simple_report.fodt ~/path/to/sldr/flat/p/pcm_Latn.xml pcm_Latn.fodt
```

The various components of this command are:

- `-l` specifies a full language tag from which components can be extracted for parts fo the report.
- `-t` specifies the template to use. Templates are in the reports/ sudirectory of this project
-  The path to an LDML file. The best results are if the file is flattened in which case fallback values will
   also appear in the report. Non flat will just give blank values.
-  The output file to generate that can loaded into libreoffice.

