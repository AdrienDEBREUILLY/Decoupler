from core import constant as const
import psycopg2


def try_connection_database():

    try:
        connection_database = psycopg2.connect(database=f"{const.DATABASE_NAME}",
                                               password=f"{const.PASSWORD}",
                                               user=f"{const.USER}",
                                               host=f"{const.HOST}",
                                               port=f"{const.PORT}")

        cursor = connection_database.cursor()

        # # Afficher la version de PostgreSQL
        # cursor.execute("SELECT version();")
        # version = cursor.fetchone()
        # print("Version : ", version, "\n")

        # fermeture de la connexion à la base de données
        cursor.close()
        connection_database.close()

    except (Exception, psycopg2.DatabaseError) as error:
        return False, error

    return True, ""


def write_into_database(room_list_data, pattern_list_data, cable_list_data, global_path_rooms_data,
                        global_path_statu, cable_list_name, pattern_list_name, conf_name):
    connection_database = psycopg2.connect(database=f"{const.DATABASE_NAME}",
                                           password=f"{const.PASSWORD}",
                                           user=f"{const.USER}",
                                           host=f"{const.HOST}",
                                           port=f"{const.PORT}")
    cursor = connection_database.cursor()

    # Setting auto commit false
    connection_database.autocommit = True

    # insert data into t_id_list_room
    if room_list_data:
        cursor.execute(f'''INSERT INTO "Decoupler".t_id_list_room (room_list) VALUES 
                                                                              ('{"/".join(room_list_data)}')''')

    # insert data into t_Pattern
    pattern_count = int
    for indice_p in pattern_list_data:
        cursor.execute(f"INSERT INTO t_pattern (electrical_train) VALUES ('{pattern_list_data[indice_p][0]}')")
        cursor.execute(f"INSERT INTO t_pattern (voltage_level) VALUES ('{pattern_list_data[indice_p][1]}')")
        cursor.execute(f"INSERT INTO t_pattern (room_origineting) VALUES ('{pattern_list_data[indice_p][2]}')")
        cursor.execute(f"INSERT INTO t_pattern (room_originating_code) VALUES ('{pattern_list_data[indice_p][3]}')")
        cursor.execute(f"INSERT INTO t_pattern (room_terminating_code) VALUES ('{pattern_list_data[indice_p][5]}')")
        cursor.execute(f"INSERT INTO t_pattern (room_terminating) VALUES ('{pattern_list_data[indice_p][4]}')")
        pattern_count = indice_p

    # insert data into t_Pattern_List
    if pattern_list_name:
        cursor.execute(f"INSERT INTO t_pattern_list (name_pattern_list) VALUES ('{pattern_list_name}')")
    if pattern_count:
        cursor.execute(f"INSERT INTO t_pattern_list (pattern_count) VALUES ('{pattern_count}')")

    # insert data into t_Cable
    cable_count = int
    # faire le plus grand entre "cable_list_data" et "global_path_data"
    for indice in global_path_rooms_data:
        if cable_list_data[indice][2] == global_path_rooms_data[indice] == global_path_statu[indice]:
            cursor.execute(f"INSERT INTO t_cable (ecs_code) VALUES ('{cable_list_data[indice][2]}')")
            cursor.execute(f"INSERT INTO t_cable (electrical_train) VALUES ('{cable_list_data[indice][12]}')")
            cursor.execute(f"INSERT INTO t_cable (voltage_level) VALUES ('{cable_list_data[indice][14]}')")
            cursor.execute(f"INSERT INTO t_cable (from_location) VALUES ('{cable_list_data[indice][19]}')")
            cursor.execute(f"INSERT INTO t_cable (from_code) VALUES ('{cable_list_data[indice][17]}')")
            cursor.execute(f"INSERT INTO t_cable (end_code) VALUES ('{cable_list_data[indice][23]}')")
            cursor.execute(f"INSERT INTO t_cable (end_location) VALUES ('{cable_list_data[indice][21]}')")
            # todo here search in read excel recup type statu in routing cable path first sheet
            cursor.execute(f"INSERT INTO t_cable (global_routing_state) VALUES ('{global_path_statu[indice][0]}')")
            cursor.execute(f"INSERT INTO t_cable (global_path) VALUES ('{global_path_rooms_data[indice][0]}')")
        else:
            cursor.execute(f"INSERT INTO t_cable (ecs_code) VALUES ('{cable_list_data[indice][2]}')")
            cursor.execute(f"INSERT INTO t_cable (electrical_train) VALUES ('{cable_list_data[indice][12]}')")
            cursor.execute(f"INSERT INTO t_cable (voltage_level) VALUES ('{cable_list_data[indice][14]}')")
            cursor.execute(f"INSERT INTO t_cable (from_location) VALUES ('{cable_list_data[indice][19]}')")
            cursor.execute(f"INSERT INTO t_cable (from_code) VALUES ('{cable_list_data[indice][17]}')")
            cursor.execute(f"INSERT INTO t_cable (end_code) VALUES ('{cable_list_data[indice][23]}')")
            cursor.execute(f"INSERT INTO t_cable (end_location) VALUES ('{cable_list_data[indice][21]}')")
        cable_count = indice

    # insert data into t_Cable_List
    if cable_list_name:
        cursor.execute(f"INSERT INTO t_cable_list (name_cable_list) VALUES ('{cable_list_name}')")
    if cable_count:
        cursor.execute(f"INSERT INTO t_cable_list (cable_count) VALUES ('{cable_count}')")

    # insert data into t_Configuration
    if conf_name:
        cursor.execute(f"INSERT INTO t_configuration (name_configuration_decoupler) VALUES ('{conf_name}')")

# def close_session():
#     # fermeture de la connexion à la base de données
#     cursor.close()
#     connection_database().close()
#     # print("La connexion PostgreSQL est fermée")