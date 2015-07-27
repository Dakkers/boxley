import os
import sys
import json
import dropbox

cmd = sys.argv[1]


def Init():
    SECRETS = open("./secrets.txt")
    app_key = SECRETS.readline().strip()
    app_secret = SECRETS.readline().strip()
    SECRETS.close()

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print "1. Go to: " + authorize_url
    print "2. Click \"Allow\" (you might have to log in first)"
    print "3. Copy the authorization code."
    code = raw_input("Enter the authorization code here: ").strip()

    # This will fail if the user enters an invalid authorization code
    access_token, user_id = flow.finish(code)

    # create ~/.boxley
    home_dir = os.path.expanduser("~")
    boxley_dir = os.path.join(home_dir, ".boxley")
    os.mkdir(boxley_dir)

    # create default config file and syncfiles
    with open(os.path.join(boxley_dir, "boxley.conf"), "w") as CONFIG:
        CONFIG.write("access_token=%s\n" % access_token)
        CONFIG.write("db_path=/Boxley\n")
        CONFIG.write("relative_to_home=true\n")
        CONFIG.write("autopush=false\nautopush_time=---\npush_on_startup=false\n")
        CONFIG.write("autopull=false\nautopull_time=---\npull_on_startup=false\n")

    SYNCFILES = open(os.path.join(boxley_dir, "files.conf"), "w")
    SYNCFILES.close()


def Add():
    """
    Adds specified file(s) and/or folder(s) to `files.conf`. By default, the
    file's Dropbox path will be the user-specified default directory plus the
    home-relative path to the file, e.g.

        ~/Documents/stuff/hi.txt  -->  Dropbox/Boxley/Documents/stuff/hi.txt

    OPTIONS

    -d
        The name of the directory (inside Dropbox/Boxley) to put this file. Can
        be used in conjunction with -root.

    -root
        Adds the file to the root of the Dropbox instead of the default DB
        default directory.
    """

    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    with open(os.path.join(boxley_dir, "boxley.conf")) as CONFIG:
        ACCESS_TOKEN = CONFIG.readline().strip().split("=")[1]
        DEFAULT_DIR  = CONFIG.readline().strip().split("=")[1]
        RELATIVE_TO_HOME = CONFIG.readline().strip().split("=")[1]
        RELATIVE_TO_HOME = True if RELATIVE_TO_HOME == "true" else False

    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    specific_dir = False
    db_path = DEFAULT_DIR       # directory to put the file on Dropbox
    cwd = os.getcwd()

    i, num_args = 2, len(sys.argv)

    syncfiles = {}
    with open(os.path.join(boxley_dir, "files.conf")) as SYNCFILES_CONTENT:
        syncfiles = json.loads(SYNCFILES_CONTENT.read())


    while i < num_args:
        param = sys.argv[i]

        if param == "-root":
            # if this is the last param, file is missing
            if i == num_args - 1:
                raise Exception("\n\No input file.")

            db_path = "/" + db_path.replace(DEFAULT_DIR, "")

        elif param == "-d":
            # if this is the last param, directory and file are both missing
            if i == num_args - 1:
                raise Exception("\n\tMissing specified directory and input file.")

            # if this is the second last param, one of (directory, file) are
            # missing
            if i == num_args - 2:
                raise Exception("\n\tMissing specified directory or input file.")

            specific_dir = True

            # this param is the flag, the next param is the specified directory
            db_path += sys.argv[i+1] + '/'

            # skip the next param
            i += 1

        else:

            file_to_add = sys.argv[i]    # e.g. hello.txt, src/test.c
            filepath, filename = os.path.split(file_to_add)
            local_path = os.path.join(cwd, file_to_add)

            # if the file is to be put in a specific directory, then it does
            # not need to be merged with the current directory.
            if not specific_dir:
                db_path = os.path.join(db_path, local_path[1:])

                # relative to home only makes sense without a specified dir.
                if RELATIVE_TO_HOME:
                    # remove the path to home
                    db_path = db_path.replace(os.path.expanduser("~"), "")

            else:
                db_path = os.path.join(db_path, file_to_add)

            db_path = db_path.replace(os.sep, "/")
            syncfiles[local_path] = db_path

        i += 1

    # append files to `files.conf`
    with open(os.path.join(boxley_dir, "files.conf"), 'w') as SYNCFILES_CONTENT:
        SYNCFILES_CONTENT.write(json.dumps(syncfiles)+'\n')


if cmd == "init":
    Init()
elif cmd == "add":
    Add()
