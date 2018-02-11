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

visual_components = [
    "Button", "CheckBox", "DataPicker", "Image", "Label",
    "ListPicker", "ListView", "PasswordTextBox", "Slider",
    "Spinner", "TextBox", "TimePicker", "WebViewer",
    "ImagePicker", "VideoPlayer", "Ball", "Canvas",
    "ImageSprite", "Circle", "Map", "Marker", "Rectangle",
    "LineString", "FeatureCollection", "Polygon",
    "ContactPicker", "EmailPicker", "PhoneNumberPicker"
    ]


def unzip_file(z_file, folder):
    with zipfile.ZipFile(z_file, 'r') as z:
        if(os.path.exists(folder)):
            print("---Project already exists---")
        else:
            print("---New project created---")
            z.extractall(folder)
            # Create a new folder with the project name and extract files there
    return z.namelist()


def check_visual_comp(components):
    visual_list = []
    for elem in components:
        if elem['type'] in visual_components:
            visual_list.append(elem['type'])
    return visual_list


def extract_json(path):
    with open(path+".scm", 'r') as scm_data:
        json_data = scm_data.readlines()[2]
    with open(path+".json", 'w') as json_file:
        json_file.write(json_data)
    with open(path+".json", 'r') as json_file:
        d = json.load(json_file)
    os.remove(path+".json")
    return d


def screen_score(scr, comp):
    if scr > 4:
        return 3
    elif scr >= 2:
        return 2
    elif scr == 1 and len(comp) > 1:
        return 1
    else:
        return 0


def get_arrangement(comp, stored):
    if "Arrangement" in comp:
        if comp not in stored:
            stored.append(comp)
    return stored


def user_interface_score(visual, arrang):
    if len(visual) >= 5 and len(arrang) > 1:
        return 3
    elif len(visual) >= 5 and len(arrang) == 1:
        return 2
    elif len(visual) > 2:
        return 1
    else:
        return 0


def get_components(key, nt_list, stored):
    nt_dict = {}    # Name, Type dict
    nt_dict['name'] = key.get('$Name')
    nt_dict['type'] = key.get('$Type')
    stored = get_arrangement(nt_dict['type'], stored)
    nt_list.append(nt_dict)
    if key.get('$Components'):
        for item in key.get('$Components'):
            if item.get('$Components'):
                get_components(item, nt_list, stored)
            else:
                nt_dict = {}
                nt_dict['name'] = item.get('$Name')
                nt_dict['type'] = item.get('$Type')
                nt_list.append(nt_dict)
                stored = get_arrangement(nt_dict['type'], stored)
    return nt_list


def get_variables(root, ns):     # Obtains the variables names
    expr = './/{' + ns + '}block[@type="global_declaration"]/{'+ns+'}field'
    blocks = root.findall(expr)
    for element in blocks:
        pass    # print(element.text)
    expr = './/{'+ns+'}block[@type="local_declaration_statement"]'
    expr += '/{'+ns+'}field'
    blocks = root.findall(expr)
    for element in blocks:
        pass    # print(element.text)


def count_bad_names(nt_list):
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
            if n.split(t)[1] in str(range(1, 99)):  # Can't change Screen1 name
                count += 1
    return float(count)/float(len(nt_list))


def naming_score(bad):
    if bad < 0.25:
        return 3
    elif bad < 0.74:
        return 2
    elif bad < 0.9:
        return 1
    else:
        return 0


def conditional_blocks(root, ns, count):
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


def conditional_score(cond_blocks):
    result = 0
    if cond_blocks['if'] > 0:
        result += 1
    if cond_blocks['else'] > 0:
        result += 1
    if cond_blocks['elseif'] > 0:
        result += 1
    return result


def loop_blocks(root, ns, count):
    wh = './/{' + ns + '}block[@type="controls_while"]'
    fRan = './/{' + ns + '}block[@type="controls_forRange"]'
    fEach = './/{' + ns + '}block[@type="controls_forEach"]'
    count['while'] += len(root.findall(wh))
    count['range'] += len(root.findall(fRan))
    count['list'] += len(root.findall(fEach))
    return count


def loop_score(loops):
    if loops['list'] > 0:
        return 3
    elif loops['range'] > 0:
        return 2
    elif loops['while'] > 0:
        return 1
    else:
        return 0


def event_blocks(root, ns, ev_list):
    expr = './/{'+ns+'}block[@type="component_event"]'
    mut = '{'+ns+"}"+'mutation'
    for element in root.findall(expr+"/"+mut):
        if element.get("event_name") not in ev_list:
            ev_list.append(element.get("event_name"))
    return len(ev_list)


def event_score(events):
    if len(events) > 3:
        return 3
    elif len(events) >= 2:
        return 2
    elif len(events) == 1:
        return 1
    else:
        return 0


def proc_blocks(root, ns, nprocs, repeated):
    result = [
        './/{'+ns+'}block[@type="procedures_defreturn"]',
        './/{'+ns+'}block[@type="procedure_callreturn"]'
        ]
    do = [
        './/{'+ns+'}block[@type="procedures_defnoreturn"]',
        './/{'+ns+'}block[@type="procedures_callnoreturn"]'
        ]
    procs = len(root.findall(result[0])) + len(root.findall(do[0]))
    calls = len(root.findall(result[1])) + len(root.findall(do[1]))
    if calls > procs:
        repeated = True
    return nprocs+procs, repeated


def proc_score(procs, repeated):
    if procs > 1 and repeated:
        return 3
    elif procs > 1:
        return 2
    elif procs == 1:
        return 1
    else:
        return 0


def list_blocks(root, ns, uni_blocks, multi_blocks):
    expr = './/{'+ns+'}block[@type="lists_create_with"]'
    multi = '/{'+ns+'}value/{'+ns+'}block[@type="lists_create_with"]'
    multi_blocks += len(root.findall(expr+multi))
    uni_blocks += len(root.findall(expr))
    return uni_blocks, multi_blocks


def list_score(uni, multi):
    if multi != 0:
        return 3
    elif uni > 1:
        return 2
    elif uni == 1:
        return 1
    else:
        return 0


def sensor_blocks(comp_dict):
    sensors = {}
    for element in comp_dict:
        if element['type'] == "AccelerometerSensor":
            sensors['accel'] = True
        if element['type'] == "BarcodeScanner":
            sensors['barscan'] = True
        if element['type'] == "Clock":
            sensors['clock'] = True
        if element['type'] == "GyroscopeSensor":
            sensors['gyros'] = True
        if element['type'] == "LocationSensor":
            sensors['location'] = True
        if element['type'] == "NearField":
            sensors['near'] = True
        if element['type'] == "OrientationSensor":
            sensors['orient'] = True
        if element['type'] == "Pedometer":
            sensors['pedometer'] = True
        if element['type'] == "ProximitySensor":
            sensors['prox'] = True

    return sensors


def media_blocks(comp_dict):
    media = {}
    for element in comp_dict:
        if element['type'] == "Camcorder":
            media['camcord'] = True
        elif element['type'] == "Camera":
            media['cam'] = True
        elif element['type'] == "ImagePicker":
            media['imgpick'] = True
        elif element['type'] == "Player":
            media['player'] = True
        elif element['type'] == "Sound":
            media['sound'] = True
        elif element['type'] == "SoundRecorder":
            media['soundrec'] = True
        elif element['type'] == "SpeechRecognizer":
            media['sprec'] = True
        elif element['type'] == "TextToSpeech":
            media['ttspeech'] = True
        elif element['type'] == "VideoPlayer":
            media['vidplay'] = True
        elif element['type'] == "YandexTranslate":
            media['yandex'] = True
    return media


def connect_blocks(comp_dict):
    score = 0
    for element in comp_dict:
        if element['type'] == "ActivityStarter":
            if score < 1:
                score = 1
        elif element['type'] == "BluetoothClient" \
                or element['type'] == "BluetoothServer":
            if score < 2:
                score = 2
        elif element['type'] == "Web":
            if score < 3:
                score = 3
    return score


def ncomp_score(total):
    if len(total) > 2:
        return 3
    elif len(total) == 2:
        return 2
    elif len(total) == 1:
        return 1
    else:
        return 0


def social_blocks(comp_dict):
    social = {}
    for element in comp_dict:
        if element['type'] == "ContactPicker":
            social['contact'] = True
        elif element['type'] == "EmailPicker":
            social['email'] = True
        elif element['type'] == "PhoneCall":
            social['phone'] = True
        elif element['type'] == "PhoneNumberPicker":
            social['numberpick'] = True
        elif element['type'] == "Sharing":
            social['share'] = True
        elif element['type'] == "Texting":
            social['text'] = True
        elif element['type'] == "Twitter":
            social['twitter'] = True
    return social


def draw_blocks(comp_dict):
    score = 0
    for element in comp_dict:
        if element['type'] == "Canvas":
            if score < 1:
                score = 1
        elif element['type'] == "Ball":
            if score < 2:
                score = 2
        elif element['type'] == "ImageSprite":
            if score < 3:
                score = 3
    return score


def operator_blocks(root, ns, oplist):
    expr = './/{'+ns+'}block'
    for block in root.findall(expr):
        block_type = block.get("type")
        if "math" in block_type or "logic" in block_type:
            if block_type not in oplist:
                oplist.append(block_type)
    return oplist


def operator_score(oplist):
    if len(oplist) > 2:
        return 3
    else:
        return len(oplist)


def data_persistance_blocks(comp_dict):
    dp_list = []
    for element in comp_dict:
        if element['type'] == "TinyWebDB" \
                or element['type'] == "TinyDB" \
                or element['type'] == "File" \
                or element['type'] == "FusiontablesControl":
            dp_list.append(element['type'])
    return dp_list


def data_persistance_score(elem_list):
    if "TinyWebDB" in elem_list:
        return 3
    elif "TinyDB" in elem_list:
        return 2
    elif "File" in elem_list or "FusiontablesControl" in elem_list:
        return 1
    else:
        return 0


def read_files(scr, folder, name):
    scr_name = name[:-4]
    with open(os.path.join(folder, name)) as bky:
        bky_content = bky.read()
    scm_content = extract_json(os.path.join(folder, scr_name))
    scr.append({
        "scrID": str(scr_name),
        "bky": bky_content,
        "scm": scm_content
        })
    return scr


def extract_data(u_name, f_name):
    f_folder = os.path.join(settings.SAVED_PROJECTS, u_name, f_name.name[:-4])
    z_list = unzip_file(f_name, f_folder)
    with open(os.path.join(f_folder, z_list[-1])) as f:
        f_content = f.read().split('.')
        ai_user = f_content[1]
        proj_id = f_content[2]
    comb = "src/appinventor"
    content_path = os.path.join(f_folder, comb, ai_user, proj_id)
    # Screens Path
    list_dir = os.listdir(content_path)
    scr = []    # List of screen components (ID, bky & scm)

    for elem in list_dir:
        scr_name, ext = elem.split('.')
        if ext == "bky":
            scr = read_files(scr, content_path, elem)

    blocks = []
    comp_dict = []
    ev_list = []
    dp_list = []
    sensors = {}
    media = {}
    social = {}
    score_connect = 0
    score_draw = 0
    proc_count = 0
    proc_rep = False
    count_blocks = 0
    cond_count = {'if': 0, 'else': 0, 'elseif': 0}
    loop_count = {'while': 0, 'range': 0, 'list': 0}
    uni_lists = 0
    multi_lists = 0
    dp_list = []
    operators_list = []
    arrangment_list = []
    for n in range(0, len(scr)):
        screen = scr[n]
        if scr[n]["bky"]:
            tree = ET.fromstring(scr[n]["bky"])
            nsxml = tree.tag.split('}', 1)[0][1:]
            # Namespace of the xml http://www.w3.org/1999/xhtml
            expr = './/{' + nsxml + '}block'
            count_blocks += len(tree.findall(expr))
            event_count = event_blocks(tree, nsxml, ev_list)
            cond_count = conditional_blocks(tree, nsxml, cond_count)
            loop_count = loop_blocks(tree, nsxml, loop_count)
            proc_count, proc_rep = proc_blocks(tree, nsxml, proc_count, proc_rep)
            uni_lists, multi_lists = list_blocks(tree, nsxml, uni_lists, multi_lists)
            get_variables(tree, nsxml)
            operators_list = operator_blocks(tree, nsxml, operators_list)
        else:
            pass    # print("There is empty screens")
            # len(scr)-=1??

        scm_path = os.path.join(content_path, scr[n]["scrID"])
        d = extract_json(scm_path)
        comp_dict = get_components(d.get('Properties'), comp_dict, arrangment_list)
    visual_list = check_visual_comp(comp_dict)
    bad_names = count_bad_names(comp_dict)
    score_scr = screen_score(len(scr), comp_dict)
    score_naming = naming_score(bad_names)
    score_cond = conditional_score(cond_count)
    score_events = event_score(ev_list)
    score_loop = loop_score(loop_count)
    score_proc = proc_score(proc_count, proc_rep)
    score_list = list_score(uni_lists, multi_lists)
    sensors = sensor_blocks(comp_dict)
    score_sensors = ncomp_score(sensors)
    media = media_blocks(comp_dict)
    score_media = ncomp_score(media)
    social = social_blocks(comp_dict)
    score_social = ncomp_score(social)
    score_connect = connect_blocks(comp_dict)
    score_draw = draw_blocks(comp_dict)
    dp_list = data_persistance_blocks(comp_dict)
    score_dp = data_persistance_score(dp_list)
    score_op = operator_score(operators_list)
    score_ui = user_interface_score(visual_list, arrangment_list)

    score = {
        'scr': score_scr, 'naming': score_naming, 'conditional': score_cond,
        'events': score_events, 'loop': score_loop, 'proc': score_proc,
        'lists': score_list, 'dp': score_dp, 'sensors': score_sensors,
        'media': score_media, 'social': score_social, 'connect': score_connect,
        'draw': score_draw, 'operator': score_op, 'ui': score_ui
        }

    return score
