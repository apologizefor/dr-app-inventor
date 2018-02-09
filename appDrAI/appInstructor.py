import os
import re
import zipfile
import xml.etree.ElementTree as ET
import json
from django.conf import settings

"""
visual_components = ["Button", "CheckBox", "DataPicker", "Image", "Label",
            "ListPicker", "ListView", "PasswordTextBox", "Slider", "Spinner",
            "TextBox", "TimePicker", "WebViewer", "HorizontalArrangement",
            "HorizontalScrollArrangement", "VerticalArrangement",
            "VerticalScrollArrangement", "ImagePicker", "VideoPlayer", "Ball",
            "Canvas", "ImageSprite", "Circle", "Map", "Marker", "Rectangle",
            "LineString", "FeatureCollection", "Polygon", "ContactPicker",
            "EmailPicker", "PhoneNumberPicker"]
"""

visual_components = ["Button", "CheckBox", "DataPicker", "Image", "Label",
            "ListPicker", "ListView", "PasswordTextBox", "Slider", "Spinner",
            "TextBox", "TimePicker", "WebViewer", "ImagePicker", "VideoPlayer",
            "Ball", "Canvas", "ImageSprite", "Circle", "Map", "Marker",
            "Rectangle", "LineString", "FeatureCollection", "Polygon",
            "ContactPicker", "EmailPicker", "PhoneNumberPicker"]

def unzipFile(z_file,folder):
    with zipfile.ZipFile(z_file, 'r') as z:
        if(os.path.exists(folder)):
            print("---Project already exists---")
        else:
            print("---New project created---")
            z.extractall(folder) # Create a new folder with the project name and extract files there
    return z.namelist()

def visualComponents(components):
    visual_list = []
    for elem in components:
        if elem['type'] in visual_components:
            visual_list.append(elem['type'])
    return visual_list

def extractJSON(path):
    with open(path+".scm",'r') as scm_data:
        json_data = scm_data.readlines()[2]
    with open(path+".json",'w') as json_file:
        json_file.write(json_data)
    with open(path+".json",'r') as json_file:
        d = json.load(json_file)
    os.remove(path+".json")
    return d

def screenScore(scr,comp):
    if scr > 4:
        return 3
    elif scr >= 2:
        return 2
    elif scr == 1 and len(comp) > 1:
        return 1
    else:
        return 0

def getArrangement(comp,stored):
    if "Arrangement" in comp:
        if comp not in stored:
            stored.append(comp)
    return stored

def userInterfaceScore(visual,arrang):
    print("Arrangement",len(visual),visual,arrang)
    if len(visual) >= 5 and len(arrang) > 1:
        return 3
    elif len(visual) >= 5 and len(arrang) == 1:
        return 2
    elif len(visual) > 2:
        return 1
    else:
        return 0

def getComponents(key,nt_list,stored):
    nt_dict = {}    # Name, Type dict
    nt_dict['name'] = key.get('$Name')
    nt_dict['type'] = key.get('$Type')
    stored = getArrangement(nt_dict['type'],stored)
    nt_list.append(nt_dict)
    if key.get('$Components'):
        for item in key.get('$Components'):
            if item.get('$Components'):
                getComponents(item, nt_list,stored)
            else:
                nt_dict = {}
                nt_dict['name'] = item.get('$Name')
                nt_dict['type'] = item.get('$Type')
                nt_list.append(nt_dict)
                stored = getArrangement(nt_dict['type'],stored)
    return nt_list

def getVariables(root,ns): # Obtains the variables names
    expr = './/{' + ns + '}block[@type="global_declaration"]/{'+ns+'}field'
    blocks = root.findall(expr)
    for element in blocks:
        pass #print(element.text)
    expr = './/{' + ns + '}block[@type="local_declaration_statement"]/{'+ns+'}field'
    blocks = root.findall(expr)
    for element in blocks:
        pass #print(element.text)

def countBadNames(nt_list):
    count = 0
    # nt_list contains COMPONENTS names and types.
    """ If there's only an empty screen this return 100%_ bad naming.
    if len(nt_list) == 1:
        return 1
    """
    for item in nt_list:
        n = item.get("name")
        t = item.get("type")
        if len(n.split(t)) == 2 and n.split(t)[0] == "":
            """
            if t == "Form":
                if n.split("Screen")[1] in str(range(2,99)): # Can't change Screen1 name
                    count += 1
            else:
            """
            if n.split(t)[1] in str(range(1,99)): # Can't change Screen1 name
                count += 1
    return float(count)/float(len(nt_list))

def namingScore(bad):
    if bad < 0.25:
        return 3
    elif bad < 0.74:
        return 2
    elif bad < 0.9:
        return 1
    else:
        return 0

def conditionalBlocks(root,ns,count):
    expr = './/{' + ns + '}block[@type="controls_if"]'
    choose = './/{' + ns + '}block[@type="controls_choose"]'
    mut = '{'+ns+"}"+'mutation'
    cond_mut = root.findall(expr + "/" + mut)
    else_c = len(root.findall(choose))
    elseif_c = 0
    total = len(root.findall(expr)) + else_c
    for tag in cond_mut:
        for attrib in tag.attrib:
            if attrib == "else":
                else_c += 1
            elif attrib == "elseif":
                elseif_c += 1
    count['if'] += total - else_c - elseif_c
    count['else'] += else_c
    count['elseif'] += elseif_c
    return count

def conditionalScore(cond_blocks):
    result = 0
    if cond_blocks['if'] > 0:
        result += 1
    if cond_blocks['else'] > 0:
        result += 1
    if cond_blocks['elseif'] > 0:
        result += 1
    return result

def loopBlocks(root,ns,count):
    wh = './/{' + ns + '}block[@type="controls_while"]'
    fRan = './/{' + ns + '}block[@type="controls_forRange"]'
    fEach = './/{' + ns + '}block[@type="controls_forEach"]'
    count['while'] += len(root.findall(wh))
    count['range'] += len(root.findall(fRan))
    count['list'] += len(root.findall(fEach))
    return count

def loopScore(loops):
    if loops['list'] > 0:
        return 3
    elif loops['range'] > 0:
        return 2
    elif loops['while'] > 0:
        return 1
    else:
        return 0

def eventBlocks(root,ns,ev_list):
    expr = './/{'+ns+'}block[@type="component_event"]'
    mut = '{'+ns+"}"+'mutation'
    for element in root.findall(expr+"/"+mut):
        if element.get("event_name") not in ev_list:
            ev_list.append(element.get("event_name"))
    return len(ev_list)

def eventScore(events):
    if len(events) > 3:
        return 3
    elif len(events) >= 2:
        return 2
    elif len(events) == 1:
        return 1
    else:
        return 0

"""
def procBlocks(root,ns,pr_list,repeated):
    expr = './/{'+ns+'}block[@type="component_method"]' # Component procedures
    mut = '{'+ns+"}"+'mutation'
    for element in root.findall(expr+"/"+mut):
        if element.get("method_name") not in pr_list:
            pr_list.append(element.get("method_name"))
        else:
            repeated = True
    return len(pr_list),repeated
"""

def procBlocks(root,ns,nprocs,repeated):
    result = ['.//{'+ns+'}block[@type="procedures_defreturn"]','.//{'+ns+'}block[@type="procedure_callreturn"]']
    do = ['.//{'+ns+'}block[@type="procedures_defnoreturn"]','.//{'+ns+'}block[@type="procedures_callnoreturn"]']
    procs = len(root.findall(result[0])) + len(root.findall(do[0]))
    calls = len(root.findall(result[1])) + len(root.findall(do[1]))
    if calls > procs:
        repeated = True
    return nprocs+procs,repeated

def procScore(procs, repeated):
    if procs > 1 and repeated:
        return 3
    elif procs > 1:
        return  2
    elif procs == 1:
        return  1
    else:
        return 0

def listBlocks(root,ns,uni_blocks,multi_blocks):
    expr = './/{'+ns+'}block[@type="lists_create_with"]'
    multi = '/{'+ns+'}value/{'+ns+'}block[@type="lists_create_with"]'
    multi_blocks += len(root.findall(expr+multi))
    uni_blocks += len(root.findall(expr))
    return uni_blocks, multi_blocks

def listScore(uni,multi):
    if multi != 0:
        return 3
    elif uni > 1:
        return 2
    elif uni == 1:
        return 1
    else:
        return 0

def sensorBlocks(root,ns,sensors):
    expr = './/{'+ns+'}mutation'
    for element in root.findall(expr):
        if element.get("component_type") == "AccelerometerSensor":
            sensors['accel'] = True
        if element.get("component_type") == "BarcodeScanner":
            sensors['barscan'] = True
        if element.get("component_type") == "Clock":
            sensors['clock'] = True
        if element.get("component_type") == "GyroscopeSensor":
            sensors['gyros'] = True
        if element.get("component_type") == "LocationSensor":
            sensors['location'] = True
        if element.get("component_type") == "NearField":
            sensors['near'] = True
        if element.get("component_type") == "OrientationSensor":
            sensors['orient'] = True
        if element.get("component_type") == "Pedometer":
            sensors['pedometer'] = True
        if element.get("component_type") == "ProximitySensor":
            sensors['prox'] = True

    return sensors

def mediaBlocks(root,ns,media):
    expr = './/{'+ns+'}mutation'
    for element in root.findall(expr):
        if element.get("component_type") == "Camcorder":
            media['camcord'] = True
        elif element.get("component_type") == "Camera":
            media['cam'] = True
        elif element.get("component_type") == "ImagePicker":
            media['imgpick'] = True
        elif element.get("component_type") == "Player":
            media['player'] = True
        elif element.get("component_type") == "Sound":
            media['sound'] = True
        elif element.get("component_type") == "SoundRecorder":
            media['soundrec'] = True
        elif element.get("component_type") == "SpeechRecognizer":
            media['sprec'] = True
        elif element.get("component_type") == "TextToSpeech":
            media['ttspeech'] = True
        elif element.get("component_type") == "VideoPlayer":
            media['vidplay'] = True
        elif element.get("component_type") == "YandexTranslate":
            media['yandex'] = True
    return media

def connectBlocks(root,ns,score):
    expr = './/{'+ns+'}mutation'
    for element in root.findall(expr):
        if element.get("component_type") == "ActivityStarter":
            if score < 1:
                score = 1
        elif element.get("component_type") == "BluetoothClient" or element.get("component_type") == "BluetoothServer":
            if score < 2:
                score = 2
        elif element.get("component_type") == "Web":
            if score < 3:
                score = 3
    return score

def nCompScore(total):
    if len(total) > 2:
        return 3
    elif len(total) == 2:
        return 2
    elif len(total) == 1:
        return 1
    else:
        return 0

def socialBlocks(root,ns,social):
    expr = './/{'+ns+'}mutation'
    for element in root.findall(expr):
        if element.get("component_type") == "ContactPicker":
            social['contact'] = True
        elif element.get("component_type") == "EmailPicker":
            social['email'] = True
        elif element.get("component_type") == "PhoneCall":
            social['phone'] = True
        elif element.get("component_type") == "PhoneNumberPicker":
            social['numberpick'] = True
        elif element.get("component_type") == "Sharing":
            social['share'] = True
        elif element.get("component_type") == "Texting":
            social['text'] = True
        elif element.get("component_type") == "Twitter":
            social['twitter'] = True
    return social

def drawBlocks(root,ns,score):
    expr = './/{'+ns+'}mutation'
    for element in root.findall(expr):
        if element.get("component_type") == "Canvas":
            if score < 1:
                score = 1
        elif element.get("component_type") == "Ball":
            if score < 2:
                score = 2
        elif element.get("component_type") == "ImageSprite":
            if score < 3:
                score = 3
    return score

def operatorBlocks(root,ns,oplist):
    expr = './/{'+ns+'}block'
    for block in root.findall(expr):
        block_type = block.get("type")
        if "math" in block_type or "logic" in block_type:
            if block_type not in oplist:
                oplist.append(block_type)
    return oplist

def operatorScore(oplist):
    if len(oplist) > 2:
        return 3
    else:
        return len(oplist)

def dataPersistanceBlocks(root,ns,elem_list):
    mut = './/{'+ns+"}"+'mutation'
    for element in root.findall(mut):
        elem_list.append(element.get("component_type"))
    return elem_list

def dataPersistanceScore(elem_list):
    if "TinyWebDB" in elem_list:
        return 3
    elif "TinyDB" in elem_list:
        return 2
    elif "File" in elem_list or "FusiontablesControl" in elem_list:
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
    dp_list = []
    sensors = {}
    media = {}
    social = {}
    connect_score = 0
    draw_score = 0
    proc_count = 0
    proc_rep = False
    count_blocks = 0
    conditional_count = {'if': 0, 'else': 0, 'elseif': 0}
    loop_count = {'while': 0, 'range': 0, 'list': 0}
    uni_lists = 0
    multi_lists = 0
    dp_list = []
    operators_list = []
    arrangment_list = []
    for n in range(0,n_scr):
        screen = scr[n]
        if scr[n]["bky"]:
            tree = ET.fromstring(scr[n]["bky"])
            namespace = tree.tag.split('}',1)[0][1:] # Namespace of the xml http://www.w3.org/1999/xhtml
            expr = './/{' +namespace + '}block'
            count_blocks += len(tree.findall(expr))
            event_count = eventBlocks(tree,namespace,ev_list)
            conditional_count = conditionalBlocks(tree,namespace,conditional_count)
            loop_count = loopBlocks(tree,namespace,loop_count)
            proc_count,proc_rep = procBlocks(tree,namespace,proc_count, proc_rep)
            sensors = sensorBlocks(tree,namespace,sensors)
            media = mediaBlocks(tree,namespace,media)
            social = socialBlocks(tree,namespace,social)
            connect_score = connectBlocks(tree,namespace,connect_score)
            draw_score = drawBlocks(tree,namespace,draw_score)
            uni_lists,multi_lists = listBlocks(tree,namespace,uni_lists,multi_lists)
            dp_list = dataPersistanceBlocks(tree,namespace,dp_list)
            getVariables(tree, namespace)
            operators_list = operatorBlocks(tree,namespace,operators_list)
        else:
            pass #print("There is empty screens")
            # n_scr-=1??

        scm_path = os.path.join(content_path, scr[n]["scrID"])
        d = extractJSON(scm_path)
        comp_dict = getComponents(d.get('Properties'), comp_dict,arrangment_list)
    visual_list = visualComponents(comp_dict)
    bad_names = countBadNames(comp_dict)
    scr_score = screenScore(n_scr,comp_dict)
    naming_score = namingScore(bad_names)
    cond_score = conditionalScore(conditional_count)
    event_score = eventScore(ev_list)
    loop_score = loopScore(loop_count)
    proc_score = procScore(proc_count,proc_rep)
    dp_score = dataPersistanceScore(dp_list)
    list_score = listScore(uni_lists,multi_lists)
    sensors_score = nCompScore(sensors)
    media_score = nCompScore(media)
    social_score = nCompScore(social)
    op_score = operatorScore(operators_list)
    ui_score = userInterfaceScore(visual_list,arrangment_list)

    return (scr_score, naming_score, cond_score, event_score, loop_score, proc_score,
            list_score, dp_score, sensors_score, media_score,social_score,connect_score,
            draw_score, op_score,ui_score)
