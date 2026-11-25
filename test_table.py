import json,re,hashlib
from pathlib import Path
root=Path(__file__).parent
d=json.loads((root/'runtime-table.json').read_text())
def tr(s):
 if s in d['translations']:return d['translations'][s]
 t=s
 for r in d['regex']:
  template=re.sub(r'\$(\d+)',lambda m:'\\g<'+m[1]+'>',r['replacement'])
  t=re.sub(r['pattern'],template,t)
 if t==s:
  for k in sorted(d['substrings'],key=len,reverse=True):t=t.replace(k,d['substrings'][k])
 return t
assert tr('本机 iOS 27.0.1（构建 24A446）')=='نظام الجهاز iOS 27.0.1 (البنية 24A446)'
assert tr('本机 iOS 27.2 beta 3（构建 24C123）')=='نظام الجهاز iOS 27.2 beta 3 (البنية 24C123)'
assert tr('取消')=='إلغاء'
assert tr('确定')=='تأكيد'
assert tr('设置')=='الإعدادات'
assert tr('Unknown text 123')=='Unknown text 123'
fmt=re.compile(r'%(?:\d+\$)?[-+ #0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hljztL])?[@diuoxXfFeEgGaAcsp%]')
mismatches=[]
for a,b in d['translations'].items():
 if sorted(fmt.findall(a))!=sorted(fmt.findall(b)):mismatches.append((a,b))
assert not mismatches,mismatches
raw=(root/'runtime-table.json').read_bytes()
assert raw in (root/'out/MirsaTranslate.dylib').read_bytes()
report={'dictionary_entries':len(d['translations']),'substrings':len(d['substrings']),'regex':len(d['regex']),'format_specifier_mismatches':len(mismatches),'example_ios':tr('本机 iOS 27.0.1（构建 24A446）'),'embedded_table_verified':True,'native_simulator_run':False,'device_tested':False,'dylib_sha256':hashlib.sha256((root/'out/MirsaTranslate.dylib').read_bytes()).hexdigest()}
(root/'out/static-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
