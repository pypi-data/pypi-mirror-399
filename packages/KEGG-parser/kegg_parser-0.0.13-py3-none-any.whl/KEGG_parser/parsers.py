"""Parsers"""

##### Methods #####
# These functions define how a section of the flat file will be processed
def split_entry(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data.split()[0]

    return current_dict

def enzyme_entry(current_dict, current_entry_name, current_entry_data):
    entry_data_split = current_entry_data.split()
    current_dict[current_entry_name] = entry_data_split[0] + ":" + entry_data_split[1]

    return current_dict


def split_name_by_comma(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data.split(', ')

    return current_dict


def split_name_by_semicolon(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data.split('; ')

    return current_dict


def split_name(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data.split()

    return current_dict


def return_self(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data

    return current_dict


def return_co_name(current_dict, current_entry_name, current_entry_data):
    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = current_entry_data
    else:
        current_dict[current_entry_name] += ' {}'.format(current_entry_data)

    return current_dict


def return_co_reaction_enzyme(current_dict, current_entry_name, current_entry_data):
    if current_entry_name in current_dict:
        current_dict[current_entry_name] += current_entry_data.split()
    else:
        current_dict[current_entry_name] = current_entry_data.split()

    return current_dict


def return_pathway_class(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = [(i[:5], i[6:]) for i in current_entry_data.split('; ')]

    return current_dict


def return_module_class(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data.split('; ')

    return current_dict


def split_equation(current_dict, current_entry_name, current_entry_data):
    equation_split = current_entry_data.split(' <=> ')
    if len(equation_split) != 2:
        raise ValueError("Equation does not have two parts: {}".format(current_entry_data))

    reactants = equation_split[0].strip().split(' + ')
    reactants = [reactant.strip().split()[-1][:6] for reactant in reactants]
    products = equation_split[1].strip().split(' + ')
    products = [product.strip().split()[-1][:6] for product in products]
    current_dict[current_entry_name] = [reactants, products]

    return current_dict


def split_and_append(current_dict, current_entry_name, current_entry_data):
    split_current_entry_data = current_entry_data.split()
    current_entry_pathway_id = split_current_entry_data[0]
    current_entry_pathway_name = ' '.join(split_current_entry_data[1:])

    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = list()

    current_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))

    return current_dict


def split_and_append_organism(current_dict, current_entry_name, current_entry_data):
    split_current_entry_data = current_entry_data.split()
    current_entry_pathway_id = split_current_entry_data[0]
    current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
    current_dict[current_entry_name] = (current_entry_pathway_id, current_entry_pathway_name)

    return current_dict


def append_to_list(current_dict, current_entry_name, current_entry_data):
    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = []

    current_dict[current_entry_name].append(current_entry_data)

    return current_dict


def add_class(current_dict, current_entry_name, current_entry_data):
    if current_entry_name in current_dict:
        current_dict[current_entry_name].append(current_entry_data)
    else:
        current_dict[current_entry_name] = [current_entry_data]

    return current_dict


def add_nested_dict(current_dict, current_entry_name, current_entry_data):
    split_current_entry_data = current_entry_data.split(': ')
    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = {}
    current_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()

    return current_dict


def add_module_orthology(current_dict, current_entry_name, current_entry_data):
    split_current_entry_data = current_entry_data.split(' ')
    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = {}
    orthology_name = [i for i in split_current_entry_data[1:] if i != '']
    current_dict[current_entry_name][split_current_entry_data[0]] = ' '.join(orthology_name)

    return current_dict


def split_module_reaction(current_dict, current_entry_name, current_entry_data):
    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = {}

    reaction_line = current_entry_data.split()
    keys = reaction_line[0].split(',')
    reaction_string = ' '.join(reaction_line[1:])
    try:
        reacts, prods = reaction_string.split(' -> ')
    except ValueError:
        reacts, prods = reaction_string.split(' <-> ')
    prods = prods.split(' + ')
    if len(prods) == 1:
        prods = prods[0].split('+')
    reacts = reacts.split(' + ')
    if len(reacts) == 1:
        reacts = reacts[0].split('+')
    for key in keys:
        current_dict[current_entry_name][key] = (tuple(reacts), tuple(prods))

    return current_dict

def split_multiline_semicolon_list(current_dict, current_entry_name, current_entry_data):
    # remove trailing semicolon and surrounding whitespace
    value = current_entry_data.strip().rstrip(';')

    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = []

    if value:
        current_dict[current_entry_name].append(value)

    return current_dict


###### FILE STRUCTURES #####
# These dictionaries define how the output of the flat files will look 

PARSE_KO_BY_FIELD = {
    'ENTRY': split_entry, 'NAME': split_name_by_comma, 'DEFINITION': return_self,
    'PATHWAY': split_and_append, 'MODULE': split_and_append, 'DISEASE': split_and_append,
    'CLASS': add_class, 'DBLINKS': add_nested_dict, 'GENES': add_nested_dict,
    'REACTION': split_and_append
}

PARSE_RN_BY_FIELD = {
    'ENTRY': split_entry, 'NAME': return_self, 'REMARK': return_self, 'COMMENT': return_self,
    'ENZYME': return_self, 'RPAIR': split_name, 'DEFINITION': split_equation, 'EQUATION': split_equation,
    'RCLASS': split_and_append, 'PATHWAY': split_and_append, 'ORTHOLOGY': split_and_append,
    'MODULE': split_and_append, 'CLASS': add_class, 'DBLINKS': add_nested_dict
}

PARSE_CO_BY_FIELD = {
    'ENTRY': split_entry, 'FORMULA': return_self, 'EXACT_MASS': return_self, 'MOL_WEIGHT': return_self,
    'REMARK': return_self, 'COMMENT': return_self, 'COMPOSITION': return_self, 'MASS': return_self,
    'NAME': return_co_name, 'REACTION': return_co_reaction_enzyme, 'ENZYME': return_co_reaction_enzyme,
    'PATHWAY': split_and_append, 'ORTHOLOGY': split_and_append, 'MODULE': split_and_append,
    'DBLINKS': add_nested_dict
}

PARSE_PATHWAY_BY_FIELD = {
    'ENTRY': split_entry, 'NAME': return_self, 'DESCRIPTION': return_self, 'KO_PATHWAY': return_self,
    'CLASS': return_pathway_class, 'PATHWAY_MAP': split_and_append, 'DISEASE': split_and_append,
    'DRUG': split_and_append, 'COMPOUND': split_and_append, 'REL_PATHWAY': split_and_append,
    'REACTION': split_and_append, 'ORTHOLOGY': split_and_append, 'MODULE': split_and_append,
    'ENZYME': split_and_append, 'DBLINKS': add_nested_dict
}

PARSE_ORGANISM_BY_FIELD = {
    'ENTRY': split_entry, 'NAME': split_name_by_comma, 'DEFINITION': return_self, 'POSITION': return_self,
    'ORTHOLOGY': split_and_append_organism, 'DRUG_TARGET': add_nested_dict, 'MOTIF': add_nested_dict,
    'DBLINKS': add_nested_dict, 'STRUCTURE': add_nested_dict, 'CLASS': add_class, 'PATHWAY': split_and_append,
    'DISEASE': split_and_append
}

PARSE_MODULE_BY_FIELD = {
    'ENTRY': split_entry, 'NAME': return_self, 'DEFINITION': return_self, 'ORTHOLOGY': split_and_append,
    'CLASS': return_module_class, 'PATHWAY': split_and_append, 'REACTION': split_module_reaction,
    'COMPOUND': add_module_orthology, 'COMMENT': return_self, 'DBLINKS': add_nested_dict
}

PARSE_ENZYME_BY_FIELD = { 
    'ENTRY': enzyme_entry, 'NAME': split_multiline_semicolon_list, 'CLASS': split_multiline_semicolon_list, 
    'ALL_REAC': split_multiline_semicolon_list
}

###### EXCLUSIONS #####
# These are sections of the flat file entries that won't be included in the final output 

NOT_CAPTURED_KO_FIELDS = ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL', 'SEQUENCE', 'BRITE', 'SYMBOL',
                          'NETWORK', 'ELEMENT')

NOT_CAPTURED_RN_FIELDS = ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL', 'BRITE')

NOT_CAPTURED_CO_FIELDS = ('BRITE', 'ATOM', 'BOND', 'BRACKET', 'ORIGINAL', 'REPEAT', 'NODE', 'EDGE', 'SEQUENCE',
                          'GENE', 'ORGANISM', 'TYPE', 'EFFICACY', 'PRODUCT', 'CLASS', 'DISEASE', 'TARGET',
                          'METABOLISM', 'INTERACTION', 'STR_MAP', 'REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL',
                          'NETWORK')

NOT_CAPTURED_PATHWAY_FIELDS = ('GENE', 'ORGANISM', 'REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL', 'INCLUDING', 
                               'REL', 'PATHWAY', 'NETWORK', 'KO', 'ELEMENT')

NOT_CAPTURED_ORGANISM_FIELDS = ('AASEQ', 'NTSEQ')

NOT_CAPTURED_MODULE_FIELDS = ('RMODULE', 'BRITE', 'REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL')

NOT_CAPTURED_ENZYME_FIELDS = ('SYSNAME',  'DBLINKS', 'ORTHOLOGY',
    'REACTION', 'SUBSTRATE', 'PRODUCT', 'COMMENT', 'HISTORY', 'REFERENCE', 'AUTHORS', 'TITLE', 
                              'JOURNAL', 'PATHWAY', 'ALL', 'GENES', 'SEQUENCE')


##### PARSERS #####
# Functions for final parsing of the flat files 
# raw records are kegg flat files as text not the file path 
def parse_ko(ko_raw_record):
    ko_dict = {}
    past_entry = None
    for line in ko_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()

        if current_entry_name == '///':
            past_entry = None
            continue

        if current_entry_name == '':
            current_entry_name = past_entry

        current_entry_data = line[12:].strip()

        if current_entry_name != '':
            if current_entry_name in PARSE_KO_BY_FIELD:
                ko_dict = PARSE_KO_BY_FIELD[current_entry_name](ko_dict, current_entry_name, current_entry_data)

            elif current_entry_name not in NOT_CAPTURED_KO_FIELDS and current_entry_name not in PARSE_KO_BY_FIELD:
                raise ValueError('What is {} in {}?'.format(current_entry_name, ko_dict['ENTRY']))

        past_entry = current_entry_name

    return ko_dict


def parse_rn(rn_raw_record):
    rn_dict = {}
    past_entry = None
    for line in rn_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()

        if current_entry_name == '///':
            past_entry = None
            continue

        if current_entry_name == '':
            current_entry_name = past_entry

        current_entry_data = line[12:].strip()

        if current_entry_name != '':
            if current_entry_name in PARSE_RN_BY_FIELD:
                rn_dict = PARSE_RN_BY_FIELD[current_entry_name](rn_dict, current_entry_name, current_entry_data)

            elif current_entry_name not in NOT_CAPTURED_RN_FIELDS and current_entry_name not in PARSE_RN_BY_FIELD:
                raise ValueError('What is {} in {}?'.format(current_entry_name, rn_dict['ENTRY']))

        past_entry = current_entry_name
    return rn_dict


def parse_co(co_raw_record):
    co_dict = {}
    past_entry = None
    for line in co_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()

        if current_entry_name == '///':
            past_entry = None
            continue

        if current_entry_name == '':
            current_entry_name = past_entry

        current_entry_data = line[12:].strip()

        if current_entry_name != '':
            if current_entry_name in PARSE_CO_BY_FIELD:
                co_dict = PARSE_CO_BY_FIELD[current_entry_name](co_dict, current_entry_name, current_entry_data)

            elif current_entry_name not in NOT_CAPTURED_CO_FIELDS and current_entry_name not in PARSE_CO_BY_FIELD:
                raise ValueError('What is {} in {}?'.format(current_entry_name, co_dict['ENTRY']))

        past_entry = current_entry_name

    return co_dict


def parse_pathway(pathway_raw_record):
    pathway_dict = {}
    past_entry = None

    for line in pathway_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()

        if current_entry_name == '///':
            past_entry = None
            continue

        if current_entry_name == '':
            current_entry_name = past_entry

        current_entry_data = line[12:].strip()

        if current_entry_name != '':
            if current_entry_name in PARSE_PATHWAY_BY_FIELD:
                pathway_dict = PARSE_PATHWAY_BY_FIELD[current_entry_name](
                    pathway_dict, current_entry_name, current_entry_data)

            elif current_entry_name != current_entry_name.upper():
                pass

            elif current_entry_name not in NOT_CAPTURED_PATHWAY_FIELDS and \
                    current_entry_name not in PARSE_PATHWAY_BY_FIELD:
                raise ValueError('What is {} in {}?'.format(current_entry_name, pathway_dict['ENTRY']))

        past_entry = current_entry_name
    return pathway_dict


def parse_organism(gene_raw_record):
    gene_dict = {}
    past_entry = None

    for line in gene_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()

        if current_entry_name == '///':
            past_entry = None
            continue

        if current_entry_name == '':
            current_entry_name = past_entry

        current_entry_data = line[12:].strip()

        if current_entry_name != '':
            if current_entry_name in PARSE_ORGANISM_BY_FIELD:
                gene_dict = PARSE_ORGANISM_BY_FIELD[current_entry_name](
                    gene_dict, current_entry_name, current_entry_data)

            elif current_entry_name != current_entry_name.upper():
                pass

            elif current_entry_name not in NOT_CAPTURED_ORGANISM_FIELDS and \
                    current_entry_name not in PARSE_ORGANISM_BY_FIELD:
                raise ValueError('What is {} in {}?'.format(current_entry_name, gene_dict['ENTRY']))

        past_entry = current_entry_name
    return gene_dict


def parse_module(module_raw_record):
    module_dict = {}
    past_entry = None

    for line in module_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()

        if current_entry_name == '///':
            past_entry = None
            continue

        if current_entry_name == '':
            current_entry_name = past_entry

        current_entry_data = line[12:].strip()
        if current_entry_data == '':
            continue

        if current_entry_name != '':
            if current_entry_name in PARSE_MODULE_BY_FIELD:
                module_dict = PARSE_MODULE_BY_FIELD[current_entry_name](
                    module_dict, current_entry_name, current_entry_data)

            elif current_entry_name != current_entry_name.upper():
                pass

            elif current_entry_name not in NOT_CAPTURED_MODULE_FIELDS and \
                    current_entry_name not in PARSE_MODULE_BY_FIELD:
                raise ValueError('What is {} in {}?'.format(current_entry_name, module_dict['ENTRY']))

        past_entry = current_entry_name
    return module_dict


def parse_enzyme(enzyme_raw_record): 
    enzyme_dict = {}
    past_entry = None

    for line in enzyme_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()

        if current_entry_name == '///':
            past_entry = None
            continue

        if current_entry_name == '':
            current_entry_name = past_entry

        current_entry_data = line[12:].strip()

        if current_entry_name != '':
            if current_entry_name in PARSE_ENZYME_BY_FIELD:
                enzyme_dict = PARSE_ENZYME_BY_FIELD[current_entry_name](enzyme_dict, current_entry_name, current_entry_data)

            elif current_entry_name not in NOT_CAPTURED_ENZYME_FIELDS and current_entry_name not in PARSE_ENZYME_BY_FIELD:
                raise ValueError('What is {} in {}?'.format(current_entry_name, enzyme_dict['ENTRY']))

        past_entry = current_entry_name

    return enzyme_dict



