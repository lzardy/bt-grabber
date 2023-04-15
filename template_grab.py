import argparse
import os
import requests
import re
import string
import sys

save_dir = '\\templates\\'
specific_file = ''

# setup --help, --dir, and --file args
parser = argparse.ArgumentParser(description='Downloads `.bt` files found on the official 010 website')
parser.add_argument('--dir', '-d', action='store', default=os.getcwd() + save_dir, help='directory to save files to')
parser.add_argument('--file', '-f', action='store', default=specific_file, help='specific file to download')
parser.add_argument('--replace', '-r', action='store_true', default=False, help='replace existing files')
args = parser.parse_args()

save_dir = args.dir + '\\'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

specific_file = args.file

# if specific_file has no extension, add it
if specific_file != '' and specific_file.find('.') == -1:
    specific_file += '.bt'

url = 'https://www.sweetscape.com/010editor/repository/templates/'

response = requests.get(url)

# response fail
if response.status_code != 200:
    print('failed to access ' + url)
    sys.exit()

tmp = re.findall(r'\.\./files/\w*\.bt',response.text)

for i in tmp:
    file_name = i[9:]

    if specific_file != '':
        if file_name.lower().find(specific_file.lower()) == -1:
            continue

    if os.path.isfile(save_dir + file_name) and not args.replace:
        continue

    tmp_name = i[2:]

    if not re.match(r'\w*\.bt',file_name):
        continue

    url = 'https://www.sweetscape.com/010editor/repository' + tmp_name
    response = requests.get(url)

    # response fail
    if response.status_code != 200:
        print('failed to download ' + file_name)
        continue

    text = str(response.text.encode('utf-8'))
    # delete first and last characters
    text = text[2:]
    text = text[:-1]
    # replace return+newline and tab
    text = text.replace('\\r\\n', '\n')
    text = text.replace('\\t', '\t')
    # fix escaped characters and newline
    j = 0
    for i in range(len(text)):
        if j < len(text) - 1:
            if text[j] == '\\' and text[j + 1] == '\\':
                text = text[:j] + text[j + 1:]
                j += 1
                continue
            if text[j] == '\\' and text[j + 1] == '\'':
                text = text[:j] + text[j + 1:]
                j += 1
                continue
            elif text[j] == '\\' and text[j + 1] == 'n':
                text = text[:j] + '\n' + text[j + 2:]
        j += 1

    # check if exists and is same
    if os.path.isfile(save_dir + file_name) and text == open(save_dir + file_name).read():
        continue

    f = open(save_dir + file_name, 'w+')
    f.write(str(text))
    f.close()
    print('downloaded ' + file_name)

print('Done!')
