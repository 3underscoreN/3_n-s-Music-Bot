# MusicBot (Discord Bot) made by 3_n#7069.
---
# NOTE
This bot and repo has been **deprecated** and is replaced by (this repo)[https://github.com/3underscoreN/3_n-s-slash-Music-Bot].

## Introduction
This is a bot I write in my free time. As bots like Groovy and Rythm are taken down by YouTube and bots my friends use (ProBot) has poor connectivity in
our region, I decided to write a bot. 

This is also my first time tracking project with git, please feel free to use and modify my code and teach me how to write python/ use git and Github (If you happpen
to find this project as a stranger. :P)

## Dependencies
You would need these python packages before you can run this program:
* `disnake`
* `pafy`
* `PyNaCl`
* `youtube-dl`
* `youtube-search`

Run the following to install these dependencies:
```
$ pip install disnake pafy PyNaCl youtube-dl youtube-search
```
Apart from that, you also need to setup your own bot in [discord developer portal](https://discord.com/developers).

---
### Optional Dependencies
If you don't like to use youtube-dl, you can use pafy's internal backend by setting environment variable `PAFY_BACKEND` to `"iternal"`. Keep in mind that I have never used it so I have no idea how it performs.

Alternatively, you can choose [yt-dlp](https://github.com/yt-dlp/yt-dlp) since `youtube-dl` repo is no longer active. However, you need to change `pafy` files so that it imports `yt_dlp` instead of `youtube_dl`.


## Deployment
Setup two environment variables:
* `OWNER`: Owner's ID
* `TOKEN`: Your bot's token

Run `main.py` after cloning the project.

## Contribution
If you would like to contribute to this project, you can always fork this repo and open a pull request once you are done with your side :)
