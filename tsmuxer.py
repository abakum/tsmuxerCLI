#!/usr/bin/python
# coding=utf8
#
'''
Helper for tsMuxeR - not GUI but CLI
'''
from __future__ import print_function, division, unicode_literals
d=0 #debug
__metaclass__ = type
import locale, codecs, os, sys
u8="utf-8"
acp=locale.setlocale(locale.LC_ALL, "").partition(".")[2] or u8
def ac(eio):
 py3=sys.version_info.major>2
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

import subprocess, inspect, json
from datetime import datetime, timedelta
if sys.version_info < (3, 6): from collections import OrderedDict
else: OrderedDict = dict
shell="SHELL" in os.environ

def tsMuxeR(*arg):
 if len(arg)>1:
  cmd=(fe,)+arg
  ps(" ".join(map(q, cmd)))
  p=subprocess.Popen(map(en, cmd), bufsize=0, universal_newlines=True, stdout=subprocess.PIPE)
  if 1:
   for line in iter(p.stdout.readline, ""): print(line, end="")
  else:
   while p.poll() is None: print(p.stdout.read(1), end="")
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
  ps(" ".join(map(q, cmd)))
  try:
   r=subprocess.check_output(map(en, cmd), stderr=subprocess.STDOUT).decode(acp)
  except subprocess.CalledProcessError as e:
   ps("return code:", e.returncode)
   ps("return text:", e.output)
   exit()
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
   exit()
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
   if "subTrack:" in me and len(me["subTrack:"])>t: ll+=['subTrack=%s'%me["subTrack:"][t]]
   if "Stream lang:" in me and me["Stream lang:"][t]: ll+=['lang=%s'%me["Stream lang:"][t]]
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
 return de(os.path.splitext(f)[1]).lower().lstrip(".")

def rep(p, a="", t=0):
 #ps("rep",p,a,t)
 if t and t not in sdl[fin]: return #t is not selected track
 if a.endswith("="): #--demux=
  ms[t]-={sed(p, -1)}
 else: ms[t]|={sed(p, t)}

def usage():
 ps(argv)
 ps("fe:", fe, "fi:", fi, "fm:", fm, "fo:", fo)
 print(r'''%s [tsMuxeR%s] [fm.meta] [fo.ext|do] [--muxOpt] \
fiList fiSel (-|fiOptList) \
fiList2 fiSel2 (-|fiOptList2) \
...
fiListLast fiSelLast (-|fiOptListLast)'''%(argv[0], exe))
 if locale.getlocale()[0] in ("Russian_Russia", "ru_RU"): print(r'''где:
 tsMuxeR - исполняемый файл tsMuxeR. Если опущен, то буду искать в каталоге где находится tsmuxer.py
 fm.meta - файл метаданных. Если fiList не опущен, то fm.meta будет создан путём запуска "tsMuxeR fi.ext" и отредактирован
           в противном случае будет прочитан из fm.meta и отредактирован
 fo.ext - выходной файл с расширениями:
  .iso - в muxOpt будут добавлены опции --blu-ray и --label="fo"
  .ts .m2ts .mts - из muxOpt будут удалены опции --demux --blu-ray ---avchd
 do - выходной каталог для demux, blu-ray или avchd
      если fo.ext и do опущены, то "tsMuxeR fm.meta fo.ext|do" не будет запущен
 muxOpt - опции для первой строки fm.meta
 fiList, ... fiListLast - список медиафайлов которые будут склеены. Имеют вид: fi+[fi2[+ ...+fiLast]]
 fiSel, ... fiSelLast - список селекторов дорожек. Имеют вид: [=selTr] [!] [+] [=selTr2] ... [!] [+] [=selTrLast]
  selTr - это одна из следующих опций:
   V - выберет видео дорожки
   A - выберет звуковые дорожки
   S - выберет дорожки субтитров
   "foo bar", foobar - выберет только те дорожки, в которых есть эта подстрока
   [0-9](0-9) - выберет дорожку с этим номером
  ! - инвертирует список выбранных дорожек
  + - Если задан: "=selTr + =selTr2" то добавит в список дорожек выбранных selTr дорожки которые соответствуют условию selTr2
      Если опущен: "=selTr =selTr2" то в списке выбраннвх дорожек останутся только дорожки, удовлетворяющие обоим условиям
 - - закомментирует все выбранные дорожки, добавив # в начало строк fm.meta, затем выберет все дорожки текущего fiList
 = - выберет все дорожки текущего fiList. Отменяет эффект всех ранее введенных selTr
 fiOptList - список опций вида: ,fiOpt[ ,fiOpt2[... ,fiOptLast]] изменит применимые опции для выбранных ранее дорожек fm.meta
например:
 "tsmuxer.py i.mkv+ my.ts =S -" создаст из i.mkv i.mkv.meta и my.ts без дорожек субтитров
 "tsmuxer.py i.mkv+ my.meta" создаст только my.meta из i.mkv
 "tsmuxer.py my.meta . =_text =1 ! -" демультиплексирует первую дорожку srt субтитров в текущий каталог
 "tsmuxer.py BD/BDMV/PLAYLIST/00001.mpls+ rus.iso =V + =rus ! -" создаст rus.iso с видео дорожками и дорожками для русскоязычных
 "tsmuxer.py --avchd BD/BDMV/PLAYLIST/00001.mpls+ AVCHD =mvc -" из BD3D сделает 2D AVCHD
 "tsmuxer.py --cut-start=28320ms --cut-end=184320ms 00042.MTS+ 42.ts =S - 00042.srt+ ,timeshift=28320 ,lang=rus ,font-name="Impact" ,font-size=65 ,font-color=0xffffffff ,bottom-offset=24 ,font-border=5 ,fadein-time=0.25 ,fadeout-time=1 ,text-align=center ,lang=rus"
             обрежет 00042.MTS, отбросит его субтитры и добавит субтитры из 00042.srt
 "tsmuxer.py --blu-ray 42.ts+43.ts BD" склеит 42.ts и 43.ts в каталог блюрэя BD
 "tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 3D1.mkv+ BD3D1" запишет в каталог BD3D1 блюрэй из 3D1.mkv
 "tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 BD1/BDMV/PLAYLIST/00001.mpls+BD2/BDMV/PLAYLIST/00001.mpls BD3D"
             объединит BD3D1 и BD3D2 и запишет BD3D
''')
 else: print(r'''where:
 tsMuxeR - tsMuxeR executable. If omitted, it will be searched in the directory where "tsmuxer.py" is located
 fm.meta - metadata file. If "fiList" is present, "fm.meta" will be created by running "tsMuxeR fi.ext". Otherwise the given "fm.meta" will be used.
 fo.ext - output file with extensions:
  .iso - options --blu-ray --label="fo" will be added to muxOpt
  .ts, .m2ts, .mts - options --demux --blu-ray --avchd will be removed from muxOpt
 do - output directory for demux, blu-ray, or avchd. If "fo.ext" and "do" are omitted then "tsMuxeR fm.meta fo.ext|do" won't be started
 muxOpt - options to be prepened to the first line of "fm.meta"
 fiList, ... fiListLast - list of the media files to be glued. Has the following syntax: "fi+[fi2[+...+fiLast]]"
 fiSel, ... fiSelLast - list of the tracks selectors. Has the following syntax: "[=selTr] [!] [+] [=selTr2] ... [!] [+] [=selTrLast]"
  selTr - is one of the following options:
   V - selects the video tracks
   A - selects the audio tracks
   S - selects the subtitle tracks
   "foo bar", foobar - selects the tracks with the given substring
   [0-9](0-9) - selects the track by its number
  ! - inverts the track selection
  + - if present: "=selTr + =selTr2" selects "selTr" then adds to the selection the tracks that match "selTr2".
      If omitted: "=selTr =selTr2" selects the tracks that match both "selTr" and "selTr2"
 - - comment all selected tracks by adding # to the beginning of the lines "fm.meta", then select all the tracks of the current "fiList" 
 = - selects all the tracks of the current "fiList". Cancels all the previous "selTr"
 fiOptList - changes the options of the selected tracks. Has the following syntax: ",fiOpt[ ,fiOpt2[... ,fiOptLast]]""
ex:
 "tsmuxer.py i.mkv+ my.ts =S -" creates "i.mkv.meta" from "i.mkv", excludes the subtitle tracks from it and produces "my.ts"
 "tsmuxer.py i.mkv+ my.meta" creates "my.meta" from "i.mkv"
 "tsmuxer.py my.meta . =_text =1 ! -" demultiplexes the first srt subtitle track into the current directory
 "tsmuxer.py BD/BDMV/PLAYLIST/00001.mpls+ rus.iso =V + =rus ! -" muxes the BD file "rus.iso" from the video track and the tracks with "rus" in it
 "tsmuxer.py --avchd BD/BDMV/PLAYLIST/00001.mpls+ AVCHD =mvc -" muxes 2D AVCHD from the given BD3D
 "tsmuxer.py --blu-ray --cut-start=28320ms --cut-end=184320ms 00042.MTS+ 42.ts =S - 00042.srt+ ,timeshift=28320 ,font-name=Impact ,font-size=65 ,font-color=0xffffffff ,bottom-offset=24 ,font-border=5 ,fadein-time=0.25 ,fadeout-time=1 ,text-align=center ,lang=rus"
             cuts 00042.MTS, strips all the subtitles from it, adds srt subtitle tracks from 00042.srt, and outputs "42.ts"
 "tsmuxer.py --blu-ray 42.ts+43.ts BD" glues 42.ts and 43.ts into the blu-ray directory "BD"
 "tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 3D1.mkv+ BD3D1" creates the blu-ray directory "BD3D1" from "3D1.mkv"
 "tsmuxer.py --blu-ray --mplsOffset=1 --m2tsOffset=1 BD1/BDMV/PLAYLIST/00001.mpls+BD2/BDMV/PLAYLIST/00001.mpls BD3D"
             glues "BD3D1" and "BD3D2" into the blu-ray directory "BD3D"
''')
 exit()

def nf(f):
 if not os.path.isfile(f):
  ps('Not found file "%s"'%f)
  usage()

def ps(*l):
 print(" ".join(map(str, l))+"@"+", ".join(str(x[2]) for x in inspect.stack()[1:]))

def comm(t):
 if t: ml[t][0]="#"+ml[t][0].lstrip("#")

def q(s):
 return '"%s"'%s if " " in s else s

def sed(s, t):
 n, eq, v=s.partition("=")
 if t<0:
  if n in md[t]: md[t].pop(n)
 else: md[t][n]=v
 return n

def t2f(s):
 try: return sum([60**(2-i)*k for i, k in enumerate(map(float, (("0:0:"+s).split(':'))[-3:]))])
 except: return 0.0
 
def f2t(s):
 return (datetime(1970, 1, 1)+timedelta(seconds=s)).strftime("%H:%M:%S.%f")[:12]
 
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
 "vbv-len",
 #"no-asyncio",
 "cut-start",
 "cut-end",
 "right-eye",
 "start-time",
 "mplsoffset",
 "m2tsoffset",
 "insertblankpl",
 "blankoffset",
 "label",
 #"extra-iso-space",
}
VAS={
 "track",
 "lang",
}
od={}
od["v"]={
 "level",
 "insertsei",
 "forcesei",
 "contsps",
 "subTrack",
 "secondary",
 "pipcorner",
 "piphoffset",
 "pipvoffset",
 "pipscale",
 "piplumma",
}
od["V"]=VAS|od["v"]|{
 "fps",
 "delpulldown",
 "ar",
}
od["A"]=VAS|{
 "timeshift",
 "down-to-dts",
 "down-to-ac3",
 "secondary",
}
od["S"]=VAS|{
 "timeshift",
 "fps",
 "3d-plane",
 "video-width",
 "video-height",
}
od["srt"]={
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
}
od["s"]=od["S"]|od["srt"]

ac(sys.stdout)
subprocess.call(map(en, ["clear" if shell else "cls"]), shell=True)
argv=[de(x) for x in sys.argv]
print("_`".join(argv))
print("Пайтон %s.%s"%(sys.version_info.major, sys.version_info.minor), sys.executable, locale.getlocale())
exe=".exe" if os.name=="nt" else ""
opt="-+=,!"
fe=de(os.path.splitext(os.path.abspath(argv[0]))[0])
fj=fe+".json"
fe+=exe #tsMuxeR
fi="" #input files
fm="" #meta file
fo="" #output file or dir
if len(sys.argv)<2: usage() #./tsmuxer.py
odl={} #dict of options
adl={} #dict of all tracks
sdl={} #dict of selected tracks
meta=[] #metadata dict
extl=("iso", "ts", "m2ts", "mts")
mo=0 #meta line copy
fin=0 #current fi
mg={} #default dict for whf
cha=[]
for a in argv[1:]:                                                       #parse arg
 if fin not in odl: odl[fin]=[]
 if a[0] in opt: odl[fin]+=[a]
 elif os.path.isdir(a) or ext(a) in extl: fo=a
 elif "+" in a:
  fin+=mo
  if not mo: fi=a.rstrip("+")
  temp=tsMuxeR(a.rstrip("+"))
  adl[fin]=set(range(len(meta)+1-mo, len(meta)+len(temp)-mo))
  sdl[fin]=adl[fin].copy()
  meta+=temp[mo:]
  mo=1
 elif ext(a)=="meta": fm=a
 elif ext(a)==exe.lstrip("."):
  nf(a)
  fe=a
if fi:
 if len(cha)>1: meta[0]+=" --custom-chapters=%s"%";".join(map(f2t, sorted(set(cha))))
 if not fm: fm=fi.split("+")[0]+".meta"
if not fi:
 nf(fm)
 with codecs.open(fm, encoding=u8) as f: meta=f.read().splitlines() #read fm
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
  p=a.lstrip(opt)
  p0=p.split("=")[0] #var name
  for MX in (MO, MB, MC):
   if p0 in MX: ms[0]-=MX
  if p0 in MC: ms[0]-=MS
  if p0 in M: rep(p, a)
  for tt in "VvASs":
   if p0 in od[tt]:
    for t in mt[tt]: rep(p, a, t)
if "bitrate" in ms[0]: rep("cbr")
else:
 if {"minbitrate", "maxbitrate"}&ms[0]: rep("vbr")
if ext(fo) in extl:
 ms[0]-=MO
 if ext(fo)==extl[0]:
  rep("blu-ray")
  if "label" not in ms[0]: rep('label="%s"'%os.path.splitext(os.path.split(fo)[1])[0])
if os.path.isfile(fj): load=json.load(open(fj))
else: load={}
dump=load.copy()
for t in mt["s"]:                       # from opt to file
 for k in od["srt"]:
  if k in md[t] and md[t][k]: dump[k]=md[t][k]
if dump!=load: json.dump(dump, fp=open(fj, "w"), sort_keys=True, indent=1)
for k in load:                          # from file to opt
 for t in mt["s"]:
  if k in md[t] and md[t][k]: continue
  md[t][k]=load[k]
  ms[t]|={k}
for t, tl in enumerate(ml): #serializ meta
 ll=[]
 for p in md[t]:
  if p in ms[t].copy():
   ms[t]-={p}
   ll+=[(p+"="+md[t][p]).rstrip("=")]
 for p in ms[t]: ll+=[p]
 if t: meta[t]=", ".join(ml[t][:2]+ll)
 else: meta[t]=" --".join(ml[t][:1]+ll)
print("\n".join(meta), file=codecs.open(fm, "w", encoding=u8), end="") #write meta
print(fm+":")
with codecs.open(fm, encoding=u8) as f: print(f.read())                #print meta
if fo: tsMuxeR(fm, fo)                                                 #run tsMuxeR fm fo
