import os
import sys
import json
import dropbox
import argparse


def _Get_Access_Token():
    app_key    = raw_input("Enter your app key here: ").strip()
    app_secret = raw_input("Enter your app secret here: ").strip()

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print
    print "1. Go to: " + authorize_url
    print "2. Click \"Allow\" (you might have to log in first)"
    print "3. Copy the authorization code."
    code = raw_input("Enter the authorization code here: ").strip()
    print

    # This will fail if the user enters an invalid authorization code
    access_token, user_id = flow.finish(code)
    return access_token


def _Make_Group_File(groupfile_path):
    """
    Creates a group file at the given path. Is of the form:
        ~/.boxley/group-GROUPNAME.json
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
        local_path_abs = os.path.abspath(local_path)
        if local_path_abs not in paths:
            print "File not found in %s: %s" % (os.path.basename(paths_filename), local_path_abs)
            pull_failed = True
            continue

        db_path = paths[local_path_abs]
        with open(local_path_abs, "wb") as f:
            content, metadata = client.get_file_and_metadata(db_path)
            f.write(content.read())
    
    return pull_failed    


def _Pull_Files_Verbosely(paths_to_pull, paths, paths_filename, client, paths_in_group, groupname=""):
    pull_failed = False

    if paths_in_group:
        print "Uploading files to group \"%s\" ..." % groupname

    for local_path in paths_to_pull:
        local_path_abs = os.path.abspath(local_path)
        if local_path_abs not in paths:
            print "File not found in %s: %s" % (os.path.basename(paths_filename), local_path_abs)
            pull_failed = True
            continue

        db_path = paths[local_path_abs]
        with open(local_path_abs, "wb") as f:
            content, metadata = client.get_file_and_metadata(db_path)
            f.write(content.read())
            if paths_in_group:
                print "\tdownloaded", local_path_abs
            else:
                print "Downloaded", local_path_abs

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
        local_path_abs = os.path.abspath(local_path)
        if local_path_abs not in paths:
            print "File not found in %s: %s" % (os.path.basename(paths_filename), local_path_abs)
            push_failed = True
            continue

        db_path = paths[local_path_abs]
        with open(local_path_abs, "rb") as f:
            client.put_file(db_path, f, overwrite=overwrite)

    return push_failed


def _Push_Files_Verbosely(paths_to_push, paths, paths_filename, client, overwrite, paths_in_group, groupname=""):
    push_failed = False

    if paths_in_group:
        print "Uploading files to group \"%s\" ..." % groupname

    for local_path in paths_to_push:
        local_path_abs = os.path.abspath(local_path)
        if local_path_abs not in paths:
            print "File not found in %s: %s" % (os.path.basename(paths_filename), local_path_abs)
            push_failed = True
            continue

        db_path = paths[local_path_abs]
        with open(local_path_abs, "rb") as f:
            client.put_file(db_path, f, overwrite=overwrite)
            if paths_in_group:
                print "\tuploaded", local_path_abs
            else:
                print "Uploaded", local_path_abs

    return push_failed


def Init():
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    if os.path.isdir(boxley_dir):
        print ("~/.boxley already exists. If you want to reset your access token, run "
               "boxley resettoken and re-enter your app key and secret.\nExiting...")
        return

    print "Creating %s..." % boxley_dir
    os.mkdir(boxley_dir)
 
    access_token = _Get_Access_Token()

    # create default config file and syncfiles
    with open(os.path.join(boxley_dir, "boxley.conf"), "w") as CONFIG:
        CONFIG.write("access_token=%s\n" % access_token)
        CONFIG.write("db_path=/Boxley\n")
        CONFIG.write("relative_to_home=true\n")
        CONFIG.write("overwrite=true\n")
        CONFIG.write("autopush=false\nautopush_time=---\npush_on_startup=false\n")
        CONFIG.write("autopull=false\nautopull_time=---\npull_on_startup=false\n")

    with open(os.path.join(boxley_dir, "paths.json"), "w") as PATHS:
        PATHS.write("{}\n")

    print "Initialized!"


def Reset_Token():
    """
    Resets the user's access token.
    """
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    if not os.path.isdir(boxley_dir):
        print "~/.boxley does not exist. Run boxley init to create it.\nExiting..."
        return

    if not os.path.isfile(os.path.join(boxley_dir, "boxley.conf")):
        print "~/.boxley/boxley.conf does not exist.\nExiting..."

    with open(os.path.join(boxley_dir, "boxley.conf")) as CONFIG:
        settings = CONFIG.readlines()
        access_token_setting = settings[0].split("=")
        access_token_setting[1] = _Get_Access_Token()
        settings[0] = "=".join(access_token_setting) + "\n"

    with open(os.path.join(boxley_dir, "boxley.conf"), "w") as CONFIG:
        CONFIG.write("".join(settings))

    print "Access token reset!"


def Add(paths_to_add, directory, groupname, root):
    """
    Adds specified file(s) and/or folder(s) to `paths.json`. By default, the
    file's Dropbox path will be the user-specified default directory plus the
    home-relative path to the file, e.g.

        ~/Documents/stuff/hi.txt  -->  /Boxley/Documents/stuff/hi.txt

    OPTIONS

    -d
        The name of the directory (inside /Boxley) to put this file. Can be 
        used in conjunction with -root.

    -g
        The groupname of the file(s). All files will be added to the same
        group.

    --root
        Adds the file to the root of the Dropbox instead of the default DB
        default directory.
    """

    home = os.path.expanduser("~")
    cwd  = os.getcwd()
    boxley_dir = os.path.join(home, ".boxley")
    with open(os.path.join(boxley_dir, "boxley.conf")) as CONFIG:
        CONFIG.readline()
        DEFAULT_DIR  = CONFIG.readline().strip().split("=")[1]
        RELATIVE_TO_HOME = CONFIG.readline().strip().split("=")[1]
        RELATIVE_TO_HOME = True if RELATIVE_TO_HOME == "true" else False

    UNIX = True if os.sep == '/' else False
    specific_dir = False

    db_path = DEFAULT_DIR + "/"  # directory to put the file on Dropbox
    new_paths = {}               # paths to add to the JSON file

    if root:
        db_path = "/"

    if directory is not None:
        specific_dir = True
        db_path += directory + "/"

    for local_path in paths_to_add:
        db_path_copy = db_path

        file_to_add = os.path.abspath(local_path)        # remove .. and what not
        filepath, filename = os.path.split(file_to_add)  # e.g. src/test.c --> src, test.c
        local_path = os.path.join(cwd, file_to_add)

        if not specific_dir:
            if UNIX:
                db_path_copy = os.path.join(db_path_copy, local_path[1:])
            else:
                db_path_copy = os.path.join(db_path_copy, local_path[3:])  # ignore C:\

            # relative to home only makes sense without a specified dir.
            if RELATIVE_TO_HOME:
                # remove the path to home
                if UNIX:
                    db_path_copy = db_path_copy.replace(home, "")
                else:
                    db_path_copy = db_path_copy.replace(os.path.abspath(home)[2:], "")  # hacky...

        else:
            db_path_copy = os.path.join(db_path_copy, local_path.replace(cwd+os.sep, "")) # yuck

        db_path_copy = db_path_copy.replace(os.sep, "/")
        new_paths[local_path] = db_path_copy

    # if a group was specified, add the files to the appropriate group file,
    # creating the group file if necessary
    if groupname is not None:
        paths_filename = os.path.join(boxley_dir, "group-%s.json" % groupname)

        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Creating it..." % groupname
            _Make_Group_File(paths_filename)

    else:
        paths_filename = os.path.join(boxley_dir, "paths.json")

    # grab the paths file, iterate over the paths that are given and add them
    with open(paths_filename) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    for local_path in new_paths:
        paths[local_path] = new_paths[local_path]

    with open(paths_filename, "w") as PATHSFILE_CONTENT:
        PATHSFILE_CONTENT.write(json.dumps(paths)+"\n")


def Delete(paths_to_delete, groupname):
    """
    Deletes a path(s) from a JSON file. If the path(s) is in a group, then the
    group name must be specified. Only paths of one group can be removed at a
    time.

    OPTIONS

    -g
        Group name. If the path(s) belongs to a group, then the group name must
        be specified. Only one group name can be specified.
    """
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")

    if groupname is not None:
        paths_filename = os.path.join(boxley_dir, "group-%s.json" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Exiting..." % groupname
            return
    else:
        paths_filename = os.path.join(boxley_dir, "paths.json")

    # grab the paths file, go through the paths specified and delete them; if 
    # the path cannot be found in the file, skip it
    with open(paths_filename) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    for local_path in paths_to_delete:
        absolute_local_path = os.path.abspath(local_path)

        if absolute_local_path not in paths:
            print "\"%s\" does not contain \"%s\"" % (local_path, absolute_local_path)
            continue
        
        del paths[absolute_local_path]

    with open(paths_filename, "w") as PATHSFILE_CONTENT:
        PATHSFILE_CONTENT.write(json.dumps(paths)+"\n")


def List(groupnames, relative_to_home, verbose):
    """
    For each group, the absolute path of every file is printed.

    OPTIONS

    --home
        Prints each file relative to home instead of relative to the root, if
        possible. 

    -v, --verbose
        Prints the corresponding Dropbox path.
    """
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")
    for groupname in groupnames:
        paths_filename = os.path.join(boxley_dir, "group-%s.json" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Skipping..." % groupname
            continue

        print "Files in '%s'" % groupname
        with open(paths_filename) as PATHSFILE:
            paths = json.loads(PATHSFILE.read())
            if len(paths) == 0:
                print "  No files found."
                continue

            if verbose:
                for local_path in paths:
                    db_path = paths[local_path]
                    if relative_to_home:
                        local_path = local_path.replace(home, "~")
                    print "  %s --> %s" % (local_path, db_path)
            else:
                for local_path in paths:
                    if relative_to_home:
                        local_path = local_path.replace(home, "~")
                    print "  %s" % local_path
        print


def Make_Group(groupnames):
    """
    Creates a group, i.e., creates a group JSON file in ~/.boxley. Multiple
    groups can be created at once.
    """
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    for groupname in groupnames:
        groupfile_path = os.path.join(boxley_dir, "group-%s.json" % groupname)

        if os.path.isfile(groupfile_path):
            print "The group \"%s\" already exists and will not be created."
            return

        _Make_Group_File(groupfile_path)


def Pull(paths_to_pull, groupname, verbose):
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

    if groupname is not None:
        paths_filename = os.path.join(boxley_dir, "group-%s.json" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Exiting..." % groupname
            return
        paths_in_group = True
    else:
        paths_filename = os.path.join(boxley_dir, "paths.json")
        paths_in_group = False

    paths = {}
    with open(paths_filename) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    pull_failed = _Pull_Files(paths_to_pull, paths, paths_filename, client, verbose, paths_in_group, groupname)
    if pull_failed:
        print "Some files failed to pull."
    else:
        print "Pulled successfully."


def Pull_Group(groupnames, verbose):
    """
    Pulls all files of the group(s) specified from Dropbox.

    OPTIONS

    -v
        Verbose output; displays a message for every file pulled.
    """

    boxley_dir, ACCESS_TOKEN = _Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    if len(groupnames) == 0:
        print "Group name(s) not specified. Exiting..."
        return

    one_pull_failed = False

    # for each group, get the .json file, get the paths from each, and then
    # push every one
    for groupname in groupnames:

        paths_filename = os.path.join(boxley_dir, "group-%s.json" % groupname)
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


def Pull_All(verbose):
    """
    Pulls all files from Dropbox.

    OPTIONS

    -v
        Verbose output; displays a message for every file pulled.
    """

    boxley_dir, ACCESS_TOKEN = _Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    one_pull_failed = False
    # get all files, remove boxley.conf from the list, then open each one and
    # pull every path in each
    all_files = os.listdir(boxley_dir)
    all_files.remove("boxley.conf")

    for paths_filename in all_files:
        print paths_filename
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


def Push(paths_to_push, duplicate_flag, groupname, overwrite_flag, verbose):
    """
    Pushes given files to Dropbox.

    OPTIONS

    --dup
        Duplicate; if the file being pushed already exists on Dropbox, then
        this file will have a duplicate name. Equivalent to having the
        `paths.json` overwrite setting set to false.

    -g
        Group name; if the file(s) belong to a group, the groupname must be
        given. Only files of one group can be pushed at a time.

    --ov
        Overwrite; if the file being pushed already exists on Dropbox, then
        this file will overwrite the existing version. Equivalent to having the
        `paths.json` overwrite setting set to true.

    -v, --verbose
        Verbose output; displays a message for every file pushed.
    """
    boxley_dir, ACCESS_TOKEN, overwrite = _Get_Push_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    if groupname is not None:
        paths_in_group = True
    else:
        paths_in_group = False

    if overwrite_flag:
        overwrite = True
    elif duplicate_flag:
        overwrite = False

    # if we're pushing files from a group, get the group json file
    if paths_in_group:
        paths_filename = os.path.join(boxley_dir, "group-%s.json" % groupname)
        if not os.path.isfile(paths_filename):
            print "Group \"%s\" does not exist. Exiting..." % groupname
            return
    else:
        paths_filename = os.path.join(boxley_dir, "paths.json")

    paths = {}
    with open(paths_filename) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    push_failed = _Push_Files(paths_to_push, paths, paths_filename, client, overwrite, verbose, paths_in_group, groupname)
    if push_failed:
        print "Some files failed to push."
    else:
        print "Pushed successfully."


def Push_Group(groupnames, duplicate_flag, overwrite_flag, verbose):
    """
    Pushes a group to Dropbox.

    OPTIONS

    --dup
        Duplicate; if the group files being pushed already exists on Dropbox,
        then the all_files will have a duplicate name. Equivalent to having the
        `paths.json` overwrite setting set to false.

    --ov
        Overwrite; if the group being pushed already exists on Dropbox, then
        this file will overwrite the existing version. Equivalent to having the
        `paths.json` overwrite setting set to true.

    -v, --verbose
        Verbose output; displays a message for every file pushed.
    """

    boxley_dir, ACCESS_TOKEN, overwrite = _Get_Push_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    if overwrite_flag:
        overwrite = True
    elif duplicate_flag:
        overwrite = False

    one_push_failed = False
    # for each group, get the .json file, get the paths from each, and then
    # push every one
    for groupname in groupnames:

        paths_filename = os.path.join(boxley_dir, "group-%s.json" % groupname)
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


def Push_All(duplicate_flag, overwrite_flag, verbose):
    """
    Pushes all files to Dropbox.

    OPTIONS

    --dup
        Duplicate; if the file being pushed already exists on Dropbox, then
        this file will have a duplicate name. Equivalent to having the
        `paths.json` overwrite setting set to false.

    --ov
        Overwrite; if the file being pushed already exists on Dropbox, then
        this file will overwrite the existing version. Equivalent to having the
        `paths.json` overwrite setting set to true.

    -v
        Verbose output; displays a message for every file pushed.
    """

    boxley_dir, ACCESS_TOKEN, overwrite = _Get_Push_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)

    if overwrite_flag:
        overwrite = True
    elif duplicate_flag:
        overwrite = False

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


def Remove_Group(groupnames, verbose):
    """
    Removes all specified group files by group name. Skips groups that do not
    exist.

    OPTIONS

    -v, --verbose
        Verbose output; prints a message for each group file to be removed.
    """
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    for groupname in groupnames:
        filename = "group-%s.json" % groupname
        group_filepath = os.path.join(boxley_dir, filename)
        if not os.path.isfile(group_filepath):
            print "Group '%s' does not exist. Skipping..."
            continue

        if verbose:
            print "Removing group '%s'." % groupname
        os.remove(group_filepath)


def main():

    if len(sys.argv) == 1:
        print "No command specified. Exiting..."
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", type=str, help="The command; this should NOT be explicitly set by the user.")
    parser.add_argument("-d", nargs=1, type=str, help="Ignore the Dropbox default directory and put the file in this directory instead.", default=[None])
    parser.add_argument("-g", nargs=1, type=str, help="Group name.", default=[None])

    dup_vs_overwrite = parser.add_mutually_exclusive_group()
    dup_vs_overwrite.add_argument("--dup", action="store_true", help="If the file being pushed already exists on Dropbox, duplicate it instead of overwriting.")
    dup_vs_overwrite.add_argument("--ov",  action="store_true", help="If the file being pushed already exists on Dropbox, overwrite it.")
    parser.add_argument("--home", action="store_true", help="List files relative to home.")
    parser.add_argument("--root", action="store_true", help="Ignore the Dropbox default directory and put the file in the root of Dropbox.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print more messages.")
    
    parser.add_argument("names", nargs='*')

    cmd = sys.argv[1]

    # since argparse can't interweave positional and optional args, this is a simple trick
    # to make the command into an optional arg by prefixing it with the '-c' flag
    args = parser.parse_args(str("-c" + " ".join(sys.argv[1:])).split())

    if cmd == "init":
        Init()
    elif cmd == "add":
        Add(args.names, args.d[0], args.g[0], args.root)
    elif cmd == "del":
        Delete(args.names, args.g[0])
    elif cmd == "ls":
        List(args.names, args.home, args.verbose)
    elif cmd == "mkgroup":
        Make_Group(args.names)
    elif cmd == "pull":
        Pull(args.names, args.g[0], args.verbose)
    elif cmd == "pullgroup":
        Pull_Group(args.names, args.verbose)
    elif cmd == "pullall":
        Pull_All(args.verbose)
    elif cmd == "push":
        Push(args.names, args.dup, args.g[0], args.ov, args.verbose)
    elif cmd == "pushgroup":
        Push_Group(args.names, args.dup, args.ov, args.verbose)
    elif cmd == "pushall":
        Push_All(args.dup, args.ov, args.verbose)
    elif cmd == "rmgroup":
        Remove_Group(args.names, args.verbose)
    elif cmd == "resettoken":
        Reset_Token()
    else:
        print "Invalid command. Exiting..."

if __name__ == '__main__':
    main()