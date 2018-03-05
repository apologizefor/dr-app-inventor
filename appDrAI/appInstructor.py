import os
import zipfile
import xml.etree.ElementTree as ET
import json
try:
    from django.conf import settings
except:
    pass

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


def unzip_file(zip_file, folder):
    with zipfile.ZipFile(zip_file, 'r') as project:
        if(os.path.exists(folder)):
            print("---Project already exists---")
        else:
            print("---New project created---")
            project.extractall(folder)
            # Create a new folder with the project name and extract files there
    return project.namelist()


def check_visual_comp(components):
    visual_list = []
    for item in components:
        if item['type'] in visual_components:
            visual_list.append(item['type'])
    return visual_list


def extract_json(path):
    with open(path+".scm", 'r') as scm_data:
        json_data = scm_data.readlines()[2]
    with open(path+".json", 'w') as json_file:
        json_file.write(json_data)
    with open(path+".json", 'r') as json_file:
        scm_content = json.load(json_file)
    os.remove(path+".json")
    return scm_content


def screen_score(screens, components):
    if screens > 4:
        return 3
    elif screens >= 2:
        return 2
    elif screens == 1 and len(components) > 1:
        return 1
    else:
        return 0


def get_arrangement(components, stored):
    if "Arrangement" in components:
        if components not in stored:
            stored.append(components)
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


def get_components(key, components, stored):
    nt_dict = {}    # Name, Type dict
    nt_dict['name'] = key.get('$Name')
    nt_dict['type'] = key.get('$Type')
    stored = get_arrangement(nt_dict['type'], stored)
    components.append(nt_dict)
    if key.get('$Components'):
        for item in key.get('$Components'):
            if item.get('$Components'):
                get_components(item, components, stored)
            else:
                nt_dict = {}
                nt_dict['name'] = item.get('$Name')
                nt_dict['type'] = item.get('$Type')
                components.append(nt_dict)
                stored = get_arrangement(nt_dict['type'], stored)
    return components


def get_variables(root, ns):     # Obtains the variables names
    expr = './/{'+ns+'}block[@type="global_declaration"]/{'+ns+'}field'
    blocks = root.findall(expr)
    for item in blocks:
        pass    # print(item.text)
    expr = './/{'+ns+'}block[@type="local_declaration_statement"]'
    expr += '/{'+ns+'}field'
    blocks = root.findall(expr)
    for item in blocks:
        pass    # print(item.text)


def count_bad_names(components):
    count = 0
    for item in components:
        n = item.get("name")
        t = item.get("type")
        if t == "Form":
            if len(n.split("Screen")) == 2 and n.split("Screen")[0] == "":
                if n.split("Screen")[1] == '1':     # Can't change Screen1
                    pass
                elif n.split("Screen")[1] in str(range(2, 99)):
                    count += 1
        elif len(n.split(t)) == 2 and n.split(t)[0] == "":
            if n.split(t)[1] in str(range(1, 99)):
                count += 1
    return float(count)/float(len(components))


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
    expr = './/{'+ns+'}block[@type="controls_if"]'
    choose = './/{'+ns+'}block[@type="controls_choose"]'
    mut = '{'+ns+"}"+'mutation'
    cond_mut = root.findall(expr+"/"+mut)
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


def loop_blocks(root, ns, blocks):
    wh = './/{'+ns+'}block[@type="controls_while"]'
    fRan = './/{'+ns+'}block[@type="controls_forRange"]'
    fEach = './/{'+ns+'}block[@type="controls_forEach"]'
    blocks['while'] += len(root.findall(wh))
    blocks['range'] += len(root.findall(fRan))
    blocks['list'] += len(root.findall(fEach))
    return blocks


def loop_score(blocks):
    if blocks['list'] > 0:
        return 3
    elif blocks['range'] > 0:
        return 2
    elif blocks['while'] > 0:
        return 1
    else:
        return 0


def event_blocks(root, ns, blocks):
    expr = './/{'+ns+'}block[@type="component_event"]'
    mut = '{'+ns+"}"+'mutation'
    for item in root.findall(expr+"/"+mut):
        if item.get("event_name") not in blocks:
            blocks.append(item.get("event_name"))
    return len(blocks)


def event_score(blocks):
    if len(blocks) > 3:
        return 3
    elif len(blocks) >= 2:
        return 2
    elif len(blocks) == 1:
        return 1
    else:
        return 0


def proc_blocks(root, ns, blocks):
    result = [
        './/{'+ns+'}block[@type="procedures_defreturn"]',
        './/{'+ns+'}block[@type="procedure_callreturn"]'
        ]
    do = [
        './/{'+ns+'}block[@type="procedures_defnoreturn"]',
        './/{'+ns+'}block[@type="procedures_callnoreturn"]'
        ]
    procs = len(root.findall(result[0])) + len(root.findall(do[0]))
    blocks['count'] += procs
    calls = len(root.findall(result[1])) + len(root.findall(do[1]))
    if calls > procs:
        blocks['rep'] = True
    return blocks


def proc_score(blocks):
    if blocks['count'] > 1 and blocks['rep']:
        return 3
    elif blocks['count'] > 1:
        return 2
    elif blocks['count'] == 1:
        return 1
    else:
        return 0


def list_blocks(root, ns, blocks):
    expr = './/{'+ns+'}block[@type="lists_create_with"]'
    multi = '/{'+ns+'}value/{'+ns+'}block[@type="lists_create_with"]'
    blocks['multi'] += len(root.findall(expr+multi))
    blocks['uni'] += len(root.findall(expr))
    return blocks


def list_score(blocks):
    if blocks['multi'] != 0:
        return 3
    elif blocks['uni'] > 1:
        return 2
    elif blocks['uni'] == 1:
        return 1
    else:
        return 0


def sensor_blocks(components):
    sensors = {}
    for item in components:
        if item['type'] == "AccelerometerSensor":
            sensors['accel'] = True
        if item['type'] == "BarcodeScanner":
            sensors['barscan'] = True
        if item['type'] == "Clock":
            sensors['clock'] = True
        if item['type'] == "GyroscopeSensor":
            sensors['gyros'] = True
        if item['type'] == "LocationSensor":
            sensors['location'] = True
        if item['type'] == "NearField":
            sensors['near'] = True
        if item['type'] == "OrientationSensor":
            sensors['orient'] = True
        if item['type'] == "Pedometer":
            sensors['pedometer'] = True
        if item['type'] == "ProximitySensor":
            sensors['prox'] = True

    return sensors


def media_blocks(components):
    media = {}
    for item in components:
        if item['type'] == "Camcorder":
            media['camcord'] = True
        elif item['type'] == "Camera":
            media['cam'] = True
        elif item['type'] == "ImagePicker":
            media['imgpick'] = True
        elif item['type'] == "Player":
            media['player'] = True
        elif item['type'] == "Sound":
            media['sound'] = True
        elif item['type'] == "SoundRecorder":
            media['soundrec'] = True
        elif item['type'] == "SpeechRecognizer":
            media['sprec'] = True
        elif item['type'] == "TextToSpeech":
            media['ttspeech'] = True
        elif item['type'] == "VideoPlayer":
            media['vidplay'] = True
        elif item['type'] == "YandexTranslate":
            media['yandex'] = True
    return media


def connect_blocks(components):
    score = 0
    for item in components:
        if item['type'] == "ActivityStarter":
            if score < 1:
                score = 1
        elif item['type'] == "BluetoothClient" \
                or item['type'] == "BluetoothServer":
            if score < 2:
                score = 2
        elif item['type'] == "Web":
            if score < 3:
                score = 3
    return score


def ncomp_score(blocks):
    if len(blocks) > 2:
        return 3
    elif len(blocks) == 2:
        return 2
    elif len(blocks) == 1:
        return 1
    else:
        return 0


def social_blocks(components):
    social = {}
    for item in components:
        if item['type'] == "ContactPicker":
            social['contact'] = True
        elif item['type'] == "EmailPicker":
            social['email'] = True
        elif item['type'] == "PhoneCall":
            social['phone'] = True
        elif item['type'] == "PhoneNumberPicker":
            social['numberpick'] = True
        elif item['type'] == "Sharing":
            social['share'] = True
        elif item['type'] == "Texting":
            social['text'] = True
        elif item['type'] == "Twitter":
            social['twitter'] = True
    return social


def draw_blocks(components):
    score = 0
    for item in components:
        if item['type'] == "Canvas":
            if score < 1:
                score = 1
        elif item['type'] == "Ball":
            if score < 2:
                score = 2
        elif item['type'] == "ImageSprite":
            if score < 3:
                score = 3
    return score


def operator_blocks(root, ns, blocks):
    expr = './/{'+ns+'}block'
    for item in root.findall(expr):
        block_type = item.get("type")
        if "math" in block_type or "logic" in block_type:
            if block_type not in blocks:
                blocks.append(block_type)
    return blocks


def operator_score(blocks):
    if len(blocks) > 2:
        return 3
    else:
        return len(blocks)


def data_persistance_blocks(components):
    dp = []
    for item in components:
        if item['type'] == "TinyWebDB" \
                or item['type'] == "TinyDB" \
                or item['type'] == "File" \
                or item['type'] == "FusiontablesControl":
            dp.append(item['type'])
    return dp


def data_persistance_score(blocks):
    if "TinyWebDB" in blocks:
        return 3
    elif "TinyDB" in blocks:
        return 2
    elif "File" in blocks or "FusiontablesControl" in blocks:
        return 1
    else:
        return 0


def read_files(screens, folder, name):
    scr_name = name[:-4]
    with open(os.path.join(folder, name)) as bky:
        bky_content = bky.read()
    scm_content = extract_json(os.path.join(folder, scr_name))
    screens.append({
        "scrID": str(scr_name),
        "bky": bky_content,
        "scm": scm_content
        })
    return screens


def extract_blocks(root, expr, blocks):
    for elem in root.findall(expr):
        block_type = elem.attrib['type']
        if block_type not in blocks.keys():
            blocks[block_type] = 1
        else:
            blocks[block_type] += 1
    return blocks

def delete_empty_projects(dirs, folder, name):
    if "assets/abstrata.PNG" in dirs:
        folder_proj = os.path.join(folder, name)
        os.remove(folder_proj)
        return True
    else:
        return False


def extract_data(user, aia):
    try:
        folder = os.path.join(settings.SAVED_PROJECTS, user, aia.name[:-4])
        dirs_zip = unzip_file(aia, folder)
    except:
        dirs_aia = '../../../AI_files/proj'
        folder = os.path.join(dirs_aia, user, aia[:-4])
        folder_new = os.path.join(dirs_aia, aia), folder
        dirs_zip = unzip_file(os.path.join(dirs_aia, aia), folder)
        if delete_empty_projects(dirs_zip, dirs_aia, aia):
            return 0, 0

    with open(os.path.join(folder, dirs_zip[-1])) as info:
        info_content = info.read().split('.')
        proj_user = info_content[1]
        proj_name = info_content[2]
    route = "src/appinventor/"+proj_user+"/"+proj_name
    folder_screens = os.path.join(folder, route)
    # Screens Path
    dirs_list = os.listdir(folder_screens)
    scr = []    # List of screen components (name, .bky & .scm)

    for elem in dirs_list:
        scr_name, ext = elem.split('.')
        if ext == "bky":
            scr = read_files(scr, folder_screens, elem)

    components = []
    list_dp = []
    list_events = []
    list_operators = []
    list_arrangement = []
    blocks = {'number': 0}
    blocks_media = {}
    blocks_social = {}
    blocks_sensors = {}
    values_list = {'uni': 0, 'multi': 0}
    values_proc = {'count': 0, 'rep': False}
    values_cond = {'if': 0, 'else': 0, 'elseif': 0}
    values_loop = {'while': 0, 'range': 0, 'list': 0}
    for s in scr:
        if s["bky"]:
            tree = ET.fromstring(s["bky"])
            nsxml = tree.tag.split('}', 1)[0][1:]
            # Namespace of the xml http://www.w3.org/1999/xhtml
            expr = './/{' + nsxml + '}block'
            blocks = extract_blocks(tree, expr, blocks)
            blocks['number'] += len(tree.findall(expr))
            event_count = event_blocks(tree, nsxml, list_events)
            values_cond = conditional_blocks(tree, nsxml, values_cond)
            values_loop = loop_blocks(tree, nsxml, values_loop)
            values_proc = proc_blocks(tree, nsxml, values_proc)
            values_list = list_blocks(tree, nsxml, values_list)
            get_variables(tree, nsxml)
            list_operators = operator_blocks(tree, nsxml, list_operators)
        else:
            pass    # print("There is empty screens")
            # len(scr)-=1??
        scm = s["scm"].get('Properties')
        components = get_components(scm, components, list_arrangement)
    list_visual = check_visual_comp(components)
    bad_names = count_bad_names(components)
    score_scr = screen_score(len(scr), components)
    score_naming = naming_score(bad_names)
    score_cond = conditional_score(values_cond)
    score_events = event_score(list_events)
    score_loop = loop_score(values_loop)
    score_proc = proc_score(values_proc)
    score_list = list_score(values_list)
    blocks_sensors = sensor_blocks(components)
    score_sensors = ncomp_score(blocks_sensors)
    blocks_media = media_blocks(components)
    score_media = ncomp_score(blocks_media)
    blocks_social = social_blocks(components)
    score_social = ncomp_score(blocks_social)
    score_connect = connect_blocks(components)
    score_draw = draw_blocks(components)
    list_dp = data_persistance_blocks(components)
    score_dp = data_persistance_score(list_dp)
    score_op = operator_score(list_operators)
    score_ui = user_interface_score(list_visual, list_arrangement)

    score = {
        'scr': score_scr, 'naming': score_naming, 'conditional': score_cond,
        'events': score_events, 'loop': score_loop, 'proc': score_proc,
        'lists': score_list, 'dp': score_dp, 'sensors': score_sensors,
        'media': score_media, 'social': score_social, 'connect': score_connect,
        'draw': score_draw, 'operator': score_op, 'ui': score_ui
        }
    return score, blocks
