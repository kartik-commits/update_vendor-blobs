&nbsp;
### Required ###
&nbsp;
_`python`_, _`pip`_ and _`colorama`_  ( Juss Google or ChatGPT to install with your system name )
### Make the script executable by ###
&nbsp;
```bash
chmod +x proprietary-deduper.py
```
Rename common proprietary-files.txt to _`common.txt`_ and device proprietary-files.txt to _`device.txt`_ ( Get this file from device dump, use DumprX )
&nbsp;
### Start the game by ###
&nbsp;
```bash
./proprietary-deduper.py common.txt device.txt
```
It is recommended to use `-v` before common.txt to see exactly purged blobs
&nbsp;
### For help  ( It is actually for short-termers like me )
&nbsp;
```bash
proprietary-deduper.py --help
```
