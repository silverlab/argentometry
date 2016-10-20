from fabric.api import *
from fabric.colors import red, green

import os, sys

env.use_ssh_config = True

env.hosts = ['nyx']

upload_dir = '/home/a/ab/abizer/projects/knh/osss/data'

def upload(path):
    if not os.path.exists(path):
        print red("Error: path %s does not exist." % path)
    else:
        response = prompt("Upload %s?" % path, default = 'y')
        if response is 'y':
            with cd(upload_dir):
                if os.path.isdir(path):
                    run('mkdir -p ' + path)

                files = put(local_path = path, remote_path = path)
                print green("Uploaded {0} files from {1}.".format(len(files), path))
        else:
            print red("Cancelling upload.")
