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
 - tsMuxeR - tsMuxeR executable. If omitted then it will be search in directory with tsmuxer.py
 - fm.meta - metadata file. If fiList not omitted then fm.meta will be created by "tsMuxeR fi.ext" and edit
           otherwise will be read and edit
 - fo.ext - output file with ext: .iso (--blu-ray and  --label="fo" will be added to muxOpt) .ts .m2ts .mts (--demux --blu-ray --avchd will be removed from muxOpt)
 - do - output directory for demux or blu-ray or avchd
      if fo.ext|do  omitted then "tsMuxeR fm.meta fo.ext|do" will not be started
 - muxOpt - options for first line of fm.meta
 - fiList, ... fiListLast - list of media files like fi+[fi2[+...+fiLast]] to be glued.
 - fiSel, ... fiSelLast - list of tracks selectors like [=selTr] [!] [+] [=selTr2] ... [!] [+] [=selTrLast]
 - selTr - is (V|A|S)|"foo bar"|foobar|\[0-9\](0-9) where fiOpt after:
  - V - will change only applicable video tracks
  - A - will change only applicable audio tracks
  - S - will change only applicable subtitle tracks
  - "foo bar", foobar - will change only applicable tracks that this substrings is included in
  - \[0-9\](0-9) - will change only applicable track with this number
 - ! - inverts selected tracks
 - \+ - will cause tracks matching the conditions of the next selTr to be added to the currently selected tracks.
     If omitted, the current selected tracks will be tracks matching both the previous selTr and the next selTr
 - \- - comment all selected before tracks by add # to the begin line of fm.meta lines, then select all the tracks
 - = - will select all the tracks of current fiList. Cancels the effect of all previously entered selTr
 - fiOpt - will change option for selected before and applicable tracks of fm.meta
ex:

 - "tsmuxer.py i.mkv+ my.ts =S -" will create i.mkv.meta and my.ts without subtitle tracks from i.mkv
 - "tsmuxer.py i.mkv+ my.meta" will create only my.meta from i.mkv
 - "tsmuxer.py my.meta . =_text =1 ! -" demultiplexes the first srt subtitle track to the current directory
 - "tsmuxer.py BD/BDMV/PLAYLIST/00001.mpls+ rus.iso =V + =rus ! -" will be muxed BD with video track and tracks for Russian
 - "tsmuxer.py --avchd BD/BDMV/PLAYLIST/00001.mpls+ AVCHD =mvc -" from BD3D will be muxed 2D AVCHD
 - "tsmuxer.py --cut-start=28320ms --cut-end=184320ms 00042.MTS+ 42.ts =S - 00042.srt+ ,timeshift=28320 ,font-name="Impact" ,font-size=65 ,font-color=0xffffffff ,bottom-offset=24 ,font-border=5 ,fadein-time=0.25 ,fadeout-time=1 ,text-align=center ,lang=rus"
             will be cut 00042.MTS, strip all its subtitles and add srt subtitle tracks from 00042.srt
 - "tsmuxer.py 42.ts+43.ts BD" glued 42.ts and 43.ts to blu-ray directory BD
 - "tsmuxer.py --mplsOffset=1 --m2tsOffset=1 3D1.mkv BD3D1" will be write to blu-ray directory BD3D1 from 3D1.mkv
 - "tsmuxer.py --mplsOffset=1 --m2tsOffset=1 BD1/BDMV/PLAYLIST/00001.mpls+BD2/BDMV/PLAYLIST/00001.mpls BD3D"
             will be glued BD3D1 and BD3D2 to blu-ray directory BD3D
