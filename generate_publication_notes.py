import sys
import os
from pprint import pprint
from lxml import etree, objectify
import requests

thisscript, path, filename = sys.argv
filepath = os.path.abspath(os.path.join(path, filename))

PEOPLE_DIR = '/Users/taylordohmen/Documents/Everything/People/'
PAPER_DIR = '/Users/taylordohmen/Documents/Everything/Papers/'

DBLP_BASE_PID = 'https://dblp.org/pid/'
DBLP_BASE_PUB = 'https://dblp.dagstuhl.de/rec/'
NAME = 'name'
PID = 'pid'
KEY = 'key'
TITLE = 'title'
CONF_PUBS = '*inproceedings'
ARTICLES = '*article'
COAUTHORS = '*co/na'
AUTHOR = 'author'

FORBIDDEN_CHAR_REPLACEMENT = {
    '/': '*slash*',
    '\\': '*hsals*',
    '[': '(',
    ']': ')',
    ':': ' -',
    '^': '*carot*',
    '|': '*pipe*',
    '#': '*hash*'
}

def sanitize(file_name):
    for k, v in FORBIDDEN_CHAR_REPLACEMENT.items():
        file_name = file_name.replace(k, v)
    return file_name

def has_properties(lines):
    return lines and lines[0] == '---\n'

def dblp_exists(lines):
    i = 1
    while lines[i] != '---\n':
        if lines[i].startswith('dblp'):
            return True
        i = i + 1
    return False

def trim_name(name):
    if name[-1].isdigit():
        return name[:-5]
    return name

dblp_url = None
with open(filepath, 'r') as file:
    for line in file.readlines():
        if line.startswith('dblp: '):
            dblp_url = line[6:].strip('\n')

assert dblp_url != None

response = requests.get(f'{dblp_url}.xml')
dblp_person = objectify.fromstring(response.text)

# CREATES md FILE FOR EACH PUBLICATION THAT DOESN'T ALREADY EXIST
existing_pubs = [pub[:-3] for pub in os.listdir(PAPER_DIR)]
publications = dblp_person.findall(CONF_PUBS) + dblp_person.findall(ARTICLES)

for pub in publications:
    title = sanitize(str(pub.title))
    if title not in existing_pubs:
        with open(f'{PAPER_DIR}{title}.md', 'w') as md_file:
            citation = requests.get(f'{DBLP_BASE_PUB}{pub.get(KEY)}.bib').text
            authors = [f'author:: [[{trim_name(str(author))}]]' for author in pub.findall('author')]
            content = f'```bibtex\n{citation}```\n' + '\n'.join(authors)
            md_file.write(content)


# CREATES md FILE FOR EACH COAUTHORS THAT DOESN'T ALREADY EXIST
coauthors = [{NAME: trim_name(str(coauthor)), PID: coauthor.get(PID)} for coauthor in dblp_person.findall(COAUTHORS) if coauthor.get(PID) != None]
existing_people = [person[:-3] for person in os.listdir(PEOPLE_DIR)]

for coauthor in coauthors:
    name, pid = coauthor[NAME], coauthor[PID]
    if name in existing_people:
        with open(f'{PEOPLE_DIR}{name}.md', 'r+') as md_file:
            content = md_file.readlines()
            if content:
                if has_properties(content) and not dblp_exists(content):
                    content = content[:1] + [f'dblp: {DBLP_BASE_PID}{pid}\n'] + content[1:]
                    md_file.seek(0, 0)
                    md_file.writelines(content)
                if not has_properties(content):
                    content = content = ['---\n', f'dblp: {DBLP_BASE_PID}{pid}\n', '---\n'] + content
                    md_file.seek(0, 0)
                    md_file.writelines(content)
            else:
                content = ['---\n', f'dblp: {DBLP_BASE_PID}{pid}\n', '---\n']
                md_file.writelines(content)
    else:
        with open(f'{PEOPLE_DIR}{name}.md', 'w') as md_file:
            md_file.writelines(['---\n', f'dblp: {DBLP_BASE_PID}{pid}\n', '---\n'])
