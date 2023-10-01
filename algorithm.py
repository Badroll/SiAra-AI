import re

def tipe(c):
    r = ""
    if (c in ["a", "n", "c", "r", "k", "f", "t", "s", "w", "l", "p", "d", "j", "y", "v", "m", "g", "b", "q", "z"]):
        r = "aksara"
    elif (c in ["H", "N", "C", "R", "K", "F", "T", "S", "W", "L", "P", "D", "J", "Y", "V", "M", "G", "B", "Q", "Z"]):
        r = "pasangan"
    elif (c in ["e", "[", "i", "u", "o"]):
        r = "vokal"
    elif (c in ["r", "=", "h"]):
        r = "paten"
    elif (c in ["\\"]):
        r = "pangkon"
    elif (c in ["]", "}", "-"]):
        r = "cakra"
    return r     

def format_list(list):
    r = []
    for i in list:
        bb = ",".join([i[0], str(i[2]), str(i[3]), str(i[4]), str(i[5])])
        r.append(bb)
    return r

def sort_horizontal_by_centroid(detections):
    # Mengurutkan objek berdasarkan koordinat x dari centroid
    sorted_objects = sorted(detections, key=lambda x: (x[2] + x[4]) / 2)  # Menggunakan koordinat x dari centroid
    return sorted_objects

def sort_vertical_by_centroid(detections):
    # Mengurutkan objek berdasarkan koordinat y dari centroid
    sorted_objects = sorted(detections, key=lambda x: (x[3] + x[5]) / 2)  # Menggunakan koordinat y dari centroid
    return sorted_objects

def sort_horizontal_by_xmin(detections):
    def get_xmin(item):
        return item[2]
    sorted_data = sorted(detections, key=get_xmin)
    return sorted_data

def get_testing_data():
    import xml.etree.ElementTree as ET
    xml_file = 'ds-object/riset1/image_2023-09-15_15-24-26.xml'
    tree = ET.parse(xml_file)
    root = tree.getroot()
    object_list = []
    for obj_elem in root.findall('.//object'):
        name = obj_elem.find('name').text
        xmin = int(obj_elem.find('.//xmin').text)
        ymin = int(obj_elem.find('.//ymin').text)
        xmax = int(obj_elem.find('.//xmax').text)
        ymax = int(obj_elem.find('.//ymax').text)
        object_list.append([name, 0.2345, xmin, ymin, xmax, ymax])
    return object_list

def find_LRTB(pos, objek, horizontal_objects):
    # BERPOTENSI MASALAH!

    # 1
    # objek test dg objek utama harus terpisah.
    # akan bermasalah jika ada objek di dalam objek (walaupun centriod keduanya berbeda).
    # cek pada variable condition

    # 2
    # algoritmanya masih berpotensi masalah
    # dengan variable condition, lalu jumlahkan centroid masing2 sumbu
    # sepertinya masih ada kemungkinan miss

    objek1_info = objek.split(',')
    xmin_objek1 = int(objek1_info[1])
    ymin_objek1 = int(objek1_info[2])
    xmax_objek1 = int(objek1_info[3])
    ymax_objek1 = int(objek1_info[4])
    objek1_centroid_x = (xmin_objek1 + xmax_objek1) / 2
    objek1_centroid_y = (ymin_objek1 + ymax_objek1) / 2

    object_centroids = []
    objcts = []
    stack = 0

    for obj_info in horizontal_objects:
        obj_info_list = obj_info.split(',')
        xmin_objek = int(obj_info_list[1])
        ymin_objek = int(obj_info_list[2])
        xmax_objek = int(obj_info_list[3])
        ymax_objek = int(obj_info_list[4])
        
        obj_centroid_x = (xmin_objek + xmax_objek) / 2
        obj_centroid_y = (ymin_objek + ymax_objek) / 2

        condition = False
        if pos == "L":
            condition = xmax_objek < xmin_objek1
        elif pos == "R":
            condition = xmin_objek > xmax_objek1
        elif pos == "T":
            condition = ymax_objek < ymin_objek1
        elif pos == "B":
            condition = ymin_objek > ymax_objek1
        
        if condition and stack <= 3:
            object_centroids.append((obj_centroid_x, obj_centroid_y))
            objcts.append(obj_info)
            stack += 1

    def euclidean_distance(x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    def euclidean_distance_x(x1, x2):
        return abs(x1 - x2)
    def euclidean_distance_y(y1, y2):
        return abs(y1 - y2)
    
    if pos == "L":
        print(objcts)
        print(object_centroids)

    closest_centroid_idx = None
    closest_centroid_distance = float('inf')

    for idx, (obj_centroid_x, obj_centroid_y) in enumerate(object_centroids):
        # #cari berdasarkan centroid tengah terdekat
        # distance = euclidean_distance(objek1_centroid_x, objek1_centroid_y, obj_centroid_x, obj_centroid_y)
        # if distance < closest_centroid_distance:
        #     closest_centroid_distance = distance
        #     closest_centroid_idx = idx

        # #cari berdasarkan centroid sumbu lawan terdekat
        # if pos == "L" or pos == "R":
        #     distance_y = euclidean_distance_y(objek1_centroid_y, obj_centroid_y)
        #     if distance_y < closest_centroid_distance:
        #         closest_centroid_distance = distance_y
        #         closest_centroid_idx = idx
        # elif pos == "T" or pos == "B":
        #     distance_x = euclidean_distance_x(objek1_centroid_x, obj_centroid_x)
        #     if distance_x < closest_centroid_distance:
        #         closest_centroid_distance = distance_x
        #         closest_centroid_idx = idx

        #cari berdasarkan penjumlajan centroid masing2 sumbu
        distance_x = euclidean_distance_x(objek1_centroid_x, obj_centroid_x)
        distance_y = euclidean_distance_y(objek1_centroid_y, obj_centroid_y)
        total_distance = distance_x + distance_y
        if total_distance < closest_centroid_distance:
            closest_centroid_distance = total_distance
            closest_centroid_idx = idx

    objek_terdekat = None
    if closest_centroid_idx is not None:
        objek_terdekat = objcts[closest_centroid_idx]
    
    print(f"Objek terdekat di sebelah {pos} dari {objek} adalah {objek_terdekat}")
    return objek_terdekat

def post_processing(test_data):
    processed = []
    for char_elemen in test_data:
        char_karakter = char_elemen[0]
        char_jenis = tipe(char_karakter)
        conf = char_elemen[1]
        if char_jenis == "aksara" or (char_jenis == "pasangan" and not char_karakter == "V"):
            if conf > 0.8:
                processed.append(char_elemen)
        elif char_karakter == "V" or char_karakter == "-" or char_jenis == "pangkon":
            if conf > 0.4:
                processed.append(char_elemen)
        elif char_jenis == "vokal":
            if conf > 0.4:
                processed.append(char_elemen)
        elif char_jenis == "paten":
            if conf > 0.4:
                processed.append(char_elemen)
        elif char_karakter == "]" or char_karakter == "}":
            if conf > 0.4:
                processed.append(char_elemen)
    print(processed)
    return processed
       
def arrange(test_data):
    listH = sort_horizontal_by_xmin(test_data)
    listH_formatted = format_list(listH)

    main_centroid_y = None
    for karakter in listH_formatted:
        karakter_elemen = karakter.split(",")
        karakter_karakter = karakter_elemen[0]
        karakter_jenis = tipe(karakter_karakter)
        karakter_xmin = int(karakter_elemen[1])
        karakter_ymin = int(karakter_elemen[2])
        karakter_xmax = int(karakter_elemen[3])
        karakter_ymax = int(karakter_elemen[4])
        if karakter_jenis == "aksara":
            main_centroid_y = (karakter_ymin + karakter_ymax) / 2
            break

    list_stack = []
    list_processed_karakter = []
    print("listH_formatted", listH_formatted)
    for i, row in enumerate(listH_formatted):
        karakter_elemen = row.split(",")
        karakter_karakter = karakter_elemen[0]
        karakter_jenis = tipe(karakter_karakter)
        karakter_xmin = int(karakter_elemen[1])
        karakter_ymin = int(karakter_elemen[2])
        karakter_xmax = int(karakter_elemen[3])
        karakter_ymax = int(karakter_elemen[4])
        if karakter_karakter == "[":
            print("TALING")
            list_processed_karakter.append(row)
            list_stack.append([row])
        elif karakter_jenis == "aksara":
            print("AKSARA",row)
            list_processed_karakter.append(row)
            # karakter_centroid_x = (karakter_xmin + karakter_xmax) / 2
            # karakter_centroid_y = (karakter_ymin + karakter_ymax) / 2
            stack_karakter = [row]
            next_centroid_x = None
            for i2, row2 in enumerate(listH_formatted):
                if i2 <= i:
                    continue
                next_elemen = row2.split(",")
                next_karakter = next_elemen[0]
                next_jenis = tipe(next_karakter)
                if next_karakter == "[" or next_jenis == "aksara":
                    next_valid = next_elemen
                    next_xmin = int(next_elemen[1])
                    next_ymin = int(next_elemen[2])
                    next_xmax = int(next_elemen[3])
                    next_ymax = int(next_elemen[4])
                    next_centroid_x = (next_xmin + next_xmax) / 2
                    print("(break)", row2)
                    break
            for i2, row2 in enumerate(listH_formatted):
                neighbor_elemen = row2.split(",")
                neighbor_karakter = neighbor_elemen[0]
                neighbor_jenis = tipe(neighbor_karakter)
                neighbor_xmin = int(neighbor_elemen[1])
                neighbor_ymin = int(neighbor_elemen[2])
                neighbor_xmax = int(neighbor_elemen[3])
                neighbor_ymax = int(neighbor_elemen[4])
                neighbor_centroid_x = (neighbor_xmin + neighbor_xmax) / 2
                # neighbor_centroid_y = (neighbor_ymin + neighbor_ymax) / 2
                rules = [
                    not row2 == row,
                    row2 not in list_processed_karakter,
                    (not neighbor_jenis == "aksara" and not neighbor_karakter == "["),
                    (next_centroid_x == None or neighbor_centroid_x < next_centroid_x)
                ]
                print("------------------------------")
                print(rules)
                print(next_centroid_x)
                print(row)
                print(row2)
                if not False in rules:
                    print("APPEND")
                    stack_karakter.append(row2)
                    list_processed_karakter.append(row2)
            #
            list_stack.append(stack_karakter)

    r = ""    
    for i, row in enumerate(list_stack):
        print(row)
        have_aksara = None
        have_pasangan = None
        have_cakra = None
        have_vokal = None
        have_paten = None
        have_pangkon = None
        for i2, row2 in enumerate(row):
            print(row2)
            karakter_elemen = row2.split(",")
            karakter_karakter = karakter_elemen[0]
            karakter_jenis = tipe(karakter_karakter)
            if karakter_jenis == "aksara":
                have_aksara = karakter_karakter
            elif karakter_jenis == "pasangan":
                have_pasangan = karakter_karakter
            elif karakter_jenis == "cakra":
                have_cakra = karakter_karakter
            elif karakter_jenis == "vokal":
                have_vokal = karakter_karakter
            elif karakter_jenis == "paten":
                have_paten = karakter_karakter
            elif karakter_jenis == "pangkon":
                have_pangkon = karakter_karakter
        if not have_aksara == None:
            r += have_aksara
        if not have_pasangan == None:
            r += have_pasangan
        if not have_cakra == None:
            r += have_cakra
        if not have_vokal == None:
            r += have_vokal
        if not have_paten == None:
            r += have_paten
        if not have_pangkon == None:
            r += have_pangkon
    
    print("==========================")
    print(r)
    return r

# ==============================================

def labeled2aksara(kalimat):
    r = ""

    ref = {'a': 'aksara_ha', 'n': 'aksara_na', 'c': 'aksara_ca', 'r': 'aksara_ra', 'k': 'aksara_ka', 'f': 'aksara_da', 't': 'aksara_ta', 's': 'aksara_sa', 'w': 'aksara_wa', 'l': 'aksara_la', 'p': 'aksara_pa', 'd': 'aksara_dha', 'j': 'aksara_ja', 'y': 'aksara_ya', 'v': 'aksara_nya', 'm': 'aksara_ma', 'g': 'aksara_ga', 'b': 'aksara_ba', 'q': 'aksara_tha', 'z': 'aksara_nga', 'H': 'pasangan_ha', 'N': 'pasangan_na', 'C': 'pasangan_ca', 'R': 'pasangan_ra', 'K': 'pasangan_ka', 'F': 'pasangan_da', 'T': 'pasangan_ta', 'S': 'pasangan_sa', 'W': 'pasangan_wa', 'L': 'pasangan_la', 'P': 'pasangan_pa', 'D': 'pasangan_dha', 'J': 'pasangan_ja', 'Y': 'pasangan_ya', 'V': 'pasangan_nya', 'M': 'pasangan_ma', 'G': 'pasangan_ga', 'B': 'pasangan_ba', 'Q': 'pasangan_tha', 'Z': 'pasangan_nga', 'u': 'sandangan_vokal_suku', 'i': 'sandangan_vokal_wulu', 'e': 'sandangan_vokal_pepet', '[': 'sandangan_vokal_taling', '/': 'sandangan_paten_layar', '=': 'sandangan_paten_cecak', 'h': 'sandangan_paten_wignyan', '\\': 'sandangan_pangkon', ']': 'sandangan_konsonan_cakra_ra', '}': 'sandangan_konsonan_cakra_keret', '-': 'sandangan_konsonan_pengkol', 'o': 'sandangan_vokal_taling_tarung'}

    chars = []
    last_taling = None
    for i, char in enumerate(kalimat):
        if char == "[":
            last_taling = i
        if char == "o" and not last_taling == None:
            chars[last_taling] = ""
        chars.append(char)

    for i in chars:
        key = i
        if i == "{":
            key = "/"
        if i == "_":
            key == "\\"
        if not key == "":
            r += ref[key] + ","

    r = r[:-1]
    
    print(r)
    return r

# ==============================================

def remove_vokal(kata):
    return kata.replace("a", "").replace("e", "").replace("ê", "").replace("i", "").replace("u", "").replace("o", "")

def vokal_sandangan(karakter):
    r = "a"
    if karakter == "sandangan_vokal_suku":
        r = "u"
    elif karakter == "sandangan_vokal_wulu":
        r = "i"
    elif karakter == "sandangan_vokal_pepet":
        r = "ê"
    elif karakter == "sandangan_vokal_taling":
        r = "e"
    elif karakter == "sandangan_vokal_taling_tarung":
        r = "o"
    return r

def paten_sandangan(karakter):
    r = ""
    if karakter == "sandangan_paten_layar":
        r = "r"
    elif karakter == "sandangan_paten_wignyan":
        r = "h"
    elif karakter == "sandangan_paten_cecak":
        r = "ng"
    return r

def konsonan_sandangan(karakter):
    r = ""
    if karakter == "sandangan_konsonan_cakra_ra":
        r = "r"
    elif karakter == "sandangan_konsonan_cakra_keret":
        r = "rê"
    elif karakter == "sandangan_konsonan_pengkol":
        r = "y"
    return r

def check_add_vokal_a(sukukata, is_last = False):
    last_is_vokal = False
    index = 0
    string_builded = ""
    if len(sukukata) == 1: #hanya aksara
        string_builded = sukukata
        if is_last:
            string_builded += "a"
    else:
        for i in sukukata:
            if index == 0:
                last_is_vokal = (i in ["a", "e", "ê", "i", "u", "o"])
                string_builded += i
            else:
                current_is_vokal = (i in ["a", "e", "ê", "i", "u", "o"])
                if (not last_is_vokal) and (not current_is_vokal):
                    string_builded += "a" + i
                else:
                    string_builded += i
                last_is_vokal = current_is_vokal
            index = index+1
    return string_builded

def format_konsonan_dobel(s, asc = True):
    if asc:
        return s.replace("th", "ť").replace("dh", "ď").replace("ny", "ñ").replace("ng", "ń")
    else:
        return s.replace("ť", "th").replace("ď", "dh").replace("ñ", "ny").replace("ń", "ng")

def aksara2latin(aksara):
    latin = ""
    
    list_aksara = list(aksara.split(","))
    index = 0
    for karakter in list_aksara:
        new_karakter = ""
        if karakter.startswith("pasangan_"):
            new_karakter = "sandangan_pangkon,aksara_" + karakter.replace("pasangan_", "")
        elif karakter == "sandangan_konsonan_cakra_ra":
            new_karakter = "sandangan_pangkon,aksara_ra"
        elif karakter == "sandangan_konsonan_cakra_keret":
            new_karakter = "sandangan_pangkon,aksara_ra,sandangan_vokal_pepet"
        elif karakter == "sandangan_konsonan_pengkol":
            new_karakter = "sandangan_pangkon," + "aksara_ya"
        elif karakter == "sandangan_paten_layar":
            new_karakter = "aksara_ra,sandangan_pangkon"
        elif karakter == "sandangan_paten_wignyan":
            new_karakter = "aksara_ha,sandangan_pangkon"
        elif karakter == "sandangan_paten_cecak":
            new_karakter = "aksara_nga,sandangan_pangkon"

        if new_karakter != "":
            list_aksara[index] = new_karakter
        index = index+1

    list_aksara = ','.join([str(elem) for elem in list_aksara])

    list_aksara = list(list_aksara.split(","))
    list_kategori = []
    for karakter in list_aksara:
        if karakter.startswith("aksara_"):
            list_kategori.append("aksara")
        elif karakter.startswith("sandangan_vokal_"):
            list_kategori.append("vokal")
        elif karakter.startswith("sandangan_pangkon"):
            list_kategori.append("pangkon")

    print("list_aksara", list_aksara)
    print("list_kategori", list_kategori)
    
    index = 0
    sukukata = []
    last_index = None
    
    print("start loop")
    for karakter in list_aksara:
        print(last_index)
        if last_index and index <= last_index:
            index = index+1
            continue

        row1 = list_kategori[index]
        row2_exist = False
        row3_exist = False
        row4_exist = False
        if len(list_kategori) >= index+1+1:
            row2_exist = True
        if len(list_kategori) >= index+1+2:
            row3_exist = True
        if len(list_kategori) >= index+1+3:
            row4_exist = True
        try:
            row2 = list_kategori[index+1]
            row3 = list_kategori[index+2]
            row4 = list_kategori[index+3]
        except Exception as e:
            print(e)
            
        if not row2_exist:
            sukukata.append([index, index])
            print(sukukata)
            last_index = index
            #continue
            index = index+1
            continue

        if row1 + row2 == "aksara" + "aksara":

            if row3_exist and row3 == "pangkon":
                sukukata.append([index, index+2])
                last_index = index+2
                #continue
                index = index+1
                continue

            elif row3_exist and row3 == "vokal":
                sukukata.append([index, index])
                last_index = index
                #continue
                index = index+1
                continue

            elif row3_exist and row3 == "aksara":
                sukukata.append([index, index])
                last_index = index
                #continue
                index = index+1
                continue 

            if not row3_exist:
                sukukata.append([index, index])
                last_index = index
                print(last_index)
                #continue
                index = index+1
                continue
        
        if row1 + row2 == "aksara" + "vokal":

            if not row3_exist:
                sukukata.append([index, index+1])
                last_index = index+1
                #continue
                index = index+1
                continue
        
            if row4_exist:

                if row3 == "aksara":

                    if row4 == "pangkon":
                        sukukata.append([index, index+3])
                        last_index = index+3
                        #continue
                        index = index+1
                        continue
                    
                    elif row4 == "vokal":
                        sukukata.append([index, index+1])
                        last_index = index+1
                        #continue
                        index = index+1
                        continue
                
                else: #mustahil
                    sukukata.append([index, index+1])
                    last_index = index+1
                    #continue
                    index = index+1
                    continue

            else:
                sukukata.append([index, index+1])
                last_index = index+1
                #continue
                index = index+1
                continue
        
        else: #mustahil
            sukukata.append([index, index+1])
            last_index = index+1
            #continue
            index = index+1
            continue

        #continue
        print("auto continue")
        index = index+1
        continue
    
    print("sukukata", sukukata)
    
    sukukata = [value for value in sukukata if type(value) != int]
    print("sukukata", sukukata)

    index = 0
    for sk in sukukata:
        print("sk", sk)
        sk_aksara = list_aksara[sk[0]:sk[1]+1]
        print("sk_aksara", sk_aksara)

        sk_builder = ""
        jndex = 0
        for char in sk_aksara:
            new_builder = ""
            if char.startswith("aksara_"):
                new_builder = remove_vokal(char.replace("aksara_", ""))
                try:
                    if sk_aksara[jndex+1].startswith("aksara_"):
                        new_builder += "a"
                except Exception as e:
                    new_builder += "a"
                    print(e)
            if char.startswith("sandangan_vokal_"):
                new_builder = vokal_sandangan(char)
            if char.startswith("sandangan_pangkon"):
                new_builder = ""
            new_builder = format_konsonan_dobel(new_builder)
            print("new_builder :",new_builder)
            sk_builder += new_builder

            jndex+=1

        print("sk_builder =", sk_builder)

        latin += sk_builder

        index = index+1
    
    latin = latin.replace("ď", "dh").replace("ť", "th").replace("ñ", "ny").replace("ń", "ng")

    # input MURNI, output MURNI
    print("LATIN =>", latin)
    print("==========================================")
    return latin