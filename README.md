gchat conversation visualizer
=============================

Some flaky scripts to log and visualize your chat history via gchat.

Fetch chats by running the script:

> ./getchats.sh [your google email address]

Example:
> ./getchats.sh johndoe@gmail.com 

You will be prompted to enter your gmail password. The final data will be downloaded to the file called "analyzed".

Note if your default python 2.7 interpreter is not `python`, then edit `config.sh` to change the `PYTHON` variable to point to it.
