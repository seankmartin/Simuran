# This document describes some filters which may be useful.

# This example demonstrates getting all the files which are not in a
# child directory starting with nc, final, or data
re_filts = ['.*\\\\(?:(?!nc).)+$',
            '.*\\\\(?:(?!final).)+$', '.*\\\\(?:(?!data).)+$']

# This example demonstrates getting all the files which are in a directory
# starting with t, and not being in a direct child directory starting with
# nc, final, or data
re_filts = ['^t(?:(?!\\\\nc).)+$',
            '^t(?:(?!\\\\final).)+$', '^t(?:(?!\\\\data).)+$']
