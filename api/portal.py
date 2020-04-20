"""Portal REST module. Provides node independent interaction"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

####################################### SITE ######################################
#
#
def application(aCTX, aArgs = None):
 """Function docstring for application. Using 'portal' config ('title', 'message' and title of start page...)

 Args:

 Output:
 """
 """ Default login information """
 ret = {'message':"Welcome to the Management Portal",'title':'Portal'}
 ret.update(aCTX.site.get('portal'))
 return ret

#
#
def menu(aCTX, aArgs = None):
 """Function docstring for menu

 Args:

 Output:
 """
 ret = {}
 ret['start'] = aCTX.site['portal'].get('start')
 ret['menu'] = resources(aCTX,{'type':'menuitem'})['data']
 ret['title'] = aCTX.site.get('portal',{}).get('title','Portal')
 return ret

#
#
def resources(aCTX, aArgs = None):
 """Function returns site information

 Args:
  - type (required)

 Output:
 """
 ret = {'data':[]}
 ret['data'] = aCTX.site.get(aArgs['type'],{})
 return ret

#
#
def resource(aCTX, aArgs = None):
 """Function returns resource href

 Args:
  - type (required)
  - title (required)

 Output:
 """
 data = aCTX.site[aArgs['type']][aArgs['title']]
 for tp in ['module','frame','tab']:
  if tp in data:
   ret = {tp:aCTX.site[aArgs['type']][aArgs['title']][tp]}
   break
 return ret

############################### Site ###########################
#
#
def theme_list(aCTX, aArgs = None):
 """ Function returns a list of available themes

 Args:

 Output:
  - list of theme names
 """
 return {'data':['light','dark']}

#
#
def theme_info(aCTX, aArgs = None):
 """ Function returns theme parameters

 Args:
  - theme (required)

 Output:
  - data - dictionary of values
 """
 themes = {
  "light":{ "main":"#F1F1F1", "head":"#1A1A1A", "head-txt":"#FFFFFF", "high":"#CB2026", "std":"#FFFFFF", "std-txt":"#000000", "ui":"#000000", "ui-txt":"#FFFFFF" },
  "dark":{  "main":"#0A0A0A", "head":"#1A1A1A", "head-txt":"#FFFFFF", "high":"#CB2026", "std":"#1A1A1A", "std-txt":"#9CA6B0", "ui":"#000000", "ui-txt":"#FFFFFF" }
 }

 theme = {"--%s-color"%k:v for k,v in themes.get(aArgs['theme'],{}).items()}
 return {'status':"OK" if len(theme) > 0 else "NOT_OK", 'data':theme}
