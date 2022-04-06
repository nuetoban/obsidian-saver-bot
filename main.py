import pathlib
import os
import re
import logging
from datetime import date, datetime
from subprocess import run, PIPE

from aiogram import Bot, Dispatcher, executor, types
from git import Repo

API_TOKEN = os.getenv("OBSIDIAN_BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(funcName)s: %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)


def auth():
    token = os.getenv("OBSIDIAN_BOT_GITHUB_TOKEN")
    # out = run(["git", "config", "--global", "credential.helper", "store"], stdout=PIPE)
    # print(out)
    out = run(
        ["gh", "auth", "login", "--with-token"], input=token.encode(), stdout=PIPE
    )
    print(out)
    out = run(["gh", "auth", "setup-git"], stdout=PIPE)
    print(out)
    out = run(["gh", "auth", "status"], stdout=PIPE)
    print(out)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler()
async def on_text(message: types.Message):
    # Pull git repo
    repo = Repo("./repo")
    o = repo.remotes.origin
    o.pull()

    today = date.today()

    # Check if the message is forward from NH (https://t.me/hacker_news_feed) channel
    if message.forward_from_chat and message.forward_from_chat.username == "hacker_news_feed":
        header = message.text.split("\n")[0].strip()
        header = (
            "(HN) ("
            + today.strftime("%Y-%m-%d")
            + ") "
            + re.sub(
                r"\s\(.{0,3}Score: \d+\+ in \d+ \w+\)", "", header, count=0, flags=0
            )
        )
        print("Creating ", header)
        with open(f"./repo/Incoming/{header}.md", "w") as f:
            f.write(message.text)
            f.write("\n\n- [ ] Completed")
            f.write("\n\n#hn")
            f.write("\n\n## What the article is about?\n")
            f.write("\n\n## What can I learn from it?\n")
    elif message.forward_from_chat and message.forward_from_chat.username:
        header = (
            "(Forward) ("
            + today.strftime("%Y-%m-%d")
            + ") "
            + f"({message.forward_from_chat.username}) "
            + datetime.now().strftime("%H:%M:%S")
        )
        print("Creating ", header)
        with open(f"./repo/Incoming/{header}.md", "w") as f:
            f.write(message.text)
            f.write("\n\n- [ ] Completed")
            f.write(f"\n\n#{message.forward_from_chat.username}")
            f.write("\n\n## What the article is about?\n")
            f.write("\n\n## What can I learn from it?\n")
    elif message.text:
        header = (
            "(Text) ("
            + today.strftime("%Y-%m-%d")
            + ") "
            + datetime.now().strftime("%H:%M:%S")
        )
        print("Creating ", header)
        with open(f"./repo/Incoming/{header}.md", "w") as f:
            f.write(message.text)
            f.write("\n\n- [ ] Completed")
            f.write("\n\n## What the article is about?\n")
            f.write("\n\n## What can I learn from it?\n")

    # Check if the message contains a link
    ...

    # If the message is just plain text, create a new note
    ...

    # If forward from channel, save the text and media and specify source
    ...

    # Add and push
    repo.git.add(f"Incoming/{header}.md")
    repo.index.commit(f"Save '{header}'")
    o.push()


if __name__ == "__main__":
    auth()

    try:
        os.stat("./repo")
    except FileNotFoundError:
        repo = Repo.clone_from(os.getenv("OBSIDIAN_BOT_GITHUB_REPO"), "./repo")
        repo.config_writer().set_value(
            "user", "name", os.getenv("OBSIDIAN_BOT_GIT_NAME")
        ).release()
        repo.config_writer().set_value(
            "user", "email", os.getenv("OBSIDIAN_BOT_GIT_EMAIL")
        ).release()

    pathlib.Path("./repo/Incoming").mkdir(exist_ok=True)
    executor.start_polling(dp)
