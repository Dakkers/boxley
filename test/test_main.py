import os
import sys
import json
import dropbox
sys.path.append("../boxley")     # damn relative paths
import main as boxley


def write_to_files(paths, contents):
    """
    Given a list of file paths and a list of file contents, each string of
    content is written to the corresponding file (i.e. the file at the same
    index.
    """
    for path, content in zip(paths, contents):
        with open(path, 'w') as FILE:
            FILE.write(content)


def remove_files(files, boxley_dir):
    """
    Given a list of file paths (in this case, actual files on the computer and
    not Boxley file paths), the files are removed if they exist.
    """
    # removes a list of files from ~/.boxley, if they exist.
    for f in files:
        f_path = os.path.join(boxley_dir, f)
        if os.path.isfile(f_path):
            os.remove(f_path)


def pull_helper(id1, id2, content1, content2, new_content1, new_content2, directory, groupname, 
                root, cwd, cwd_without_home, client):
    """
    Helper for the `Pull`, `Pull_Group` and `Pull_All` commands. Creates 2
    example files with `content1` and `content2`, puts them on Dropbox
    manually (using the API), adds the paths to a JSON file, and then replaces
    their content with `new_content1` and `new_content2`.
    """
    file1_path = os.path.join(cwd, "example-files/file_%d.txt" % id1)
    file2_path = os.path.join(cwd, "example-files/file_%d.txt" % id2)
    paths = [file1_path, file2_path]

    # create the files and put them on Dropbox
    write_to_files(paths, [content1, content2])
    with open(file1_path, "rb") as FILE1:
        client.put_file("/Boxley/%s/example-files/file_%d.txt" % (cwd_without_home, id1),
                        FILE1, overwrite=True)
    with open(file2_path, "rb") as FILE2:
        client.put_file("/Boxley/%s/example-files/file_%d.txt" % (cwd_without_home, id2),
                        FILE2, overwrite=True)

    boxley.Add(paths, directory, groupname, root)
    # edit the files
    write_to_files(paths, [new_content1, new_content2])

    return paths


def push_helper_1(id1, id2, content1, content2, directory, groupname, root, cwd):
    """
    One helper for the `Push`, `Push_Group` and `Push_All` commands. Creates
    2 example files and writes `content1` and `content2` to them, and then adds
    them to a JSON file.
    """
    file1_path = os.path.join(cwd, "example-files/file_%d.txt" % id1)
    file2_path = os.path.join(cwd, "example-files/file_%d.txt" % id2)
    paths = [file1_path, file2_path]

    # create the files and add them to a conf file
    write_to_files(paths, [content1, content2])
    boxley.Add(paths, directory, groupname, root)

    return paths


def push_helper_2(conffile_path, boxley_dir, client):
    # pull all files and compare with old version
    with open(os.path.join(boxley_dir, conffile_path)) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    for local_path in paths:
        with open(local_path) as FILE:
            content, metadata = client.get_file_and_metadata(paths[local_path])
            assert FILE.read() == content.read()


def test_Setup_Tests():
    """
    This doesn't actually test anything, I just don't know how to create a
    function to do a setup with pytest.
    """
    exfiles_path = os.path.join(os.getcwd(), "example-files")
    if not os.path.isdir(exfiles_path):
        os.mkdir(exfiles_path)

    assert True


def test_Make_Group_File():
    boxley_dir = os.path.join(os.path.expanduser("~"), ".boxley")
    group_filepath = os.path.join(boxley_dir, "group-test.json")
    boxley._Make_Group_File(group_filepath)
    with open(group_filepath) as TESTFILE:
        content = TESTFILE.read()

    assert content == "{}\n"


def test_Add():
    """
    `Add` is tested by creating a dictionary that should be identical to a json
    file after a file is added to it.

    NOTE: removes all paths from `paths.json`.

    Tests:
        - adding two files to `paths.json`
        - adding two files to `paths.json` in a specific directory "Add-Test-1"
        - adding two files to `paths.json` in a specific directory "Add-Test-2"
            in the Dropbox root
        - adding two files to a group "addtest3" in a specific directory
            "Add-Test-3" in the Dropbox root
    """
    # default Dropbox directory = /Boxley
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")
    cwd = os.getcwd()
    cwd_without_home = cwd.replace(home, "")[1:]  # remove leading /

    path1 = os.path.join(cwd, "example-files/file_1.txt")
    path2 = os.path.join(cwd, "example-files/file_2.txt")
    paths_to_add = [path1, path2]

    # remove paths from `paths.json`
    with open(os.path.join(boxley_dir, "paths.json"), "w") as PATHSCONF:
        PATHSCONF.write("{}\n")

    # should go to /Boxley/.../boxley/test/example-files/file_*.txt
    boxley.Add(paths_to_add, None, None, False)
    with open(os.path.join(boxley_dir, "paths.json")) as PATHS:
        paths = { 
            path1: "/Boxley/%s/example-files/file_1.txt" % cwd_without_home,
            path2: "/Boxley/%s/example-files/file_2.txt" % cwd_without_home
        }
        assert paths == json.loads(PATHS.read())

    # should go to /Boxley/Add-Test-1/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-1", None, False)
    with open(os.path.join(boxley_dir, "paths.json")) as PATHS:
        paths = {path1:"/Boxley/Add-Test-1/example-files/file_1.txt", path2:"/Boxley/Add-Test-1/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())

    # should go to /Boxley/Add-Test-2/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-2", "addtest2", False)
    with open(os.path.join(boxley_dir, "group-addtest2.json")) as PATHS:
        paths = {path1: "/Boxley/Add-Test-2/example-files/file_1.txt", path2: "/Boxley/Add-Test-2/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())

    # should go to /Add-Test-3/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-3", "addtest3", True)
    with open(os.path.join(boxley_dir, "group-addtest3.json")) as PATHS:
        paths = {path1: "/Add-Test-3/example-files/file_1.txt", path2: "/Add-Test-3/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())


def test_Delete():
    """
    `Delete` is tested by adding a file to a json file using `Add` and then
    deleting the file from the json file.

    Tests:
        - deleting two files from `paths.json`
        - deleting two files from a group "deletetest"
    """
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")
    cwd = os.getcwd()

    path1 = os.path.join(cwd, "example-files/file_1.txt")
    path2 = os.path.join(cwd, "example-files/file_2.txt")
    paths = [path1, path2]

    boxley.Add(paths, None, None, False)
    boxley.Add(paths, None, "deletetest", False)

    boxley.Delete(paths, None)
    with open(os.path.join(boxley_dir, "paths.json")) as PATHS:
        assert "{}\n" == PATHS.read()

    boxley.Delete(paths, "deletetest")
    with open(os.path.join(boxley_dir, "group-deletetest.json")) as PATHS:
        assert "{}\n" == PATHS.read()


def test_Make_Group():
    """
    `Make_Group` is tested by checking to see if files exist in ~/.boxley.

    Tests:
        - make multiple groups "groupA", "groupB"
    """
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")

    boxley.Make_Group(["groupA", "groupB"])
    assert os.path.isfile(os.path.join(boxley_dir, "group-groupA.json")) == True
    assert os.path.isfile(os.path.join(boxley_dir, "group-groupB.json")) == True


def test_Pull():
    """
    `Pull` is tested by manually putting a file on Dropbox, using `Add` to add
    the file to a json file, changing the local copy of the file, pulling the
    file from Dropbox, and then verifying that it is identical to what it was
    before the local changes were made.

    Tests:
        - adding two files to `paths.json`
        - adding two files to a group "pulltest"
    """
    home = os.path.expanduser("~")
    boxley_dir, ACCESS_TOKEN = boxley._Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    cwd_without_home = cwd.replace(home, "")[1:]  # remove leading /

    content1, content2 = "hello\nhello\ngoodbye!", "just-some-garbage"
    new_content1, new_content2 = "some random new garbage\n", "POOP: People Order Our Patties\n"
    paths = pull_helper(1, 2, content1, content2, new_content1, new_content2, None, None,
                        False, cwd, cwd_without_home, client)

    boxley.Pull(paths, None, False)

    with open(paths[0]) as FILE1:
        assert content1 == FILE1.read()
    with open(paths[1]) as FILE2:
        assert content2 == FILE2.read()

    # files that are in a group
    content3, content4 = "I'M IN a group!!", "as\n\nam\n\ni\n"
    new_content3, new_content4 = "ugh.\n", "Mr. Robot is awesome.\n" 
    paths = pull_helper(3, 4, content3, content4, new_content3, new_content4, None, "pulltest",
                        False, cwd, cwd_without_home, client)

    boxley.Pull(paths, "pulltest", False)

    with open(paths[0]) as FILE3:
        assert content3 == FILE3.read()
    with open(paths[1]) as FILE4:
        assert content4 == FILE4.read()


def test_Pull_Group():
    """
    `Pull_Group` is tested similarly to `Pull`.

    Tests:
        - pulling a single group "pullgrouptest_A"
        - pulling multiple groups "pullgrouptest_B", "pullgrouptest_C"
    """
    home = os.path.expanduser("~")
    boxley_dir, ACCESS_TOKEN = boxley._Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    cwd_without_home = cwd.replace(home, "")[1:]  # remove leading /

    # files that are not in a group
    content1, content2 = "group1file1", "groupunfiledeux"
    new_content1, new_content2 = "i dunno man\n", "out of ideas\n"
    paths = pull_helper(1, 2, content1, content2, new_content1, new_content2, None,
                        "pullgrouptest_A", False, cwd, cwd_without_home, client)

    boxley.Pull_Group(["pullgrouptest_A"], False)

    with open(paths[0]) as FILE1:
        assert content1 == FILE1.read()
    with open(paths[1]) as FILE2:
        assert content2 == FILE2.read()

    # files that are in a group
    content3, content4 = "groupBfileAAA", "groupBfileBBB"
    content5, content6 = "zippo", "nada!"
    new_content3, new_content4 = "idea: artists\n", "sirensceol\n"
    new_content5, new_content6 = "gibbz\n", "free the skies\n"
    paths1 = pull_helper(3, 4, content3, content4, new_content3, new_content4, None,
                         "pullgrouptest_B", False, cwd, cwd_without_home, client)
    paths2 = pull_helper(5, 6, content5, content6, new_content5, new_content6, None,
                         "pullgrouptest_C", False, cwd, cwd_without_home, client)

    boxley.Pull_Group(["pullgrouptest_B", "pullgrouptest_C"], False)

    with open(paths1[0]) as FILE3:
        assert content3 == FILE3.read()
    with open(paths1[1]) as FILE4:
        assert content4 == FILE4.read()
    with open(paths2[0]) as FILE5:
        assert content5 == FILE5.read()
    with open(paths2[1]) as FILE6:
        assert content6 == FILE6.read()


def test_Pull_All():
    """
    `Pull_All` is tested similarly to `Pull`.

    NOTE: this test removes all files in ~/.boxley except for `boxley.conf` and
    `paths.json`.

    Tests:
        - add two files to `paths.json` and two files to a group "pullalltest"
    """
    home = os.path.expanduser("~")
    boxley_dir, ACCESS_TOKEN = boxley._Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    cwd_without_home = cwd.replace(home, "")[1:]

    content1, content2 = "my groceries\n", "eggs\nbacon\n"
    content3, content4 = "iceberg lettuce\npeppers\n", "chocolate milk\n"
    new_content1, new_content2 = "games I play\n", "saints row 3\ndino d-day\n"
    new_content3, new_content4 = "battleblock theater\n", "freaking meatbags\n\n"

    all_files = os.listdir(boxley_dir)
    all_files.remove("boxley.conf")
    all_files.remove("paths.json")
    for f in all_files:
        os.remove(os.path.join(boxley_dir, f))

    paths1 = pull_helper(1, 2, content1, content2, new_content1, new_content2, None, None, 
                         False, cwd, cwd_without_home, client)
    paths2 = pull_helper(3, 4, content3, content4, new_content3, new_content4, None, "pullalltest", 
                         False, cwd, cwd_without_home, client)

    boxley.Pull_All(False)

    with open(paths1[0]) as FILE1:
        assert content1 == FILE1.read()
    with open(paths1[1]) as FILE2:
        assert content2 == FILE2.read()
    with open(paths2[0]) as FILE3:
        assert content3 == FILE3.read()
    with open(paths2[1]) as FILE4:
        assert content4 == FILE4.read()


def test_Push():
    """
    `Push` is tested by creating a local file, adding it to a json file (via
    `Add`), pushing the file, then manually pulling the file and comparing it.

    NOTE: this test removes all paths in `paths.json`, and removes the file
    `group-pushtest.json` (if it exists).

    Tests:
        - adding two files to `paths.json`
        - adding two files to a group 'pushtest'
    """
    boxley_dir, ACCESS_TOKEN = boxley._Get_Push_Settings()[:2]
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    with open(os.path.join(boxley_dir, "paths.json"), "w") as PATHSCONF:
        PATHSCONF.write("{}\n")
    remove_files(["group-pushtest.json"], boxley_dir)

    # TEST: regular files
    content1, content2 = "I am tired\n", "of being creative.\n"
    local_paths = push_helper_1(1, 2, content1, content2, None, None, False, cwd)
    boxley.Push(local_paths, False, None, True, False)
    push_helper_2("paths.json", boxley_dir, client)

    # TEST: files in a group
    content3, content4 = "Green is not\n", "a creative colour.\n"
    local_paths = push_helper_1(3, 4, content3, content4, None, "pushtest", False, cwd)
    boxley.Push(local_paths, False, "pushtest", True, False)
    push_helper_2("group-pushtest.json", boxley_dir, client)


def test_Push_Group():
    """
    `Push_Group` is tested similarly to `Push`.

    NOTE: removes the files `group-pushgrouptestA.json`,
    `group-pushgrouptestB.json`, `group-pushgrouptestC.json` if they exist.

    Tests:
        - pushing a single group 'pushgrouptestA'
        - pushing multiple groups, 'pushgrouptestB', 'pushgrouptestC'

    Each group has two files in it.
    """
    boxley_dir, ACCESS_TOKEN = boxley._Get_Push_Settings()[:2]
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    remove_files(["group-pushgrouptestA.json", "group-pushgrouptestB.json",
                  "group-pushgrouptestC.json"], boxley_dir)

    # TEST: two files in one group
    content1, content2 = "It's time to think\n", "creatively!\n"
    push_helper_1(1, 2, content1, content2, None, "pushgrouptestA", False, cwd)
    boxley.Push_Group(["pushgrouptestA"], False, True, False)
    push_helper_2("group-pushgrouptestA.json", boxley_dir, client)

    # TEST: two groups with two files each
    content3, content4 = "It's just a\n", "boring old orange!\n"
    content5, content6 = "Maybe to you\n", "but not to me!\n"
    push_helper_1(3, 4, content3, content4, None, "pushgrouptestB", False, cwd)
    push_helper_1(5, 6, content5, content6, None, "pushgrouptestC", False, cwd)
    boxley.Push_Group(["pushgrouptestB", "pushgrouptestC"], False, True, False)
    push_helper_2("group-pushgrouptestB.json", boxley_dir, client)
    push_helper_2("group-pushgrouptestC.json", boxley_dir, client)


def test_Push_All():
    """
    `Push_All` is tested similarly to `Push`.

    NOTE: removes all files from ~/.boxley except for `boxley.conf` and
    `paths.json`. Removes all paths from `paths.json`.

    Tests:
        - putting two files in `paths.json` and groups 'pushalltestA' and
          'pushalltestB'
    """
    boxley_dir, ACCESS_TOKEN = boxley._Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    with open(os.path.join(boxley_dir, "paths.json"), "w") as PATHSCONF:
        PATHSCONF.write("{}\n")

    all_files = os.listdir(boxley_dir)
    all_files.remove("boxley.conf")
    all_files.remove("paths.json")
    for f in all_files:
        os.remove(os.path.join(boxley_dir, f))

    content1, content2 = "I see a\n", "silly face!\n"
    content3, content4 = "I use my hair\n", "to express myself!\n"
    content5, content6 = "I see a hat\n", "I see a cat!\n"
    push_helper_1(1, 2, content1, content2, None, None, False, cwd)
    push_helper_1(3, 4, content3, content4, None, "pushalltestA", False, cwd)
    push_helper_1(5, 6, content5, content6, None, "pushalltestB", False, cwd)

    boxley.Push_All(False, True, False)
    push_helper_2("paths.json", boxley_dir, client)
    push_helper_2("group-pushalltestA.json", boxley_dir, client)
    push_helper_2("group-pushalltestB.json", boxley_dir, client)
