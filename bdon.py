#!/usr/bin/python
# coding=utf8
#
'''Read Blu-ray Disk's index.bdmv, MovieObject.bdmv and part of *.mpls to json
Write from json to index.bdmv, MovieObject.bdmv
Thanks to https://sites.google.com/site/videofan3d and https://code.videolan.org/videolan/libbluray.git
'''
from __future__ import print_function, division, unicode_literals
__metaclass__ = type
import sys, os, locale, struct, fnmatch, inspect
if sys.version_info<(3, 6): from collections import OrderedDict as od
else: od = dict

def ps(*l):
 print(" ".join(map(str, l))+"@"+", ".join(str(x[2]) for x in inspect.stack()[1:]))

indx_object_type_hdmv=1
indx_object_type_bdj=2
indx_hdmv_playback_type_movie=0
indx_hdmv_playback_type_interactive=1
indx_bdj_playback_type_movie=2
indx_bdj_playback_type_interactive=3
ocm=0b11111111110011110000111100011111

video_format={
 0: "0",
 1: "480i",
 2: "576i",
 3: "480p",
 4: "1080i",
 5: "720p",
 6: "1080p",
 7: "576p",
 8: "2160p",
 9: "2160i",
}
frame_rate={
 0: "0",
 1: "23_976",
 2: "24",
 3: "25",
 4: "29_97",
 5: "Reserved-5",
 6: "50",
 7: "59_94",
}
video_stream={
 0x01: "MPEG-1 Video",
 0x02: "MPEG-2 Video",
 #0x10: "MPEG-4 Video",
 0x1b: "H.264",
 0x20: "MVC",
 0x24: "H.265",
 #0x42: "AVS Video",
 #0x88: "VC-9",
 0xEA: "VC-1",
}
audio_stream={
 0x03: "MPEG-1 Audio",
 0x04: "MPEG-2 Audio",
 0x0f: "AAC",
 0x11: "AAC RAW",
 0x80: "LPCM",
 0x81: "AC-3",
 0x82: "DTS",
 0x83: "TrueHD",
 0x84: "AC-3 Plus",
 0x85: "DTS-HD",
 0x86: "DTS-HD MA",
 #0x87: "AC-3 Plus ATSC", 
 0xA1: "AC-3 Plus Secondary",
 0xA2: "DTS-HD Secondary",
 0xA3: "DRA", #0x??
 0xA4: "DRA Extension", #0x??
}
other_stream={
 #0x00: "DVB",
 0x90: "PGS",
 0x91: "IGS",
 0x92: "Text Subtitle",
}
audio_resentation={
 0: "0",
 1: "Mono",
 2: "Reserved-2",
 3: "Stereo",
 4: "Reserved-4",
 5: "Reserved-5",
 6: "Multi Channel"
}
sampling_frequency={
 0: "0",
 1: "48 kHz",
 2: "Reserved-2",
 3: "Reserved-3",
 4: "96 kHz",
 5: "192 kHz",
 0xC: "48/192 kHz",
 0xE: "48/96 kHz",
}
insn={
 0b0000000000: "Nop",
 0b0000000001: "GoTo",
 0b0000000010: "Break",
 0b0000100000: "Jump_Object",
 0b0000100001: "Jump_Title",
 0b0000100010: "Call_Object",
 0b0000100011: "Call_Title",
 0b0000100100: "Resume",
 0b0001000000: "Play_PL",
 0b0001000001: "Play_PLatPI",
 0b0001000010: "Play_PLatMK",
 0b0001000011: "Terminate_PL",
 0b0001000100: "Link_PI",
 0b0001000101: "Link_MK",
 0b0100000001: "Bitwise_Compare",
 0b0100000010: "Equal",
 0b0100000011: "Not_Equal",
 0b0100000100: "Greater_or_Equal",
 0b0100000101: "Greater_than",
 0b0100000110: "Less_or_Equal",
 0b0100000111: "Less_than",
 0b1000000001: "Move",
 0b1000000010: "Swap",
 0b1000000011: "Add",
 0b1000000100: "Sub",
 0b1000000101: "Mul",
 0b1000000110: "Div",
 0b1000000111: "Mod",
 0b1000001000: "Rnd",
 0b1000001001: "And",
 0b1000001010: "Or",
 0b1000001011: "Xor",
 0b1000001100: "Bit_Set",
 0b1000001101: "Bit_Clear",
 0b1000001110: "Shift_Left",
 0b1000001111: "Shift_Right",
 0b1000100001: "SetStream",
 0b1000100010: "SetNVTimer",
 0b1000100011: "SetButton_Page",
 0b1000100100: "EnableButton",
 0b1000100101: "DisableButton",
 0b1000100110: "SetSecondaryStream",
 0b1000100111: "PopUpMenu_Off",
 0b1000101000: "Still_On",
 0b1000101001: "Still_Off",
 0b1000101010: "SetOutputMode",
 0b1000101011: "SetStreamSS",
 0b1000110000: "reserved_0x10",
 0b1000110001: "reserved_0x11",
}
bdfe={
 "index.bdmv": "INDX",
 "movieobject.bdmv": "MOBJ",
 "id.bdmv": "BDID",
 "sound.bdmv": "BCLK",
 "mpls": "MPLS",
 "clpi": "HDMV",
 "bdjo": "BDJO",
 "index.bdm": "INDX",
 "movieobj.bdm": "MOBJ",
 "mpl": "MPLS",
 "cli": "HDMV",
}
def UHD(D4, hdr_flags, dic):
 if dic: return od({'ID1': 3, 'ID2': 1, 'data_block': [0, 0, 0, 8, D4, 0, hdr_flags, 0, 0, 0, 0, 0]})
 disk_type, unk0, exist_4k_flag=StruBi(D4).unpack("4 3 1")
 hdr=StruBi(hdr_flags)
 unk2=hdr.unpack(3)
 if dic==None:
  hdrl=[x  for x in ("HDR10PLUS", "SL_HDR2", "DV", "HDR10", "SDR") if hdr.unpack(1)]
  dt=str(disk_type)
  if disk_type==5: dt+="; 66/100GB disk; max 122 Mbps"
  ps("UHD disc type: %s, 4k: %d, HDR: %s"%(dt, exist_4k_flag, "; ".join(hdrl)))
 return unk0, unk2
  
def hevc(id1, id2, data_block, log):
 if (id1, id2)==(3, 1):
  hevc_len, D4, unk1, hdr_flags, unk3, unk4=StruBu(data_block).unpack("> I 4B I")
  unk0, unk2=UHD(D4, hdr_flags, log)
  if unk0|unk1|unk2|unk3|unk4: ps("index.bdmv: unknown data in extension 3.1: 0x%02x 0x%02x 0x%02x 0x%02x 0x%08x"%(unk0, unk1, unk2, unk3, unk4))
 else: ps("parse_indx_extension: unknown extension %d.%d"%(id1, id2))

class StruBu(object):
 def __init__(self, b):
  self.b=b
  self.lb=len(b) 
  self.ob=0; self.rb=self.lb
  
 def skip(self, form="", offset=None):
  if type(offset) is int:
   self.ob=offset; self.rb=self.lb-offset
  if not type(form) is int: form=struct.calcsize(form)
  self.ob+=form; self.rb-=form
  return self.ob
 
 def unpack(self, form="", offset=None):
  if type(offset) is int:
   self.ob=offset; self.rb=self.lb-offset
  if type(form) is int:
   if form>0: form="%ss"%form
   elif form<0: form=">%sB"%-form
   else: form="%ss"%self.rb
   if 0:
    r=self.b[self.ob:][:form] if form else self.b[self.ob:]
    self.ob+=form; self.rb-=form
    return r
  size=struct.calcsize(form)
  if not size: #reset
   self.ob=0; self.rb=self.lb
   return 0
  self.rb-=size
  if self.rb<0: r=struct.unpack(form, (self.b+b"\0"*-self.rb)[self.ob:][:size])
  else: r=struct.unpack(form, self.b[self.ob:][:size])
  self.ob+=size
  return r if len(r)>1 else r[0] #not vector for scalar result
 
class StruBi(object):
 def __init__(self, b, bits=8):
  self.b=b
  self.lb=bits
  self.ob=0; self.rb=self.lb
  
 def unpack(self, size=0, offset=None):
  r=[]
  if type(offset) is int:
   self.ob=offset; self.rb=self.lb-offset
  for f in ("%s"%size).split():
   i=int(f)
   if not i: i=self.rb #tail
   sh=self.rb-i
   self.ob+=i; self.rb-=i
   ma=(2**i-1)<<sh
   r+=[(self.b&ma)>>sh]
  return r if len(r)>1 else r[0]
 
def ascii(b):
 return b.rstrip(b"\0").decode("ascii")
 
def psr(s):
 r=s.lower()
 psr=0
 if r.startswith("reg_"): r=r.replace("reg_", "")
 elif r.startswith("psr_"):
  psr=0x80000000
  r=r.replace("psr_", "")
 try: i=int(r, 0)
 except:
  ps("Error parse int from '%s'"%s)
  i=0
 return i|psr

def basename(f):
 return os.path.basename(f).lower()
 
def dn(f, n=1):
 for i in range(n): f=os.path.dirname(f)
 return f
 
def ext(f):
 return suff(os.path.basename(f))

def suff(f):
 return os.path.splitext(f)[1].lstrip(os.extsep).lower()

def pack(loi):
 return struct.pack("%sB"%len(loi), *loi)
 
def bdk(OBJE, ver):
 if ver<2: return {
 "INDX": "index.bdm",
 "MOBJ": "movieobj.bdm",
 "MPLS": "00000.mpl",
 "HDMV": "00000.cli",
}.get(OBJE)
 else: return {
 "INDX": "index.bdmv",
 "MOBJ": "movieobject.bdmv",
 "BDID": "id.bdmv",
 "BCLK": "sound.bdmv",
 "MPLS": "00000.mpls",
 "HDMV": "00000.clpi",
 "BDJO": "00000.bdjo",
}.get(OBJE)

def prop(self, OBJE):
  k=bdk(OBJE, self.ver)
  obj=self.bd.get(k)
  if obj: return obj
  self.bd[k]=globals()[OBJE](self.path, ver=self.ver)
  return self.bd[k]
  
def propl(self, OBJE, pattern):
  obj=[self.bd[k] for k in self.select(pattern)]
  if obj: return obj
  k=bdk(OBJE, self.ver)
  self.bd[k]=globals()[OBJE](self.path, ver=self.ver)
  return [self.bd[k]]
 
class BD(object):
 def __init__(self, path="."):
  self.path=path
  if os.path.isfile(os.path.join(path, "BDMV", "index.bdm")): self.ver=1.0
  elif os.path.isfile(os.path.join(path, "BDMV", "index.bdmv")): self.ver=2.0
  else: self.ver=0
  self.bd={} #{"index.bdmv": INDX(), ...}
  self.scan()

 @property
 def ind(self):
  return prop(self, "INDX")

 @property
 def mov(self):
  return prop(self, "MOBJ")

 @property
 def idb(self):
  return prop(self, "BDID")
 
 @property
 def sou(self):
  return prop(self, "BCLK")
  
 @property
 def mpl(self):
  return propl(self, "MPLS", "*.%s*"%inspect.stack()[0][3])
  
 @property
 def cli(self):
  return propl(self, "HDMV", "*.%s*"%inspect.stack()[0][3])
  
 @property
 def bdj(self):
  return propl(self, "BDJO", "*.%s*"%inspect.stack()[0][3])
 
 def __str__(self):
  r=["%s: %s"%(self.__class__.__name__, self.__dict__)]
  for v in self.bd.values(): r+=[str(v)]
  return "\n".join(r)

 def select(self, pattern="*.*"):
  return  sorted(fnmatch.filter(self.bd.keys(), pattern))
 
 def scan(self):
  self.count={}
  self.uhd=0
  self.is4K=0
  self.isV3=0
  self.SS_content_exist_flag=0
  self.initial_output_mode_preference=0
  self.D4=0
  self.UHD={}
  all=sorted(self.bd.keys())
  for k in all:
   obj=bdfe.get(suff(k)) or bdfe.get(k)
   if obj in self.count: self.count[obj]+=1
   else: self.count[obj]=1
   if obj=="MPLS":
    self.uhd|=self.bd[k].uhd
    self.is4K|=self.bd[k].is4K
    self.isV3|=self.bd[k].isV3
    if self.bd[k].SS_content:
     self.SS_content_exist_flag=1
     if self.count[obj]==1: self.initial_output_mode_preference=1
  self.D4=0x51 if self.is4K else 0x20
  if self.uhd&0b11110: self.UHD=UHD(self.D4, self.uhd, 1)
  else: self.uhd=1  
  return len(all)
 
 def write(self, pattern="*.*", json={}):
  fl=self.select(pattern)
  count=len(fl)
  k=pattern.lower()
  if json and count<2:
   if count: self.bd[k].write(json)
   else:
    obj=bdfe.get(suff(pattern)) or bdfe.get(k)
    if obj:
     self.bd[k]=globals()[obj](self.path) #create obj
     self.bd[k].write(json)
   return 1
  if json:
   ps("Not allowed write json to more than one file of BD")
   return 0
  for k in fl: self.bd[k].write()
  self.scan()
  return count
 
 def read(self, pattern="*.*"):
  count=0
  g=[]
  for r, d, f in os.walk(self.path): #glob(os.path.join(self.path, "**", pattern), recursive=True)
   if "BACKUP" in r.upper(): continue
   g.extend(os.path.join(r, x) for x in fnmatch.filter(f, pattern))
  for p in sorted(g):
   k=basename(p)
   obj=bdfe.get(ext(p)) or bdfe.get(k)
   if obj:
    count+=1
    self.bd[k]=globals()[obj](p) #create obj
    self.bd[k].read()
  self.scan()
  return count
  
class BDMV(object):
 def __init__(self, path=".", json={}):
  self.SIG=self.__class__.__name__
  self.ver=0
  self.json=od(json)
  self.file=[]
  for p in self.pn:
   pp=os.path.join(path, *p)
   if not os.path.isdir(pp): os.mkdir(pp)
   self.file+=[os.path.join(pp, self.fn)]
   
 def __str__(self):
  return " %s: %s"%(self.__class__.__name__, self.__dict__)
  
 def write(self, json={}):
  "Pack self.bin from json or self.json  then write to files of BD"
  if json: self.json=od(json)
  self.tobin(self.json)
  if self.bin:
   for f in self.file:
    ps("Write '%s'"%f)
    try:
     with open(f, 'wb') as wb: wb.write(self.bin)
    except: ps("Error writing '%s' from %s.bin"%f)
  else: ps("Empty %s.bin packed from '%s'"%(self.SIG, json if json else self.json))
  
 def read(self):
  "Read files of BD to bin then unpack to json"
  for i, f in enumerate(self.file):
   ps("Read '%s'"%f)
   try:
    with open(f, 'rb') as rb: self.bin=rb.read()
   except:
    ps("Error reading '%s'"%f)
    if i: self.bin=b""
   else: break
  if not self.bin: ps("Empty %s.bin"%self.SIG)
  self.tojson()
  return self.json
 
 def tojson(self):
  pass

 def tobin(self, json={}):
  pass

def fe(fn, path):
 return  dn(path, 2) if basename(path)==fn.lower() else path
 
def z5(ex, path):
 return  (basename(path), dn(path, 3)) if ext(path)==ex else ("00000.%s"%ex, path)
 
class BCLK(BDMV):
 def __init__(self, path=".", json={}):
  self.fn="sound.bdmv"
  self.pn=("BDMV", "AUXDATA"), ("BDMV", "BACKUP", "AUXDATA")
  BDMV.__init__(self, dn(path, 3) if basename(path)==self.fn else path, json)

class INDX(BDMV):
 def __init__(self, path=".", json={}, ver=2):
  self.fn=bdk("INDX", ver)
  self.pn=("BDMV", ), ("BDMV", "BACKUP")
  #super().__init__(fe(self.fn, path), json)
  BDMV.__init__(self, fe(self.fn, path), json)
  
 def tobin(self, json={}):
  if json: self.json=od(json)
  b=b""
  if not self.SIG in self.json: return b
  ji=self.json[self.SIG]["AppInfoBDMV"]
  SS=ji["initial_output_mode_preference"]<<6|ji["SS_content_exist_flag"]<<5
  VF={video_format[k]:k for k in video_format}.get(ji["video_format"], 0)<<4
  VF|={frame_rate[k]:k for k in frame_rate}.get(ji["frame_rate"], 0)
  AppInfoBDMV=struct.pack("> 2B 32s", SS, VF, pack(ji["content_provider_user_data"]))
  AppInfoBDMV=struct.pack("> I", len(AppInfoBDMV))+AppInfoBDMV
  index_start=struct.calcsize("8s 2I 24s")
  index_start+=len(AppInfoBDMV)
  ji=self.json[self.SIG]["Indexes"]
  num_titles=len(ji["Title"])
  Indexes=b
  for i, ti in enumerate(("FirstPlayback", "TopMenu")+tuple(range(num_titles))):
   if i==2: ji=self.json[self.SIG]["Indexes"]["Title"]
   Indexes+=struct.pack("> B 3s", ji[ti]["object_type"]<<6|ji[ti]["access_type"]<<4, b)
   if ji[ti]["object_type"]==indx_object_type_hdmv: 
    if ji[ti]["playback_type"]>1:
     ps("%s: invalid HDMV playback type %s (%s)"%(self.fn, ji[ti]["playback_type"], ti))
     ji[ti]["playback_type"]-=2
    Indexes+=struct.pack("> B 1s H 4s", ji[ti]["playback_type"]<<6, b, ji[ti]["mobj_id_ref"], b)
   elif ji[ti]["object_type"]==indx_object_type_bdj:
    if ji[ti]["playback_type"]<2:
     ps("%s: invalid BD-J playback type %s (%s)"%(self.fn, ji[ti]["playback_type"], ti))
     ji[ti]["playback_type"]+=2
    Indexes+=struct.pack("> B 1s 5s 1s", ji[ti]["playback_type"]<<6, b, ji[ti]["bdjo_file_name"].encode("ascii"), b)
   else:
    ps("%s: unknown object type %s (%s)"%(self.fn, ji[ti]["object_type"], ti))
    Indexes+=struct.pack("> 8s", b)
   if i==1: Indexes+=struct.pack("> H", num_titles)
  Indexes=struct.pack("> I", len(Indexes))+Indexes
  extension_data_start=0
  ExtensionData=b
  if "ExtensionData" in self.json[self.SIG]:
   ji=self.json[self.SIG]["ExtensionData"]
   num_entries=len(ji)
   all_ext=b
   for ex in range(num_entries):
    data_block=pack(ji[ex]["data_block"])
    ext_len=len(data_block)+struct.calcsize("2H 2I")
    all_ext+=struct.pack("> 2H 2I", ji[ex]["ID1"], ji[ex]["ID2"], ext_len, len(data_block))
    all_ext+=data_block
    hevc(ji[ex]["ID1"], ji[ex]["ID2"], data_block, None) #ps
   if len(all_ext):
    ExtensionData=struct.pack("> 2I 3s B", len(all_ext)+struct.calcsize("I 3s B"),len(all_ext), b, num_entries)
    ExtensionData+=all_ext
    extension_data_start=index_start+len(Indexes)
  self.bin=struct.pack("> 8s 2I 24s", (self.SIG+self.json[self.SIG]["version_number"]).encode("ascii"), index_start, extension_data_start, b)
  self.bin+=AppInfoBDMV
  self.bin+=Indexes
  self.bin+=ExtensionData
  return self.bin
  
 def tojson(self):
  self.json=od({self.SIG: {}})
  bu=StruBu(self.bin)
  if self.SIG!=ascii(bu.unpack("> 4s")): return self.json
  version_number, index_start, extension_data_start=bu.unpack("> 4s 2I")
  self.ver=int(version_number)/100.0
  self.json[self.SIG]["reserved_header"]=[0]
  bu.skip(24)
  app_info_len, SS, VF=bu.unpack("> I 2B")
  SS=StruBi(SS)
  VF=StruBi(VF)
  self.json=od({
 self.SIG: od({
  "version_number": ascii(version_number),
  "reserved_header": [0],
  "AppInfoBDMV": od({
   "reserved01": SS.unpack(1),
   "initial_output_mode_preference": SS.unpack(1),
   "SS_content_exist_flag": SS.unpack(1),
   "reserved02": SS.unpack(0),
   "video_format": video_format.get(VF.unpack(4), "0"),
   "frame_rate": frame_rate.get(VF.unpack(4), "0"),
   "content_provider_user_data": bu.unpack(-(app_info_len-struct.calcsize("I 2B"))),
  }),
  "Indexes":od({
   "FirstPlayback": od({}),
   "TopMenu": od({}),
   "Title":[],
  }),
 }),
})
  bu.skip("> I", index_start)
  bu.skip("B 3s B 1s H 4s"*2) #"FirstPlayback", "TopMenu"
  num_titles=bu.unpack("> H")
  index_len=bu.unpack("> I", index_start)
  for i, ti in enumerate(("FirstPlayback", "TopMenu")+tuple(range(num_titles))):
   ji=self.json[self.SIG]["Indexes"]
   if i>1:
    ji=self.json[self.SIG]["Indexes"]["Title"]
    ji+=[od({})]
   ji[ti]["object_type"], ji[ti]["access_type"]=StruBi(bu.unpack("> B")).unpack("2 2")
   ji[ti]["reserved01"]=StruBu(b"\0"+bu.unpack(3)).unpack("> I")
   ji[ti]["playback_type"]=StruBi(bu.unpack("> B")).unpack(2)
   ji[ti]["reserved02"]=bu.unpack("> B")
   if ji[ti]["object_type"]==indx_object_type_hdmv: 
    if ji[ti]["playback_type"]>1: ps("%s: invalid HDMV playback type %s (%s)"%(self.fn, ji[ti]["playback_type"], ti))
    ji[ti]["mobj_id_ref"]=bu.unpack("> H")
    ji[ti]["reserved03"]=bu.unpack("> I")
   elif ji[ti]["object_type"]==indx_object_type_bdj:
    if ji[ti]["playback_type"]<2: ps("%s: invalid BD-J playback type %s (%s)"%(self.fn, ji[ti]["playback_type"], ti))
    ji[ti]["bdjo_file_name"]=ascii(bu.unpack("> 5s"))
    ji[ti]["reserved03"]=bu.unpack("> B")
   else: ps("%s: unknown object type %s (%s)"%(self.fn, ji[ti]["object_type"], ti))
   if i==1: bu.skip("> H") #num_titles
  if extension_data_start:
   self.json[self.SIG]["ExtensionData"]=[]
   ji=self.json[self.SIG]["ExtensionData"]
   length, address, padding, num_entries=bu.unpack("> 2I 3s B", extension_data_start)
   for ex in range(num_entries):
    ji+=[od({})]
    ji[ex]["ID1"], ji[ex]["ID2"], ext_start, ext_len=bu.unpack("> 2H 2I")
    ji[ex]["data_block"]=StruBu(self.bin).unpack(-ext_len, extension_data_start+ext_start)
   for ed in self.json[self.SIG]["ExtensionData"]: hevc(ed["ID1"], ed["ID2"], pack(ed["data_block"]), 0)
  return self.json

class MOBJ(BDMV):
 def __init__(self, path=".", json={}, ver=2):
  self.fn=bdk("MOBJ", ver)
  self.pn=("BDMV", ), ("BDMV", "BACKUP")
  BDMV.__init__(self, fe(self.fn, path), json)

 def tobin(self, json={}):
  if json: self.json=od(json)
  b=b""
  if not self.SIG in self.json: return b
  insnL={insn[k].lower():k for k in insn}
  MovieObjects=b
  for jm in self.json[self.SIG]["MovieObjects"]:
   MovieObjects+=struct.pack("> 2B H",
    jm["resume_intention_flag"]<<7|jm["menu_call_mask"]<<6|jm["title_search_mask"]<<5,
    jm["reserved01"],
    len(jm["NavigationCommand"]))
   for jn in jm["NavigationCommand"]:
    if "command" in jn:
     cl=jn["command"].lower().split()
     op_cnt=len(cl)-1
     if "operation_code" not in jn:
      try: gso=insnL[cl[0]]
      except:
       gso=0
       ps("Error parse command from '%s'"%cl[0])     
      grp, sub_grp, opt=StruBi(gso, 10).unpack("2 3 5")
      imm=[0, 0]
      for op in range(op_cnt):
       if cl[op+1].startswith("reg_"): continue
       if cl[op+1].startswith("psr_"): continue
       imm[op]=1
      jn["operation_code"]=StruBu(pack([op_cnt<<5|grp<<3|sub_grp,
       imm[0]<<7|imm[1]<<6|(opt if grp==0 else 0),
       opt if grp==1 else 0,
       opt if grp==2 else 0])).unpack("> I")&ocm
     if "operand_1" not in jn: 
      jn["operand_1"]=psr(cl[1]) if op_cnt>0 else 0
     if "operand_2" not in jn: 
      jn["operand_2"]=psr(cl[2]) if op_cnt>1 else 0
    MovieObjects+=struct.pack("> 3I",
     jn["operation_code"],
     jn["operand_1"],
     jn["operand_2"])
  MovieObjects=struct.pack("> I 4s H",
   struct.calcsize("4s H")+len(MovieObjects),
   b,
   len(self.json[self.SIG]["MovieObjects"]))+MovieObjects
  extension_data_start=0
  ExtensionData=b
  if "ExtensionData" in self.json[self.SIG]:
   ji=self.json[self.SIG]["ExtensionData"]
   all_ext=b
   for ex in range(len(ji)):
    data_block=pack(ji[ex]["data_block"])
    ext_len=len(data_block)+struct.calcsize("2H 2I")
    all_ext+=struct.pack("> 2H 2I", ji[ex]["ID1"], ji[ex]["ID2"], ext_len, len(data_block))
    all_ext+=data_block
   if len(all_ext):
    ExtensionData=struct.pack("> 2I 3s B",
     struct.calcsize("I 3s B")+len(all_ext),
     len(all_ext),
     b,
     num_entries)
    ExtensionData+=all_ext
    extension_data_start=strct.calcsize("8s I 28s")+len(MovieObjects)
  self.bin=struct.pack("> 8s I 28s", (self.SIG+self.json[self.SIG]["version_number"]).encode("ascii"), extension_data_start, b)
  self.bin+=MovieObjects
  self.bin+=ExtensionData
  return self.bin
  
 def tojson(self):
  self.json=od({self.SIG: {}})
  bu=StruBu(self.bin)
  if self.SIG!=ascii(bu.unpack("> 4s")): return self.json
  version_number, extension_data_start=bu.unpack("> 4s I")
  self.ver=int(version_number)/100.0
  self.json[self.SIG]["version_number"]=ascii(version_number)
  self.json[self.SIG]["reserved_header"]=[0]
  bu.skip(28)
  data_len, pad=bu.unpack("> 2I")
  num_objects=bu.unpack("> H")
  self.json[self.SIG]["MovieObjects"]=[]
  for mo in range(num_objects):
   jm=od({})
   jm["resume_intention_flag"], jm["menu_call_mask"], jm["title_search_mask"]=StruBi(bu.unpack("> B")).unpack("1 1 1")
   jm["reserved01"], num_cmds=bu.unpack("> B H")
   jm["NavigationCommand"]=[]
   for nc in range(num_cmds):
    jn=od({})
    jn["operation_code"]=bu.unpack("> I")&ocm
    op_cnt, grp, sub_grp, imm_op1, imm_op2, pad, branch_opt, pad, cmp_opt, pad, set_opt=StruBi(jn["operation_code"], 32).unpack("3 2 3 1 1 2 4 4 4 3 5")
    jn["operand_1"], jn["operand_2"]=bu.unpack("> 2I")
    ins=((grp<<3)|sub_grp)<<5
    try: opt=(branch_opt, cmp_opt, set_opt)[grp]
    except:
     ins=opt=0
     ps("Error grp %s"%grp)
    co=insn.get(ins|opt)
    if not co:
     co="Nop"
     ps("Error parse command from '%s'"%ins)
    jn["command"]=" ".join((co, ("%s" if imm_op1 else "reg_%s")%jn["operand_1"], ("%s" if imm_op2 else "reg_%s")%jn["operand_2"])[:op_cnt+1])
    jm["NavigationCommand"]+=[jn]
   self.json[self.SIG]["MovieObjects"]+=[jm]
  return self.json 

class BDID(BDMV):
 def __init__(self, path=".", json={}):
  self.fn="id.bdmv"
  self.pn=("CERTIFICATE", ), ("CERTIFICATE", "BACKUP")
  BDMV.__init__(self, fe(self.fn, path), json)

class BDJO(BDMV):
 def __init__(self, path=".", json={}):
  self.fn, path=z5("bdjo", path)
  self.pn=("BDMV", "BDJO"), ("BDMV", "BACKUP", "BDJO")
  BDMV.__init__(self, path, json)

class HDMV(BDMV):
 def __init__(self, path=".", json={}, ver=2):
  self.fn, path=z5("clp" if ver<2 else "clpi", path)
  self.pn=("BDMV", "CLIPINF"), ("BDMV", "BACKUP", "CLIPINF")
  BDMV.__init__(self, path, json)

class MPLS(BDMV):
 def __init__(self, path=".", json={}, ver=2):
  self.fn, path=z5("mpl" if ver<2 else "mpls", path)
  self.pn=("BDMV", "PLAYLIST"), ("BDMV", "BACKUP", "PLAYLIST")
  BDMV.__init__(self, path, json)
  self.SS_content=0
  self.uhd=0
  self.is4K=0
  self.isV3=0

 def tojson(self):
  self.json=od({self.SIG: {}})
  bu=StruBu(self.bin)
  if self.SIG!=ascii(bu.unpack("> 4s")): return self.json
  version_number, list_pos, mark_pos, ext_pos=bu.unpack("> 4s 3I")
  self.ver=int(version_number)/100.0
  if self.ver==3: self.isV3=1 
  self.json[self.SIG]["version_number"]=ascii(version_number)
  self.json[self.SIG]["PlayList"]=od({})
  length, padding, list_count, sub_count=bu.unpack("> I 3H", list_pos)
  self.json[self.SIG]["PlayList"]["PlayItem"]=[]
  for p in range(list_count):
   pi=od({})
   pil=bu.unpack("> H")
   pi["Clip_Information_file_name"]=ascii(bu.unpack("> 5s"))
   pi["Clip_codec_identifier"]=ascii(bu.unpack("> 4s"))
   pi["reserved01"]=bu.unpack("> B")
   pi["is_multi_angle"], pi["connection_condition"]=StruBi(bu.unpack("> B")).unpack("1 0", 3)
   pi["ref_to_STC_id"], pi["IN_time"], pi["OUT_time"], uo=bu.unpack("> B 2I 8s")
   pi["PlayItem_random_access_flag"]=StruBi(bu.unpack("> B")).unpack(1)
   pi["still_mode"], pi["still_time"]=bu.unpack("> B H")
   if pi["is_multi_angle"]:
    angle_count=bu.unpack("> b")
    is_different_audio, is_seamless_angle=StruBi(bu.unpack("> B")).unpack("1 1", 6)
    if angle_count<1: angle_count=1
   else: angle_count=1
   for an in range(1, angle_count): 
    aclip_id, acodec_id, astc_id=bu.unpack("> 5s 4s B")
   lenSTN, padding, num_video, num_audio, num_pg, num_ig=bu.unpack("> 2H 4B")
   num_secondary_audio, num_secondary_video, num_pip_pg=bu.unpack("> 3B")
   number_of_DolbyVision_video_stream_entries, s4=bu.unpack("> B 4s")
   pi["STN_table"]=od({"stream": []})
   for si in range(num_video+num_audio+num_pg+num_ig+num_secondary_audio+num_secondary_video+num_pip_pg+number_of_DolbyVision_video_stream_entries):
    st=od({})
    next=bu.unpack("> B")+bu.skip(0) #next=StreamAttributes
    st["type"]=bu.unpack("> B")      #StreamEntry 
    if st["type"] in (2, 3, 4): subpath_id=bu.unpack("> B")
    if st["type"]==4: subclip_id=bu.unpack("> B")
    if st["type"] in (1, 2, 3, 4): st["pid"]=bu.unpack("> H")
    else: 
     ps("unrecognized stream type %02x"%st["type"])
     pi["STN_table"]["stream"]+=[st]
     self.json[self.SIG]["PlayList"]["PlayItem"]+=[pi]
     return self.json
    next=bu.unpack("> B", next)+bu.skip(0) #next=StreamEntry
    coding_type=bu.unpack("> B")           #StreamAttributes
    st["stream_coding_type"]=hex(coding_type)
    if coding_type in video_stream:
     st["stream_coding_type"]=video_stream[coding_type]
     VF=StruBi(bu.unpack("> B"))
     st["video_format"]=video_format.get(VF.unpack(4), "0")
     if st["video_format"].startswith("2160"): self.is4K|=1
     st["frame_rate"]=frame_rate.get(VF.unpack(4), "0")
     if coding_type==0x24: 
      st["reserved_uhd"], st["reserved01"]=bu.unpack("> B H")
      if   st["reserved_uhd"]==0x12: self.uhd|=0b10010 #HDR10plus and HDR10
      elif st["reserved_uhd"]==0x80: self.uhd|=0b10000 #HDR10plus
      elif st["reserved_uhd"]==0x22: self.uhd|=0b00100 #DV
     else:  st["reserved01"]=StruBu(b"\0"+bu.unpack(3)).unpack("> I")
    if coding_type in audio_stream:
     st["stream_coding_type"]=audio_stream[coding_type]
     ap, sf=StruBi(bu.unpack("> B")).unpack("4 4")
     st["audio_presentation_type"]=audio_resentation.get(ap, "?")
     st["sampling_frequency"]=sampling_frequency.get(sf, "?")
    if coding_type in other_stream:
     st["stream_coding_type"]=other_stream[coding_type]
     if coding_type==0x92: char_code=bu.unpack("> B")
    if coding_type not in video_stream: st["language_code"]=ascii(bu.unpack("> 3s"))
    if "stream_coding_type" not in st:
     ps("unrecognized coding type %02x"%coding_type)
     pi["STN_table"]["stream"]+=[st]
     self.json[self.SIG]["PlayList"]["PlayItem"]+=[pi]
     return self.json
    if (
     num_video+num_audio+num_pg+num_ig<=si<num_video+num_audio+num_pg+num_ig+num_secondary_audio or
     num_video+num_audio+num_pg+num_ig+num_secondary_audio<=si<num_video+num_audio+num_pg+num_ig+num_secondary_audio+num_secondary_video or
     num_video+num_audio+num_pg+num_ig+num_secondary_audio+num_secondary_video<=si<num_video+num_audio+num_pg+num_ig+num_secondary_audio+num_secondary_video+num_pip_pg or
    0):
     ps("Stream #%s is secondary"%(si+1))
     num, B=bu.unpack("> 2B")
     bu.skip(num+num%2) #word align
    if num_video+num_audio+num_pg+num_ig+num_secondary_audio+num_secondary_video+num_pip_pg<=si<num_video+num_audio+num_pg+num_ig+num_secondary_audio+num_secondary_video+num_pip_pg+number_of_DolbyVision_video_stream_entries:
     ps("Stream #%s is Dolby Video"%(si+1))
    bu.ob=next
    pi["STN_table"]["stream"]+=[st]
   self.json[self.SIG]["PlayList"]["PlayItem"]+=[pi]
  if not ext_pos: return self.json
  self.json[self.SIG]["ExtensionData"]=[]
  length, address, padding, num_entries=bu.unpack("> 2I 3s B", ext_pos)
  for ex in range(num_entries):
   ed=od({})
   ed["ID1"], ed["ID2"], ext_start, ext_len=bu.unpack("> 2H 2I")
   if (ed["ID1"], ed["ID2"])==(2, 1):
    ps("3D content exists")
    self.SS_content=3
   ed["data_block"]=StruBu(self.bin).unpack(-ext_len, ext_pos+ext_start)
   self.json[self.SIG]["ExtensionData"]+=[ed]
  return self.json

if __name__=="__main__":
 import json
 def ac(eio):
  import sys, locale, os, codecs
  global py3, u8, acp, de, en
  py3=sys.version_info.major>2
  u8="utf-8"
  acp=locale.setlocale(locale.LC_ALL, "").partition(".")[2] or u8
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

 ac(sys.stdout)
 print("Пайтон %s.%s"%(sys.version_info.major, sys.version_info.minor), sys.executable, locale.getlocale())
 argv=[de(x) for x in sys.argv]
 
 bd=BD(argv[1])
 bd.read("*.bdm*")
 ps(json.dumps(bd.ind.json, indent=4))
 bd.read("*.mpl*")
 ps(bd)
