import glob
import sys
from distutils.core import setup
import py2exe
import zipfile
import subprocess
import os

def get_hg_rev(file_path):
    pipe = subprocess.Popen(
        ["hg", "log", "-l", "1", "--template", "{rev}", file_path],
        stdout=subprocess.PIPE
        )
    return pipe.stdout.read()

def getLatestRev():
    files = os.listdir('.')
    files = [file for file in files if file.endswith('.py')]
    latestRev = 0
    for file in files:
        tempRev = int(get_hg_rev(file))
        #print tempRev
        if (tempRev > latestRev):
            latestRev = tempRev
    return latestRev

version = 0.1
build = getLatestRev()

versionStr = str(version) + 'b' + str(build)

data_files=[('.', glob.glob(sys.prefix + '/Lib/site-packages/UnRAR2/UnRARDLL/unrar.dll'))]
options_bundle_none = dict(bundle_files = 3, dist_dir = './dist/kindlemanga_none-' + versionStr)
options_bundle_depends = dict(bundle_files = 2, dist_dir = './dist/kindlemanga_dep-' + versionStr)
options_bundle_python = dict(bundle_files = 1, dist_dir = './dist/kindlemanga-' + versionStr)

myPath = options_bundle_python['dist_dir']

#setup(script_args=['py2exe'], windows=['kindlemanga.py'], data_files=data_files, options = {'py2exe':options_bundle_none})
#setup(script_args=['py2exe'], windows=['kindlemanga.py'], data_files=data_files, options = {'py2exe':options_bundle_depends})
setup(script_args=['py2exe'], windows=['kindlemanga.py'], data_files=data_files, options = {'py2exe':options_bundle_python})

zip = zipfile.ZipFile(myPath + '.zip', 'w', zipfile.ZIP_DEFLATED)

oldPath = os.getcwd()
os.chdir(os.path.split(myPath)[0])
print '---------------------------------------------'
print 'Zipping files...'
for dirpath, dirnames, filenames in os.walk(os.path.split(myPath)[1]):
    for fname in filenames:
        fullname = os.path.join(dirpath, fname)
        print '\t', fullname
        zip.write(fullname)
zip.close()
print 'Done!'
print '---------------------------------------------'
os.chdir(oldPath)