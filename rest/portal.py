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
 if aCTX.site.get('portal') and aCTX.site['portal'].get('start'):
  ret['start'] = True
  ret['menu'] = [{'icon':'images/icon-start.png', 'title':'Start','type':'menuitem' }]
  item = aCTX.site['menuitem'][aCTX.site['portal']['start']]
  for tp in ['module','frame','tab']:
   if tp in item:
    ret['menu'][0][tp] = item[tp]
    break
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
  for k,item in aCTX.site.get(type,{}).items():
   data = {'title':k,'type':type,'icon':item['icon']}
   ret['data'].append(data)
   for tp in ['module','frame','tab']:
    if tp in item:
     data[tp] = item[tp]
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
