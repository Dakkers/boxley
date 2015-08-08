# Boxley
Boxley is a git-like CLI for syncing files with Dropbox.


## About
Boxley allows you to add any file to a list of files (`paths.json`) that can then be synchronized with Dropbox. When adding a file to this list, the directory in Dropbox that the file will be synced to can be specified. Files can also be organized into "groups", so that you don't have to push individual files or all of your files at once.


## Installation
Installation of Boxley, unfortunately, requires you to create your own Dropbox app. The reason for this is Boxley requires full read/write permissions to your Dropbox, so if I were to distribute the API key with the app, it would pose a security risk, I think.

See [INSTALL.md](./INSTALL.md) for full instructions.


## Settings
The default settings are as follows (found in `~/.boxley/boxley.conf`):

```
access_token=YOUR_ACCESS_TOKEN
db_dir=/Boxley/
relative_to_home=true
overwrite=true
autopush=false
autopush_time=---
push_on_startup=false
autopull=false
autopull_time=---
pull_on_startup=false
```

- **access_token**: A user-specific Dropbox access token. Don't alter this! It is created with `init`.
- **db_dir**: The default directory to sync with. Make sure to have a trailing `/` at the end, regardless of your OS.
- **relative_to_home**: Tells Boxley to include the path to your home directory in the Dropbox file paths.
- **overwrite**: Tells Dropbox to overwrite the files that are pushed, instead of duplicating them.

Other settings not yet implemented. Sorry :(


## Usage
A simple example:

```bash
echo Hellogoodbye > my_file.txt
boxley add my_file.txt
boxley push my_file.txt
```

## Commands
I like examples, so I'll put a lot here. My notation for displaying the mapping between the local file path and the Dropbox file path is as such:

```
/home/you/some/path/file.txt  -->  /Boxley/some/path/file.txt
```

These commands assume the default settings are used. See above.


### `add [options] [files]`
Adds file paths to `paths.json`, which can then be pushed. If a group is specified (see `-g` below), then the path is added to a group file instead. The Dropbox file path defaults to the local file path. Multiple files can be specified, and *should* work with any option.

Example:

```bash
boxley add file.txt
# /home/you/some/path/file.txt  -->  /Boxley/some/path/file.txt

boxley add fileA.txt fileB.txt
# /home/you/some/path/fileA.txt  -->  /Boxley/some/path/fileA.txt
# /home/you/some/path/fileB.txt  -->  /Boxley/some/path/fileB.txt
```

If `RELATIVE_TO_HOME` is `false`, then:

```bash
boxley add file.txt
# /home/you/some/path/file.txt  -->  /Boxley/home/you/some/path/file.txt
```

#### Options
##### `-g`
Adds the file path(s) to the group file specified by its name. Group filenames are of the form `group-GROUPNAME.json`. If the group does not already exist, it is created.

```bash
boxley add -g mygroup file.txt
# /home/you/some/path/file.txt  -->  /Boxley/some/path/file.txt
# this is found in  ~/.boxley/group-mygroup.json
```

##### `-root`
Ignores the default directory in `boxley.json`. Can be used in conjunction with `-d`.

```bash
boxley add -root file.txt
# /home/you/some/path/file.txt  -->  /some/path/file.txt
```

If `RELATIVE_TO_HOME` is `false`, then:

```bash
boxley add -root file.txt
# /home/you/some/path/file.txt  -->  /home/you/some/path/file.txt
```

##### `-d`
Specifies which Dropbox directory the file will be synced to. Can be used in conjunction with `-root`.

The following example will hold regardless of `RELATIVE_TO_HOME`'s value.

```bash
boxley add -d MyDirectory file.txt
# /home/you/some/path/file.txt  -->  /Boxley/MyDirectory/file.txt

boxley add -root -d MyDirectory file.txt
# /home/you/some/path/file.txt  -->  /MyDirectory/file.txt
```


### `del [options] [files]`
Deletes file paths from `paths.json`. If a group is specified (see `-g` below), then the file path is deleted from the group file instead. If a file path  cannot be found in the corresponding `.json` file, it is skipped.

Example:

```bash
boxley add file.txt
# /home/you/some/path/file.txt  -->  /Boxley/some/path/file.txt

boxley add fileA.txt fileB.txt
# /home/you/some/path/fileA.txt  -->  /Boxley/some/path/fileA.txt
# /home/you/some/path/fileB.txt  -->  /Boxley/some/path/fileB.txt
```

If `RELATIVE_TO_HOME` is `false`, then:

```bash
boxley del file.txt
```

#### Options
##### `-g`
Deletes the file path(s) from the group file specified by its name. If the group does not exist, the process is aborted.

```bash
boxley del -g mygroup file.txt
```


### `mkgroup [groupname]`
Creates a group file.

```bash
boxley mkgroup awesomestuff     # creates ~/.boxley/group-awesomestuff.json
```


### `pull [options] [file(s)]`
Pulls specified files from Dropbox. If a file belongs to a group, its group name MUST be specified, unless it belongs to both `paths.json` and a group, in which case, either one can be specified. Files of different groups CANNOT be pulled at the same time; only files of one group can be. If a file specified does not exist in the `*.json` file it *should* belong to, then it will be skipped.

```bash
boxley pull myfile.txt
boxley pull file_A.txt file_B.txt

# if file_C.txt and file_D.txt are in the group "hello"
boxley push -g hello file_C.txt file_D.txt
```

#### Options
##### `-g`
Group that the file(s) belong to. Multiple groups cannot be specified. If a file belongs to a group, its group must be specified.

##### `-v`
Verbose output; prints a message for every file that is pulled.


### `pullall [options]`
Pulls ALL files (those specified in `paths.json` and all `group-*.json` files) from Dropbox. If a file in the `*.json` file cannot be found, it is skipped.

```bash
boxley pullall
```

#### Options
##### `-v`
Verbose output; prints a message for every file that is pushed.


### `pullgroup [options] [groupname(s)]`
Pulls files in specified group(s) from Dropbox. If a file in the `group-*.json` file cannot be found, it is skipped.

```bash
boxley pullgroup awesomestuff     # a single group
boxley pullgroup assets sprites   # multiple groups!
```

#### Options
##### `-v`
Verbose output; prints a message for every file that is pulled.


### `push [options] [file(s)]`
Pushes specified files to Dropbox. If a file belongs to a group, its group name MUST be specified, unless it belongs to both `paths.json` and a group, in which case, either one can be specified. Files of different groups CANNOT be added at the same time; only files of one group can be. If a file specified does not exist in the `*.json` file it *should* belong to, then it will be skipped.

```bash
boxley push myfile.txt
boxley push file_A.txt file_B.txt

boxley push --dup myfile.txt    # duplicate file instead of overwriting

# if file_C.txt and file_D.txt are in the group "hello"
boxley push -g hello file_C.txt file_D.txt
```

#### Options
##### `--dup`
Duplicate; if the file being pushed already exists on Dropbox, then this file will have a duplicate name. Equivalent to having the `paths.json` overwrite setting set to false.

##### `-g`
Group that the file(s) belong to. Multiple groups cannot be specified. If a file belongs to a group, its group must be specified.

##### `--ov`
Overwrite; if the file being pushed already exists on Dropbox, then this file will overwrite the existing version. Equivalent to having the `paths.json` overwrite setting set to true.

##### `-v`
Verbose output; prints a message for every file that is pushed.


### `pushall [options]`
Pushes ALL paths (those specified in `paths.json` and all `group-*.json` files) to Dropbox. If a file in the `*.json` file cannot be found, it is skipped.

```bash
boxley pushall
```

#### Options
##### `--dup`
Duplicate; if the file being pushed already exists on Dropbox, then this file will have a duplicate name. Equivalent to having the `paths.json` overwrite setting set to false.

##### `--ov`
Overwrite; if the file being pushed already exists on Dropbox, then this file will overwrite the existing version. Equivalent to having the `paths.json` overwrite setting set to true.

##### `-v`
Verbose output; prints a message for every file that is pushed.


### `pushgroup [options] [groupname(s)]`
Pushes specified group(s) to Dropbox. If a file in the `group-*.json` file cannot be found, it is skipped.

```bash
boxley pushgroup awesomestuff     # a single group

boxley pushgroup -d sprites models    # push multiple groups, and duplicate files instead of overwriting
```

#### Options
##### `--dup`
Duplicate; if the group files being pushed already exist on Dropbox, then these files will have duplicate names. Equivalent to having the `paths.json` overwrite setting set to false.

##### `--ov`
Overwrite; if the group files being pushed already exist on Dropbox, then these files will overwrite the existing versions. Equivalent to having the `paths.json` overwrite setting set to true.

##### `-v`
Verbose output; prints a message for every file that is pushed.

## Testing
py.test is required for running Boxley's tests. Tests **must** be run inside the `test/` directory due to a relative import. The tests can be run by simply running `py.test` inside the directory.


## Contributing
Boxley, like all of us, has a few issues. These issues are put here on GitHub. If you feel as if you can fix any of those issues, feel free to submit a pull request!


## License
GPL
