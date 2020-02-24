# tsmuxer.py
Helper for tsMuxeR - not GUI but CLI
## Credits
- Roman Vasilenko - for creating tsMuxeR 
- https://github.com/justdan96/tsMuxer - for today's development tsMuxer
## Usage
tsmuxer.py [tsMuxeR[.exe]] [fm.meta] [fo.ext|do] [--muxOpt] fiList fiSel -|fiOptList fiList2 fiSel2 -|fiOptList2 ... fiListLast fiSelLast -|fiOptListLast

### where:
 - tsMuxeR - tsMuxeR executable. If omitted, it will be searched in the directory where `tsmuxer.py` is located
 - fm.meta - metadata file. If "fiList" is present, "fm.meta" will be created by running
 ```
 tsMuxeR[.exe] fi.ext
 ```
 Otherwise the given `fm.meta` will be used.
 - fo.ext - output file with extension:
   - .iso - --blu-ray --label="fo" will be added to muxOpt
   - .ts, .m2ts, .mts - --demux --blu-ray --avchd will be removed from muxOpt

 - do - output directory for demux, blu-ray, or avchd. If `fo.ext` and `do` are omitted then
 ```
 tsMuxeR[.exe] fm.meta fo.ext|do
 ```
 won't be started
 - muxOpt - options to be prepened to the "fm.meta"
 - fiList, ... fiListLast - list of the media files to be glued. Has the following syntax: `fi+[fi2[+...+fiLast]]`
 - fiSel, ... fiSelLast - list of the tracks selectors. Has the following syntax: `[=selTr] [!] [+] [=selTr2] ... [!] [+] [=selTrLast]`
   - selTr - is one of the following options:
           - V - selects the video tracks
           - A - selects the audio tracks
           - S - selects the subtitle tracks
           - "foo bar", foobar - selects the tracks with the given substring
           - \[0-9\](0-9) - selects the track by its number
   - ! - inverts the track selection
   - \+ - adds to the selection the tracks that match the next `selTr`. If omitted, selects the tracks that match both the previous `selTr` and the next `selTr`
 - \- - comments all the selected tracks in the "fm.meta" file, then selects all the tracks of current `fiList`
 - = - selects all the tracks of the current "fiList". Cancels all the previous `selTr`
 - fiOptList - changes the options of the selected tracks. Has the following syntax: `,fiOpt[ ,fiOpt2[... ,fiOptLast]]`
### ex:
```
tsmuxer.py i.mkv+ my.ts =S -
```
creates `i.mkv.meta` from `i.mkv`, excludes the subtitle tracks from it and produces `my.ts`
```
tsmuxer.py i.mkv+ my.meta
```
creates `my.meta` from `i.mkv`
```
tsmuxer.py my.meta . =_text =1 ! -
```
demultiplexes the first srt subtitle track into the current directory
```
tsmuxer.py BD/BDMV/PLAYLIST/00001.mpls+ rus.iso =V + =rus ! -
```
muxes the BD file `rus.iso` from the video track and the tracks with "rus" in it
```
tsmuxer.py --avchd BD/BDMV/PLAYLIST/00001.mpls+ AVCHD =mvc -
```
muxes 2D AVCHD from the given BD3D
```
tsmuxer.py --blu-ray --cut-start=28320ms --cut-end=184320ms 00042.MTS+ 42.ts =S - 00042.srt+ ,timeshift=28320 ,font-name=Impact ,font-size=65 ,font-color=0xffffffff ,bottom-offset=24 ,font-border=5 ,fadein-time=0.25 ,fadeout-time=1 ,text-align=center ,lang=rus
```
cuts 00042.MTS, strips all the subtitles from it, adds srt subtitle tracks from `00042.srt`, and outputs `42.ts`
```
tsmuxer.py --blu-ray 42.ts+43.ts BD
```
glues `42.ts` and `43.ts` into the blu-ray directory `BD`
```
tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 3D1.mkv+ BD3D1
```
creates the blu-ray directory `BD3D1` from `3D1.mkv`
```
tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 BD1/BDMV/PLAYLIST/00001.mpls+BD2/BDMV/PLAYLIST/00001.mpls BD3D
```
glues `BD3D1` and `BD3D2` into the blu-ray directory `BD3D`
