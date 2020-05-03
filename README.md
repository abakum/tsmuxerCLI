# tsmuxer.py
Helper for tsMuxeR - not GUI but CLI
## Credits
- Roman Vasilenko - for creating tsMuxeR 
- [justdan96](https://github.com/justdan96/tsMuxer) - for today's development tsMuxer
- [videofan3d](https://sites.google.com/site/videofan3d) - for BDtools
- [libbluray](https://code.videolan.org/videolan/libbluray.git) - for open source
## Usage
- Look [usage](https://github.com/abakum/tsmuxerCLI/blob/master/usage.eng.txt) for Linux
- Смотри [использование](https://github.com/abakum/tsmuxerCLI/blob/master/usage.rus.txt) для Windows

### ex:

```
tsmuxer.py my.ts i.mkv+ =S -
```
creates `my.ts` from `i.mkv` without the subtitle tracks
```
tsmuxer.py my.meta i.mkv+
```
creates `my.meta` from `i.mkv`
```
tsmuxer.py my.meta . =_text =1 ! -
```
demultiplexes the first SRT subtitle track into the current directory
```
tsmuxer.py rus.iso BD/BDMV/PLAYLIST/00001.mpls+ =V + =rus ! -
```
muxes `rus.iso` from the video track and the tracks with `rus` in it
```
tsmuxer.py AVCHD --avchd BD+ =mvc -
```
if `BD/` has `BDMV/PLAYLIST/` will find first mpls (ex `00000.mpls`) excludes the MVC track and muxes 2D AVCHD
```
tsmuxer.py 42.ts --cut-start=28320ms --cut-end=184320ms 00042.MTS+ =S - 00042.srt+ ,timeshift=28320ms ,lang=rus ,font-name="Impact" ,font-size=65 ,font-color=0xffffffff ,bottom-offset=24 ,font-border=5 ,fadein-time=0.25 ,fadeout-time=1 ,text-align=center ,lang=rus
```
cuts `00042.MTS`, strips all the subtitles from it, adds SRT subtitle tracks from `00042.srt`, saves given the SRT options to `tsmuxer.json`, and outputs `42.ts`
```
tsmuxer.py BD --blu-ray 42.ts+43.ts
```
glues 42.ts and 43.ts into the blu-ray directory `BD` Omitted SRT options will be read from `tsmuxer.json`
```
tsmuxer.py MT --blu-ray 42.ts+ --mplsOffset=1 --m2tsOffset=10 
tsmuxer.py MT --blu-ray 43.ts+ --mplsOffset=2 --m2tsOffset=20 
tsmuxer.py MT
```
makes 2-title blu-ray directory `MT` where `tsmuxer.py MT` rebuild index.bdmv and MovieObject.bdmv with help of MPLS2JSON.exe 
```
tsmuxer.py BD3D1 --blu-ray 3D1.mkv+
```
creates the blu-ray directory `BD3D1` from `3D1.mkv`
```
tsmuxer.py BD3D --blu-ray list.txt
```
if in file `list.txt` is `BD3D1+BD3D2` then glues `BD3D1` with `BD3D2` into the blu-ray directory `BD3D`

```
tsmuxer.py dir_with_demuxed a.ts+ =track=4352 + =track=4353 ! -
```
or 
```
tsmuxer.py dir_with_demuxed a.ts+ =track=0x1100 + =track=0x1101 ! -
```
demuxed track 0x1100 and track 0x1101 from a.ts to dir_with_demuxed
