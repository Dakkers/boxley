# Boxley
Boxley is a CLI for syncing specific files with Dropbox in any directory.

## About
Boxley allows you to add any file to a list of files (`paths.conf`) that can then be synchronized with Dropbox. When adding a file to this list, the directory in Dropbox that the file will be synced to can be specified. Files can also be organized into "groups", so that you don't have to push individual files or all of your files at once.

## Installation
All of these commands take place in a terminal.

To start using Boxley, initialize it, follow the link it spits out, get the authorization code, and paste it back in the terminal. 

```
boxley init
1. Go to: https://www.dropbox.com/1/oauth2/authorize?response_type=code&client_id=le4w3kfr8fmlg0d
2. Click "Allow" (you might have to log in first)
3. Copy the authorization code.
Enter the authorization code here: 
```

Now you can start using Boxley! Great job.

## Settings
The default settings are as follows (found in `~/.boxley/boxley.conf`):

```
access_token=r3aHBkL-OloAAAAAAAABvL6bch_122KBkzu3OI8kKanIyS3UN0AxKdRPUfQfWNgU
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

- **access_token**: A user-specific Dropbox access token. Don't alter this!
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
Adds file paths to `paths.conf`, which can then be pushed. If a group is specified (see `-g` below), then the path is added to a group file instead. The Dropbox file path defaults to the local file path. Multiple files can be specified, and *should* work with any option.

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
Adds the file path(s) to the group file specified by its name. Group filenames are of the form `group-GROUPNAME.conf`. If the group does not already exist, it is created.

```bash
boxley add -g mygroup file.txt
# /home/you/some/path/file.txt  -->  /Boxley/some/path/file.txt
# this is found in  ~/.boxley/group-mygroup.conf
```

##### `-root`
Ignores the default directory in `boxley.conf`. Can be used in conjunction with `-d`.

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


### `mkgroup [groupname]`
Creates a group file.

```bash
boxley mkgroup awesomestuff     # creates ~/.boxley/group-awesomestuff.conf
```


### `pull [options] [file(s)]`
Pulls specified files from Dropbox. If a file belongs to a group, its group name MUST be specified, unless it belongs to both `paths.conf` and a group, in which case, either one can be specified. Files of different groups CANNOT be pulled at the same time; only files of one group can be. If a file specified does not exist in the `*.conf` file it *should* belong to, then it will be skipped.

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


### `push [options] [file(s)]`
Pushes specified files to Dropbox. If a file belongs to a group, its group name MUST be specified, unless it belongs to both `paths.conf` and a group, in which case, either one can be specified. Files of different groups CANNOT be added at the same time; only files of one group can be. If a file specified does not exist in the `*.conf` file it *should* belong to, then it will be skipped.

```bash
boxley push myfile.txt
boxley push file_A.txt file_B.txt

boxley push -d myfile.txt    # duplicate file instead of overwriting

# if file_C.txt and file_D.txt are in the group "hello"
boxley push -g hello file_C.txt file_D.txt
```

#### Options
##### `-d`
Duplicate; if the file being pushed already exists on Dropbox, then this file will have a duplicate name. Equivalent to having the `paths.conf` overwrite setting set to false. If both -d and -o flags are entered, the one entered LAST will take priority, regardless of the `paths.conf` setting.

##### `-g`
Group that the file(s) belong to. Multiple groups cannot be specified. If a file belongs to a group, its group must be specified.

##### `-o`
Overwrite; if the file being pushed already exists on Dropbox, then this file will overwrite the existing version. Equivalent to having the `paths.conf` overwrite setting set to true. If both -d and -o flags are entered, the one entered LAST will take priority, regardless of the `paths.conf` setting.

##### `-v`
Verbose output; prints a message for every file that is pushed.


### `pushall [options]`
Pushes ALL paths (those specified in `paths.conf` and all `group-*.conf` files) to Dropbox. If a file in the `*.conf` file cannot be found, it is skipped.

```bash
boxley pushall
```

#### Options
##### `-d`
Duplicate; if the file being pushed already exists on Dropbox, then this file will have a duplicate name. Equivalent to having the `paths.conf` overwrite setting set to false. If both -d and -o flags are entered, the one entered LAST will take priority, regardless of the `paths.conf` setting.

##### `-o`
Overwrite; if the file being pushed already exists on Dropbox, then this file will overwrite the existing version. Equivalent to having the `paths.conf` overwrite setting set to true. If both -d and -o flags are entered, the one entered LAST will take priority, regardless of the `paths.conf` setting.

##### `-v`
Verbose output; prints a message for every file that is pushed.


### `pushgroup [options] [groupname(s)]`
Pushes specified group(s) to Dropbox. If a file in the `group-*.conf` file cannot be found, it is skipped.

```bash
boxley pushgroup awesomestuff     # a single group

boxley pushgroup -d sprites models    # push multiple groups, and duplicate files instead of overwriting
```

#### Options
##### `-d`
Duplicate; if the group files being pushed already exist on Dropbox, then these files will have duplicate names. Equivalent to having the `paths.conf` overwrite setting set to false. If both -d and -o flags are entered, the one entered LAST will take priority, regardless of the `paths.conf` setting.

##### `-o`
Overwrite; if the group files being pushed already exist on Dropbox, then these files will overwrite the existing versions. Equivalent to having the `paths.conf` overwrite setting set to true. If both -d and -o flags are entered, the one entered LAST will take priority, regardless of the `paths.conf` setting.

##### `-v`
Verbose output; prints a message for every file that is pushed.

## TODO
Implement:

- pull
- pullall
- del
- addfolder
- delfolder
- autopush
- autopull

Bugs:

- don't allow for re-initialization

Possible features:

- warnings for pushing to already existing files
- allow a local file to have multiple Dropbox links (this is possible in groups)
- `.boxleyignore` -- file to specify what files to ignore when adding folders

Code cleanup:

- Some things can definitely be wrapped in functions ... do that

## Development Usage
To use Boxley as a developer, you need to create your own Dropbox app. The Dropbox app must use the Core API, and musth have permissions to write files anywhere in the user's Dropbox. After doing this, create a file in the root directory called `secrets.txt` with the following contents:

```
YOUR_APP_KEY
YOUR_APP_SECRET
```

where `YOUR_APP_KEY` and `YOUR_APP_SECRET` must be your app's "app key" and "app secret" respectively. Then follow the Installation steps.