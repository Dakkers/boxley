# Installation
There are two ways to use Boxley. The first is to get the executable, which is far easier. If you don't trust executables though, and prefer to install (and possibly build) things from source, you can do that. It's a bit more of a process.

## Method 1 (Executable)
(The executable isn't online yet -- sorry!)

### Initialization

To start using Boxley, initialize it, follow the link it spits out, get the authorization code, and paste it back in the terminal. 

```
boxley init
1. Go to: https://www.dropbox.com/1/oauth2/authorize?response_type=code&client_id=le4w3kfr8fmlg0d
2. Click "Allow" (you might have to log in first)
3. Copy the authorization code.
Enter the authorization code here: 
```

Now you can start using Boxley! Great job.

## Method 2 (Installing From Source)
Installing from source requires you to make your own Dropbox app. There are also instructions on building the source into an executable below.

1. Head to the [Dropbox app console](https://www.dropbox.com/developers/apps)
2. Click "create app"
3. Verify your email, if necessary
4. Select "**Dropbox API app**" as the type of app you'd like to create
5. Select "**No**" to the question "Can your app be limited to its own folder?"
6. Select "**All file types**" to the question "What type of files does your app need access to?"
7. Provide an app name -- it doesn't need to be called Boxley

Then, clone this repository and put it somewhere. Inside the top level of the directory you cloned it to, create a file called `secrets.txt` with the following contents:

```
YOUR_APP_KEY
YOUR_APP_SECRET
```

where `YOUR_APP_KEY` and `YOUR_APP_SECRET` must be your app's "app key" and "app secret" respectively, which can be found on the Dropbox app console. Then run `python main.py init` and follow the instructions. All of the other commands can be run as `python main.py COMMAND` with whatever options.

## Turning the source into an executable
If you want to turn the repository into an executable, you can try a python library that creates executables. Unfortunately, it's different on different operating systems. 

Before starting, you'll need to install the [Dropbox Python SDK](https://www.dropbox.com/developers/core/sdks/python).

### Ubuntu
I've had success with Nuitka.

#### Nuitka

Using Nuitka is simple enough. On Ubuntu 14.04, I downloaded the .deb file from the [Nuitka downloads page](http://nuitka.net/pages/download.html), and ran the following:

```
sudo dpkg -i nuitka.deb
sudo apt-get update
sudo apt-get install -f

nuitka --recurse-all main.py
```

The last command will create `main.exe`, which can be renamed to `boxley` and put in your path. Then run `boxley init`.
s