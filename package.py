from pathlib import Path
import zipfile,plistlib,struct,json,hashlib
r=Path('/home/kit/drift-ar')
src=Path('/files/Drift-signed_01a211ae-f8fb-718e-863e-c9f5f3563527.ipa')
dylib=Path(__file__).parent/'out/MirsaTranslate.dylib'
out=r/'Drift-ar2.ipa'
with zipfile.ZipFile(src) as z:
 pn=next(n for n in z.namelist() if n.count('/')==2 and n.endswith('.app/Info.plist'))
 base=pn.rsplit('/',1)[0];info=plistlib.loads(z.read(pn))
 bn=base+'/'+info['CFBundleExecutable'];b=bytearray(z.read(bn));original_length=len(b)
 assert b[:4]==bytes.fromhex('cffaedfe')
 n,sz=struct.unpack_from('<II',b,16);o=32;offsets=[];signatures=[]
 for _ in range(n):
  cmd,size=struct.unpack_from('<II',b,o);assert size>=8 and o+size<=32+sz
  if cmd in (0x21,0x2c):assert struct.unpack_from('<I',b,o+16)[0]==0,'encrypted'
  if cmd==0x19:
   ns=struct.unpack_from('<I',b,o+64)[0]
   for i in range(ns):
    so=o+72+i*80;length=struct.unpack_from('<Q',b,so+40)[0];off=struct.unpack_from('<I',b,so+48)[0]
    if off and length:offsets.append(off)
  if cmd==0x1d:
   off,length=struct.unpack_from('<II',b,o+8)
   assert off>0 and off+length<=len(b)
   signatures.append((off,length,bytes(b[off:off+length])))
  o+=size
 name=b'@executable_path/Frameworks/MirsaTranslate.dylib\0'
 size=(24+len(name)+7)&~7
 command=struct.pack('<IIIIII',0xc,size,24,0,0x10000,0x10000)+name
 command+=b'\0'*(size-len(command))
 assert min(offsets)>=o+size and not any(b[o:o+size]),'no safe header padding'
 b[o:o+size]=command
 struct.pack_into('<II',b,16,n+1,sz+size)
 for off,length,sig in signatures:assert bytes(b[off:off+length])==sig
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as w:
  for zi in z.infolist():
   # Keep original signature blobs/ranges for signer compatibility. They are stale
   # after changing the header and MUST be replaced by the recipient's signer.
   w.writestr(zi,bytes(b) if zi.filename==bn else z.read(zi.filename))
  zi=zipfile.ZipInfo(base+'/Frameworks/MirsaTranslate.dylib');zi.external_attr=0o100755<<16
  zi.compress_type=zipfile.ZIP_DEFLATED;w.writestr(zi,dylib.read_bytes())
  # Optional override is included so the table is inspectable and replaceable.
  w.writestr(base+'/Frameworks/MirsaTranslations.json',(Path(__file__).parent/'runtime-table.json').read_bytes())
 report={'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'binary':bn,'load_command':name.rstrip(b'\0').decode(),'added_command_bytes':size,'original_binary_length_preserved':len(b)==original_length,'original_signature_ranges_preserved':len(signatures),'requires_resigning':True,'device_tested':False}
(r/'runtime-package-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
