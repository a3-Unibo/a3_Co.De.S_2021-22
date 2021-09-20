import rhinoscriptsyntax as rs
import scriptcontext as sc

"""
Script written by Alessio Erioli - mod of willemderks.com
Script version October 6, 2020
"""

def AutolabelPoints():
    text_height = 10
    font_name = 'Arial'
    if (sc.sticky.has_key("NumPrefix")):
        prefix = sc.sticky["NumPrefix"]
    else:
        prefix = ""

    if (sc.sticky.has_key("NumSuffix")):
        suffix = sc.sticky["NumSuffix"]
    else:
        suffix = ""
    
    ids = rs.GetObjects('Select points to label', 1)
    if not ids: return
    
    start = rs.GetInteger("Start index",0)
    if not start: start=0
    
    prefix = rs.StringBox('Numbering prefix (Cancel for none)', default_value = prefix, title = "Number prefix")
    if not prefix: prefix = ''
    sc.sticky["NumPrefix"] = prefix
    
    suffix = rs.StringBox('Numbering suffix (Cancel for none)', default_value = suffix, title = "Number suffix")
    if not suffix: suffix = ''
    sc.sticky["NumSuffix"] = suffix
    
    count = start + len(ids)
    padding = len(str(count))
    
    pad_str =  '{}'.format(':0{}d'.format(padding))
    pad_str = '{'+pad_str+'}'
    
    dot_ids = []
    
    for i,id in enumerate(ids):
        num_str = pad_str.format(start+i)
        text_str = '{}{}{}'.format(prefix, num_str, suffix)
        pt = id
        dot_id = rs.AddTextDot(text_str, pt)
        #rs.TextDotFont(dot_id, font_name)
        #rs.TextDotHeight(dot_id, text_height)
        dot_ids.append(dot_id)

    rs.AddObjectsToGroup(dot_ids, rs.AddGroup())

    
AutolabelPoints()   