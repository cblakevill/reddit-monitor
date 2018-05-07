# reddit-monitor

Monitor certain subreddits live.

# Configuration
* Add subreddits you want to monitor in the subreddit list.
* Add regexes to the filter phrase list to filter by thread title. Phrases can set to either include or exclude mathcing threads.

# Installation 
Intall pyinstaller and run 
```
pyinstaller --onefile --windowed src/reddit_monitor.pyw
```
from the root directory. The excecutable is produced in the dist directory.
