# See https://docs.python.org/2/library/profile.html

import pstats
p = pstats.Stats('profile.out')
# p.strip_dirs().sort_stats(-1).print_stats()

print("Biggest cumulative users")
p.sort_stats('cumulative').print_stats(20)

print("Biggest time users")
p.sort_stats('time').print_stats(20)

# p.sort_stats('time', 'cumulative').print_stats(.5, 'init')
# p.print_callers(.5, 'init')
