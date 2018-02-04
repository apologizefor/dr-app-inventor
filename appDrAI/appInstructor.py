import os
import re
import zipfile
import xml.etree.ElementTree as ET
import json
from django.conf import settings

def unzipFile(z_file,folder):
    with zipfile.ZipFile(z_file, 'r') as z:
        if(os.path.exists(folder)):
            print("---Project already exists---")
        else:
            print("---New project created---")
            z.extractall(folder) # Create a new folder with the project name and extract files there
    return z.namelist()

def extractJSON(path):
    with open(path+".scm",'r') as scm_data:
        json_data = scm_data.readlines()[2]
    with open(path+".json",'w') as json_file:
        json_file.write(json_data)
    with open(path+".json",'r') as json_file:
        d = json.load(json_file)
    os.remove(path+".json")
    return d

def getNameType(key,nt_list):
    nt_dict = {}    # Name, Type dict
    nt_dict['name'] = key.get('$Name')
    nt_dict['type'] = key.get('$Type')
    nt_list.append(nt_dict)
    if key.get('$Components'):
        for item in key.get('$Components'):
            if item.get('$Components'):
                getNameType(item, nt_list)
            else:
                nt_dict = {}
                nt_dict['name'] = item.get('$Name')
                nt_dict['type'] = item.get('$Type')
                nt_list.append(nt_dict)
    return nt_list

def searchBadNames(nt_list):
    count = 0
    for item in nt_list:
        n = item.get("name")
        t = item.get("type")
        #print(n,t)
        if(len(n.split(t)) == 2):
            count += 1
    return count

def conditionalBlocks(root,ns):
    expr = './/{' + ns['xmlns'] + '}block[@type="controls_if"]'
    mut = '{'+ns["xmlns"]+"}"+'mutation'
    cond_mut = root.findall(expr + "/" + mut)
    total = len(root.findall(expr))
    else_c = 0
    elseif_c = 0
    cond = {}
    for tag in cond_mut:
        for attrib in tag.attrib:
            if attrib == "else":
                else_c += 1
            elif attrib == "elseif":
                elseif_c += 1
    return(total - else_c - elseif_c, else_c, elseif_c)

def loopBlocks(root,ns):
    wh = './/{' + ns['xmlns'] + '}block[@type="controls_while"]'
    fRan = './/{' + ns['xmlns'] + '}block[@type="controls_forRange"]'
    fEach = './/{' + ns['xmlns'] + '}block[@type="controls_forEach"]'
    while_c = len(root.findall(wh))
    fRan_c = len(root.findall(fRan))
    fEach_c = len(root.findall(fEach))
    return(while_c, fRan_c, fEach_c)

def eventBlocks(root,ns):
    expr = './/{' + ns['xmlns'] + '}block[@type="component_event"]'
    return len(root.findall(expr))

def procBlocks(root,ns):
    expr = './/{' + ns['xmlns'] + '}block[@type="component_method"]'
    return len(root.findall(expr))

def listBlocks(root,ns):
    expr = './/{' + ns['xmlns'] + '}block'
    lists_c = 0
    all_blocks = root.findall(expr)
    for block in all_blocks:
        if block.get("type").split('_')[0] == "lists":
            lists_c += 1
    return lists_c

def extractData(u_name, f_name):
    f_folder = os.path.join(settings.SAVED_PROJECTS,u_name,f_name.name[:-4])
    z_list = unzipFile(f_name,f_folder)
    with open(os.path.join(f_folder, z_list[-1])) as f:
        f_content = f.read().split('.')
        ai_user_id = f_content[1]
        proj_id = f_content[2]
    content_path = os.path.join(f_folder,"src","appinventor",ai_user_id,proj_id) # Screens Path
    list_dir = os.listdir(content_path)

    n_scr = 0   # Number of screens
    scr = []    # List of screen components (ID, bky & scm)

    for elem in list_dir:
        scr_name, ext = elem.split('.')
        if ext == "bky":
            with open(os.path.join(content_path,elem)) as bky:
                bky_content = bky.read()
            scm_content = extractJSON(os.path.join(content_path,scr_name))
            scr.append({"scrID":str(scr_name),"bky":bky_content,"scm":scm_content})
            n_scr += 1

    blocks = []
    bl_dict = []
    count_blocks = 0
    conditional_count = {'if': 0, 'else': 0, 'elseif': 0}
    loop_count = {'while': 0, 'range': 0, 'list': 0}
    event_count = 0
    proc_count = 0
    lists_count = 0
    for n in range(0,n_scr):
        screen = scr[n]
        if scr[n]["bky"]:
            tree = ET.fromstring(scr[n]["bky"])
            namespace = {'xmlns': tree.tag.split('}',1)[0][1:]} # Namespace of the xml http://www.w3.org/1999/xhtml
            """ COUNT BLOCKS """
            tag = "block"
            expr = './/{' +namespace['xmlns'] + '}'+ tag
            #for block in tree.findall(expr):
            #    print(block.get("type"));
            count_blocks += len(tree.findall(expr))
            event_count += eventBlocks(tree,namespace)
            if_c, else_c, elseif_c = conditionalBlocks(tree,namespace)
            conditional_count['if'] += if_c
            conditional_count['else'] += else_c
            conditional_count['elseif'] += elseif_c
            w_c, fr_c, fl_c = loopBlocks(tree,namespace)
            loop_count['while'] += w_c
            loop_count['range'] += fr_c
            loop_count['list'] + fl_c
            proc_count += procBlocks(tree,namespace)
            lists_count += listBlocks(tree,namespace)
        else:
            pass #print("There is empty screens")
            # n_scr-=1??

        scm_path = os.path.join(content_path, scr[n]["scrID"])
        d = extractJSON(scm_path)
        bl_dict = getNameType(d.get('Properties'), bl_dict)
    bad_names = float(searchBadNames(bl_dict))/float(len(bl_dict))
    return (n_scr, round(bad_names,3), conditional_count, event_count, loop_count, proc_count, lists_count)
