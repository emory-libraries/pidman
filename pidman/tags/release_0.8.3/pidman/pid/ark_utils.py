import re

# utility functions for dealing with ARKs

def normalize_ark(part):
    """ Normalize portion of ark (noid or qualifier) according to ARK spec:
        Removing "/" and "." if the last character
        Removing hyphens - they are considered insignificant and should be ignored
    """
    return part.replace('-', '').rstrip('/.')

# characters or character sets allowed within the qualifier portion of an ARK
qualifier_allowed_characters = ['a-z', 'A-Z', '0-9', '=', '#', '*', '+',
    '@', '_', '$', '%', '-', '.', '/']

def valid_qualifier(qual):
    """ Check if a qualifier string is valid according to the allowed characters
        defined in the ARK spec.
    """
    # if any invalid characters are found, the qualifier is not valid
    return not(invalid_qualifier_characters(qual))
        
def invalid_qualifier_characters(qual):
    """ Finds and returns a list of any character strings that are not allowed
        in an ARK qualifier.
    """
    # regexp search for any characters other than those that are allowed
    pattern = re.compile('([^' + ''.join(qualifier_allowed_characters) + ']+)')
    return re.findall(pattern, qual)

