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
 """Function docstring for menu TBD

 Args:

 Output:
 """
 ret = {}
 if aCTX.site.get('portal') and aCTX.site['portal'].get('start'):
  ret['start'] = True
  item = aCTX.site['menuitem'][aCTX.site['portal']['start']]
  ret['menu'] = [{'icon':'images/icon-start.png', 'title':'Start', 'href':item['href'], 'view':item.get('view','inline'),'type':'menuitem' }]
 else:
  ret['start'] = False
  ret['menu'] = []
 ret['menu'].extend(resources(aCTX,{'type':'menuitem'})['data'])
 ret['title'] = aCTX.site.get('portal',{}).get('title','Portal')
 return ret

#
#
def resources(aCTX, aArgs = None):
 """Function returns site information

 Args:
  - type (optional)

 Output:
 """
 ret = {}
 types = ['menuitem','tool'] if not 'type' in aArgs else [aArgs['type']]
 ret['data'] = []
 for type in types:
  ret['data'].extend([{'title':k,'type':type,'href':v['href'],'icon':v['icon'],'view':v.get('view','inline')} for k,v in aCTX.site.get(type,{}).items()])
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
 ret = {'href':aCTX.site[aArgs['type']][aArgs['title']]['href']}
 return ret
