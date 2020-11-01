import sys, tty
from time import perf_counter as clock
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import defaultdict
import termios
import glob

TIMEOUT = 1.00
Profile = Dict[Tuple[int, int], int]

def get_profiles() -> List[Tuple[str, Profile]]:
  res = []
  for filename in glob.glob('profile_*.txt'):
    with open(filename) as file:
      profile: Profile = eval(''.join(file))
      res.append([filename, profile])
  return res

def make_profile() -> Profile:
  @dataclass
  class BioKey:
    key: int
    time: float = field(default_factory=clock)

  print("please typing something. press (escape) to exit")
  old_settings = termios.tcgetattr(sys.stdin)
  tty.setcbreak(sys.stdin)

  keys: List[BioKey] = []
  while True:
    key = ord(sys.stdin.read(1))  # key captures the key-code 
    print(chr(key), end='')
    if key == 27: break
    else: keys.append(BioKey(key))

  termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

  ddict: Dict[Tuple[int, int], List[float]] = defaultdict(list)
  for a, b, in zip(keys, keys[1:]):
    timeuse = b.time - a.time
    if timeuse < TIMEOUT:
      ddict[(a.key, b.key)].append(timeuse)

  medict = { k: sum(v) / len(v) for k, v in ddict.items() }
  return medict

def save_profile(profile: Profile, name = None):
  if name is None: 
    name = input("who are you ? ")
  with open(f"profile_{name}.txt", "w") as file:
    file.write(str(profile))

def compare_profile(lhs: Profile, rhs: Profile):
  diffs = [lhs[key] - rhs[key] for key in set(lhs).intersection(set(rhs))]
  return sum(diff ** 2 for diff in diffs) / len(diffs)

if __name__ == "__main__":
  my_profile = make_profile()
  for name, saved_profile in get_profiles():
    result = compare_profile(saved_profile, my_profile)
    print(name, result)
  save_profile(my_profile)