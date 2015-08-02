import os
import sys
import json
sys.path.append("../boxley")     # damn relative paths
import main as boxley


def test_Make_Group_File():
    boxley._Make_Group_File("example-files/group-test.conf")
    with open("example-files/group-test.conf") as TESTFILE:
        content = TESTFILE.read()

    assert content == "{}\n"


def test_Add():
    # default Dropbox directory = /Boxley
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")
    cwd = os.getcwd()
    cwd_without_home = cwd.replace(home, "")[1:]  # remove leading /

    path1 = os.path.join(cwd, "example-files/file_1.txt")
    path2 = os.path.join(cwd, "example-files/file_2.txt")
    paths_to_add = [path1, path2]

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
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")
    cwd = os.getcwd()

    path1 = os.path.join(cwd, "example-files/file_1.txt")
    path2 = os.path.join(cwd, "example-files/file_2.txt")
    paths = [path1, path2]

    boxley.Add(paths, None, None, False)
    boxley.Add(paths, None, "testgroup", False)

    boxley.Delete(paths, None)
    with open(os.path.join(boxley_dir, "paths.conf")) as PATHS:
        assert "{}\n" == PATHS.read()

    boxley.Delete(paths, "testgroup")
    with open(os.path.join(boxley_dir, "group-testgroup.conf")) as PATHS:
        assert "{}\n" == PATHS.read()
