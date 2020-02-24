# tsmuxer.py
Helper for tsMuxeR - not GUI but CLI
# Credits
- Roman Vasilenko - for creating tsMuxeR 
- https://github.com/justdan96/tsMuxer - for today's development tsMuxer

# Usage
tsmuxer.py [tsMuxeR[.exe]] [fm.meta] [fo.ext|do] [--muxOpt] \
fiList fiSel (-|,fiOpt) \
fiList2 fiSel2 (-|,fiOpt2) \
...
fiListLast fiSelLast (-|,fiOptLast)

where:
 - tsMuxeR - tsMuxeR executable. If omitted, then I will search it in the directory with tsmuxer.py
 - fm.meta - metadata file. If fiList is not omitted, then fm.meta will be created from "tsMuxeR fi.ext" and edited
           otherwise it will be read and edited
 - fo.ext - output file with extension:
   + .iso - the options --blu-ray and --label="fo" will be added to muxOpt
   + .ts .m2ts .mts - the options --demux --blu-ray --avchd will be removed from muxOpt
 - do - output directory for demux or blu-ray or avchd
   if fo.ext|do is omitted, then "tsMuxeR fm.meta fo.ext|do" will not start
 - muxOpt - options for first line of fm.meta
 - fiList, ... fiListLast - a list of media files of the form: fi+[fi2[+...+fiLast]] that will be glued.
 - fiSel, ... fiSelLast - a list of track selectors of the form: [=selTr] [!] [+] [=selTr2] ... [!] [+] [=selTrLast]
 - selTr - is (V|A|S)|"foo bar"|foobar|[0-9](0-9) where fiOptList after:
  - V - will only change the options applicable to video tracks
  - A - will only change soundtrack options
  - S - will only change the options applicable to the subtitle tracks
  - "foo bar", foobar - will change the applicable options of only those tracks that have this substring
  - \[0-9\](0-9) - will change the applicable options for the track with this number
 - ! - inverts the list of selected tracks
 - \+ - in the list: =selTr + =selTr2 will add to the list of tracks selected =selTr tracks that match the condition =selTr2
     If omitted: =selTr =selTr2 then only tracks that satisfy both conditions will remain in the list of selected tracks
 - \- - comment out all the selected tracks, adding # to the beginning of the lines fm.meta, then select all the fiList tracks
 - = - will select all the tracks of the current fiList. Cancels the effect of all previously entered selTr
 - fiOptList - a list of options of the form: ,fiOpt [,fiOpt2 [...,fiOptLast]] will change the applicable options for previously selected tracks fm.meta
ex:
 - "tsmuxer.py i.mkv+ my.ts =S -" will create i.mkv.meta and my.ts without subtitle tracks from i.mkv
 - "tsmuxer.py i.mkv+ my.meta" will create only my.meta from i.mkv
 - "tsmuxer.py my.meta . =_text =1 ! -" demultiplexes the first srt subtitle track to the current directory
 - "tsmuxer.py BD/BDMV/PLAYLIST/00001.mpls+ rus.iso =V + =rus ! -" will create rus.iso with video tracks and tracks for those who understand the Russian language
 - "tsmuxer.py --avchd BD/BDMV/PLAYLIST/00001.mpls+ AVCHD =mvc -" from BD3D will make 2D AVCHD
 - "tsmuxer.py --cut-start=28320ms --cut-end=184320ms 00042.MTS+ 42.ts =S - 00042.srt+ ,timeshift=28320 ,font-name="Impact" ,font-size=65 ,font-color=0xffffffff ,bottom-offset=24 ,font-border=5 ,fadein-time=0.25 ,fadeout-time=1 ,text-align=center ,video-width=1920 ,video-height=1080 ,fps=50.0 ,lang=rus"
             will cut 00042.MTS, discard its subtitles and add subtitles from 00042.srt
 - "tsmuxer.py --blu-ray 42.ts+43.ts BD" glued 42.ts and 43.ts to blu-ray directory BD
 - "tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 3D1.mkv+ BD3D1" writes blu-ray from 3D1.mkv to the BD3D1 directory
 - "tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 BD1/BDMV/PLAYLIST/00001.mpls+BD2/BDMV/PLAYLIST/00001.mpls BD3D"
             combine BD3D1 and BD3D2 and write to BD3D
