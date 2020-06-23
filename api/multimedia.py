"""Multimedia API module. Provides generic control functionality

 config section: multimedia
 - torrent_directory
 - media_directory
 - temp_directory

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from os import remove, rmdir, walk, path as ospath, devnull, chmod, rename
#
#
def list(aCTX, aArgs):
 """Function docstring for list TBD

 Args:

 Output:
 """
 ret = {'data':[]}
 try:
  ret['root'] = aCTX.config['multimedia']['torrent_directory']
  for path,_,files in walk(ret['root']):
   ret['data'].extend([{'path':path,'file':file} for file in files if file[-3:] in ['mp4','mkv']])
 except Exception as err:
  ret['status'] = 'NOT_OK'
  ret['info']= str(err)
 else:
  ret['status'] = 'OK'
 return ret

#
#
def cleanup(aCTX, aArgs):
 """Function docstring for cleanup TBD

 Args:

 Output:
  - <data> - type,path,item,status,(info)
 """
 ret = {'root':aCTX.config['multimedia']['torrent_directory'],'data':[]}
 for path,dirs,files in walk(ret['root']):
  for item in files:
   try: remove(ospath.join(path,item))
   except Exception as err: ret['data'].append({'type':'file','path':path,'item':item,'status':'NOT_OK','info':str(err)})
   else: ret['data'].append({'type':'file','path':path,'item':item,'status':'OK'})
  for item in dirs:
   if item == '.':
    continue
   try: rmdir(ospath.join(path,item))
   except Exception as err: ret['data'].append({'type':'directory','path':path,'item':item,'status':'NOT_OK','info':str(err)})
   else: ret['data'].append({'type':'directory','path':path,'item':item,'status':'OK'})
 return ret

#
#
def delete(aCTX, aArgs):
 """Function docstring for delete TBD

 Args:
  - path (required)
  - file (required)

 Output:
 """
 try: remove(ospath.join(aArgs['path'],aArgs['file']))
 except Exception as err:
  ret = {'status':'NOT_OK','info':str(err),'deleted':False}
 else:
  ret = {'status':'OK','deleted':True}
 return ret

#
#
def transfer(aCTX, aArgs):
 """Function docstring TBD

 Args:
  - path (required)
  - file (required)

 Output:
 """
 from shutil import move
 try: move( ospath.join(aArgs['path'],aArgs['file']), ospath.join(aCTX.config['multimedia']['media_directory'],aArgs['file']) )
 except Exception as err:
  ret = {'status':'NOT_OK','info':str(err)}
 else:
  ret = {'status':'OK','result':'transfered'}
 return ret

################################################# Media Functions ################################################
#
#
def check_srt(aCTX, aArgs):
 """Function find the 'first' SRT file in a directory

 Args:
  - filepath (cond optional)
  - path (cond optional)
  - file (cond optional)

 Output: Return anguage abbreviation, language name, srtfile if found
 """
 ret = {'status':'OK'}
 filename = (aArgs.get('filepath') if aArgs.get('filepath') else ospath.join(aArgs.get('path'),aArgs.get('file')))[:-4]
 if   ospath.exists("%s.eng.srt"%filename):
  ret['data'] = {'code':'eng','name':"English",'file':"%s.eng.srt"%filename}
  ret['found'] = True
 elif ospath.exists("%s.swe.srt"%filename):
  ret['data'] = {'code':'swe','name':"Swedish",'file':"%s.swe.srt"%filename}
  ret['found'] = True
 elif ospath.exists(filename + ".srt"):
  ret['data'] = {'code':'eng','name':"English",'file':"%s.srt"%filename}
  ret['found'] = True
 else:
  ret['data'] = {'code':None,'name':None,'file':None}
  ret['found'] = False
 return ret

#
#
def check_title(aCTX, aArgs):
 """Function tries to determine if this is a series or movie and then how to rename the file such that it would be easy to catalog

 Args:
  - filepath (cond optional)
  - path (cond optional)
  - file (cond optional)

 Output:
  - name
  - info
  - type
  - episode (in case type == 'series')
 """
 from re import search
 if aArgs.get('filepath'):
  fpath,filename = ospath.split(aArgs['filepath'])
 else:
  fpath,filename = aArgs.get('path'),aArgs.get('file')
 data  = {'path':fpath,'name':None,'info':None,'title':None}
 ret ={'status':'OK','data':data}
 prefix = filename[:-4].replace("."," ").title()
 # Info start means episode info, like S01E01."whatever".suffix
 is_series = search(r"[sS][0-9]{1,2}[eE][0-9]{1,2}-*[eE]*[0-9]*",prefix)

 if is_series:
  data['type'] = 'series'
  info_start, info_end, title_end = is_series.end(), len(prefix), is_series.start()-1
  data['episode'] = prefix[is_series.start():info_start].upper().replace("-","")

  # Title date is prefix[0] - prefix[where we found season info]
  # ... but maybe there is more, like the idiots who named Modus who added a " - " instead of a "." or just " "
  data['title'] = prefix[0:title_end] if prefix[title_end-2:title_end+1] != " - " else prefix[0:title_end-2]

  clean_search = search(r" (?:720|1080|Swesub).",prefix)
  if clean_search:
   info_end = clean_search.start()

  if info_end != info_start:
   data['episode'] = data['episode'] + prefix[info_start:info_end]

  data['info'] = "%(title)s - %(episode)s"%data
  data['name'] = "%(title)s %(episode)s"%data
 else:
  data['type'] = 'movie'
  has_year=search(r"\.(?:19|20)[0-9]{2}",prefix)
  if has_year:
   year = prefix[has_year.start()+1:has_year.end()]
   data['title'] = prefix[0:has_year.start()]
   data['info'] = "%s (%s)"%(data['title'],year)
   data['name'] = "%s %s"%(data['title'],year)
  else:
   clean_search = search(r" (?:720|1080|Swesub).",prefix)
   data['title'] = prefix
   data['info'] = prefix[0:clean_search.start()] if clean_search else prefix
   data['name'] = data['info']

 data['name']="%s.%s"%(data['name'].replace(" ","."),filename[-3:])
 return ret

#
#
def check_content(aCTX, aArgs):
 """Function docstring for check_content. Checks file using avprobe to determine content and how to optimize file

 Args:
  - filepath (cond optional)
  - path (cond optional)
  - file (cond optional)

  - srt (optional), do we already have an SRT?

 Output:
 """
 from subprocess import Popen, PIPE, STDOUT
 data = {}
 ret = {'status':'NOT_OK','data':data}

 filename = aArgs.get('filepath') if aArgs.get('filepath') else ospath.join(aArgs.get('path'),aArgs.get('file'))
 data['video'] = {'language':'eng', 'set_default':False}
 data['audio'] = {'add':[], 'remove':[], 'add_aac':True }
 data['subtitle'] = {'add':[], 'remove':[], 'languages':[] }

 if aArgs.get('srt'):
  data['subtitle']['languages'].append(aArgs.get('srt'))
 if not ospath.exists(filename):
  ret['info'] = 'NO_SUCH_FILE'
  return ret
 try:
  p1 = Popen(["avprobe", filename], stdout=PIPE, stderr=PIPE)
  p2 = Popen(["sed","-n","s/.*Stream #[0-9]\\:\\([0-9]*\\)\(.*\\): \\([AVS][a-z]*\\)/\\3#\\1#\\2#/p"], stdin=p1.stderr, stdout=PIPE)
  entries = p2.communicate()[0].decode()
 except Exception as e:
  ret['info'] = str(err)
 else:
  from re import sub
  for line in entries.split('\n'):
   if line:
    type,slot,lang,info = line.split('#')
    lang = sub('[()]','',lang)
    # Special case for Video, we are not interested in something without fps..
    if   type == 'Video' and "fps" in info:
     if lang:
      data['video']['language'] = lang
     else:
      data['video']['set_default'] = True
    elif type == 'Audio':
     if not lang or lang in ['eng','swe'] or (lang in ['fre','jpn','chi','ita','nor'] and '(default)' in info) or lang == data['video']['language']:
      data['audio']['add'].append(slot)
      if data['audio']['add_aac'] and 'aac' in info and 'stereo' in info:
       data['audio']['add_aac'] = False
     else:
      data['audio']['remove'].append(slot)
    elif type == 'Subtitle':
     if not lang: lang = 'eng'
     # if sub with lang is there already or not a sought lang then remove
     if lang in data['subtitle']['languages'] or not lang in ['eng','swe']:
      data['subtitle']['remove'].append(slot)
     else:
      data['subtitle']['add'].append(slot)
      data['subtitle']['languages'].append(lang)
  ret['status'] = 'OK'
 return ret

#
#
def process(aCTX, aArgs):
 """Process a media file

 Args:
  - filepath (cond optional)
  - path (cond optional)
  - file (cond optional)
  - name (optional)
  - info (optional) 
  - title (optional) - for mp4 series episode
  - episode (optional) - for mp4 series

 Output:
 """
 from time import time
 from subprocess import check_call, call
 filename = aArgs.get('filepath') if aArgs.get('filepath') else ospath.join(aArgs.get('path'),aArgs.get('file'))
 data = {'prefix':filename[:-4],'suffix':filename[-3:],'rename':False}
 ret = {'status':'NOT_OK','info':None,'data':data,'seconds':int(time())}
 # INTERNAL from rims.api.multimedia import check_srt
 srt  = check_srt(aCTX, {'filepath':filename})['data']
 # INTERNAL from rims.api.multimedia import check_title
 info = aArgs if aArgs.get('name') and aArgs.get('info') else check_title(aCTX, {'filepath':filename})['data']
 dest = ospath.abspath(ospath.join(info['path'],info['name']))
 data.update({'changes':{'subtitle':"",'audio':"",'srt':"",'aac':""},'dest':dest})

 try:
  if filename != dest:
   try:  rename(filename,dest)
   except Exception as e: ret['info'] = str(e)
   else: data['rename'] = True

  if data['suffix'] == 'mkv' and not ret['info']:
   if srt['code']:
    srtfile = "%s.process"%srt['file']
    data['changes']['srt']="--language 0:{0} --track-name 0:{0} -s 0 -D -A {1}".format(srt['code'], repr(ospath.abspath(srtfile)))
    rename(srt['file'],srtfile)

   probe = check_content(aCTX, {'filepath':dest,'srt':srt.get('code')})['data']

   # if forced download or if there are subs to remove but no subs to add left
   if probe['subtitle']['remove']:
    data['changes']['subtitle'] = "--no-subtitles" if not probe['subtitle']['add'] else "--stracks " + ",".join(map(str,probe['subtitle']['add']))

   if probe['audio']['remove'] and probe['audio']['add']:
    data['changes']['audio'] = "--atracks " + ",".join(map(str,probe['audio']['add']))

   if (data['rename'] or probe['video']['set_default'] or probe['audio']['add_aac'] or data['changes']['subtitle'] or data['changes']['audio'] or srt['code']):
    FNULL = open(devnull, 'w')

    if data['rename']:
     call(['mkvpropedit', '--set', "title=" + info['info'], dest], stdout=FNULL, stderr=FNULL)

    if probe['video']['set_default']:
     call(['mkvpropedit', '--edit', 'track:v1', '--set', 'language=eng', dest], stdout=FNULL, stderr=FNULL)

    if probe['audio']['add_aac'] or data['changes']['audio'] or data['changes']['subtitle'] or srt['code']:
     from tempfile import mkdtemp
     data['aac_probe'] = probe['audio']['add_aac']
     tmpfile = filename + ".process"
     rename(dest,tmpfile)
     tempd   = aCTX.config['multimedia']['temp_directory']
     tempdir = mkdtemp(suffix = "",prefix = 'aac.',dir = tempd)

     if probe['audio']['add_aac']:
      check_call(['avconv', '-i', tmpfile ,'-vn', '-acodec', 'pcm_s16le', '-ac', '2', tempdir + '/audiofile.wav'], stdout=FNULL, stderr=FNULL)
      check_call(['normalize-audio', tempdir + '/audiofile.wav'], stdout=FNULL, stderr=FNULL)
      check_call(['faac', '-c', '48000', '-b', '160', '-q', '100', tempdir + '/audiofile.wav', '-o',tempdir + '/audiofile.aac'], stdout=FNULL, stderr=FNULL)
      data['changes']['aac'] = "--language 0:{} --default-track 0 {}/audiofile.aac".format(probe['video']['language'], tempdir)
     
     call(["mkvmerge -o '{}' {} {} '{}' {} {}".format(dest,data['changes']['subtitle'],data['changes']['audio'],tmpfile, data['changes']['aac'], data['changes']['srt'])], stdout=FNULL, stderr=FNULL, shell=True)
     call(['rm','-fR',tempdir])
     remove(tmpfile)

    if srt['code']: rename(srtfile,srtfile + "ed")

  elif data['suffix'] == 'mp4' and data['rename'] and (srt['code'] or aArgs.get('modify')):
   FNULL = open(devnull, 'w')
   if srt['code']:
    tmpfile = filename + ".process"
    rename(dest,tmpfile)
    chmod(srt['file'], 0o666)
    chmod(dest, 0o666)
    call(['MP4Box -add {0}:hdlr=sbtl:lang={1}:name={2}:group=2:layer=-1:disable {3} -out {4}'.format( repr(srt['file']), srt['code'], srt['name'], repr(tmpfile), repr(dest))], shell=True, stdout=FNULL)
    rename(srt['file'],"%s.processed"%srt['file'])
    remove(tmpfile)
   if aArgs.get('modify'):
    if info['episode']:
     call(['mp4tags', '-o', info['episode'], '-n', info['episode'][1:3], '-M', info['episode'][4:6], '-S', info['title'], '-m', info['info'], dest], stdout=FNULL, stderr=FNULL)
    else:
     ret['warn'] = "Movie modification not implemented"

 except Exception as err:
  ret['info'] = str(err)
 else:
  if ospath.exists(dest):
   chmod(dest, 0o666)
   ret['status'] = 'OK'
  else:
   ret['info'] = 'COMPLETE_NO_FILE'
 ret['seconds'] = (int(time()) - ret['seconds'])
 return ret


################################################ TBD ################################################
#
#
def delay_set(aCTX, aArgs):
 """Sets offset in ms for file 'original' (MKV)

 Args:
  - original (required)
  - offset (required). ms

 Output:
 """
 from time import time
 from subprocess import Popen, PIPE, check_call, call, STDOUT
 filename = aArgs.get('filepath') if aArgs.get('filepath') else ospath.join(aArgs.get('path'),aArgs.get('file'))
 ret = {'status':'NOT_OK','timestamp':int(time())}

 absfile = ospath.abspath(filename)
 tmpfile = absfile + ".delayset"

 # Find subtitle position
 try:
  p1 = Popen(["mkvmerge","--identify", filename], stdout=PIPE, stderr=PIPE)
  entries = p1.communicate()[0].decode()
 except Exception as err:
  ret['error']= str(err)
 else:
  for line in entries.split('\n'):
   slots = line.split(' ')
   if slots[0] == "Track" and slots[3] == "subtitles":
    offset=slots[2][0:-1] + ":" + aArgs.get('offset',0)
    try:
     rename(absfile,tmpfile)
     FNULL = open(devnull, 'w')
     check_call(["mkvmerge -o "+ repr(absfile) + " -y " + offset + " " + repr(tmpfile)], stdout=FNULL, stderr=FNULL, shell=True)
     remove(tmpfile)
     chmod(absfile,0o666)
    except Exception as err:
     ret['error'] = str(err)
    else:
     ret['status'] = 'OK'
 return ret
