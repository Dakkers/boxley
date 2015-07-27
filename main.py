import os
import sys
import dropbox

cmd = sys.argv[1]


def Init():
    SECRETS = open('./secrets.txt')
    app_key = SECRETS.readline().strip()
    app_secret = SECRETS.readline().strip()
    SECRETS.close()

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code.'
    code = raw_input("Enter the authorization code here: ").strip()

    # This will fail if the user enters an invalid authorization code
    access_token, user_id = flow.finish(code)

    # create ~/.boxley
    home_dir = os.path.expanduser("~")
    boxley_dir = os.path.join(home_dir, ".boxley")
    os.mkdir(boxley_dir)

    # create default config file and syncfiles
    with open(os.path.join(boxley_dir, 'boxley.conf'), "w") as CONFIG:
        CONFIG.write("access_token=%s\n" % access_token)
        CONFIG.write("db_dir=Boxley\n")
        CONFIG.write("autopush=false\nautopush_time=---\npush_on_startup=false\n")
        CONFIG.write("autopull=false\nautopull_time=---\npull_on_startup=false\n")

    SYNCFILES = open(os.path.join(boxley_dir, 'files.conf'), "w")
    SYNCFILES.close()


if cmd == 'init':
    Init()
