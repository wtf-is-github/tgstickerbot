import json
import os
import random
import uuid
from aiogram import Bot, types, Dispatcher, F
from aiogram.filters import Command
from yarl import URL

dp = Dispatcher()


@dp.message(Command("start", "help"))
async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b> and "
        "welcome to a whole new world of redirecting people to Google in a toxic way. "
        "Use this bot in chats in a definitely-brand-new way - as inline bot (wow).\n"
    )
    await message.answer(
        "It is worth trying yourself - here's the example\n"
        "<pre>@googlefwdbot special relativity</pre>"
    )


def toxic_responder(query, username="me"):
    # TODO: actually parse google results or change this toxic bragging
    s = (
        "Oh wow, what a question. You wouldn't believe how many results Google brings up for that one! "
        f"A quick search shows that there are over {random.randrange(1, 9999) * 1_000_000:,} results for that query!\n"
    )
    endings = [
        f"But you still decided to ask <b>{username}</b> to do it instead of doing a simple Google search yourself? Unbelievable.",
        f"So, despite the vast number of results on Google, you turned to <b>{username}</b> for the answer. How interesting.",
        "With so much information readily available on Google, "
        "it's surprising that you didn't just look it up yourself. Curious.",
    ]

    s += random.choice(endings)
    s += f"""\nAnyway, here's the link: <a href = '{google_url_builder(query)}'>{query}</a>"""
    return s


def non_toxic_responder(query):
    return f"Let's see what Google has to say: \n<a href = '{google_url_builder(query)}'>{query}</a>"


def google_url_builder(query: str) -> str:
    url = URL("https://google.com/search")
    url = url.with_query(
        {
            "q": query,
        }
    )
    return str(url)


# @dp.inline_query(F.text.startswith("duck"))
@dp.inline_query()
async def inline(inline_query: types.InlineQuery):
    search_query = inline_query.query or "google"

    # url = URL("https://google.com/search")
    # url = url.with_query(
    #     {
    #         "q": search_query,
    #     }
    # )

    toxic_message = toxic_responder(search_query, inline_query.from_user.full_name)

    toxic_input_content = types.InputTextMessageContent(
        message_text=toxic_message,
        parse_mode="HTML",
        # entities=[
        #     types.MessageEntity(
        #         url=str(url),
        #         type="url",
        #         offset=len(toxic_message) - len(str(url)),
        #         length=len(str(url)),
        #     )
        # ],
    )
    toxic_item = types.InlineQueryResultArticle(
        type="article",
        id=str(uuid.uuid4()),
        title=f"{search_query!r} results from Google - Toxic",
        input_message_content=toxic_input_content,
        # url=str(url),
    )

    nice_message = non_toxic_responder(search_query)

    nice_input_content = types.InputTextMessageContent(
        message_text=nice_message,
        parse_mode="HTML",
        # entities=[
        #     types.MessageEntity(
        #         url=str(url),
        #         type="url",
        #         offset=len(nice_message) - len(str(url)),
        #         length=len(str(url)),
        #     )
        # ],
    )

    nice_item = types.InlineQueryResultArticle(
        type="article",
        id=str(uuid.uuid4()),
        title=f"{search_query!r} results from Google - Nice",
        input_message_content=nice_input_content,
        # url=str(url),
    )

    await inline_query.answer(results=[toxic_item, nice_item])


@dp.message()
async def everything_else_handler(message: types.Message) -> None:
    stickers = [
        "CAACAgIAAxkBAAMpY_Y6uF6FG5gUNwOzoiT3UGKommYAAlYiAAK2O_FJPplpexqjmkAuBA",
        "CAACAgIAAxkBAAMnY_Y6d7rL8Ah29ymIZlJSxdYFaxkAAugsAAKBLfhJ5UOR1AiBUCEuBA",
        "CAACAgIAAxkBAAMrY_Y691FI4x8gvJr7z3i0cvGIIfwAAh0kAAKhP_lJMAb3hMw2srMuBA",
        "CAACAgIAAxkBAAMxY_Y7QLSfKPiv7ZblzL7RmCgvXbIAAtcPAAKLuKlKne54AolxjesuBA",
        "CAACAgIAAxkBAAMzY_Y7oHSgd6e5QpZMbN_Z7ZXY2tgAApEjAAJPAYBLrHqJz9mQcIAuBA",
    ]
    try:
        await message.answer_sticker(random.choice(stickers))
    except TypeError:
        await message.answer("Nice try!")


async def handler(event, context):
    if event["httpMethod"] == "POST":
        bot = Bot(
            os.environ.get("TOKEN"),
            parse_mode="HTML",
        )

        update = json.loads(event["body"])
        update = types.Update.parse_obj(update)

        await dp.feed_update(bot=bot, update=update)
        print(json.loads(event["body"]))
        return {"statusCode": 200, "body": "ok"}
    return {"statusCode": 405}
