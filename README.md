# tsmuxer.py
Helper for tsMuxeR - not GUI but CLI
## Credits
- Roman Vasilenko - for creating tsMuxeR 
- [justdan96](https://github.com/justdan96/tsMuxer) - for today's development tsMuxer
## Usage
- Look [usage](https://github.com/abakum/tsmuxerCLI/blob/master/usage.eng.txt)
- Смотри [использование](https://github.com/abakum/tsmuxerCLI/blob/master/usage.rus.txt)

### ex:
```
tsmuxer.py my.ts i.mkv+ =S -
```
creates `i.mkv.meta` from `i.mkv`, excludes the subtitle tracks from it and produces `my.ts`
```
"tsmuxer.py my.meta i.mkv+"
```
creates `my.meta` from `i.mkv`
```
tsmuxer.py my.meta . =_text =1 ! -
```
demultiplexes the first srt subtitle track into the current directory
```
tsmuxer.py rus.iso BD/BDMV/PLAYLIST/00001.mpls+ =V + =rus ! -
```
muxes the BD file `rus.iso` from the video track and the tracks with "rus" in it
```
tsmuxer.py AVCHD --avchd BD/BDMV/PLAYLIST/00001.mpls+ =mvc -
```
muxes 2D AVCHD from the given BD3D
```
tsmuxer.py 42.ts --cut-start=28320ms --cut-end=184320ms 00042.MTS+ =S - 00042.srt+ ,timeshift=28320 ,lang=rus ,font-name="Impact" ,font-size=65 ,font-color=0xffffffff ,bottom-offset=24 ,font-border=5 ,fadein-time=0.25 ,fadeout-time=1 ,text-align=center ,lang=rus
```
cuts `00042.MTS`, strips all the subtitles from it, adds SRT subtitle tracks from `00042.srt`, saves given the SRT options to `tsmuxer.json` and outputs `42.ts`
```
tsmuxer.py BD --blu-ray 42.ts+43.ts
```
glues `42.ts` and `43.ts` into the blu-ray directory `BD`. Omitted SRT options will be read from `tsmuxer.json`
```
tsmuxer.py BD3D1 --blu-ray --mplsOffset=1 --m2tsOffset=1 3D1.mkv+
```
creates the blu-ray directory `BD3D1` from `3D1.mkv`
```
tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 BD1/BDMV/PLAYLIST/00001.mpls+BD2/BDMV/PLAYLIST/00001.mpls BD3D
```
glues `BD3D1` and `BD3D2` into the blu-ray directory `BD3D`
