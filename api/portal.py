"""Portal REST module. Provides node independent interaction"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

####################################### SITE ######################################
#
#
def application(aRT, aArgs):
 """Function docstring for application. Using 'portal' config ('title', 'message' and title of start page...)

 Args:

 Output:
 """
 ret = {'message':"Welcome to the Management Portal",'title':'Portal'}
 ret.update(aRT.config['site'].get('portal'))
 return ret

#
#
def menu(aRT, aArgs):
 """Function docstring for menu

 Args:

 Output:
 """
 data = {}
 data['start'] = aRT.config['site']['portal'].get('start')
 # INTERNAL from rims.api.portal import resources
 data['menu'] = resources(aRT,{'type':'menuitem'})['data']
 data['title'] = aRT.config['site'].get('portal',{}).get('title','Portal')
 return {'status':'OK','data':data}

#
#
def resources(aRT, aArgs):
 """Function returns site information

 Args:
  - type (required)

 Output:
 """
 ret = {'data':[]}
 ret['data'] = aRT.config['site'].get(aArgs['type'],{})
 return ret

#
#
def resource(aRT, aArgs):
 """Function returns resource href

 Args:
  - type (required)
  - title (required)

 Output:
 """
 data = aRT.config['site'][aArgs['type']][aArgs['title']]
 for tp in ['module','frame','tab']:
  if tp in data:
   ret = {tp:aRT.config['site'][aArgs['type']][aArgs['title']][tp]}
   break
 return ret

############################### Site ###########################
#
#
def theme_list(aRT, aArgs):
 """ Function returns a list of available themes

 Args:

 Output:
  - list of theme names
 """
 themes = ['light','dark']
 themes.extend(aRT.config.get('site',{}).get('theme',{}).keys())
 return {'data':themes}

#
#
def theme_info(aRT, aArgs):
 """ Function returns theme parameters

 Args:
  - theme (required)

 Output:
  - data - dictionary of values
 """
 themes = {
  "light":{ "main":"#F1F1F1", "head":"#1A1A1A", "head-focus":"#666666", "head-txt":"#FFFFFF", "high":"#CB2026", "std":"#FFFFFF", "std-txt":"#000000", "ui":"#000000", "ui-txt":"#FFFFFF" },
  "dark":{  "main":"#0A0A0A", "head":"#1A1A1A", "head-focus":"#666666", "head-txt":"#FFFFFF", "high":"#CB2026", "std":"#1A1A1A", "std-txt":"#9CA6B0", "ui":"#000000", "ui-txt":"#FFFFFF" }
 }
 theme = {f"--{k}-color":v for k,v in themes.get(aArgs['theme'],aRT.config.get('site',{}).get('theme',{}).get(aArgs['theme'],{})).items()}
 return {'status':"OK" if theme else "NOT_OK", 'data':theme}
