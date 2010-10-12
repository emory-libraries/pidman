# This noid minting logic was originally implemented in the Noid.pm Perl
# module by John Kunze. We began using the original Perl code for generating
# NOIDs, but in re-examining how we used the utility we realzied we didn't
# really use most of its functionality at all. By the time we realized this
# we were calling into the Perl code from within a Postgres database
# underneath this Django application. We decided to remove a few layers of
# dependencies by reimplementing the tiny bit of NOID-generation logic we
# actually used in Python for direct access from Django.

ALPHABET = '0123456789bcdfghjkmnpqrstvwxz'
ALPHASIZE = len(ALPHABET)

def _digits(num):
    '''Represent num in base ALPHASIZE. Return an array of digits, most
    significant first.'''
    if not num:
        return []
    arr = []
    while num:
        digit = num % ALPHASIZE
        num = num // ALPHASIZE
        arr.append(digit)
    arr.reverse()
    return arr

def _checksum(digits):
    '''Custom per-digit checksum algorithm originally implemented in Noid.pm
    and duplicated here for compatibility'''
    sum = 0
    pos = 1
    for digit in digits:
        sum += pos * digit
        pos += 1
    return sum % ALPHASIZE

def encode_noid(num):
    '''Encode an integer as a NOID string, including final checksum
    character.'''
    digits = _digits(num)
    digits.append(_checksum(digits))
    return ''.join([ ALPHABET[digit] for digit in digits ])

def decode_noid(noid):
    '''Decode the integer represented by a NOID string, ignoring the final
    checksum character.'''
    noid = noid[:-1] # strip csum
    pidlen = len(noid)
    power = len(noid) - 1
    num = 0
    for ch in noid:
        num += ALPHABET.index(ch) * (ALPHASIZE ** power)
        power -= 1
    return num
