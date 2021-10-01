# http://www.shikadi.net/moddingwiki/King%27s_Bounty_Saved_game_Format
# http://www.shikadi.net/moddingwiki/King%27s_Bounty_Map_Format

import os
import copy
import json
import logging
import build_report
from datetime import datetime
import shutil

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('default')

ARTIFACTS = [
    'Sword of Prowess',
    'Shield of Protection',
    'Crown of Command',
    'Articles of Nobility',
    'Amulet of Augmentation',
    'Ring of Heroism',
    'Book of Necros',
    'Anchor of Admiralty',
]

CONTINENTS = [
    'Continentia',
    'Forestria',
    'Archipelia',
    'Saharia',
]

MOUNT = {
    0: 'Boat',
    4: 'Fly',
    8: 'Horse',
}

CLASS = [
    "Knight",
    "Paladin",
    "Sorceress",
    "Barbarian",
]

VILLIANS = [
    'Murray the Miser',
    'Hack the Rogue',
    'Princess Almola',
    'Baron Johnno Makahl',
    'Dread Pirate Rob',
    'Canegor the Mystic',
    'Sir Moradon the Cruel',
    'Prince Barrowpine',
    'Bargash Eyesore',
    'Rinaldus Drybone',
    'Ragface',
    'Mahk Bellowspeak',
    'Auric Whiteskin',
    'Czar Nikolai the Mad',
    'Magus Deathspell',
    'Urthrax Killspite',
    'Arech Dragonbreath',
]

UNITS = [
    'Peasants',
    'Sprites',
    'Militia',
    'Wolves',
    'Skeletons',
    'Zombie',
    'Gnomes',
    'Orcs',
    'Archers',
    'Elves',
    'Pikemen',
    'Nomads',
    'Dwarves',
    'Ghosts',
    'Knights',
    'Ogres',
    'Barbarians',
    'Trolls',
    'Cavalry',
    'Druids',
    'Archmages',
    'Vampires',
    'Giants',
    'Demons',
    'Dragons',
]

SPELLS = [
    'Clone',
    'Teleport',
    'Fireball',
    'Lightning',
    'Freeze',
    'Resurrect',
    'Turn Undead',
    'Bridge',
    'Time Stop',
    'Find Villain',
    'Castle Gate',
    'Town Gate',
    'Instant Army',
    'Raise Control',
]

CASTLES = [
    ['Azram', 0, 30, 27],
    ['Basefit', 1, 47, 6],
    ['Cancomar', 0, 36, 49],
    ['Duvock', 1, 30, 18],
    ['Endryx', 2, 11, 46],
    ['Faxis', 0, 22, 49],
    ['Goobare', 2, 41, 36],
    ['Hyppus', 2, 43, 27],
    ['Irok', 0, 11, 30],
    ['Jahn', 1, 41, 34],
    ['Lorshe', 2, 52, 57],
    ['Kookamunga', 0, 57, 58],
    ['Mooseweigh', 1, 25, 39],
    ['Nilslag', 0, 22, 24],
    ['Ophiraund', 0, 6, 57],
    ['Portalis', 0, 58, 23],
    ['Quinderwitch', 1, 42, 56],
    ['Rythacon', 0, 54, 6],
    ['Spockana', 3, 17, 39],
    ['Tylitch', 2, 9, 18],
    ['Uzare', 3, 41, 12],
    ['Vutar', 0, 40, 5],
    ['Wankelforte', 0, 40, 41],
    ['Xelox', 2, 45, 6],
    ['Yeneverre', 1, 19, 19],
    ['Zyzzarzaz', 3, 46, 43],
]

TOWNS = [
    ('Riverton', 0, 29, 12),
    ('Underfoot', 1, 58, 4),
    ('Paths End', 0, 38, 50),
    ('Anomaly', 1, 34, 23),
    ('Topshore', 2, 5, 50),
    ('Lakeview', 0, 17, 44),
    ('Simpleton', 2, 13, 60),
    ('Centrapf', 2, 9, 39),
    ('Quilin Point', 0, 14, 27),
    ('Midland', 1, 58, 33),
    ('Xoctan', 0, 51, 28),
    ('Overthere', 2, 57, 57),
    ('Elans Landing', 1, 3, 37),
    ('Kings Haven', 0, 17, 21),
    ('Bayside', 0, 41, 58),
    ('Nyre', 0, 50, 13),
    ('Dark Corner', 1, 58, 60),
    ('Isla Vista', 0, 57, 5),
    ('Grimworld', 3, 9, 60),
    ('Japper', 2, 13, 7),
    ('Vengeance', 3, 7, 3),
    ('Hunterville', 0, 12, 3),
    ('Fjord', 0, 46, 35),
    ('Yakonia', 2, 49, 8),
    ('Woods End', 1, 3, 8),
    ('Zaezoizu', 3, 58, 48),
]


def parse_character_file(file_name, do_update, save_game):
    if os.path.exists(file_name) is False:
        raise FileNotFoundError("File does not exist - %s" % file_name)

    with open(file_name, 'rb') as input_fh:
        data = bytearray(input_fh.read())

    if do_update is True:
        do_updates(data)
        with open(file_name, 'wb') as output_fh:
            output_fh.write(data)

    # for idx in range(0xe4a, 0xe75):
    #     logger.info(data[idx])

    # pattern = [0, 1, 0, 4, 3, 6, 1, 11, 4, 9, 19, 12, 5, 11, 9, 15, 9, 13, 13, 11, 5, 0, 13, 16, 17, 19]
    # pattern = [57, 8]
    # result = search_pattern(data, pattern)
    # logger.info("Pattern=%s\ncount=%d\nMatch=%s", pattern, len(result), result)
    # return
    # data = Path(file_name).read_bytes()

    results = get_patterns(data)
    # log_results(file_name, results)
    data = pretty_print_results(results, True)
    logger.info(data)

    if save_game is True:
        save_game_file(file_name, results)


def save_game_file(file_name, results):
    char_buf = pretty_print_results(results, True)
    base_name = os.path.basename(file_name).split('.')[0]
    new_file_name = base_name + datetime.now().strftime(" %Y-%m-%d %H-%M-%S REM=") + \
        str(results['time']['days left'])
    new_file_path = os.path.join(os.path.dirname(file_name), new_file_name + '.DAT')
    text_file_path = os.path.join(os.path.dirname(file_name), new_file_name + '.txt')
    base_file_path = os.path.join(os.path.dirname(file_name), base_name + '.txt')
    with open(text_file_path, 'w') as text_fh:
        text_fh.write(char_buf)
    with open(base_file_path, 'w') as text_fh:
        text_fh.write(char_buf)

    shutil.copy(file_name, new_file_path)
    logger.info("New Save File '%s'", new_file_name)


def search_pattern(data, pattern):
    found_idx = []

    for idx in range(len(data)):
        match = False
        for match_idx in range(len(pattern)):
            if data[idx + match_idx] != pattern[match_idx]:
                match = False
                break
            match = True

        if match is True:
            found_idx.append(idx)

    return found_idx


def log_results(file_name, results):
    logger.info((json.dumps(results, indent=4, sort_keys=True)))
    output_file_dir = os.path.dirname(file_name)
    output_file_name = os.path.basename(file_name).split('.')[0] + '.json'
    output_path = os.path.join(output_file_dir, output_file_name)
    with open(output_path, 'w') as json_fh:
        json.dump(results, json_fh, indent=4, sort_keys=True)


def pretty_print_results(results, char_info=False):
    d_format1 = "%-30s: %s\n"
    d_format2 = "%-28s: %s\n"
    br_obj = build_report.BuildReport()

    if char_info is True:
        br_obj.add_line("Character\n")
        br_obj.add_line(d_format1 % ('Name', results['character']['name']), indent=1)
        br_obj.add_line(d_format1 % ('Class', results['character']['class']), indent=1)
        br_obj.add_line(d_format1 % ('Rank', results['character']['rank'] + 1), indent=1)
        br_obj.add_line(d_format1 % ('Leadership',
                                    "%d (%d)" % (results['character']['base leadership'],
                                                 results['character']['leadership'])), indent=1)
        br_obj.add_line(d_format1 % ('Commission', results['character']['commission']), indent=1)
        br_obj.add_line(d_format1 % ('Knows Magic', results['character']['knows magic']), indent=1)
        br_obj.add_line(d_format2 % ('spell power', results['character']['spell power']), indent=2)
        br_obj.add_line(d_format2 % ('max spells', results['character']['max spells']), indent=2)
        br_obj.add_table(list_of_dicts=results['character']['spells'], indent=3)
        br_obj.add_line(d_format1 % ('Siege Engine', results['character']['siege weapons']), indent=1)

        br_obj.add_line(d_format1 % ('Gold', results['character']['gold']), indent=1)
        br_obj.add_line("Character\n", indent=1)
        br_obj.add_line(d_format2 % ('Days Left', results['time']['days left']), indent=2)
        br_obj.add_line(d_format2 % ('Steps Left', results['time']['steps left']), indent=2)
        br_obj.add_line(d_format2 % ('Time Stop', results['time']['time stop']), indent=2)
        br_obj.add_line(d_format1 % ('Followers Killed', results['character']['followers killed']), indent=1)
        br_obj.add_line("Army\n", indent=1)
        br_obj.add_table(list_of_lists=results['character']['army'], indent=3)

    for continent in results['map']:
        continent_dict = results['map'][continent]
        br_obj.add_line('\n' + continent + '\n', indent=0)
        br_obj.add_line("Accessible:%d\n" % continent_dict['accessible'], indent=1)
        if 'map chest to next continent' in continent_dict:
            map_data = continent_dict['map chest to next continent'][0]
            br_obj.add_line("Map to next continent:                                 [%3d,%3d]\n" %
                            (map_data[0], map_data[1]), indent=1)

        if results['scepter']['continent'] == continent:
            scepter_data = results['scepter']
            br_obj.add_line("Scepter              :                                 [%3d,%3d]\n" %
                            (scepter_data['x'], scepter_data['y']), indent=1)

        br_obj.add_line("Castles\n", indent=1)
        for castle in continent_dict['castles']:
            castle_dict = continent_dict['castles'][castle]
            br_obj.add_line("%-14s visited=%d owned=%-21s [%3d,%3d]\n" %
                            (castle, castle_dict['visited'], castle_dict['owned_by'], castle_dict['x'],
                             castle_dict['y']), indent=2)

        br_obj.add_line("Towns\n", indent=1)
        for town in continent_dict['towns']:
            town_dict = continent_dict['towns'][town]
            br_obj.add_line("%-14s visited=%d spell=%-21s [%3d,%3d]\n" %
                            (town, town_dict['visited'], town_dict['spell_sold'], town_dict['x'],
                             town_dict['y']), indent=2)

        br_obj.add_line("Dwellings\n", indent=1)
        for unit in continent_dict['dwellings']:
            if unit['x'] == 0 and unit['y'] == 0:
                continue

            br_obj.add_line("%-14s count=%4d                            [%3d,%3d]\n" %
                            (unit['unit'], unit['count'], unit['x'], unit['y']), indent=2)

        map_count = len(continent_dict['artifact'])
        if map_count == 0:
            br_obj.add_line("No unfound Artifacts\n", indent=1)
        else:
            br_obj.add_line("Unfound Artifacts\n", indent=1)
            split = 5
            for map_idx in range(map_count):
                map_dict = continent_dict['artifact'][map_idx]
                br_obj.add_line("[%3d,%3d]" % (map_dict['x'], map_dict['y']), indent=2)
                if (map_idx + 1) % split == 0:
                    br_obj.add_line("\n")
            mod = (map_idx+1) % split
            if mod != 0:
                br_obj.add_line("\n")

        map_count = len(continent_dict['treasure'])
        if map_count == 0:
            br_obj.add_line("No unfound Treasure\n", indent=1)
        else:
            br_obj.add_line("Unfound Treasure\n", indent=1)
            split = 5
            for map_idx in range(map_count):
                map_dict = continent_dict['treasure'][map_idx]
                br_obj.add_line("[%3d,%3d]" % (map_dict['x'], map_dict['y']), indent=2)
                if (map_idx + 1) % split == 0:
                    br_obj.add_line("\n")

            mod = (map_idx + 1) % split
            if mod != 0:
                br_obj.add_line("\n")

        map_count = len(continent_dict['wanderers'])
        if map_count == 0:
            br_obj.add_line("No Wanderers\n", indent=1)
        else:
            br_obj.add_line("Wanderers\n", indent=1)

            split = 5
            for map_idx in range(map_count):
                map_dict = continent_dict['wanderers'][map_idx]
                br_obj.add_line("[%3d,%3d]" % (map_dict['x'], map_dict['y']), indent=2)
                if (map_idx + 1) % split == 0:
                    br_obj.add_line("\n")

            mod = (map_idx + 1) % split
            if mod != 0:
                br_obj.add_line("\n")

    br_obj.add_line("\nSpells\n", indent=0)
    for spell_name in results['spells']:
        br_obj.add_line(spell_name + "\n", indent=1)
        for city in results['spells'][spell_name]:
            br_obj.add_line("%-14s - %-14s                      [%3d,%3d]\n" %
                            (city['continent'], city['town'], city['x'], city['y']), indent=2)

    return br_obj.get_buffer()


def get_patterns(data):
    rules = {
        'name': {
            'start': 0x0,
            'stop': 0xa,
            'type': 'array',
            'size': 1,
        },
        'class': 0xb,
        'rank': 0xc,
        'spell power': 0xd,
        'max spells': 0xe,
        'villians caught': {
            'start': 0xf,
            'stop': 0x1f,
            'type': 'array',
            'size': 1,
        },
        'artifact found': {
            'start': 0x20,
            'stop': 0x27,
            'type': 'array',
            'size': 1,
        },
        'continent available': {
            'start': 0x28,
            'stop': 0x2b,
            'type': 'array',
            'size': 1,
        },
        # 'is orb found': {
        #     'start': 0x2c,
        #     'stop': 0x2f,
        #     'type': 'array',
        #     'size': 1,
        # },
        'number of spells': {
            'start': 0x30,
            'stop': 0x3d,
            'type': 'array',
            'size': 1,
        },
        'knows magic': 0x3e,
        'siege weapons': 0x3f,
        'current contract': 0x40,
        'hero army': {
            'start': 0x41,
            'stop': 0x45,
            'type': 'array',
            'size': 1,
        },
        'delay': 0x46,
        'difficulty': 0x47,
        'sounds': 0x48,
        'walk beep': 0x49,
        'animation': 0x4A,
        'show army size': 0x4b,
        'hero continent': 0x4c,
        'hero x': 0x4d,
        'hero y': 0x4e,
        'last x': 0x4f,
        'last y': 0x50,
        'boat x': 0x51,
        'boat y': 0x52,
        'boat continent': 0x53,  # 0xff == no boat
        'mount mode': 0x54,  # 0x00 boat, 0x04 fly, 0x08 horse
        'cga palette': 0x55,
        'spell sold in town': {
            'start': 0x56,
            'stop': 0x69,
            'type': 'array',
            'size': 1,
        },
        # 'contract cycle': {
        #     'start': 0x70,
        #     'stop': 0x74,
        #     'type': 'array',
        #     'size': 1,
        # },
        'last contract': 0x75,  # starts as 0x04,
        'max contract': 0x76,  # stats as 0x05
        'steps left': 0x77,  # until end of day
        'unknown3': 0x78,
        'castle owned by': {
            'start': 0x79,
            'stop': 0x92,
            'type': 'array',
            'size': 1,
        },
        'castle visited': {
            'start': 0x93,
            'stop': 0xac,
            'type': 'array',
            'size': 1,
        },
        'town visited': {
            'start': 0xad,
            'stop': 0xc6,
            'type': 'array',
            'size': 1,
        },
        'scepter continent': 0xc7,
        'scepter x': 0xc8,
        'scepter y': 0xc9,
        # 'fog of war': {
        #     'start': 0xca,
        #     'stop': 0x8c9,
        #     'type': 'array',
        #     'size': 1,
        # },
        # 'garrison troops': {
        #     'start': 0x8ca,
        #     'stop': 0x94b,
        #     'type': 'array',
        #     'size': 1,
        # },
        # 'foeF coords': {
        #     'start': 0x94c,
        #     'stop': 0x973,
        #     'type': 'continent_coord',
        #     'group_size': 5,
        # },
        'map chests coords': {
            'start': 0x974,
            'stop': 0x979,
            'type': 'continent_coord',
            'group_size': 1,
        },
        # 'orb chests coords': {
        #     'start': 0x97a,
        #     'stop': 0x981,
        #     'type': 'continent_coord',
        #     'group_size': 1,
        # },
        # 'teleporter coords': {
        #     'start': 0x982,
        #     'stop': 0x991,
        #     'type': 'continent_coord',
        #     'group_size': 2,
        # },
        'dwelling coords': {
            'start': 0x992,
            'stop': 0x9e9,
            'type': 'continent_coord',
            'group_size': 11,
        },
        # 'foeH coords': {
        #     'start': 0x9ea,
        #     'stop': 0xb01,
        #     'type': 'continent_coord',
        #     'group_size': 35,
        # },
        # 'foeH troops': {
        #     'start': 0xb02,
        #     'stop': 0xca5,
        #     'type': 'array',
        #     'size': 3,
        # },
        # 'foeH numbers': {
        #     'start': 0xca6,
        #     'stop': 0xe49,
        #     'type': 'array',
        #     'size': 3,
        # },
        'dwelling N troop': {
            'start': 0xe4a,
            'stop': 0xe75,
            'type': 'continent_array',
            'size': 1,
            'group_size': 11,
        },
        'dwelling N population': {
            'start': 0xe76,
            'stop': 0xea1,
            'type': 'continent_array',
            'size': 1,
            'group_size': 11,
        },
        'scepter key': 0xea2,  # XOR
        'base leadership': {
            'start': 0xea3,
            'stop': 0xea4,
            'type': 'val',
        },
        'leadership': {
            'start': 0xea5,
            'stop': 0xea6,
            'type': 'val',
        },
        'commission': {
            'start': 0xea7,
            'stop': 0xea8,
            'type': 'val',
        },
        'followers killed': {
            'start': 0xea9,
            'stop': 0xeaa,
            'type': 'val',
        },
        'hero army numbers': {
            'start': 0xeab,
            'stop': 0xeb4,
            'type': 'array',
            'size': 2,
        },
        # 'garrison numbers': {
        #     'start': 0xeb5,
        #     'stop': 0xfb8,
        #     'type': 'array',
        #     'size': 1,
        # },
        'time stop': {
            'start': 0xfb9,
            'stop': 0xfba,
            'type': 'val',
        },
        'days left': {
            'start': 0xfbb,
            'stop': 0xfbc,
            'type': 'val',
        },
        'gold': {
            'start': 0xfc1,
            'stop': 0xfc4,
            'type': 'val',
        },
    }

    results = {}

    for rule in rules:
        start = None
        stop = None
        rule_type = 'val'
        size = 1
        group_size = 100000000
        if isinstance(rules[rule], dict):
            if 'start' in rules[rule]:
                start = rules[rule]['start']
            if 'stop' in rules[rule]:
                stop = rules[rule]['stop']
            if 'type' in rules[rule]:
                rule_type = rules[rule]['type']
            if 'size' in rules[rule]:
                size = rules[rule]['size']
            if 'group_size' in rules[rule]:
                group_size = rules[rule]['group_size']
        elif isinstance(rules[rule], int):
            start = rules[rule]
        else:
            raise ValueError("Rule '%s' is not a dict or int" % rule)

        if start is None:
            raise ValueError("Rule '%s' does not have a start value" % rule)

        if stop is None:
            val = data[start]
        elif rule_type == 'array':
            val = []
            for sub_start in range(start, stop + 1, size):
                sub_stop = sub_start + size
                val.append(int.from_bytes(data[sub_start:sub_stop], byteorder='little', signed=False))
        elif rule_type == 'continent_array':
            val = {}
            temp_val = []
            for sub_start in range(start, stop + 1, size):
                sub_stop = sub_start + size
                value = int.from_bytes(data[sub_start:sub_stop], byteorder='little', signed=False)
                temp_val.append(value)
            for idx in range(len(CONTINENTS)):
                group_start = idx * group_size
                group_stop = group_start + group_size
                val[CONTINENTS[idx]] = temp_val[group_start:group_stop]

        elif rule_type == 'continent_coord':
            val = {}
            continent = []
            count = 0
            size = 2
            continent_count = 0
            total_bytes = stop + 1 - start
            for sub_start in range(start, stop + 1, size):
                continent.append([data[sub_start], data[sub_start + 1]])
                count += 1
                if count == group_size:
                    count = 0
                    val[CONTINENTS[continent_count]] = copy.deepcopy(continent)
                    continent_count += 1
                    continent.clear()

        else:
            val = int.from_bytes(data[start:stop], byteorder='little', signed=False)

        results[rule] = val

    group_spells(results)
    group_scepter(results)
    group_character(results)
    group_options(results)
    group_positions(results)
    group_contracts(results)
    group_time(results)
    group_map(results)
    group_map_data(data[0xfc5:], results)

    return results


def group_spells(results):
    group = 'spells'
    results[group] = {}
    for spell_name in SPELLS:
        results[group][spell_name] = []

    for idx in range(len(results['spell sold in town'])):
        town_name = TOWNS[idx][0]
        continent = TOWNS[idx][1]
        x = TOWNS[idx][2]
        y = TOWNS[idx][3]
        spell_name = SPELLS[results['spell sold in town'][idx]]
        results[group][spell_name].append({
            'town': town_name,
            'continent': CONTINENTS[continent],
            'x': x,
            'y': y,
        })


def group_scepter(results):
    group = 'scepter'
    results[group] = {}
    for scepter_rule in ['scepter x', 'scepter y', 'scepter continent']:
        new_rule = scepter_rule.split()[1]
        results[group][new_rule] = results[scepter_rule] ^ results['scepter key']
        del results[scepter_rule]

    results[group]['continent'] = CONTINENTS[results[group]['continent']]

    del results['scepter key']


def group_character(results):
    group = 'character'
    results[group] = {'name': '', 'army': [], 'artifacts': {}, 'spells': {}}
    for rule in ['base leadership', 'class', 'commission', 'followers killed', 'gold', 'knows magic', 'leadership',
                 'max spells',  'rank', 'spell power', 'siege weapons']:
        results[group][rule] = results[rule]
        del results[rule]
    results[group]['class'] = CLASS[results[group]['class']]

    for idx in range(len(results['artifact found'])):
        results[group]['artifacts'][ARTIFACTS[idx]] = results['artifact found'][idx]

    for name_char in results['name']:
        if name_char == 0:
            break
        results[group]['name'] = results[group]['name'] + chr(name_char)
    del results['name']
    for idx in range(5):
        if results['hero army'][idx] == 0xff:
            label = 'Empty'
        else:
            label = UNITS[results['hero army'][idx]]
        results[group]['army'].append([label, results['hero army numbers'][idx]])

    for idx in range(len(results['number of spells'])):
        results[group]['spells'][SPELLS[idx]] = results['number of spells'][idx]

    del results['number of spells']
    del results['artifact found']
    del results['hero army']
    del results['hero army numbers']


def group_options(results):
    group = 'options'
    results[group] = {}
    for rule in ['animation', 'cga palette', 'delay', 'difficulty',  'show army size', 'sounds', 'unknown3',
                 'walk beep']:
        results[group][rule] = results[rule]
        del results[rule]


def group_positions(results):
    group = 'position'
    results[group] = {}
    for rule in ['boat continent', 'boat x', 'boat y', 'hero continent', 'hero x', 'hero y', 'last x', 'last y',
                 'mount mode']:
        results[group][rule] = results[rule]
        del results[rule]

    results[group]['mount mode'] = MOUNT[results[group]['mount mode']]


def group_contracts(results):
    group = 'contract'
    results[group] = {}
    for rule in ['current contract', 'last contract',  'max contract']:
        results[group][rule] = results[rule]
        del results[rule]
    results[group]['villians caught'] = {}
    for idx in range(len(VILLIANS)):
        if results['villians caught'][idx] == 0:
            x = -1
            y = -1
            continent = 'unknown'
            castle = 'unknown'

            for castle_idx in range(len(CASTLES)):
                if results['castle owned by'][castle_idx] == idx:
                    castle = CASTLES[castle_idx][0]
                    continent = CONTINENTS[CASTLES[castle_idx][1]]
                    x = CASTLES[castle_idx][2]
                    y = CASTLES[castle_idx][3]
                    break

            caught = 'No'
        else:
            x = 0
            y = 0
            continent = ''
            castle = ''
            caught = 'Yes'

        results[group]['villians caught'][VILLIANS[idx]] = {
            'caught': caught,
            'x': x,
            'y': y,
            'continent': continent,
            'castle': castle,
        }
    del results['villians caught']


def group_time(results):
    group = 'time'
    results[group] = {}
    for rule in ['days left', 'steps left', 'time stop']:
        results[group][rule] = results[rule]
        del results[rule]


def group_map(results):
    group = 'map'
    results[group] = {}
    for continent_idx in range(len(CONTINENTS)):
        continent = CONTINENTS[continent_idx]
        results[group][continent] = {'dwellings': [], 'towns': {}, 'castles': {}}
        if continent in results['map chests coords']:
            results[group][continent]['map chest to next continent'] = results['map chests coords'][continent]
        results[group][continent]['accessible'] = results['continent available'][continent_idx]
        for dwelling_idx in range(len(results['dwelling N troop'][continent])):
            results[group][continent]['dwellings'].append({
                'unit': UNITS[results['dwelling N troop'][continent][dwelling_idx]],
                'count': results['dwelling N population'][continent][dwelling_idx],
                'x': results['dwelling coords'][continent][dwelling_idx][0],
                'y': results['dwelling coords'][continent][dwelling_idx][1],
            })

    for idx in range(len(CASTLES)):
        castle = CASTLES[idx][0]
        continent = CONTINENTS[CASTLES[idx][1]]
        x = CASTLES[idx][2]
        y = CASTLES[idx][3]
        visited = results['castle visited'][idx]
        castle_owned_by = results['castle owned by'][idx]
        villian_id = castle_owned_by & 0x1f
        if castle_owned_by == 0x7f:
            castle_owned_by = 'Nobody'
        elif castle_owned_by == 0xff:
            castle_owned_by = 'You'
        elif villian_id < len(VILLIANS):
            castle_owned_by = VILLIANS[villian_id]
        else:
            logger.info("unknown castle owned by=0x%02x (%d) | villian_id=0x%02x (%d)",
                        castle_owned_by, castle_owned_by, villian_id, villian_id)

        results[group][continent]['castles'][castle] = {
            'visited': visited,
            'owned_by': castle_owned_by,
            'x': x,
            'y': y,
        }

    sold_len = len(results['spell sold in town'])
    for idx in range(len(TOWNS)):
        town = TOWNS[idx][0]
        continent = CONTINENTS[TOWNS[idx][1]]
        x = TOWNS[idx][2]
        y = TOWNS[idx][3]
        visited = results['town visited'][idx]

        if idx < sold_len:
            spell_sold = SPELLS[results['spell sold in town'][idx]]
        else:
            spell_sold = 'unknown' + ' ' + hex(idx)

        results[group][continent]['towns'][town] = {
            'visited': visited,
            'spell_sold': spell_sold,
            'x': x,
            'y': y,
        }

    # del results['spell sold in town']
    del results['castle visited']
    del results['castle owned by']
    del results['town visited']
    del results['continent available']
    del results['map chests coords']
    del results['dwelling N troop']
    del results['dwelling N population']
    del results['dwelling coords']


def do_updates(data):
    # Flight Mode
    data[0x54] = 4
    #
    # Turn off beeps
    data[0x48] = 0
    data[0x49] = 0
    #
    # # Set Location
    # x = 20
    # y = 20
    # data[0x4c] = 1
    # data[0x4d] = x
    # data[0x4e] = y
    # data[0x4f] = x
    # data[0x50] = y

    # Set Timestop
    data[0xfb9] = 0x10
    data[0xfba] = 0x0

    # Set leadership
    data[0xea3] = 0x0
    data[0xea4] = 0xf0
    data[0xea5] = 0x0
    data[0xea6] = 0xf0

    # castle_base = 0x93
    # town_base = 0xad
    # for idx in range(26):
    #     data[castle_base + idx] = 0
    #     data[town_base + idx] = 0

    # Army
    army_id = 24
    base_army_unit = 0x41
    base_army_size = 0xeab
    for idx in range(5):
        if idx == 0:
            data[base_army_unit + idx] = army_id + idx
            data[base_army_size + idx * 2] = 0x00
            data[base_army_size + 1 + idx * 2] = 0x01
        else:
            data[base_army_unit + idx] = 0xff
            data[base_army_size + idx * 2] = 0
            data[base_army_size + 1 + idx * 2] = 0

    # Visited Towns
    base_town = 0xad
    for idx in range(26):
        data[base_town + idx] = 1

    # Add Spells
    data[0x3e] = 1
    data[0xe] = 200
    base_spell_count = 0x30
    for idx in range(14):
        data[base_spell_count + idx] = 50


def group_map_data(map_data, results):
    map_trans = {
        0x00: {'name': "Grass", 'display': False},

        0x01: {'name': 'Desert', 'display': False},
        0x02: {'name': 'Desert', 'display': False},
        0x03: {'name': 'Desert', 'display': False},
        0x04: {'name': 'Desert', 'display': False},
        0x05: {'name': 'Desert', 'display': False},
        0x06: {'name': 'Desert', 'display': False},
        0x07: {'name': 'Desert', 'display': False},

        0x14: {'name': "Coast", 'display': False},
        0x15: {'name': "Coast", 'display': False},
        0x16: {'name': "Coast", 'display': False},
        0x17: {'name': "Coast", 'display': False},
        0x18: {'name': "Coast", 'display': False},
        0x19: {'name': "Coast", 'display': False},
        0x1a: {'name': "Coast", 'display': False},
        0x1b: {'name': "Coast", 'display': False},
        0x1c: {'name': "Coast", 'display': False},
        0x1d: {'name': "Coast", 'display': False},
        0x1e: {'name': "Coast", 'display': False},
        0x1f: {'name': "Coast", 'display': False},

        0x20: {'name': "Sea", 'display': False},

        0x21: {'name': "Forest", 'display': False},
        0x22: {'name': "Forest", 'display': False},
        0x23: {'name': "Forest", 'display': False},
        0x24: {'name': "Forest", 'display': False},
        0x25: {'name': "Forest", 'display': False},
        0x26: {'name': "Forest", 'display': False},
        0x27: {'name': "Forest", 'display': False},
        0x28: {'name': "Forest", 'display': False},
        0x29: {'name': "Forest", 'display': False},
        0x2a: {'name': "Forest", 'display': False},
        0x2b: {'name': "Forest", 'display': False},
        0x2c: {'name': "Forest", 'display': False},
        0x2d: {'name': "Forest", 'display': False},
        0x2e: {'name': "Forest", 'display': False},
        0x2f: {'name': "Forest", 'display': False},

        0x35: {'name': 'Desert', 'display': False},

        0x3a: {'name': "Mountain", 'display': False},
        0x3b: {'name': "Mountain", 'display': False},
        0x3c: {'name': "Mountain", 'display': False},
        0x3d: {'name': "Mountain", 'display': False},
        0x3e: {'name': "Mountain", 'display': False},
        0x3f: {'name': "Mountain", 'display': False},
        0x40: {'name': "Mountain", 'display': False},
        0x41: {'name': "Mountain", 'display': False},
        0x42: {'name': "Mountain", 'display': False},
        0x43: {'name': "Mountain", 'display': False},
        0x44: {'name': "Mountain", 'display': False},
        0x45: {'name': "Mountain", 'display': False},
        0x46: {'name': "Mountain", 'display': False},
        0x47: {'name': "Mountain", 'display': False},

        0x80: {'name': "Magic Barrier", 'display': False},
        0x85: {'name': "Castle Gate", 'display': False},
        0x8a: {'name': "Town", 'display': False},
        0x8b: {'name': "Treasure Chest", 'display': True},
        0x8c: {'name': "Plains Dwelling", 'display': False},
        0x8d: {'name': "Forest Dwelling", 'display': False},
        0x8e: {'name': "Cave Dwelling", 'display': False},
        0x8f: {'name': "Dungeon Dwelling", 'display': False},
        0x90: {'name': "Sign", 'display': False},
        0x91: {'name': "Follower", 'display': True},
        0x92: {'name': "Artifact 1", 'display': True},
        0x93: {'name': "Artifact 2", 'display': True},
    }

    group = 'map'
    for cont_idx in range(0, 4):
        cont_offset = cont_idx * 0x1000
        continent = CONTINENTS[cont_idx]
        results[group][continent]['wanderers'] = []
        results[group][continent]['treasure'] = []
        results[group][continent]['artifact'] = []

        for x in range(0, 63 + 1):
            x_offset = x
            for y in range(0, 63 + 1):
                y_offset = y * 64
                offset = cont_offset + x_offset + y_offset
                value = map_data[offset]
                value_dict = map_trans.get(value, {'name': 'Unknown %02x' % value, 'display': True})
                value_name = value_dict['name']
                value_display = value_dict['display']

                # if value < 0x80:
                #     continue
                #
                # if value_display is True:
                #     logger.info("cont=%-11s x=%2d y=%2d = %02x - %s",
                #                 continent, x, y, map_data[offset], value_name)

                if value == 0x91:
                    results[group][continent]['wanderers'].append({'x': x, 'y': y})
                if value == 0x8b:
                    results[group][continent]['treasure'].append({'x': x, 'y': y})
                if value == 0x92 or value == 0x93:
                    results[group][continent]['artifact'].append({'x': x, 'y': y})


file_name = os.path.join('e:\\', 'data', 'Documents', 'dosbox', 'kingsbounty', 'BIG_SCOR.DAT')
# parse_character_file('ZELDA2.DAT')
parse_character_file(file_name, False, True)
# parse_character_file(os.path.join('e:\\', 'data', 'Documents', 'dosbox', 'kingsbounty', 'ZELDA.DAT'), False)
# parse_character_file(os.path.join('e:\\', 'data', 'Documents', 'dosbox', 'kingsbounty', 'BOB_PAL.DAT'), True)

