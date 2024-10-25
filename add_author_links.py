import sys
import os

this_script, path, name = sys.argv
abs_file_path = os.path.abspath(os.path.join(path, name))

with open(abs_file_path, 'r+') as md_file:
    lines = md_file.readlines()
    authors = [author[author.find('[')+1 : author.find(']')] for author in lines[-2].split(',')]
    md_file.write('\n\n')
    md_file.writelines([f'author:: [[{author}]]\n' for author in authors])
