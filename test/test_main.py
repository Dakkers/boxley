import os
import sys
import json
import dropbox
sys.path.append("../boxley")     # damn relative paths
import main as boxley


def file_writer(paths, file1_content, file2_content):
    # edit the files
    with open(paths[0], 'w') as FILE1:
        FILE1.write(file1_content)
    with open(paths[1], 'w') as FILE2:
        FILE2.write(file2_content)


def pull_helper(id1, id2, content1, content2, new_content1, new_content2, directory, groupname, 
                root, cwd, cwd_without_home, client):
    # files that are not in a group
    file1_path = os.path.join(cwd, "example-files/file_%d.txt" % id1)
    file2_path = os.path.join(cwd, "example-files/file_%d.txt" % id2)
    paths = [file1_path, file2_path]

    # create the files and put them on Dropbox
    file_writer(paths, content1, content2)
    with open(file1_path, "rb") as FILE1:
        client.put_file("/Boxley/%s/example-files/file_%d.txt" % (cwd_without_home, id1),
                        FILE1, overwrite=True)
    with open(file2_path, "rb") as FILE2:
        client.put_file("/Boxley/%s/example-files/file_%d.txt" % (cwd_without_home, id2),
                        FILE2, overwrite=True)

    boxley.Add(paths, directory, groupname, root)

    # edit the files, pull
    file_writer(paths, new_content1, new_content2)

    return paths


def push_helper(id1, id2, content1, content2, directory, groupname, root, cwd):
    # files that are not in a group
    file1_path = os.path.join(cwd, "example-files/file_%d.txt" % id1)
    file2_path = os.path.join(cwd, "example-files/file_%d.txt" % id2)
    paths = [file1_path, file2_path]

    # create the files and add them to a conf file
    file_writer(paths, content1, content2)
    boxley.Add(paths, directory, groupname, root)

    return paths


def test_Make_Group_File():
    boxley._Make_Group_File("example-files/group-test.conf")
    with open("example-files/group-test.conf") as TESTFILE:
        content = TESTFILE.read()

    assert content == "{}\n"


def test_Add():
    """
    `Add` is tested by creating a dictionary that should be identical to a conf
    file after a file is added to it.

    NOTE: removes all paths from `paths.conf`.

    Tests:
        - adding two files to `paths.conf`
        - adding two files to `paths.conf` in a specific directory "Add-Test-1"
        - adding two files to `paths.conf` in a specific directory "Add-Test-2"
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

    # remove paths from `paths.conf`
    with open(os.path.join(boxley_dir, "paths.conf"), "w") as PATHSCONF:
        PATHSCONF.write("{}\n")

    # should go to /Boxley/.../boxley/test/example-files/file_*.txt
    boxley.Add(paths_to_add, None, None, False)
    with open(os.path.join(boxley_dir, "paths.conf")) as PATHS:
        paths = { 
            path1: "/Boxley/%s/example-files/file_1.txt" % cwd_without_home,
            path2: "/Boxley/%s/example-files/file_2.txt" % cwd_without_home
        }
        assert paths == json.loads(PATHS.read())

    # should go to /Boxley/Add-Test-1/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-1", None, False)
    with open(os.path.join(boxley_dir, "paths.conf")) as PATHS:
        paths = {path1:"/Boxley/Add-Test-1/example-files/file_1.txt", path2:"/Boxley/Add-Test-1/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())

    # should go to /Boxley/Add-Test-2/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-2", "addtest2", False)
    with open(os.path.join(boxley_dir, "group-addtest2.conf")) as PATHS:
        paths = {path1: "/Boxley/Add-Test-2/example-files/file_1.txt", path2: "/Boxley/Add-Test-2/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())

    # should go to /Add-Test-3/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-3", "addtest3", True)
    with open(os.path.join(boxley_dir, "group-addtest3.conf")) as PATHS:
        paths = {path1: "/Add-Test-3/example-files/file_1.txt", path2: "/Add-Test-3/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())


def test_Delete():
    """
    `Delete` is tested by adding a file to a conf file using `Add` and then
    deleting the file from the conf file.

    Tests:
        - deleting two files from `paths.conf`
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
    with open(os.path.join(boxley_dir, "paths.conf")) as PATHS:
        assert "{}\n" == PATHS.read()

    boxley.Delete(paths, "deletetest")
    with open(os.path.join(boxley_dir, "group-deletetest.conf")) as PATHS:
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
    assert os.path.isfile(os.path.join(boxley_dir, "group-groupA.conf")) == True
    assert os.path.isfile(os.path.join(boxley_dir, "group-groupB.conf")) == True


def test_Pull():
    """
    `Pull` is tested by manually putting a file on Dropbox, using `Add` to add
    the file to a conf file, changing the local copy of the file, pulling the
    file from Dropbox, and then verifying that it is identical to what it was
    before the local changes were made.

    Tests:
        - adding two files to `paths.conf`
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

    NOTE: this file removes all files in ~/.boxley except for `boxley.conf` and
    `paths.conf`.

    Tests:
        - add two files to `paths.conf` and two files to a group "pullalltest"
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
    all_files.remove("paths.conf")
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
    Push is tested by creating a local file, adding it to a conf file (via
    `Add`), pushing the file, then manually pulling the file and comparing it.
    """
    boxley_dir, ACCESS_TOKEN = boxley._Get_Push_Settings()[:2]
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    with open(os.path.join(boxley_dir, "paths.conf"), "w") as PATHSCONF:
        PATHSCONF.write("{}\n")

    content1, content2 = "I am tired\n", "of being creative.\n"
    local_paths = push_helper(1, 2, content1, content2, None, None, False, cwd)
    boxley.Push(local_paths, False, None, True, False)

    # pull all files and compare with old version
    with open(os.path.join(boxley_dir, "paths.conf")) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    for local_path in paths:
        with open(local_path) as FILE:
            content, metadata = client.get_file_and_metadata(paths[local_path])
            assert FILE.read() == content.read()

    content3, content4 = "Green is not\n", "a creative colour.\n"
    local_paths = push_helper(3, 4, content3, content4, None, "pushtest", False, cwd)
    boxley.Push(local_paths, False, "pushtest", True, False)

    # pull all files and compare with old version
    with open(os.path.join(boxley_dir, "group-pushtest.conf")) as PATHSFILE_CONTENT:
        paths = json.loads(PATHSFILE_CONTENT.read())

    for local_path in paths:
        with open(local_path) as FILE:
            content, metadata = client.get_file_and_metadata(paths[local_path])
            assert FILE.read() == content.read()
