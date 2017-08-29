# SARC File Manager
A tool for managing files inside SARC archives (.sarc or .szs files).

## Features
- Add new file name entries to existing SARC files. (This will **ONLY** generate the file entry, with a size of 1 byte. Use better tools such as Every File Explorer to replace the new added entry with a proper file.)

## Compatibility
- **Files must be Yaz0 decompressed, use Every File Explorer to decompress them.**
- Only little endian files are supported (3DS).
- Files with a SFNT section aren't supported. (This includes some SARCs which have proper names in Every File Explorer instead of a hex number.)

## Planned features
- Find a way to properly add actual files, instead of just a file entry with 1 byte size.
- Remove files.
- Add big endian (wii u) support.
- Add support for SARCs with SFNT section.

## Credits
- Gericom: All the research about SARC files.
