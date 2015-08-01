import os
import sys
import json
import dropbox

cmd = sys.argv[1]


def _Make_Group_File(groupfile_path):
    """
    Creates a group file at the given path. Is of the form:
        ~/.boxley/group-GROUPNAME.conf
    """
    with open(groupfile_path, "w") as GROUPFILE:
        GROUPFILE.write("{}\n")


def _Get_Push_Settings():
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    with open(os.path.join(boxley_dir, "boxley.conf")) as CONFIG:
        ACCESS_TOKEN = CONFIG.readline().strip().split("=")[1]
        CONFIG.readline()
        CONFIG.readline()
        OVERWRITE = CONFIG.readline().strip().split("=")[1]

    if OVERWRITE == "true":
        overwrite = True
    else:
        overwrite = False
    return boxley_dir, ACCESS_TOKEN, overwrite


def _Get_Pull_Settings():
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    with open(os.path.join(boxley_dir, "boxley.conf")) as CONFIG:
        ACCESS_TOKEN = CONFIG.readline().strip().split("=")[1]
    return boxley_dir, ACCESS_TOKEN


def _Pull_Files(paths_to_pull, paths, paths_filename, client, verbose, paths_in_group, groupname=""):
    if verbose:
        pull_failed = _Pull_Files_Verbosely(paths_to_pull, paths, paths_filename, client, paths_in_group, groupname)
    else:
        pull_failed = _Pull_Files_Quietly(paths_to_pull, paths, paths_filename, client)

    return pull_failed


def _Pull_Files_Quietly(paths_to_pull, paths, paths_filename, client):
    """
    Pulls all paths in the list `paths_to_pull`.
    """

    pull_failed = False

    for local_path in paths_to_pull:
        if local_path not in paths:
            print "File not found in %s: %s" % (os.path.basename(paths_filename), local_path)
            pull_failed = True
            continue

        db_path = paths[local_path]
        with open(local_path, "wb") as f:
            content, metadata = client.get_file_and_metadata(db_path)
            f.write(content.read())
    
    return pull_failed    


def _Pull_Files_Verbosely(paths_to_pull, paths, paths_filename, client, paths_in_group, groupname=""):
    pull_failed = False

    if paths_in_group:
        print "Uploading files to group \"%s\" ..." % groupname

    for local_path in paths_to_pull:
        if local_path not in paths:
            print "File not found in %s: %s" % (os.path.basename(paths_filename), local_path)
            pull_failed = True
            continue

        db_path = paths[local_path]
        with open(local_path, "wb") as f:
            content, metadata = client.get_file_and_metadata(db_path)
            f.write(content.read())
            if paths_in_group:
                print "\tdownloaded", local_path
            else:
                print "Downloaded", local_path

    return pull_failed


def _Push_Files(paths_to_pull, paths, paths_filename, client, overwrite, verbose, paths_in_group, groupname=""):
    if verbose:
        push_failed = _Push_Files_Verbosely(paths_to_pull, paths, paths_filename, client, overwrite, paths_in_group, groupname)
    else:
        push_failed = _Push_Files_Quietly(paths_to_pull, paths, paths_filename, client, overwrite)

    return push_failed


def _Push_Files_Quietly(paths_to_push, paths, paths_filename, client, overwrite):
    push_failed = False

    for local_path in paths_to_push:
        if local_path not in paths:
            print "File not found in %s: %s" % (os.path.basename(paths_filename), local_path)
            push_failed = True
            continue

        db_path = paths[local_path]
        with open(local_path, "rb") as f:
            client.put_file(db_path, f, overwrite=overwrite)

    return push_failed


def _Push_Files_Verbosely(paths_to_push, paths, paths_filename, client, overwrite, paths_in_group, groupname=""):
    push_failed = False

    if paths_in_group:
        print "Uploading files to group \"%s\" ..." % groupname

    for local_path in paths_to_push:
        if local_path not in paths:
            print "File not found in %s: %s" % (os.path.basename(paths_filename), local_path)
            push_failed = True
            continue

        db_path = paths[local_path]
        with open(local_path, "rb") as f:
            client.put_file(db_path, f, overwrite=overwrite)
            if paths_in_group:
                print "\tuploaded", local_path
            else:
                print "Uploaded", local_path

    return push_failed


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
        CONFIG.write("overwrite=true\n")
        CONFIG.write("autopush=false\nautopush_time=---\npush_on_startup=false\n")
        CONFIG.write("autopull=false\nautopull_time=---\npull_on_startup=false\n")

    with open(os.path.join(boxley_dir, "paths.conf"), "w") as PATHS:
        PATHS.write("{}\n")


def Add():
    """
    Adds specified file(s) and/or folder(s) to `paths.conf`. By default, the
    file's Dropbox path will be the user-specified default directory plus the
    home-relative path to the file, e.g.

        ~/Documents/stuff/hi.txt  -->  /Boxley/Documents/stuff/hi.txt

    OPTIONS

    -d
        The name of the directory (inside /Boxley) to put this file. Can be 
        used in conjunction with -root.

    -root
        Adds the file to the root of the Dropbox instead of the default DB
        default directory.
    """

    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")
    with open(os.path.join(boxley_dir, "boxley.conf")) as CONFIG:
        ACCESS_TOKEN = CONFIG.readline().strip().split("=")[1]
        DEFAULT_DIR  = CONFIG.readline().strip().split("=")[1]
        RELATIVE_TO_HOME = CONFIG.readline().strip().split("=")[1]
        RELATIVE_TO_HOME = True if RELATIVE_TO_HOME == "true" else False

    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    UNIX = True if os.sep == '/' else False
    add_to_group = False
    specific_dir = False
    db_path = DEFAULT_DIR       # directory to put the file on Dropbox
    cwd = os.getcwd()
    new_paths = {}

    i, num_args = 2, len(sys.argv)

    while i < num_args:
        param = sys.argv[i]

        if param == "-g":
            # if this is the last param, groupname and file are both missing
            if i == num_args - 1:
                raise Exception("\n\tMissing specified directory and input file.")

            # if this is the second last param, one of (groupname, file) are missing
            if i == num_args - 2:
                raise Exception("\n\tMissing groupname or input file.")

            # this param is the flag, next param is groupname
            groupname = sys.argv[i+1]

            add_to_group = True
            i += 1   # skip next param

        elif param == "-root":
            # if this is the last param, file is missing
            if i == num_args - 1:
                raise Exception("\n\No input file.")

            db_path = "/" + db_path.replace(DEFAULT_DIR, "")

        elif param == "-d":
            # if this is the last param, directory and file are both missing
            if i == num_args - 1:
                raise Exception("\n\tMissing specified directory and input file.")

            # if this is the second last param, one of (directory, file) are missing
            if i == num_args - 2:
                raise Exception("\n\tMissing specified directory or input file.")

            # this param is the flag, the next param is the specified directory
            db_path += sys.argv[i+1] + "/"

            specific_dir = True
            i += 1  # skip the next param

        else:

            # db_path will be modified, but if there are multiple files, we
            # don't want it to be -- create a copy of it to modify instead
            db_path_copy = db_path

            file_to_add = sys.argv[i]    # e.g. hello.txt, src/test.c
            if not UNIX:
                # if using Windows, something like the Git Bash command prompt instead of
                # cmd uses / instead of \; this makes all /'s into \'s
                file_to_add = os.path.abspath(file_to_add)

            print db_path_copy

            filepath, filename = os.path.split(file_to_add)  # e.g. src/test.c --> src, test.c
            local_path = os.path.join(cwd, file_to_add)

            # if the file is to be put in a specific directory, then it does
            # not need to be merged with the current directory.
            if not specific_dir:
                if UNIX:
                    db_path_copy = os.path.join(db_path_copy, local_path[1:])
                else:
                    db_path_copy = os.path.join(db_path_copy, local_path[3:])  # ignore C:\

                print db_path_copy

                # relative to home only makes sense without a specified dir.
                if RELATIVE_TO_HOME:
                    # remove the path to home
                    if UNIX:
                        db_path_copy = db_path_copy.replace(home, "")
                    else:
                        db_path_copy = db_path_copy.replace(os.path.abspath(home)[2:], "")  # hacky...

                print db_path_copy

            else:
                db_path_copy = os.path.join(db_path_copy, file_to_add)

            db_path_copy = db_path_copy.replace(os.sep, "/")
            new_paths[local_path] = db_path_copy

        i += 1

    # if a group was specified, add the files to the appropriate group file,
    # creating the group file if necessary
    if add_to_group:
        paths_filename = os.path.join(boxley_dir, "group-%s.conf" % groupname)

        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Creating it..." % groupname
            _Make_Group_File(paths_filename)

    else:
        paths_filename = os.path.join(boxley_dir, "paths.conf")

    # grab the paths file, iterate over the paths that are given and add them
    paths = {}
    with open(paths_filename) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    for local_path in new_paths:
        paths[local_path] = new_paths[local_path]

    with open(paths_filename, "w") as PATHSFILE_CONTENT:
        PATHSFILE_CONTENT.write(json.dumps(paths)+"\n")


def Delete():
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")

    delete_from_group = False
    paths_to_delete = []

    i, num_args = 2, len(sys.argv)
    while i < num_args:
        param = sys.argv[i]

        if param == "-g":
            if i == num_args - 1:
                raise Exception("\n\tMissing specified directory and input file.")

            if i == num_args - 2:
                raise Exception("\n\tMissing groupname or input file.")

            if delete_from_group:
                raise Exception("\n\tOnly one group can be specified.")

            groupname = sys.argv[i+1]
            delete_from_group = True
            i += 1

        else:
            paths_to_delete.append(param)

        i += 1

    if delete_from_group:
        paths_filename = os.path.join(boxley_dir, "group-%s.conf" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Exiting..." % groupname
            return
    else:
        paths_filename = os.path.join(boxley_dir, "paths.conf")

    # grab the paths file, go through the paths specified and delete them; if 
    # the path cannot be found in the file, skip it
    with open(paths_filename) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    for local_path in paths_to_delete:
        absolute_local_path = os.path.abspath(local_path)

        if absolute_local_path not in paths:
            print "\"%s\" does not contain \"%s\"" % (file_path, absolute_local_path)
            continue
        
        del paths[absolute_local_path]

    with open(paths_filename, "w") as PATHSFILE_CONTENT:
        PATHSFILE_CONTENT.write(json.dumps(paths)+"\n")


def Make_Group():
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    groupname = sys.argv[2]
    groupfile_path = os.path.join(boxley_dir, "group-%s.conf" % groupname)

    if os.path.isfile(groupfile_path):
        print "The group \"%s\" already exists and will not be created."
        return

    _Make_Group_File(groupfile_path)


def Pull():
    """
    Pulls files from Dropbox.

    OPTIONS

    -g
        Group name; if the files being pulled belong to a group, the groupname
        must be specified. Only files of one group can be pulled at a time.

    -v
        Verbose; prints a message for every file pulled.
    """
    
    boxley_dir, ACCESS_TOKEN = _Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    verbose = False
    paths_in_group = False
    groupname = ""
    paths_to_pull = []

    i, N = 2, len(sys.argv)
    while i < N:
        param = sys.argv[i]

        if param == "-g":
            if paths_in_group:
                raise Exception("Only one group can be specified.")
            paths_in_group = True
            groupname = sys.argv[i+1]
            i += 1
        
        elif param == "-v":
            verbose = True

        else:
            paths_to_pull.append(os.path.abspath(sys.argv[i]))
            
        i += 1

    if paths_in_group:
        paths_filename = os.path.join(boxley_dir, "group-%s.conf" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Exiting..." % groupname
            return
    else:
        paths_filename = os.path.join(boxley_dir, "paths.conf")

    paths = {}
    with open(paths_filename) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    pull_failed = _Pull_Files(paths_to_pull, paths, paths_filename, client, verbose, paths_in_group, groupname)
    if pull_failed:
        print "Some files failed to pull."
    else:
        print "Pulled successfully."


def Pull_Group():
    """
    Pulls all files of the group(s) specified from Dropbox.

    OPTIONS

    -v
        Verbose output; displays a message for every file pulled.
    """

    boxley_dir, ACCESS_TOKEN = _Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    verbose = False
    groupnames = []

    i, N = 2, len(sys.argv)
    while i < N:
        param = sys.argv[i]

        if param == "-v":
            verbose = True

        else:
            groupnames.append(param)
            
        i += 1

    if len(groupnames) == 0:
        print "Group name(s) not specified. Exiting..."
        return

    one_pull_failed = False

    # for each group, get the .conf file, get the paths from each, and then
    # push every one
    for groupname in groupnames:

        paths_filename = os.path.join(boxley_dir, "group-%s.conf" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Skipping..." % groupname
            continue

        paths = {}
        with open(paths_filename) as PATHSFILE_CONTENT:
            paths = json.loads(PATHSFILE_CONTENT.read())

        with open(os.path.join(boxley_dir, paths_filename)) as PATHSFILE_CONTENT:
            paths = json.loads(PATHSFILE_CONTENT.read())
            pull_failed = _Pull_Files(paths.keys(), paths, paths_filename, client, verbose, True, groupname)
            if pull_failed:
                one_pull_failed = True

    if one_pull_failed:
        print "Some files failed to be pulled."
    else:
        print "Pulled successfully."


def Pull_All():
    """
    Pulls all files from Dropbox.

    OPTIONS

    -v
        Verbose output; displays a message for every file pulled.
    """

    boxley_dir, ACCESS_TOKEN = _Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    verbose = False
    groupnames = []

    i, N = 2, len(sys.argv)
    while i < N:
        param = sys.argv[i]

        if param == "-v":
            verbose = True

        else:
            raise Exception("\n\tInvalid option. Available options are: -v")
            
        i += 1

    one_pull_failed = False
    # get all files, remove boxley.conf from the list, then open each one and
    # pull every path in each
    all_files = os.listdir(boxley_dir)
    all_files.remove("boxley.conf")
    for paths_filename in all_files:
        is_group = False
        groupname = ""

        with open(os.path.join(boxley_dir, paths_filename)) as PATHSFILE_CONTENT:
            paths = json.loads(PATHSFILE_CONTENT.read())
            if "group" in paths_filename:
                groupname = paths_filename[6:-5]
                is_group = True

            pull_failed = _Pull_Files(paths.keys(), paths, paths_filename, client, verbose, is_group, groupname)
            if pull_failed:
                one_pull_failed = True

    if one_pull_failed:
        print "Some files failed to be pulled."
    else:
        print "All files pulled successfully."


def Push():
    """
    Pushes given files to Dropbox.

    OPTIONS

    -d
        Duplicate; if the file being pushed already exists on Dropbox, then
        this file will have a duplicate name. Equivalent to having the
        `paths.conf` overwrite setting set to false. If both -d and -o flags
        are entered, the one entered last will take priority, regardless of
        the `paths.conf` setting.

    -g
        Group name; if the file(s) belong to a group, the groupname must be
        given. Only files of one group can be pushed at a time.

    -o
        Overwrite; if the file being pushed already exists on Dropbox, then
        this file will overwrite the existing version. Equivalent to having the
        `paths.conf` overwrite setting set to true. If both -d and -o flags are
        entered, the one entered last will take priority, regardless of the 
        `paths.conf` setting.

    -v
        Verbose output; displays a message for every file pushed.
    """

    boxley_dir, ACCESS_TOKEN, overwrite = _Get_Push_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    paths_to_push = []
    verbose = False
    paths_in_group = False
    groupname = ""

    i, N = 2, len(sys.argv)
    while i < N:
        param = sys.argv[i]

        if param == "-d":
            overwrite = False

        elif param == "-g":
            if paths_in_group:
                raise Exception("Only one group can be specified.")
            paths_in_group = True
            groupname = sys.argv[i+1]
            i += 1

        elif param == "-o":
            overwrite = True
        
        elif param == "-v":
            verbose = True

        else:
            paths_to_push.append(os.path.abspath(sys.argv[i]))
            
        i += 1

    # if we're pushing files from a group, get the group conf file
    if paths_in_group:
        paths_filename = os.path.join(boxley_dir, "group-%s.conf" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Exiting..." % groupname
            return
    else:
        paths_filename = os.path.join(boxley_dir, "paths.conf")

    paths = {}
    with open(paths_filename) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    push_failed = _Push_Files(paths_to_push, paths, paths_filename, client, overwrite, verbose, paths_in_group, groupname)
    if push_failed:
        print "Some files failed to push."
    else:
        print "Pushed successfully."


def Push_Group():
    """
    Pushes a group to Dropbox.

    OPTIONS

    -d
        Duplicate; if the group files being pushed already exists on Dropbox,
        then the all_files will have a duplicate name. Equivalent to having the
        `paths.conf` overwrite setting set to false. If both -d and -o flags
        are entered, the one entered last will take priority, regardless of
        the `paths.conf` setting.

    -o
        Overwrite; if the group being pushed already exists on Dropbox, then
        this file will overwrite the existing version. Equivalent to having the
        `paths.conf` overwrite setting set to true. If both -d and -o flags are
        entered, the one entered last will take priority, regardless of the 
        `paths.conf` setting.

    -v
        Verbose output; displays a message for every file pushed.
    """

    boxley_dir, ACCESS_TOKEN, overwrite = _Get_Push_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    groupnames = []
    verbose = False

    i, N = 2, len(sys.argv)
    while i < N:
        param = sys.argv[i]

        if param == "-d":
            overwrite = False

        elif param == "-o":
            overwrite = True
        
        elif param == "-v":
            verbose = True

        else:
            groupnames.append(param)
            
        i += 1

    if len(groupnames) == 0:
        print "Group name(s) not specified. Exiting..."
        return

    one_push_failed = False
    # for each group, get the .conf file, get the paths from each, and then
    # push every one
    for groupname in groupnames:

        paths_filename = os.path.join(boxley_dir, "group-%s.conf" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Skipping..." % groupname
            continue

        paths = {}
        with open(paths_filename) as PATHSFILE_CONTENT:
            paths = json.loads(PATHSFILE_CONTENT.read())

        push_failed = False
        with open(os.path.join(boxley_dir, paths_filename)) as PATHSFILE_CONTENT:
            paths = json.loads(PATHSFILE_CONTENT.read())
            push_failed = _Push_Files(paths.keys(), paths, paths_filename, client, overwrite, verbose, True, groupname)
            if push_failed:
                one_push_failed = True

    if one_push_failed:
        print "Some files failed to push."
    else:
        print "Pushed successfully."


def Push_All():
    """
    Pushes all files to Dropbox.

    OPTIONS

    -d
        Duplicate; if the file being pushed already exists on Dropbox, then
        this file will have a duplicate name. Equivalent to having the
        `paths.conf` overwrite setting set to false. If both -d and -o flags
        are entered, the one entered last will take priority, regardless of
        the `paths.conf` setting.

    -o
        Overwrite; if the file being pushed already exists on Dropbox, then
        this file will overwrite the existing version. Equivalent to having the
        `paths.conf` overwrite setting set to true. If both -d and -o flags are
        entered, the one entered last will take priority, regardless of the 
        `paths.conf` setting.

    -v
        Verbose output; displays a message for every file pushed.
    """

    if len(sys.argv) > 5:
        raise Exception("\n\tToo many options.")

    boxley_dir, ACCESS_TOKEN, overwrite = _Get_Push_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    verbose = False

    i, N = 2, len(sys.argv)
    while i < N:
        param = sys.argv[i]

        if param == "-v":
            verbose = True

        elif param == "-d":
            overwrite = False

        elif param == "-o":
            overwrite = True

        else:
            raise Exception("\n\tInvalid option. Available options are: -d, -o, -v")

        i += 1

    one_push_failed = False
    # get all files, remove boxley.conf from the list, then open each one and
    # push every path in each
    all_files = os.listdir(boxley_dir)
    all_files.remove("boxley.conf")
    for paths_filename in all_files:
        is_group = False
        groupname = ""

        with open(os.path.join(boxley_dir, paths_filename)) as PATHSFILE_CONTENT:
            paths = json.loads(PATHSFILE_CONTENT.read())
            if "group" in paths_filename:
                groupname = paths_filename[6:-5]
                is_group = True

            push_failed = _Push_Files(paths.keys(), paths, paths_filename, client, overwrite, verbose, is_group, groupname)
            if push_failed:
                one_push_failed = True

    if one_push_failed:
        print "Some files failed to push."
    else:
        print "All files pushed successfully."


if cmd == "init":
    Init()
elif cmd == "add":
    Add()
elif cmd == "del":
    Delete()
elif cmd == "mkgroup":
    Make_Group()
elif cmd == "pull":
    Pull()
elif cmd == "pullgroup":
    Pull_Group()
elif cmd == "pullall":
    Pull_All()
elif cmd == "push":
    Push()
elif cmd == "pushgroup":
    Push_Group()
elif cmd == "pushall":
    Push_All()
