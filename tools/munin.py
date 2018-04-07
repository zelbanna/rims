"""Module docstring.

Module for graph interaction

Exports:
- discover
- widget_cols
- widget_rows

"""  
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"

def _print_graph_link(asource, aX = "399", aY = "224"):
 from time import time
 stop  = int(time())-300
 start = stop - 24*3600 
 print "<A TARGET=main_cont HREF='munin-cgi/munin-cgi-html/static/dynazoom.html?"
 print "cgiurl_graph=/munin-cgi/munin-cgi-graph&plugin_name={0}&size_x=800&size_y=400&start_epoch={1}&stop_epoch={2}'>".format(asource,str(start),str(stop))
 print "<IMG width={0} height={1} ALT='munin graph:{2}' SRC='/munin-cgi/munin-cgi-graph/{2}-day.png' /></A>".format(aX, aY, asource)

def widget_cols(asources):
 lwidth = 3 if len(asources) < 3 else len(asources)
 print "<DIV STYLE='padding:5px; width:{}px; height:240px; float:left;'>".format(str(lwidth * 410))
 for src in asources:
  _print_graph_link(src)
 print "</DIV>"

def widget_rows(asources):
 lheight = 3 if len(asources) < 3 else len(asources)
 print "<DIV STYLE='padding-top:10px; padding-left:5px; width:420px; height:{}px; float:left;'>".format(str(lheight * 230))
 for src in asources:         
  _print_graph_link(src)      
 print "</DIV>"
