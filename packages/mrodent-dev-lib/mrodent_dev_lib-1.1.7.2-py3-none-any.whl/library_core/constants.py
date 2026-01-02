import pathlib, sys, os

# get project name
print(f'+++ __file__ |{__file__}|')
cwd_path = pathlib.Path.cwd()
print(f'+++ cwd_path |{cwd_path}|')

"""
2025-12-28 typically found when lib (mrodent-dev-lib) is a pip-installed module:
+++ __file__ |D:\apps\Python\virtual_envs\dev_doc_indexer\lib\site-packages\library_core\constants.py|
+++ cwd_path |D:\My documents\software projects\EclipseWorkspace\doc_indexer|
"""

# path_parts = pathlib.Path(__file__).parts
# PROJECT_NAME = path_parts[-2]
# print(f'>>> PROJECT_NAME |{PROJECT_NAME}| path_parts to file |{path_parts}|') # i.e. "lib" 


# # get type of run

# IS_PRODUCTION = None
# for path_part in path_parts[:-2]:
#   lc_path_part = path_part.lower()
#   if 'operative' in lc_path_part:
#     IS_PRODUCTION = True
#   elif 'workspace' in lc_path_part:
#     IS_PRODUCTION = False
# if IS_PRODUCTION is None:
#   print(f'FATAL. {__file__}. Neither "operative" nor "workspace" found in path parts: {path_parts[:-2]}', file=sys.stderr)
#   sys.exit()


cwd_path_parts = cwd_path.parts
determined_run_type = False
run_type_index = -1
for i, part in enumerate(cwd_path_parts):
  part_lc = part.lower()
  if part_lc == 'operative':
    IS_PRODUCTION = True
    determined_run_type = True
    
    break
  elif 'workspace' in part_lc:
    IS_PRODUCTION = False
    determined_run_type = True
    break
if not determined_run_type:
  print(f'FATAL. {__file__}. Neither "operative" nor "workspace" found in CWD path parts: {cwd_path_parts}', file=sys.stderr)
  sys.exit()

PROJECT_NAME = cwd_path_parts[i + 1]

# print(f'>>> PROJECT_NAME |{PROJECT_NAME}| __file__ {__file__}')


# get PART2 env var value
PART2_NAME = 'PART2'
PART2_VAL = os.environ.get(PART2_NAME)
if PART2_VAL == None:
  print(f'FATAL. Environment variable |{PART2_NAME}| not set', file=sys.stderr)
  sys.exit()
# print(f'>>> env var |{PART2_VAL}|')

# get git OS
lc_os_name = sys.platform.lower()
IS_LINUX = None
if lc_os_name.startswith('lin'):
  IS_LINUX = True
elif lc_os_name.startswith('win'):
  IS_LINUX = False
if IS_LINUX == None:
  print(f'FATAL. Cannot operate in OS {sys.platform}', file=sys.stderr)
  sys.exit()
