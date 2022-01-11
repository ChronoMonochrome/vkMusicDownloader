**Python3** script to download music from Vkontakte social network.  
The script was tested on **python 3.6.9** on **Linux Mint 19.3**.

08.12.2021 Update:
+ Music download via **m3u8** URL.

18.11.2020 Update:
+ Updated dependencies
+ Added program parameter, **./main.py -n** not to authorize over again (can be used after a successful authorization).

10.10.2019 Update:
+ Added albums download.

### How to use:

```bash
apt-get install ffmpeg
pip3 install -r requirements.txt
./src/main.py
```
On a first run script will ask you to authorize:
```bash
Authorize again? yes/no
> yes
```
Then will ask a login we'll be using to authorize:
```bash
Enter login
> my_login 
```
Then enter a password:
```bash
Enter password
> 
```
Then enter profile/group ID which music we want to download from:
```bash
Enter profile id
> 
```
You can find an ID by the name, e.g. [here](http://regvk.com/id/)

If everything was done correctly, you should see something like this:
```bash
You've been successfully authorized.
Preparing to download...
App will attempt to download 113 tracks from your profile page.
Downloading...

1 Already downloaded: Ленинград - i_$uss.mp3.
2 Already downloaded: Chamdo - Tibetan Gorshay Dance.mp3.
...
113 tracks downloaded in: 6.139557838439941 сек.

```
