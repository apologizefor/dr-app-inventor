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

def getComponents(key,nt_list):
    nt_dict = {}    # Name, Type dict
    nt_dict['name'] = key.get('$Name')
    nt_dict['type'] = key.get('$Type')
    nt_list.append(nt_dict)
    if key.get('$Components'):
        for item in key.get('$Components'):
            if item.get('$Components'):
                getComponents(item, nt_list)
            else:
                nt_dict = {}
                nt_dict['name'] = item.get('$Name')
                nt_dict['type'] = item.get('$Type')
    return nt_list

def getVariables(root,ns): # Obtains the variables names
    expr = './/{' + ns + '}block[@type="global_declaration"]/{'+ns+'}field'
    blocks = root.findall(expr)
    for element in blocks:
        print(element.text)
    expr = './/{' + ns + '}block[@type="local_declaration_statement"]/{'+ns+'}field'
    blocks = root.findall(expr)
    for element in blocks:
        print(element.text)

def searchBadNames(nt_list):
    count = 0
    # nt_list contains COMPONENTS names and types.
    for item in nt_list:
        n = item.get("name")
        t = item.get("type")
        #print(n,t)
        if(len(n.split(t)) == 2):
            count += 1
    return count

def conditionalBlocks(root,ns):
    expr = './/{' + ns + '}block[@type="controls_if"]'
    mut = '{'+ns+"}"+'mutation'
    cond_mut = root.findall(expr + "/" + mut)
    total = len(root.findall(expr))
    else_c = 0
    elseif_c = 0
    for tag in cond_mut:
        for attrib in tag.attrib:
            if attrib == "else":
                else_c += 1
            elif attrib == "elseif":
                elseif_c += 1
    result = {'if':total - else_c - elseif_c,'else':else_c,'elseif':elseif_c}
    return result

def loopBlocks(root,ns):
    wh = './/{' + ns + '}block[@type="controls_while"]'
    fRan = './/{' + ns + '}block[@type="controls_forRange"]'
    fEach = './/{' + ns + '}block[@type="controls_forEach"]'
    while_c = len(root.findall(wh))
    fRan_c = len(root.findall(fRan))
    fEach_c = len(root.findall(fEach))
    result = {'while':while_c,'range': fRan_c, 'list':fEach_c}
    return result

def eventBlocks(root,ns,ev_list):
    expr = './/{'+ns+'}block[@type="component_event"]'
    mut = '{'+ns+"}"+'mutation'
    for element in root.findall(expr+"/"+mut):
        if element.get("event_name") not in ev_list:
            ev_list.append(element.get("event_name"))
    return len(ev_list)

def procBlocks(root,ns,pr_list,repeated):
    expr = './/{'+ns+'}block[@type="component_method"]'
    mut = '{'+ns+"}"+'mutation'
    for element in root.findall(expr+"/"+mut):
        if element.get("method_name") not in pr_list:
            pr_list.append(element.get("method_name"))
        else:
            repeated = True
    return len(pr_list),repeated

def listBlocks(root,ns):
    expr = './/{'+ns+'}block'
    lists_c = 0
    all_blocks = root.findall(expr)
    for block in all_blocks:
        if block.get("type").split('_')[0] == "lists":
            lists_c += 1
    return lists_c

def screenScore(scr):
    if scr > 4:
        return 3
    elif scr >= 2:
        return 2
    elif scr == 1:
        return 1
    else:
        return 0

def namingScore(bad):
    if bad < 0.25:
        return 3
    elif bad < 0.74:
        return 2
    elif bad < 0.9:
        return 1
    else:
        return 0

def conditionalScore(cond_blocks):
    result = 0
    if cond_blocks['if'] > 0:
        result += 1
    if cond_blocks['else'] > 0:
        result += 1
    if cond_blocks['elseif'] > 0:
        result += 1
    return result

def eventScore(events):
    if len(events) > 3:
        return 3
    elif len(events) >= 2:
        return 2
    elif len(events) == 1:
        return 1
    else:
        return 0

def loopScore(loops):
    result = 0
    if loops['while'] > 0:
        result += 1
    if loops['range'] > 0:
        result += 1
    if loops['list'] > 0:
        result += 1
    return result

def procScore(procs, repeated):
    if procs > 1 and repeated:
        return 3
    elif procs > 1:
        return  2
    elif procs == 1:
        return  1
    else:
        return 0

def dataPersistanceScore(root,ns):
    mut = './/{'+ns+"}"+'mutation'
    elem_list = []
    for element in root.findall(mut):
        elem_list.append(element.get("component_type"))

    if "TinyWebDB" in elem_list:
        return 3
    elif "TinyDB" in elem_list:
        return 2
    elif "File" in elem_list or "FusiontablesControl" in elem_list:
        return 1
    else:
        return 0

def listScore(lists):
    if lists > 2:
        return 3
    elif lists == 2:
        return 2
    elif lists == 1:
        return 1
    else:
        return 0

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
    comp_dict = []
    ev_list = []
    proc_list = []
    proc_rep = False
    count_blocks = 0
    conditional_count = {'if': 0, 'else': 0, 'elseif': 0}
    loop_count = {'while': 0, 'range': 0, 'list': 0}
    lists_count = 0
    for n in range(0,n_scr):
        screen = scr[n]
        if scr[n]["bky"]:
            tree = ET.fromstring(scr[n]["bky"])
            namespace = tree.tag.split('}',1)[0][1:] # Namespace of the xml http://www.w3.org/1999/xhtml
            expr = './/{' +namespace + '}block'
            count_blocks += len(tree.findall(expr))
            event_count = eventBlocks(tree,namespace,ev_list)
            conditional_count = conditionalBlocks(tree,namespace)
            loop_count = loopBlocks(tree,namespace)
            proc_count, proc_rep = procBlocks(tree,namespace,proc_list, proc_rep)
            lists_count += listBlocks(tree,namespace)
            getVariables(tree, namespace)
        else:
            pass #print("There is empty screens")
            # n_scr-=1??

        scm_path = os.path.join(content_path, scr[n]["scrID"])
        d = extractJSON(scm_path)
        comp_dict = getComponents(d.get('Properties'), comp_dict)
    bad_names = float(searchBadNames(comp_dict))/float(len(comp_dict))
    scr_score = screenScore(n_scr)
    naming_score = namingScore(bad_names)
    cond_score = conditionalScore(conditional_count)
    event_score = eventScore(ev_list)
    loop_score = loopScore(loop_count)
    proc_score = procScore(proc_count,proc_rep)
    dp_score = dataPersistanceScore(tree,namespace)
    list_score = listScore(lists_count)
    return (scr_score, naming_score, cond_score, event_score, loop_score, proc_score, list_score, dp_score)
