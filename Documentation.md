# Documentation

## Overview

This archive service consists of mainly two parts, metadata and body.

Every BMS files and ZIP files are handled with MD5 hash.

- BMS files are represented as `BMS_` + MD5 hash, total length of 36.
  - For example, "[NO NIGHT MORE SOUL! [HYPER7]](http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&bmsid=126951)" is represented with `BMS_860df95676b8367a22b596a689b866ca`.
- ZIP files are represented as `ZIP_` + MD5 hash, total length of 36.
  - For example, ZIP file containing song "NO NIGHT MORE SOUL" is represented with `ZIP_b092b5aa6cfdb04e28ecc59c8b2175cd`.
  - This code is only used at this service.

## Metadata

Metadata consist of two files currently, and may be added:

- `BMS2ZIP.json` located at [`/BMS2ZIP.json`](https://bms.kyouko.moe/BMS2ZIP.json)
  - `BMS2ZIP.json` is directory mapping BMS file to list of ZIP files. Each zip file in list holds BMS file given as key. There may be two or more ZIP file corresponds to BMS file. Only one of them is up-to-date, usually the last one, but it is subject to change.
- - `ZIP2BMS.json` located at [`/ZIP2BMS.json`](https://bms.kyouko.moe/ZIP2BMS.json)
  - `ZIP2BMS.json` is dictionary mapping ZIP file to list of BMS files. Each list holds every hash of BMS in zip. There can be multiple BMS in single zip. (Which is natural, supporting various difficulty.)

We will going to support other `json` files, such as name and composer of the song of ZIP file, difficulty name of BMS file, deprecated zip file list, and so on.

## Body

To download zip file, use link `/zip/` + MD5 hash of zip + `.zip`.

For example, to download NO NIGHT MORE SOUL, use link [`/zip/ZIP_5ee8f3972d8d7cb4c86a7afc3b36cf57.zip`](
https://bms.kyouko.moe/zip/ZIP_5ee8f3972d8d7cb4c86a7afc3b36cf57.zip)

Every ZIP file..

- uses UTF-8 name, also storing Unicode file names in an extra header field. 
- has all bms files in root directory.

