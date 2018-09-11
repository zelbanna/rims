"""Controls API module. Provides generic control functionality"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  
 Output:
 """
 from os import walk
 ret = {'files':[]}
 try:
  ret['root'] = SC['multimedia']['torrent_directory']
  for path,_,files in walk(ret['root']):
   for file in files:
    if file[-3:] in ['mp4','mkv']:
     ret['files'].append({'path':path,'file':file})
 except Exception as err:
  ret['error']= str(err)
 return ret

#
#
def cleanup(aDict):
 """Function docstring for list TBD

 Args:
  
 Output:
 """
 from os import walk, remove, rmdir
 ret = {'root':SC['multimedia']['torrent_directory'],'items':[]}
 for path,dirs,files in walk(ret['root']):
  for item in files:
   try: remove(ospath.join(path,item))
   except Exception as err: ret['items'].append({'item':'error','info':str(err)})
   else: ret['items'].append({'item':'file','info':item})
  for item in dirs:
   if item == '.':
    continue
   try: rmdir(ospath.join(path,item))
   except Exception as err: ret['items'].append({'item':'error','info':str(err)})
   else: ret['items'].append({'item':'dir','info':item})
 return ret

#
#
def transfer(aDict):
 """Function docstring for transfer TBD

 Args:
  - path (required)
  - file (required)
  
 Output:
 """
 from shutil import move
 ret = {'res':'NOT_OK','source':ospath.join(aDict['path'],aDict['file']),'destination':ospath.join(SC['multimedia']['media_directory'],aDict['file'])}
 try: move(ret['source'],ret['destination'])
 except Exception as err: ret['error'] = str(err)
 else: ret['res'] = 'OK'
 return ret

#
#
def delete(aDict):    
 """Function docstring for transfer TBD

 Args:
  - path (required)   
  - file (required)       
  
 Output:
 """
 from os import remove
 ret = {'res':'NOT_OK'}
 try: remove(ospath.join(aDict['path'],aDict['file']))
 except Exception as err: ret['error'] = str(err)
 else: ret['res'] = 'OK'
 return ret

#
#
def services(aDict):
 """Function docstring for services TBD

 Args:
 
 Output:
 """
 return {'services':[{'name':x,'service':SC['services'][x]} for x in SC['services'].keys()]}

################################################# Media Functions ################################################
#
#
def check_srt(aDict):
 """Function docstring for check_srt. Find the 'first' SRT file in a directory, 

 Args:
  - filepath (cond optional)
  - path (cond optional)
  - file (cond optional)

 Output: Return anguage abbreviation, language name, srtfile if found
 """
 ret = {}
 filename = (aDict.get('filepath') if aDict.get('filepath') else ospath.join(aDict.get('path'),aDict.get('file')))[:-4]
 if   ospath.exists("%s.eng.srt"%filename):
  ret = {'code':'eng','name':"English",'file':"%s.eng.srt"%filename}
 elif ospath.exists("%s.swe.srt"%filename):
  ret = {'code':'swe','name':"Swedish",'file':"%s.swe.srt"%filename}
 elif ospath.exists(filename + ".srt"):
  ret = {'code':'eng','name':"English",'file':"%s.srt"%filename}
 else:
  ret = {'code':None,'name':None,'file':None}
 return ret

#
#
def check_title(aDict):
 """Function docstring for check_title. Function tries to determine if this is a series or movie and then how to rename the file such that it would be easy to catalog

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
 if aDict.get('filepath'):
  fpath,filename = ospath.split(aDict['filepath']) 
 else:
  fpath,filename = aDict.get('path'),aDict.get('file')
 ret = {'path':fpath,'name':None,'info':None,'title':None}
 prefix = filename[:-4].replace("."," ").title()
 # Info start means episode info, like S01E01."whatever".suffix
 is_series = search(r"[sS][0-9]{1,2}[eE][0-9]{1,2}-*[eE]*[0-9]*",prefix)

 if is_series:
  ret['type'] = 'series'
  info_start, info_end, title_end = is_series.end(), len(prefix), is_series.start()-1
  ret['episode'] = prefix[is_series.start():info_start].upper().replace("-","")		

  # Title date is prefix[0] - prefix[where we found season info]
  # ... but maybe there is more, like the idiots who named Modus who added a " - " instead of a "." or just " "
  ret['title'] = prefix[0:title_end] if not prefix[title_end-2:title_end+1] == " - " else prefix[0:title_end-2]

  clean_search = search(r" (?:720|1080|Swesub).",prefix)
  if clean_search:
   info_end = clean_search.start()
 
  if info_end != info_start:
   ret['episode'] = ret['episode'] + prefix[info_start:info_end]

  ret['info'] = "%(title)s - %(episode)s"%ret
  ret['name'] = "%(title)s %(episode)s"%ret
 else:
  ret['type'] = 'movie'
  has_year=search(r"\.(?:19|20)[0-9]{2}",prefix)
  if has_year:
   year = prefix[has_year.start()+1:has_year.end()]
   ret['title'] = prefix[0:has_year.start()]
   ret['info'] = "%s (%s)"%(ret['title'],year)
   ret['name'] = "%s %s"%(ret['title'],year)
  else:
   clean_search = search(r" (?:720|1080|Swesub).",prefix)
   ret['title'] = prefix
   ret['info'] = prefix[0:clean_search.start()] if clean_search else prefix
   ret['name'] = ret['info']

 ret['name']="%s.%s"%(ret['name'].replace(" ","."),filename[-3:])
 return ret

#
#
def check_content(aDict):
 """Function docstring for check_content. Checks file using avprobe to determine content and how to optimize file

 Args:
  - filepath (cond optional)
  - path (cond optional)   
  - file (cond optional)

  - srt (optional), do we already have an SRT?

 Output:
 """ 
 from subprocess import Popen, PIPE, STDOUT
 ret = {'res':'NOT_OK'}
 filename = aDict.get('filepath') if aDict.get('filepath') else ospath.join(aDict.get('path'),aDict.get('file'))
 ret['video'] = {'language':'eng', 'set_default':False}
 ret['audio'] = {'add':[], 'remove':[], 'add_aac':True }
 ret['subtitle'] = {'add':[], 'remove':[], 'languages':[] }

 if aDict.get('srt'):
  ret['subtitle']['languages'].append(aDict.get('srt'))
 if not ospath.exists(filename):
  ret['error'] = 'NO_SUCH_FILE'
  return ret
 try:
  p1 = Popen(["avprobe", filename], stdout=PIPE, stderr=PIPE)
  p2 = Popen(["sed","-n","s/.*Stream #[0-9]\\:\\([0-9]*\\)\(.*\\): \\([AVS][a-z]*\\)/\\3#\\1#\\2#/p"], stdin=p1.stderr, stdout=PIPE)
  entries = p2.communicate()[0]
 except Exception as e:
  ret['error'] = str(err)
 else:
  from re import sub
  for line in entries.split('\n'):
   if line:
    type,slot,lang,info = line.split('#')
    lang = sub('[()]','',lang)   
    # Special case for Video, we are not interested in something without fps..
    if   type == 'Video' and "fps" in info:
     if lang:
      ret['video']['language'] = lang
     else:
      ret['video']['set_default'] = True
    elif type == 'Audio':
     if not lang or lang in ['eng','swe'] or (lang in ['fre','jpn','chi','ita','nor'] and '(default)' in info) or lang == ret['video']['language']:
      ret['audio']['add'].append(slot)
      if ret['audio']['add_aac'] and 'aac' in info and 'stereo' in info:
       ret['audio']['add_aac'] = False
     else:
      ret['audio']['remove'].append(slot)
    elif type == 'Subtitle':
     if not lang: lang = 'eng'
     # if sub with lang is there already or not a sought lang then remove
     if lang in ret['subtitle']['languages'] or not lang in ['eng','swe']:
      ret['subtitle']['remove'].append(slot)
     else:
      ret['subtitle']['add'].append(slot)
      ret['subtitle']['languages'].append(lang)
  ret['res'] = 'OK'
 return ret

#
#
def process(aDict):
 """Function docstring for process. Process a media file

 Args:
  - filepath (cond optional)
  - path (cond optional)                 
  - file (cond optional)

 Output:
 """
 from time import time
 from subprocess import check_call, call
 from os import devnull,chmod,rename,remove
 from zdcp.core.common import log
 filename = aDict.get('filepath') if aDict.get('filepath') else ospath.join(aDict.get('path'),aDict.get('file'))
 ret  = {'prefix':filename[:-4],'suffix':filename[-3:],'timestamp':int(time()),'rename':False,'res':'NOT_OK','error':None}
 srt  = check_srt({'filepath':filename})
 info = aDict if aDict.get('name') and aDict.get('info') else check_title({'filepath':filename})
 dest = ospath.abspath(ospath.join(info['path'],info['name']))
 ret.update({'info':info,'srt':srt,'changes':{'subtitle':"",'audio':"",'srt':""},'dest':dest})

 try:

  if filename != dest:
   try:  rename(filename,dest)
   except Exception as e: ret['error'] = str(e)
   else: ret['rename'] = True

  if ret['suffix'] == 'mkv' and not ret['error']:
   if srt['code']:
    log("INFO - %s - SRT found:%s"%(filename,srt['code']))
    srtfile = "%s.process"%srt['file']
    ret['changes']['srt']="--language 0:{0} --track-name 0:{0} -s 0 -D -A {1}".format(srt['code'], repr(ospath.abspath(srtfile)))
    rename(srt['file'],srtfile)

   probe = check_content({'filepath':dest,'srt':srt.get('code')})
   ret['probe'] = probe

   # if forced download or if there are subs to remove but no subs to add left 
   if len(probe['subtitle']['remove']) > 0:
    ret['changes']['subtitle'] = "--no-subtitles" if len(probe['subtitle']['add']) == 0 else "--stracks " + ",".join(map(str,probe['subtitle']['add']))

   if len(probe['audio']['remove']) and len(probe['audio']['add']) > 0:
    ret['changes']['audio'] = "--atracks " + ",".join(map(str,probe['audio']['add']))
 
   if (ret['rename'] or probe['video']['set_default'] or probe['audio']['add_aac'] or len(ret['changes']['subtitle']) or len(ret['changes']['audio']) or srt['code']):
    log("INFO - %s - Modifying file"%filename)
    FNULL = open(devnull, 'w')

    if ret['rename']:
     ret['update_title'] = info['info']
     call(['mkvpropedit', '--set', "title=" + info['info'], dest], stdout=FNULL, stderr=FNULL)

    if probe['video']['set_default']:
     call(['mkvpropedit', '--edit', 'track:v1', '--set', 'language=eng', dest], stdout=FNULL, stderr=FNULL)

    if probe['audio']['add_aac'] or len(ret['changes']['audio']) or len(ret['changes']['subtitle']) or srt['code']:
     from tempfile import mkdtemp
     log("INFO - %s - Modifying addaac:%s Modify: %s %s"%(probe['audio']['add_aac'],ret['changes']['subtitle'],ret['changes']['audio'], ret['changes']['srt']) )
     tmpfile = filename + ".process"
     rename(dest,tmpfile)
     tempd   = SC['multimedia']['temp_directory'] 
     tempdir = mkdtemp(suffix = "",prefix = 'aac.',dir = tempd)

     if probe['audio']['add_aac']:
      check_call(['avconv', '-i', tmpfile ,'-vn', '-acodec', 'pcm_s16le', '-ac', '2', tempdir + '/audiofile.wav'], stdout=FNULL, stderr=FNULL)
      check_call(['normalize-audio', tempdir + '/audiofile.wav'], stdout=FNULL, stderr=FNULL)
      check_call(['faac', '-c', '48000', '-b', '160', '-q', '100', '-s', tempdir + '/audiofile.wav', '-o',tempdir + '/audiofile.aac'], stdout=FNULL, stderr=FNULL)
      ret['changes']['srt'] = "--language 0:{} --default-track 0 {}/audiofile.aac ".format(probe['video']['language'], tempdir) + ret['changes']['srt']

     call(["mkvmerge -o '{}' {} {} '{}' {}".format(dest,ret['changes']['subtitle'],ret['changes']['audio'],tmpfile, ret['changes']['srt'])], stdout=FNULL, stderr=FNULL, shell=True)
     call(['rm','-fR',tempdir])
     remove(tmpfile)

    if srt['code']: rename(srtfile,srtfile + "ed")

  elif ret['suffix'] == 'mp4' and ret['rename'] and (srt['code'] or aDict.get('modify')):
   FNULL = open(devnull, 'w')
   if srt['code']:
    tmpfile = filename + ".process"
    rename(dest,tmpfile)
    chmod(srt['file'], 0666)
    chmod(dest, 0666)
    call(['MP4Box -add {0}:hdlr=sbtl:lang={1}:name={2}:group=2:layer=-1:disable {3} -out {4}'.format( repr(srt['file']), srt['code'], srt['name'], repr(tmpfile), repr(dest))], shell=True, stdout=FNULL)
    rename(srt['file'],"%s.processed"%srt['file'])
    remove(tmpfile)
   if aDict.get('modify'):
    if info['episode']:
     call(['mp4tags', '-o', info['episode'], '-n', info['episode'][1:3], '-M', info['episode'][4:6], '-S', info['title'], '-m', info['info'], dest], stdout=FNULL, stderr=FNULL)
    else:
     log("WARN - %s - Movie modifications not implemented"%filename)

 except Exception as err:
  ret['error'] = str(err)
  log("XCPT - %s - Error: %s"%(filename,str(err)))
 else:
  ret['seconds'] = (int(time()) - ret['timestamp'])
  if ospath.exists(dest):
   log("INFO - %s - Success - processed in % seconds"%(filename,ret['seconds']))
   chmod(dest, 0666)
   ret['res'] = 'OK'
  else:
   log("ERRR - %s - FAILURE PROCESSING!"%filename)
   ret['error'] = 'COMPLETE_NO_FILE'

 return ret


################################################ TBD ################################################
#
#
def mkv_delay_set(aDict):
 """Function docstring for mkv_delay_set. Sets offset in ms for file xyz

 Args:
  - original (required)
  - offset (required). ms

 Output:
 """
 from time import time
 from subprocess import Popen, PIPE, check_call, call, STDOUT
 from os import devnull,rename,remove
 filename = aDict.get('filepath') if aDict.get('filepath') else ospath.join(aDict.get('path'),aDict.get('file'))
 ret = {'res':'NOT_OK','timestamp':int(time())}

 absfile = ospath.abspath(filename)
 tmpfile = absfile + ".delayset"

 # Find subtitle position 
 try:
  p1 = Popen(["mkvmerge","--identify", filename], stdout=PIPE, stderr=PIPE)
  entries = p1.communicate()[0]
 except Exception as err:
  ret['error']= str(err)
 else:
  for line in entries.split('\n'):
   slots = line.split(' ')
   if slots[0] == "Track" and slots[3] == "subtitles":
    offset=slots[2][0:-1] + ":" + aDict.get('offset',0)
    try:
     rename(absfile,tmpfile)
     FNULL = open(devnull, 'w')
     check_call(["mkvmerge -o "+ repr(absfile) + " -y " + offset + " " + repr(tmpfile)], stdout=FNULL, stderr=FNULL, shell=True)
     remove(tmpfile)
     chmod(absfile,0666)
    except Exception as err:
     ret['error'] = str(err)
    else:
     ret['res'] = 'OK'
 return ret
