from os.path import isfile, isdir
import core.communication_excel as exl
import core.constant as const
import core.database as db
import re
import wx


def make_cable_path_dict(cable_path_path: str):  # -> dict
    """
        Goal:
            Obtain two dictionaries, one will be used for the "more complete" code,
            and another will be "simplified".
        Args:
            cable_path_path (str): Recovery (global path) => the path of cable path.
        Return:
            statue (bool): Return statue False if the file not corresponding and True if no anomalies, that all is good.
            cable_path_dict (dict): This dictionary retrieves the parts corresponding to the associated cable,
                these parts having to be in the order of the element "order".
            cable_dict_with_list_associated_rooms (dict): This dictionary takes the first dictionary,
                and simplifies it for easier reading for entering this data into the database.
    """
    cable_path = exl.read(cable_path_path, 1, initial_header=False)
    cable_path_statu = exl.read(cable_path_path, 0, initial_header=False)
    first_row = cable_path[0]  # Take the first row in order to obtain a model.
    # Condition: check here if one element of the global path is missing.
    if const.CABLE not in first_row or const.ORDER not in first_row or const.ELEMENT not in first_row:
        return False, "", ""
    else:
        cable_path_dict = dict()
        cable_dict_with_list_associated_rooms = dict()
        cable_global_routing_state = dict()
        for row in cable_path:  # Global path reading and organisation of this, for code.
            cable = row[const.CABLE]
            order = int(row[const.ORDER])
            room = row[const.ELEMENT]
            if cable not in cable_path_dict:
                cable_path_dict[cable] = {"room": list()}
            cable_path_dict[cable]["room"].append((order, room))
            cable_path_dict[cable]["room"].sort(key=lambda x: x[0])
        # Cable path dictionary reading and simplification of this, for input data in DataBase.
        for cable_code, rooms in cable_path_dict.items():
            if cable_code not in cable_dict_with_list_associated_rooms:
                cable_dict_with_list_associated_rooms[cable_code] = tuple()
            for key, room in rooms.items():
                for t in room:
                    cable_dict_with_list_associated_rooms[cable_code] += (t[1], )

        for row in cable_path_statu:  # récupère deux chose le cable et sons global routing state
            cable_state = row[const.CABLE]
            if cable_state not in cable_global_routing_state:
                cable_global_routing_state[cable_state] = row["GLOBALROUTINGSTATE"]

        return True, cable_path_dict, cable_dict_with_list_associated_rooms, cable_global_routing_state


def make_cable_name_dict(cable_list_path: str, cable_path_dict: dict):  # -> tuple
    """
        Goal:
            Get three new element after reading "cable_list_path",
            and a dictionary of the corresponding cable names between the cable_list and the cable_path_dict.
        Args:
            cable_list_path (str): Recovery (cable list).
            cable_path_dict (dict): Recovery (cable path dictionary).
        Return:
            statue (bool): Return statue False if the file not corresponding and True if no anomalies, that all is good.
            cable_name_dict (dict): Creation cable name dictionary for have list on the cables target for the "Decoupler".
            cable_list (list): Export this data of cable list after reading "cable_list_path".
            upper_header (list): Export this data of cable list after reading "cable_list_path", header clean for me.
            header (list): Export this data of cable list after reading "cable_list_path", header origin of file excel.
    """
    cable_list, upper_header, header = exl.read(cable_list_path, initial_header=True)
    first_row = cable_list[0]  # Take the first row in order to obtain a model.
    if const.CODE not in first_row:  # Condition: check here if the column code of the cable list is missing.
        return False, "", "", "", ""
    else:
        cable_name_dict = dict()
        # The purpose of this loop is to have a dictionary of all the corresponding cables,
        # between the cable list and the cable path dict to form the cable name dict.
        for row in cable_list:
            cable_name = row[const.CODE]
            if cable_name in cable_path_dict:
                cable_name_dict[cable_name] = True
            else:
                cable_name_dict[cable_name] = False
        # todo here : couplage avec glabal path et globalrouting state (Optionel)
        return True, cable_name_dict, cable_list, upper_header, header


''' Make the cable list in dictionary rearrange with the path of the cable list and the global path enter, 
    read the input path of the cable list with the initial header and put it in the corresponding variable 
    then check the cable name and also in the global path '''


def make_room_list(room_list_path: str) -> list:
    """
        Goal:
            Get three new element after reading "cable_list_path",
            and a dictionary of the corresponding cable names between the cable_list and the cable_path_dict.
        Args:
            room_list_path (list): Recovery (room list).
        Return:
            room_list (list): Export of the room list.
    """
    room_list_unformated = exl.read_csv(room_list_path)
    room_list = list()
    for row in room_list_unformated:
        if len(row) == 0:
            continue
        simplified_row = row[0][1:-1]  # remove the first and last character.
        if len(simplified_row) == 11 and simplified_row[-3: -1] == "ZL":  # and latest by "zl":
            room_list.append(simplified_row)
    return room_list


def make_decoupling_pattern_list(decoupling_pattern_path: str):  # -> list
    """
        Goal:
            Reading pattern list, adaptation to the system "Regex" for reorganisation in decoupling pattern list.
        Args:
            decoupling_pattern_path (str): Recovery pattern list for decoupling, using if cable not routed.
        Return:
            decoupling_pattern_list (list): Export the decoupling pattern list adapted to the code reading.
    """
    if decoupling_pattern_path:
        file_data = exl.read(decoupling_pattern_path, initial_header=False)
    else:
        return True, list()
    first_row = file_data[0]
    if const.ROOMORIGINATING not in first_row or const.ROOMTERMINATING not in first_row or \
            const.ELECTRICALTRAIN not in first_row or const.VOLTAGELEVEL not in first_row or \
            const.ROOMORIGINATING_CODE not in first_row or const.ROOMTERMINATING_CODE not in first_row:
        return False, ""
    else:
        # string indices must be integers
        # arranges the values as desired
        decoupling_pattern_list = list()
        for line in file_data:
            line[const.ROOMORIGINATING] = line[const.ROOMORIGINATING].replace("*", ".*").replace("?", ".")
            line[const.ROOMTERMINATING] = line[const.ROOMTERMINATING].replace("*", ".*").replace("?", ".")

            if line[const.ELECTRICALTRAIN] != "*":
                line[const.ELECTRICALTRAIN] = str(int(line[const.ELECTRICALTRAIN]))
            if line[const.VOLTAGELEVEL] != "*":
                line[const.VOLTAGELEVEL] = str(int(line[const.VOLTAGELEVEL]))

            decoupling_pattern_list.append(line)

        return True, decoupling_pattern_list


def is_in_decoupling(room_for_cable: list, room_list: list) -> bool:
    """
        Goal:
        Args:
        Return:
    """
    # Convert the two lists into sets.
    set_room_cable = set(room_for_cable)
    set_room_liste = set(room_list)
    # Get the elements in common.
    intersection_set = set_room_cable.intersection(set_room_liste)  # Set_room_cable & set_room_liste.
    # Know if something in intersection.
    if len(intersection_set) == 0:
        return False
    else:
        return True


def get_first_and_last_room_for_cable(dict_ordered_room: dict, list_room_decopling: list):
    """
        Goal:
        Args:
        Return:
    """
    order_of_project = list()
    for order in dict_ordered_room:
        room = dict_ordered_room[order]
        if room in list_room_decopling:
            order_of_project.append(order)
    if len(order_of_project) == 0:
        return None, None
    # order_de_projet_ordoned = list()
    order_de_projet_ordoned = sorted(order_of_project)
    # dict_ordered_room_ordoned = list()
    ordered_room_key_ordoned = sorted(dict_ordered_room.keys())
    if order_de_projet_ordoned[0] == ordered_room_key_ordoned[0]:
        first = dict_ordered_room[ordered_room_key_ordoned[0]]
    else:
        index = ordered_room_key_ordoned.index(order_de_projet_ordoned[0])
        first = dict_ordered_room[ordered_room_key_ordoned[index - 1]]
    if order_de_projet_ordoned[-1] == ordered_room_key_ordoned[-1]:
        last = dict_ordered_room[ordered_room_key_ordoned[-1]]
    else:
        index = ordered_room_key_ordoned.index(order_de_projet_ordoned[-1])
        last = dict_ordered_room[ordered_room_key_ordoned[index + 1]]
    return first, last


def decoupling_pattern_match(electrical_train: str, voltage_level: str, room_originating: str, room_terminating: str,
                             decoupling_pattern_list: list) -> tuple:
    """
        Goal:
        Args:
        Return:
    """
    # line == donnée de comparaisont
    for line in decoupling_pattern_list:
        electrical_train_valid = bool(electrical_train == line[const.ELECTRICALTRAIN] or "*" ==
                                      line[const.ELECTRICALTRAIN])
        voltage_level_valid = bool(voltage_level == line[const.VOLTAGELEVEL] or "*" == line[const.VOLTAGELEVEL])
        room_originating_valid = bool(re.match(line[const.ROOMORIGINATING], room_originating))
        room_terminating_valid = bool(re.match(line[const.ROOMTERMINATING], room_terminating))

        if electrical_train_valid and voltage_level_valid and room_originating_valid and room_terminating_valid:
            room_originating_final = line[const.ROOMORIGINATING_CODE]
            room_terminating_final = line[const.ROOMTERMINATING_CODE]

            return room_originating_final, room_terminating_final
    return None, None


def make_decoupling(cable_path_dict: dict, room_list: list, cable_list: list, decoupling_pattern_list: list) -> dict:
    """
        Goal:
        Args:
        Return:
    """
    first_last_dict_dec = dict()
    # pour tout les "cable_name" dans "cable_name_dict"
    for cable in cable_list:
        cable_name = cable[const.CODE]
        # verification de l'existance de "cable_name" dans "cable_path_dict"
        if cable_name in cable_path_dict:  # if cable is rooted/have global path
            # verification si "cable_name" est dans "decoupling"
            rooms = cable_path_dict[cable_name]["room"]
            if is_in_decoupling(rooms, room_list):
                ordered_room = cable_path_dict[cable_name]["order"]
                first, last = get_first_and_last_room_for_cable(ordered_room, room_list)
                if first is not None:
                    first_last_dict_dec[cable_name] = {f"{const.FIRST}": first, f"{const.LAST}": last}
        else:
            electrical_train = cable[const.ELECTRICALTRAIN]
            voltage_level = cable[const.VOLTAGELEVEL]
            room_originating = cable[const.ROOMORIGINATING]
            room_terminating = cable[const.ROOMTERMINATING]
            # faire matcher Electrical_train, Voltage_level, Room_originating, Room_terminating parmi l'une des ligne
            # dans Donnée_du_fichier_final
            room_originating_final, room_terminating_final = decoupling_pattern_match(electrical_train, voltage_level,
                                                                                      room_originating,
                                                                                      room_terminating,
                                                                                      decoupling_pattern_list)
            if room_originating_final is not None:
                if room_originating_final == "":
                    room_originating_final = room_originating
                if room_terminating_final == "":
                    room_originating_final = room_terminating
                first_last_dict_dec[cable_name] = {f"{const.FIRST}": room_originating_final,
                                                   f"{const.LAST}": room_terminating_final}
    return first_last_dict_dec


def make_final_list(cable_list: list, decoupling_dict: dict) -> list:
    """
        Goal:
        Args:
        Return:
    """
    final_list = list()
    for row in cable_list:
        decoupleur_status_list = list()
        cable_name = row[const.CODE]
        if cable_name in decoupling_dict:
            first = decoupling_dict[cable_name][const.FIRST]
            last = decoupling_dict[cable_name][const.LAST]
            if first != row[const.FROM_LOCATION]:
                row[const.FROM_LOCATION] = first
                decoupleur_status_list.append(const.FROM_LOCATION)
            if last != row[const.END_LOCATION]:
                row[const.END_LOCATION] = last
                decoupleur_status_list.append(const.END_LOCATION)
            row["Decoupleur_Status"] = decoupleur_status_list
            final_list.append(row)
    return final_list


def main(conf_name: str, cable_list_name: str, cable_list_path: str, cable_path_path: str, room_list_path: str,
         pattern_list_name: str, decoupling_pattern_path: str, folder_path: str, file_name: str,
         progressbar: wx.ProgressDialog):  # -> tuple
    """
        Goal:
        Args:
        Return:
    """
    progressbar.Update(1, "[1/2] Read global path")
    status, cable_path_dict, cable_path_dict_simplified, global_routing_state = make_cable_path_dict(cable_path_path)
    if not status:
        return False, "Error: Invalid format for global path file."
    progressbar.Update(2, "[1/2] Read cable list")
    status, cable_name_dict, cable_list, cable_list_header_simplified, cable_list_header = make_cable_name_dict(
        cable_list_path, cable_path_dict)
    if not status:
        return False, "Error: Invalid format for cable list file."
    progressbar.Update(3, "[1/2] Read room list")
    room_list = make_room_list(room_list_path)
    room_error = list()
    for room in room_list:
        if not room[-3:-1] == "ZL":
            room_error.append(room)
    if room_error:
        return False, f"Error: This value or not valid in room list: \n {room_error}"
    progressbar.Update(4, "[1/2] Read pattern decoupling list")
    status, decoupling_pattern_list = make_decoupling_pattern_list(decoupling_pattern_path)
    if not status:
        return False, "Error: Invalid format for decoupling pattern file."

    print(room_list)

    db.write_into_database(room_list, decoupling_pattern_list, cable_list, cable_path_dict_simplified,
                           global_routing_state, cable_list_name, pattern_list_name, conf_name)

    progressbar.Update(5, "[1/2] Created cable decoupling dict")
    decoupling_cable_dict = make_decoupling(cable_path_dict, room_list, cable_list, decoupling_pattern_list)
    progressbar.Update(6, "[1/2] Created final list")
    final_list = make_final_list(cable_list, decoupling_cable_dict)
    progressbar.Update(7, "[1/2] Creation of file in final path")
    final_path = f"{folder_path}/{file_name}.xlsx"
    progressbar.Update(8, "[1/2] Writing")
    exl.write(final_path, final_list, cable_list_header, cable_list_header_simplified, progressbar)
    return True, ""
    # except Exception as e:
    #        return False, e


# conf_name, cable_list_name, cable_list, global_path, room_list, pattern_list_name,
#                                 decoupling_pattern_list, output_folder, file_name, progress_dialog

def check(conf_name: str, cable_list_name: str, cable_list_path: str, cable_path_path: str, room_list_path: str,
          pattern_list_name: str, decoupling_pattern_path: str, folder_path: str, file_name: str,
          progressbar: wx.ProgressDialog):  # -> tuple
    """
        Goal:
        Args:
        Return:
    """
    missing_file_list = list()
    if conf_name == "":
        missing_file_list.append("Configuration_name")
    if cable_list_name == "":
        missing_file_list.append("Cable_List_name")
    if not isfile(cable_list_path):
        missing_file_list.append("Cable_list")
    if not isfile(cable_path_path):
        missing_file_list.append("Global_path")
    if not isfile(room_list_path):
        missing_file_list.append("Room_list")
    if not isdir(folder_path):
        missing_file_list.append("Folder_path")
    if file_name == "":
        missing_file_list.append("File_name")

    if len(missing_file_list) != 0:
        missing_file_list = ", ".join(missing_file_list)
        return True, f"This file are missing : \n {missing_file_list}"

    status, error = db.try_connection_database()
    if not status:
        return False, f"Erreur lors de la connexion à PostgreSQL, {error}"

    status, error = main(conf_name, cable_list_name, cable_list_path, cable_path_path, room_list_path,
                         pattern_list_name, decoupling_pattern_path, folder_path, file_name, progressbar)
    if status:
        return True, f"{const.STATUS_TRUE}"
    else:
        return False, error


# clp = "C:/Users/G75480/Documents/projet/cable_list_decoupling/data/DedaleCablelist(unit1).xlsx"
# cpp = "C:/Users/G75480/Documents/projet/cable_list_decoupling/data/2020-07-12 - Reference  - Cables Paths.xlsx"
# rlp = "C:/Users/G75480/Documents/projet/cable_list_decoupling/data/HRB.csv"
# dpl = "C:/Users/G75480/Desktop/Taches/projet/cable_list_decoupling/data/HRB-Decoupling_capture.xlsx
# fp = "C:/Users/G75480/Documents/projet/cable_list_decoupling/data"
# fn = "HRB_TOTO"

# a = main(clp, cpp, rlp, dpl, fp, fn)
