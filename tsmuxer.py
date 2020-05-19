#!/usr/bin/python
# coding=utf8
#
'''
Helper for tsMuxeR - not GUI but CLI
'''
from __future__ import print_function, division, unicode_literals
d=0 #debug
__metaclass__ = type
def ac(eio):
 import sys, locale, os, codecs
 global py3, u8, acp, de, en
 py3=sys.version_info.major>2
 u8="utf-8"
 acp=locale.setlocale(locale.LC_ALL, "").partition(".")[2] or u8
 global de, en
 de, en =(lambda s : s,
          lambda s : s) if py3 else (
          lambda s : s.decode(acp),
          lambda s : s.encode(acp))
 mingw="MINGW_PREFIX" in os.environ
 if mingw: pass #dirty fix misdetection of sys.stdout.encoding as cpXXXX in mingw@Mintty
 elif py3 or not eio.isatty() or eio.encoding.lstrip("cp")==acp: return
 setattr(sys, eio.name.strip("<>"), codecs.getwriter(u8 if mingw else
                                                     acp)(eio.detach() if py3 else
                                                          eio))
 ps(eio, "encoding='%s'"%eio.encoding, acp)

import sys, locale, os, codecs, subprocess, inspect, json, bdon
from glob import glob
from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta

shell="SHELL" in os.environ

def makeMO():
 jmo={"MOBJ": {
 "version_number": "0200",
 "reserved_header": [0],
 "MovieObjects":[],
 }
}
 jm=jmo["MOBJ"]["MovieObjects"]
 #0 FirstPlayback for not java
 jm+=[{
 "resume_intention_flag": 0,
 "menu_call_mask": 0, "title_search_mask": 0, "reserved01": 0,
 "NavigationCommand": [{
  "command": "Move reg_4 2"
}, {
  "command": "Jump_Title 1"
}]}]
 #1 TopMenu for java
 jm+=[{
 "resume_intention_flag": 0,
 "menu_call_mask": 0, "title_search_mask": 0, "reserved01": 0,
 "NavigationCommand": [{
  "command": "Nop"
}]}]
 #2 Title for 2D
 jm+=[{
 "resume_intention_flag": 1,
 "menu_call_mask": 0, "title_search_mask": 0, "reserved01": 0,
 "NavigationCommand": [{
  "command": "SetOutputMode 0"
}, {
  "command": "Move reg_4 psr_4"
}, {
  "command": "Add reg_4 1"
}, {
  "command": "Play_PL psr_4"
}, {
  "command": "Jump_Title reg_4"
}]}]
 #3 LastTitle for 2D
 jm+=[{
 "resume_intention_flag": 1,
 "menu_call_mask": 0, "title_search_mask": 0, "reserved01": 0,
 "NavigationCommand": [{
  "command": "SetOutputMode 0"
}, {
  "command": "Move reg_4 1"
}, {
  "command": "Play_PL psr_4"
}, {
  "command": "Jump_Title reg_4"
}]}]
 #4 TopMenu for not java
 jm+=[{
 "resume_intention_flag": 1,
 "menu_call_mask": 0, "title_search_mask": 0, "reserved01": 0,
 "NavigationCommand": [{
  "command": "Jump_Title reg_4"
}]}]
 #5 Title for 3D
 jm+=[{
 "resume_intention_flag": 1,
 "menu_call_mask": 0, "title_search_mask": 0, "reserved01": 0,
 "NavigationCommand": [{
  "command": "SetOutputMode 1"
}, {
  "command": "Move reg_4 psr_4"
}, {
  "command": "Add reg_4 1"
}, {
  "command": "Play_PL psr_4"
}, {
  "command": "Jump_Title reg_4"
}]}]
 #6 LastTitle for 3D
 jm+=[{
 "resume_intention_flag": 1,
 "menu_call_mask": 0, "title_search_mask": 0, "reserved01": 0,
 "NavigationCommand": [{
  "command": "SetOutputMode 1"
}, {
  "command": "Move reg_4 1"
}, {
  "command": "Play_PL psr_4"
}, {
  "command": "Jump_Title reg_4"
}]}]
 #7 FirstPlayback for java
 jm+=[{
 "resume_intention_flag": 0,
 "menu_call_mask": 0, "title_search_mask": 0, "reserved01": 0,
 "NavigationCommand": [{
  "command": "SetOutputMode 1"
}, {
  "command": "Move reg_4 2"
}, {
  "command": "Jump_Title 1"
}]}]
 return jmo

def do():
 bd=bdon.BD(fo)
 if not bd.ver: return
 if 0:
  global f2
  f2=fe.replace(name(argv[0]), "MPLS2JSON")
  nf(f2)
  PLAYLIST=os.path.join(fo, "BDMV", "PLAYLIST")
  if not os.path.isdir(PLAYLIST): return                                          
  pl=sorted(glob(PLAYLIST+"/[0-9][0-9][0-9][0-9][0-9].mpls"))
  lenpl=len(pl)
  if not lenpl: return
 lenpl=bd.read("*.mpl*")
 #ps(json.dumps(makeMO(), sort_keys=True, indent=4))
 if 1:
  bd.read("*.bdm*")
  #ps(json.dumps(bd.mov.json, indent=4))
  bd.mov.write(makeMO())
  #ps(json.dumps(bd.mov.read(), indent=4))
 else:
  mo=bdon.MOBJ(fo)
  #ps(json.dumps(mo.read(), indent=4))
  mo.write(makeMO())
 matrix='''
2D             object_type playback_type mobj_id_ref bdjo_file_name
FirstPlayback  1           0             0           x
TopMenu        1           1             4           x
Title          1           0             2           x
TitleLast      1           0             3           x

3D             object_type playback_type mobj_id_ref bdjo_file_name
FirstPlayback  1           0             0           x
TopMenu        1           1             4           x
Title          1           0             5           x
TitleLast      1           0             6           x

2Djava         object_type playback_type mobj_id_ref bdjo_file_name
FirstPlayback  1           0             7           x
TopMenu        1           1             1           x
TitleFirst     2           2             x           00000
Title          1           0             2           x
TitleLast      1           0             3           x

3Djava         object_type playback_type mobj_id_ref bdjo_file_name
FirstPlayback  1           0             7           x
TopMenu        1           1             1           x
TitleFirst     2           2             x           00000
Title          1           0             5           x
TitleLast      1           0             6           x
'''
 tl=[]
 for ti, mpl in enumerate(bd.mpl):
  tl+=[{
 "object_type": bdon.indx_object_type_hdmv,
 "access_type": 0, "reserved01": 0,
 "playback_type": bdon.indx_hdmv_playback_type_movie, "reserved02": 0,
 "mobj_id_ref": (2 if ti<lenpl-1 else 3)+mpl.SS_content, "reserved03": 0
}]
 bdjo=bd.read("*.bdjo")>0
 if bdjo:
  tl[0]={
 "object_type": bdon.indx_object_type_bdj, "access_type": 0, "reserved01": 0,
 "playback_type": bdon.indx_bdj_playback_type_movie, "reserved02": 0,
 "bdjo_file_name": name(bd.select("*.bdjo")[0]), "reserved03": 0,
}
 jn={
 "INDX": {
  "version_number": "0300" if bd.is4K or bd.isV3 else "0200", "reserved_header": [0],
  "AppInfoBDMV": {"reserved01": 0,
   "initial_output_mode_preference": bd.initial_output_mode_preference,
   "SS_content_exist_flag": bd.SS_content_exist_flag, "reserved02": 0,
   "video_format": "0", "frame_rate": "0",
   "content_provider_user_data": list(map(ord, (os.path.basename(argv[0])+"\0"*32)[:32])),
  },
  "Indexes": {
   "FirstPlayback": {
    "object_type": bdon.indx_object_type_hdmv, "access_type": 0, "reserved01": 0,
    "playback_type": bdon.indx_hdmv_playback_type_movie, "reserved02": 0,
    "mobj_id_ref": 7*bd.SS_content_exist_flag*bdjo, "reserved03": 0,
   },
   "TopMenu": {
    "object_type": bdon.indx_object_type_hdmv, "access_type": 0, "reserved01": 0,
    "playback_type": bdon.indx_hdmv_playback_type_interactive, "reserved02": 0,
    "mobj_id_ref": 1 if bdjo else 4, "reserved03": 0,
   },
   "Title": tl
  }
 }
}
 if bd.uhd!=1: jn["INDX"]["ExtensionData"]=[bd.UHD]
 if 0: ps(jn)
 else:
  #ps(json.dumps(bd.bd["index.bdmv"].json, sort_keys=True, indent=4))
  #ps(json.dumps(jn, sort_keys=0, indent=4))
  bd.ind.write(jn)
  #ps(json.dumps(bd.ind.read(), sort_keys=0, indent=4))

def tsMuxeR(*arg):
 if len(arg)>1:
  cmd=(fe,)+arg[:2]
  ps(cmd)
  if 1:
   try: err=subprocess.call(map(en, cmd))
   except OSError as e: ps(str(e))
  else:
   p=subprocess.Popen(map(en, cmd), bufsize=0, universal_newlines=True, stdout=subprocess.PIPE)
   for line in iter(p.stdout.readline, ""): print(line, end="")
  return
 if 0: return r'''MUXOPT --no-pcr-on-video-pid --vbr --vbv-len=500
V_MPEG4/ISO/AVC, 00045.MTS, track=4113
A_AC3, 00045.MTS, track=4352
S_HDMV/PGS, 00045.MTS, fps=50, track=4608
S_TEXT/UTF8, "D:\AV\2020\20200111 ДР Аллы.mkv", font-name="Arial", font-size=65, font-color=0xffffffff, bottom-offset=24, font-border=5, text-align=center, video-width=1920, video-height=1080, fps=50, track=4, lang=rus'''.splitlines()
 fl=arg[0].split("+")
 dur=0.0
 global cha
 for i, f in enumerate(fl):
  nf(f)
  cmd=(fe,)+(f,)
  ps(cmd)
  try: bu=subprocess.check_output(map(en, cmd))
  except subprocess.CalledProcessError as e:
   ps("return code:", e.returncode)
   ps("return text:", e.output)
   exit(1)
  except OSError as e:
   ps(str(e))
   exit(1)
  if not i:
   if bu.startswith(b"Network"):
    global fme
    fme=acp
  r=bu.decode(fme)
  print(r)
  me={}
  li=("Track ID:", "Stream type:", "Stream ID:", "Stream info:", "Stream lang:", "subTrack:")
  lii=("Marks:", "Duration:", "Stream delay:", "start-time:")
  for l in r.splitlines():
   for s in li+lii:
    if l.startswith(s):
     if not s in me: me[s]=[]
     me[s]+=[l[len(s):].strip()]
  if not "Stream info:" in me:
   ps('Not found tracks in "%s"'%f)
   exit(1)
  me["Chapters:"]=[]
  if "Marks:" in me:
   for ch in me["Marks:"]: me["Chapters:"]+=ch.split()
   cha+=[dur+t2f(x) for x in me["Chapters:"]]
  if "Duration:" in me: dur+=t2f(me["Duration:"][0])
  if i: continue
  for sl in me["Stream info:"]:
   for su in ("Profile:", "Resolution:", "Frame rate:", "Bitrate:", "Sample Rate:", "Channels:"):
    if su in sl:
     if not su in me: me[su]=sl.partition(su+" ")[2].split()[0]
  if "Resolution:" in me:
   me["Width:"], me["Height:"]=me["Resolution:"].split(":")[:2]
   me["Height:"]=me["Height:"].rstrip("ip.")
  for whf in ("Width:", "Height:", "Frame rate:"):
   if whf in me and whf not in mg: mg[whf]=me[whf]
  for x in lii[1:]:
   if su in me: me[su]=me[su][0]
  ll="MUXOPT --no-pcr-on-video-pid --new-audio-pes --vbr --vbv-len=500".split()
  #if "Chapters:" in me and len(me["Chapters:"])>1: ll+=["--custom-chapters=%s"%";".join(me["Chapters:"])]
  if "start-time:" in me: ll+=["--start-time=%s"%me["start-time:"][0]]
  if d: ps("me:", me)
  mm=[" ".join(ll)]
  qfi='"%s"'%'"+"'.join(fl)
  for t, tl in enumerate(me["Stream ID:"]):
   ll=[tl]
   ll+=[qfi]
   if "Track ID:" in me: ll+=['track=%s'%me["Track ID:"][t]]
   if "subTrack:" in me and len(me["subTrack:"])>t: ll+=['subtrack=%s'%me["subTrack:"][t]]
   if "Stream lang:" in me and me["Stream lang:"][t]: ll+=['lang=%s'%me["Stream lang:"][t]]
   if "/i" in tl.lower():
    ll+=["insertsei"]
    ll+=["contsps"]
   if "s"==tl.lower().lstrip("#")[0]:
    for lgd in (me, mg):
     if "Frame rate:" in lgd:
      ll+=['fps='+lgd["Frame rate:"]]
      break
    if "/u" in tl.lower():
     for lgd in (me, mg):
      if "Width:" in lgd:
       ll+=['video-width='+lgd["Width:"]]
       break
     for lgd in (me, mg):
      if "Height:" in lgd:
       ll+=['video-height='+lgd["Height:"]]
       break
   mm+=[", ".join(ll)]
  if d: ps("mm:", mm)
 return mm

def ext(f):
 return de(os.path.splitext(f)[1]).lower().lstrip(os.extsep)

def name(f):
 return de(os.path.splitext(os.path.basename(f))[0])

def rep(p, a="", t=0):
 #ps("rep",p,a,t)
 if t and t not in sdl[fin]: return #t is not selected track
 if a.endswith("="): #--demux=
  ms[t]-={sed(p, -1)}
 else: ms[t]|={sed(p, t)}

def usage(ec=0):
 ps(argv)
 ps("fe:", fe, "fi:", fi, "fm:", fm, "fo:", fo)
 j=fj if ec else "tsmuxer.json"
 print(r'''%s [tsMuxeR%s] [fm.meta] [fo.ext|do] \
[--muxOpt] \
[--muxOpt2] \
...
[--muxOptLast] \
fiList fiSel [-] [fiOptList] \
fiList2 fiSel2 [-] [fiOptList2] \
...
fiListLast fiSelLast [-] [fiOptListLast]'''%(argv[0] if ec else "tsmuxer.py", exe if ec else "[.exe]"))
 tr("", 'где:',
        'where:')
 tr(' tsMuxeR - ', 'исполняемый файл tsMuxeR. Если опущен, то буду искать в каталоге где находится tsmuxer.py',
                   'executable. If omitted, it will be searched in the directory where `tsmuxer.py` is located')
 tr(' fm.meta - ', 'файл метаданных. Если fiList не опущен, то fm.meta будет создан путём запуска `tsMuxeR fi.ext`',
                   'metadata file. If `fiList` is present, `fm.meta` will be created by running `tsMuxeR fi.ext`.')
 tr('           ', 'и отредактирован. В противном случае будет прочитан из fm.meta и отредактирован.',
                   'Otherwise the given `fm.meta` will be used.')
 tr(' fo.ext - ', 'выходной файл с расширениями:',
                  'output file with extensions:')
 tr('  .iso - ', 'в muxOpt будут добавлены опции --blu-ray и --label="fo"',
                 'options --blu-ray --label="fo" will be added to muxOpt')
 tr('  .ts, .m2ts, .mts - ', 'из muxOpt будут удалены опции --demux --blu-ray ---avchd',
                             'options --demux --blu-ray --avchd will be removed from muxOpt')
 tr(' do - ', 'выходной каталог для demux, blu-ray или avchd.',
              'output directory for demux, blu-ray or avchd.')
 tr('      ', 'если fo.ext и do опущены, то `tsMuxeR fm.meta fo.ext|do` не будет запущен',
              "if `fo.ext` and `do` are omitted then `tsMuxeR fm.meta fo.ext|do` won't be started")
 tr('      ', 'если fm.meta и все fiList опущены но указан do в котором есть do~BDMV~PLAYLIST~*.mpls, то do~BDMV~*.bdmv будут откорректированы чтоб блюрей стал мультитайтловым',
              'if `fm.meta` and all `fiList` are omitted but present `do` with `do~BDMV~PLAYLIST~*.mpls` then `do~BDMV~*.bdmv` will be adjusted so that the bluray becomes multi-title')
 tr('      ', 'MPLS2JSON.exe из BDTools https://forum.doom9.org/showthread.php?t=174563 используется для этого. Сделай ссылку на него или скопируй туда где %s'%(fe if ec else "tsMuxeR.exe"),
              '`MPLS2JSON.exe` from BDTools https://forum.doom9.org/showthread.php?t=174563 is used for this. Make a link to it or copy to where `%s`'%(fe if ec else "tsMuxeR.exe"))
 tr(' muxOpt, ... muxOptLast - ', 'опции для первой строки fm.meta',
                                  'options to be prepened to the first line of `fm.meta`')
 tr(' fiList, ... fiListLast - ', 'список медиафайлов которые будут склеены. Имеют вид: fi+[fi2[+ ...+fiLast]]',
                                  'list of the media files to be glued. Has the following syntax: `fi+[fi2[+...+fiLast]]`')
 tr('                          ', 'Если вместо fiList  указать fil.txt то fiList в кодировке UTF8 будет прочитан из fil.txt',
                                  'If instead of `fiList` specify `fil.txt` then `fiList` in UTF8 encoding will be read from `fil.txt`')
 tr('  fi, ... fiLast - ', 'это один из вариантов:',
                           'is one of the following variants:')
 tr('   file.ext - ', 'имя медиа файла который добавится к склейке',
                      'name of the media file that is added to the gluing')
 tr('   BD, AVCHD - ', 'каталоги в которых есть BDMV~PLAYLIST~ добавит в склейку первый файл',
                       'directories in which there is `BDMV~PLAYLIST~` adds the first file to the gluing')
 tr('   directory - ', 'каталог в котором нет BDMV~PLAYLIST~ добавляет в склейку все файлы каталога',
                       'a directory in which there is no `BDMV~PLAYLIST~` adds all files of directory to the gluing')
 tr('   "directory~pattern" - ', 'шаблон pattern с подстановочными символами: ? или * добавит в склейку все файлы в directory удовлетворяющие шаблону',
                                 'wildcard pattern: ? or * add to the gluing all files in `directory` matching the `pattern`')
 tr('  "directory**pattern" - ', 'рекурсивно добавит в склейку все файлы в directory удовлетворяющие шаблону *pattern',
                                 'recursively add to the gluing all the files in the `directory` matching the `*pattern`')
 tr(' fiSel, ... fiSelLast - ', 'список селекторов дорожек. Имеют вид: [=selTr] [!] [+] [=selTr2] ... [!] [+] [=selTrLast] [=]',
                                'list of the tracks selectors. Has the following syntax: `[=selTr] [!] [+] [=selTr2] ... [!] [+] [=selTrLast] [=]`')
 tr(' selTr - ', 'это одна из следующих опций:',
                 'is one of the following options:')
 tr('  V - ', 'выберет видео дорожки',
               'selects the video tracks')
 tr('  A - ', 'выберет звуковые дорожки',
               'selects the audio tracks')
 tr('  S - ', 'выберет дорожки субтитров',
               'selects the subtitle tracks')
 tr('  "foo bar", foobar - ', 'выберет только те дорожки, в которых есть эта подстрока',
                               'selects the tracks with the given substring')
 tr('  [0-9](0-9) - ', 'выберет дорожку с этим номером',
                        'selects the track by its number')
 tr('  ! - ', 'инвертирует список выбранных дорожек',
              'inverts the track selection')
 tr('  + - ', 'Если задан: `=selTr + =selTr2` то добавит в список дорожек выбранных selTr дорожки которые соответствуют условию selTr2.',
              'if present: `=selTr + =selTr2` selects `selTr` then adds to the selection the tracks that match `selTr2`.')
 tr('      ', 'Если опущен: `=selTr =selTr2` то в списке выбраннвх дорожек останутся только дорожки, удовлетворяющие обоим условиям',
              'If omitted: `=selTr =selTr2` selects the tracks that match both `selTr` and `selTr2`')
 tr('  = - ', 'выбирает все дорожки текущего fiList. Отменяет эффект всех ранее введенных selTr',
              'selects all the tracks of the current `fiList`. Cancels all the previous `selTr`')
 tr(' - - ', 'комментирует все выбранные дорожки, добавив # в начало строк fm.meta, затем выбирает все дорожки как =',
             'comment all selected tracks by adding # to the beginning of the lines `fm.meta`, then select all the tracks as =')
 tr(' fiOptList - ', 'список опций вида: ,fiOpt[ ,fiOpt2[... ,fiOptLast]] изменит применимые опции для выбранных ранее дорожек',
                     'changes the options of the selected tracks. Has the following syntax: `,fiOpt[ ,fiOpt2[... ,fiOptLast]]`')
 tr("", 'например:',
        'ex:')
 tr(' `tsmuxer.py my.ts i.mkv+ =S -`\n             ', 'создаст из i.mkv my.ts без дорожек субтитров',
                                                      'creates `my.ts` from `i.mkv` without the subtitle tracks')
 tr(' `tsmuxer.py my.meta i.mkv+` ', 'создаст только my.meta из i.mkv',
                                     'creates `my.meta` from `i.mkv`')
 tr(' `tsmuxer.py my.meta . =_text =1 ! -`\n             ', 'демультиплексирует первую дорожку SRT субтитров в текущий каталог',
                                                            'demultiplexes the first SRT subtitle track into the current directory')
 tr(' `tsmuxer.py rus.iso BD~BDMV~PLAYLIST~00001.mpls+ =V + =rus ! -`\n             ', 'создаст rus.iso с видео дорожками и дорожками для русскоязычных',
                                                                                       'muxes `rus.iso` from the video track and the tracks with `rus` in it')
 tr(' `tsmuxer.py AVCHD --avchd BD+ =mvc -` ', 'если в BD~ есть BDMV~PLAYLIST~ найдёт в нём первый mpls (например 00000.mpls)',
                                               'if `BD~` has `BDMV~PLAYLIST~` will find first mpls (ex `00000.mpls`)')
 tr('             ', 'отбросит MVC дорожку и сделает 2D AVCHD',
                     'excludes the MVC track and muxes 2D AVCHD')
 if 0: tr(' `tsmuxer.py fromDemuxed.ts fromDemuxed+` ', 'найдёт в fromDemuxed~ все дорожки и сделает fromDemuxed.ts',
                                                  'will find in `fromDemuxed~` all tracks and produces `fromDemuxed.ts`')
 print(' `tsmuxer.py 42.ts --cut-start=28320ms --cut-end=184320ms 00042.MTS+ =S - 00042.srt+ ,timeshift=28320ms ,lang=rus ,font-name="Impact" ,font-size=65 ,font-color=0xffffffff ,bottom-offset=24 ,font-border=5 ,fadein-time=0.25 ,fadeout-time=1 ,text-align=center ,lang=rus`')
 tr('             ', 'обрежет 00042.MTS, отбросит его субтитры, добавит субтитры из 00042.srt,',
                     'cuts `00042.MTS`, strips all the subtitles from it, adds SRT subtitle tracks from `00042.srt`,')
 tr('             ', 'запишет указанные SRT опции в `%s` и создаст 42.ts'%j,
                     'saves given the SRT options to `%s`, and outputs `42.ts`'%j)
 tr(' `tsmuxer.py BD --blu-ray 42.ts+43.ts` ' ,'склеит 42.ts и 43.ts в каталог блюрэя BD',
                                               'glues 42.ts and 43.ts into the blu-ray directory `BD`')
 tr('             ' ,'Опущенные опции SRT будут прочитаны из `%s`'%j,
                     'Omitted SRT options will be read from `%s`'%j)
 tr(' `tsmuxer.py MT --blu-ray 42.ts+ --mplsOffset=1 --m2tsOffset=10` ' ,'запишет первый тайтл блюрэя в MT',
                                               'creates the first title from 42.ts into the blu-ray directory `MT`')
 tr(' `tsmuxer.py MT --blu-ray 43.ts+ --mplsOffset=2 --m2tsOffset=20` ' ,'запишет второй тайтл блюрэя в MT',
                                               'creates the second title from 43.ts into the blu-ray directory `MT`')
 tr(' `tsmuxer.py MT` ' ,'MT~BDMV~*.bdmv будут откорректированы чтоб блюрей стал мультитайтловым',
                         '`MT~BDMV~*.bdmv` will be adjusted so that the bluray becomes multi-title')
 tr(' `tsmuxer.py BD --blu-ray MT~BDMV~PLAYLIST+`' ,'создаст однотайтловый BD из мультитайтлового блюрея MT',
                                                    'creates the one-title blu-ray `BD` from multi-tile blu-ray `MT`')
 tr(' `tsmuxer.py AVCHD --avchd MT**.*ts+`' ,'создаст однотайтловый AVCHD из мультитайтлового блюрэя MT',
                                             'creates the one-title AVCHD `AVCHD` from multi-tile blu-ray `MT`')
 tr(' `tsmuxer.py BD3D1 --blu-ray 3D1.mkv+` ' ,'запишет в каталог BD3D1 блюрэй из 3D1.mkv',
                                               'creates the blu-ray directory `BD3D1` from `3D1.mkv`')
 tr(' `tsmuxer.py BD3D --blu-ray list.txt` ' ,'если в файле list.txt будет `BD3D1+BD3D2`',
                                              'if in file `list.txt` is `BD3D1+BD3D2`')
 tr('             ' ,'то склеит BD3D1 с BD3D2 и запишет блюрэй BD3D',
                     'then glues `BD3D1` with `BD3D2` into the blu-ray directory `BD3D`')
 exit(ec)

def nf(f):
 if not os.path.isfile(f):
  ps('Not found file "%s"'%f)
  usage(1)

def ps(*l):
 print(" ".join(map(str, l))+"@"+", ".join(str(x[2]) for x in inspect.stack()[1:]))

def comm(t):
 if t: ml[t][0]="#"+ml[t][0].lstrip("#")

def sed(s, t):
 n, eq, v=s.partition("=")
 if t<0:
  if n in md[t]: md[t].pop(n)
 else: md[t][n]=v
 return n

def t2f(s):
 try: return sum([60**(2-i)*k for i, k in enumerate(map(float, (("0:0:"+s.replace(",", ".")).split(':'))[-3:]))])
 except: return 0.0
 
def f2t(s):
 return (datetime(1970, 1, 1)+timedelta(seconds=s)).strftime("%H:%M:%S.%f")[:12]

def tr(comm, rus, eng):
 print((comm+(rus if ru else eng)).replace("~", os.sep))

def dq(n, v):
 r=[di["c"].get(n, n)]
 if v:
  if n in di["q"] and v.strip('"')==v: v='"%s"'%v
  elif n.startswith("cut") and not set("ms")&set(v): v="%ims"%(t2f(v)*1000)
  elif n.startswith("time") and set(":.,")&set(v): v="%i"%(t2f(v)*1000)
  r+=[v]
 return "=".join(r)
 
if __name__!="__main__": exit()#---------------------------------------------------------------------------
MO={
 "demux",
 "blu-ray",
 "blu-ray-v3",
 "avchd",
}
MB={
 "vbr",
 "minbitrate",
 "maxbitrate",
 "cbr",
 "bitrate",
}
MC={
 "auto-chapters",
 "custom-chapters",
}
MS={
 "split-duration",
 "split-size",
}
M=MO|MB|MC|MS|{
 "pcr-on-video-pid",
 "new-audio-pes",
 "hdmv-descriptors",
 "vbv-len",
 "no-asyncio",
 "cut-start",
 "cut-end",
 "right-eye",
 "start-time",
 "mplsoffset",
 "m2tsoffset",
 "insertblankpl",
 "blankoffset",
 "label",
 "extra-iso-space",
}
VAS={
 "track",
 "lang",
}
di={}
di["v"]={
 "level",
 "insertsei",
 "forcesei",
 "contsps",
 "subtrack",
 "secondary",
 "pipcorner",
 "piphoffset",
 "pipvoffset",
 "pipscale",
 "piplumma",
}
di["V"]=VAS|di["v"]|{
 "fps",
 "delpulldown",
 "ar",
}
di["A"]=VAS|{
 "timeshift",
 "down-to-dts",
 "down-to-ac3",
 "secondary",
 "default",
}
di["S"]=VAS|{
 "timeshift",
 "fps",
 "3d-plane",
 "video-width",
 "video-height",
}
di["srt"]={
 "font-name",
 "font-color",
 "font-size",
 "font-italic",
 "font-bold",
 "font-underline",
 "font-strikeout",
 "bottom-offset",
 "font-border",
 "fadein-time",
 "fadeout-time",
 "line-spacing",
 "default",
}
di["s"]=di["S"]|di["srt"]
di["q"]={
 "font-name",
 "label",
}
di["c"]={
 "delpulldown": "delPulldown",
 "insertsei": "insertSEI",
 "forcesei": "forceSEI",
 "contsps": "contSPS",
 "subtrack": "subTrack",
 "pipcorner": "pipCorner",
 "piphoffset": "pipHOffset",
 "pipvoffset": "pipVOffset",
 "pipscale": "pipScale",
 "piplumma": "pipLumma",
 "mplsoffset": "mplsOffset",
 "m2tsoffset": "m2tsOffset",
 "insertblankpl": "insertBlankPL",
 "blankoffset": "blankOffset",
}

ac(sys.stdout)
fme=u8
ru=locale.getlocale()[0] in ("Russian_Russia", "ru_RU")
if sys.version_info<(3, 6): from collections import OrderedDict
else: OrderedDict = dict

#subprocess.call(map(en, ["clear" if shell else "cls"]), shell=True)
print("Пайтон %s.%s"%(sys.version_info.major, sys.version_info.minor), sys.executable, locale.getlocale())
argv=[de(x) for x in sys.argv]
exe=".exe" if os.name=="nt" or sys.platform in ("msys", "win32") else ""
opt="-+=,!"
fe=de(os.path.splitext(os.path.abspath(argv[0]))[0])
fj=fe+".json" #for SRT options
fe+=exe #tsMuxeR
fi="" #input files
fm="" #meta file
fo="" #output file or dir
if len(sys.argv)<2: usage() #./tsmuxer.py
ps(argv)
odl={} #dict of options
adl={} #dict of all tracks
sdl={} #dict of selected tracks
meta=[] #metadata dict
extl=("iso", "ts", "m2ts")
mo=0 #meta line copy
fin=0 #current fi
mg={} #default dict for whf
cha=[]
for a in argv[1:]:                                                       #parse arg
 if a.lower()=="-h":
  ru=not ru
  usage()
 if fin not in odl: odl[fin]=[]
 if a[0] in opt:
  odl[fin]+=[a]
  continue
 elif os.path.isdir(a) or ext(a) in extl or a.endswith(os.sep): fo=a
 elif set("+*?")&set(a) or ext(a)=="txt":                               #fi
  fin+=mo
  if ext(a)=="txt":
   nf(a)
   try:
    with codecs.open(a, encoding=u8) as f: a=f.read().replace('"', "")
   except: ps('Error read list of media files from "%s"'%f.name)
  a=a.strip("+")
  fil=[]
  for inp in a.split("+"):
   if set("*?")&set(inp):
    recur=inp.split("**")
    fil+=bdon.bdglob(recur[0], "*"+recur[1]) if len(recur)>1 else sorted(glob(inp))
   elif os.path.isdir(inp):
    PLAYLIST=os.path.join(inp, "BDMV", "PLAYLIST")
    if os.path.isdir(PLAYLIST): fil+=sorted(glob(PLAYLIST+"/*.mp*"))[:1]
    else: fil+=sorted(glob(os.path.join(inp, "*")))
   else: fil+=[inp]
  a="+".join(fil) 
  if not mo: fi=a
  temp=tsMuxeR(a)
  adl[fin]=set(range(len(meta)+1-mo, len(meta)+len(temp)-mo))
  sdl[fin]=adl[fin].copy()
  meta+=temp[mo:]
  mo=1
 elif ext(a)=="meta": fm=a
 elif ext(a)==exe.lstrip(os.extsep):
  nf(a)
  fe=a
 else: fo=a
if fi:
 if cha: meta[0]+=" --custom-chapters=%s"%";".join(map(f2t, sorted(set(cha))))
else:
 if not os.path.isfile(fm) and fo:
  do()
  exit()
 nf(fm)
 try:
  with codecs.open(fm, encoding=fme) as f: meta=f.read().splitlines() #read fm in utf-8
 except:
  fme=acp
  with codecs.open(fm, encoding=fme) as f: meta=f.read().splitlines() #read fm in acp
 adl[0]=set(range(1, len(meta)))
 sdl[0]=adl[0].copy()
if d:
 ps("meta:", meta)
 ps("odl:", odl)
 ps("adl:", adl)
 ps("sdl:", adl)
ml=[] #meta opt matrix
md=[] #meta dict matrix
ms=[] #meta sets matrix
mt={"v":[], "s":[]} #meta trac dict
for t, tl in enumerate(meta):                                       #parse meta
 ml.append(tl.split("," if t else "--"))
 xl=ml[t][0].upper().lstrip("#")
 x0=xl[0]
 if not x0 in mt: mt[x0]=[]
 mt[x0].append(t)
 if x0=="V" and "/ISO" in xl: mt["v"].append(t)
 if x0=="S" and "/UTF" in xl: mt["s"].append(t)
 md.append(OrderedDict())
 ms.append(set())
 for j, y in enumerate(ml[t]):
  y=y.strip()
  if j>(1 if t else 0): ms[t].add(sed(y, t))
  else: ml[t][j]=y.lstrip("#")
if d:
 ps("ml:", ml)
 ps("md:", md)
 ps("ms:", ms)
 ps("mt:", mt)
plus=0
for fin in odl:
 for a in odl[fin]:                                                 #parse options
  if a=="+":              #or
   plus=1
   continue
  if a in set("=-!"):
   print(sorted(sdl[fin]), a, "", end="")
   if a=="-":             #comment
    for t in sdl[fin]: comm(t)
   if a=="!": sdl[fin]=adl[fin]-sdl[fin] #invert
   else: sdl[fin]=adl[fin].copy()
   ps(sorted(sdl[fin]))
   plus=0
   continue
  if a.startswith("="):   #selector
   print(sorted(sdl[fin]), ("+ " if plus else "")+a, "", end="")
   a=a[1:]
   if a in set("VAS"):    #V
    if plus: sdl[fin]|=adl[fin]&set(mt[a[0]])
    else: sdl[fin]&=adl[fin]&set(mt[a[0]])
   elif a.isnumeric():    #=1
    if plus:
     if len(adl[fin])>int(a)-1: sdl[fin]|={list(adl[fin])[int(a)]-1}
    else:
     if len(sdl[fin])>int(a)-1: sdl[fin]={sorted(sdl[fin])[int(a)-1]}
   else:                  #substr
    hex=a.split("=0x")
    if len(hex)>1: a="=".join((hex[0], str(int(hex[1] ,16))))
    if plus:
     for t in adl[fin]:
      if a.lower() in ", ".join(ml[t]).lower(): sdl[fin]|={t}
    else:
     for t in sdl[fin].copy():
      if a.lower() in ", ".join(ml[t]).lower(): continue
      sdl[fin]-={t}
   ps(sorted(sdl[fin]))
   plus=0
   continue
  p=a.lstrip(opt).lower()
  p0=p.split("=")[0] #var name
  for MX in (MO, MB, MC):
   if p0 in MX: ms[0]-=MX
  if p0 in MC: ms[0]-=MS
  if p0 in M: rep(p, a)
  for tt in "VvASs":
   if p0 in di[tt]:
    for t in mt[tt]: rep(p, a, t)
if "bitrate" in ms[0]: rep("cbr")
else:
 if {"minbitrate", "maxbitrate"}&ms[0]: rep("vbr")
if ext(fo) in extl:
 ms[0]-=MO
 if ext(fo)==extl[0]:
  rep("blu-ray")
  if "label" not in ms[0]: rep('label="%s"'%os.path.splitext(os.path.split(fo)[1])[0])
if {"blu-ray", "avchd"}&ms[0]:
 rep("new-audio-pes")
 rep("hdmv-descriptors")
load={}
if os.path.isfile(fj):
 try: load=json.load(open(fj))
 except: ps('Error read SRT options from "%s"'%fj)
dump=load.copy()
for t in mt["s"]:                       
 for k in (di["srt"]|{"lang"})&ms[t]:   # from opt to file
  if md[t][k]: dump[k]=md[t][k]
 for k in set(load.keys())-ms[t]:       # from file to opt
  md[t][k]=load[k]
  ms[t]|={k}
if dump and dump!=load:
 try: json.dump(dump, fp=open(fj, "w"), sort_keys=True, indent=1)
 except: ps('Error save SRT options to "%s"'%fj)
for t, tl in enumerate(ml):             #serializ meta
 ll=[]
 for p in md[t]:
  if p in ms[t].copy():
   ms[t]-={p}
   ll+=[dq(p, md[t][p])]
 for p in ms[t]: ll+=[p]
 if t: meta[t]=", ".join(ml[t][:2]+ll)
 else: meta[t]=" --".join(ml[t][:1]+ll)
mfc="\n".join(meta)
print("8><---"+(fm or "fm.meta")+":\n"+mfc+"\n8><---")                                                    #print meta
if fo or fm:
 fmi=fm
 if not fmi:
  if 0: fm=fi.split("+")[0]+".meta"
  else:
   ft=NamedTemporaryFile()
   fm=ft.name
   ft.close()
 try: 
  if fo or fmi: print(mfc, file=codecs.open(fm, "w", encoding=fme), end="")#save meta
  if fo: tsMuxeR(fm, fo)                                                   #run tsMuxeR fm fo
 finally: 
  if not fmi: os.remove(fm)
