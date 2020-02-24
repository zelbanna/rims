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
