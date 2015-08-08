# Installation
There are two ways to install Boxley, both of which require the creation of a Dropbox app, which is pretty simple. The first way is via Pip, which is simple. The second way is installing from source.


## Making a Dropbox app
1. Head to the [Dropbox app console](https://www.dropbox.com/developers/apps)
2. Click "create app"
3. Verify your email, if necessary
4. Select "**Dropbox API app**" as the type of app you'd like to create
5. Select "**No**" to the question "Can your app be limited to its own folder?"
6. Select "**All file types**" to the question "What type of files does your app need access to?"
7. Provide an app name -- it doesn't need to be called Boxley


## Method 1 (Installing via Pip)
The first step, of course, is simply:

```
pip install boxley
```

This will also install the Dropbox SDK, which is required. Then, you should be able to run `boxley init`. See below for instructions on this.


## Method 2 (Installing From Source)
Installing from source requires you to make your own Dropbox app and install the Dropbox Python SDK. There are also instructions on building the source into an executable below.

See below ([Other things/Making a Dropbox app](#Making-a-Dropbox-app)) for instructions on how to make a Dropbox app.

Then, clone this repository and put it somewhere.

**NOTE**: if you are using Windows and are planning on making the source into an executable, skip to the instructions below.

Install the [Dropbox Python SDK](https://www.dropbox.com/developers/core/sdks/python). Then running `python main.py init` should work. See below for instructions on this.


## Initialization
Running `boxley init` will create `~/.boxley`, and a `boxley.conf` and `paths.json` inside. It will ask for the app key and app secret, which you can get from the Dropbox app console. Enter these, follow the link to get an access token, enter that as well, and you should be good to go.


## Turning the source into an executable
If you want to turn the repository into an executable, you can try a python library that creates executables. Unfortunately, it's different on different operating systems. 

### Ubuntu
I've had success with Nuitka.

Before starting, you'll need to install the [Dropbox Python SDK](https://www.dropbox.com/developers/core/sdks/python).

#### Nuitka

Using Nuitka is simple enough. On Ubuntu 14.04, I downloaded the .deb file from the [Nuitka downloads page](http://nuitka.net/pages/download.html), and ran the following:

```
sudo dpkg -i nuitka.deb
sudo apt-get update
sudo apt-get install -f

nuitka --recurse-all main.py
```

The last command will create `main.exe`, which can be renamed to `boxley` and put in your path. Then run `boxley init`.

### Windows
I've only had success with PyInstaller thus far. Nuitka and Py2Exe didn't seem to work.

#### PyInstaller
**NOTE**: this is working for Dropbox SDK v2.2.0. If the SDK changes significantly, these instructions may not work.

First, install [PyWin32](http://sourceforge.net/projects/pywin32/files/) -- make sure to install the correct version depending on your version of Python.

Then install PyInstaller with `pip install pyinstaller`. This should probably be run in a command prompt with administrator privileges (right click > run as admin...).

Then get the [Dropbox Python SDK](https://www.dropbox.com/developers/core/sdks/python), but **DO NOT** install it via pip. Actually download the SDK and decompress it. Navigate to the `dropbox/` folder and edit `rest.py`.

In `rest.py`, add `import os` to the import statements. Then change line 27 from

```python
TRUSTED_CERT_FILE = pkg_resources.resource_filename(__name__, 'trusted-certs.crt')     # BAD!
```

to

```python
TRUSTED_CERT_FILE = os.path.join(os.path.dirname(sys.executable), 'trusted-certs.crt')    # GOOD!
```

Backup the `trusted-certs.crt` file to another directory. Then run `python -m compileall`. Then go back to the root of the directory (`dropbox-x.x.x`) and run `python setup.py install`.

Now, in Boxley's directory, run `pyinstaller -F main.py`. This will create `dist/`, `build/` and `main.spec`. Inside `dist/` is the executable. Copy the `trusted-certs.crt` file to `dist/`. Then, run `./dist/main.exe init` and it should work!

**NOTE**: If you decide to move `./dist/main.exe` to another folder, *be sure to move* `trusted-certs.crt` with it!
