from typing import NamedTuple

import string as st
from datetime import datetime

__all__ = (
    'FIRST_JANUARY_1970',
    'ALLOWED_CHARACTERS',
    'EDGE_CHARACTERS_CASES',
    'EDGE_CHARACTERS_TABLE',
    'PUNCTUATIONS_AND_DIGITS',
    'PAD_TABLE',
    'LETTERS_EMOJI',
    'LETTERS_TABLE',
    'EMOJIS_TABLE',
    'NUMBERS_EMOJI',
    'NUMBERS_TABLE',
    'Channels',
    'Categories',
    'StaffRoles',
    'ExtraRoles'
)

FIRST_JANUARY_1970 = datetime(1970, 1, 1, 0, 0, 0, 0)
ALLOWED_CHARACTERS = tuple(st.printable)
EDGE_CHARACTERS_CASES = {
    '@': 'a',
    '0': 'o',
    '1': 'i',
    '$': 's',
    '!': 'i',
    '9': 'g',
    '5': 's',
}
EDGE_CHARACTERS_TABLE = str.maketrans(EDGE_CHARACTERS_CASES)
PUNCTUATIONS_AND_DIGITS = tuple(list(st.punctuation) + list(st.digits))
PAD_TABLE = str.maketrans({k: '' for k in PUNCTUATIONS_AND_DIGITS})

LETTERS_EMOJI = {
    'a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩',
    'e': '🇪', 'f': '🇫', 'g': '🇬', 'h': '🇭',
    'i': '🇮', 'j': '🇯', 'k': '🇰', 'l': '🇱',
    'm': '🇲', 'n': '🇳', 'o': '🇴', 'p': '🇵',
    'q': '🇶', 'r': '🇷', 's': '🇸', 't': '🇹',
    'u': '🇺', 'v': '🇻', 'w': '🇼', 'x': '🇽',
    'y': '🇾', 'z': '🇿'
}
NUMBERS_EMOJI = {
    '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣',
    '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣',
    '8': '8️⃣', '9': '9️⃣'
}
LETTERS_TABLE = str.maketrans(LETTERS_EMOJI)
NUMBERS_TABLE = str.maketrans(NUMBERS_EMOJI)

EMOJIS_TABLE = str.maketrans({v: k for k, v in LETTERS_EMOJI.items()})


class Channels(NamedTuple):
    verify = 1097610035548393512

    tickets = 1097613823101370510
    news = 1097610035548393514
    boosts = 1097610035548393515
    rules = 1097610035548393516
    welcome = 1097610035548393517
    roles = 1097610035548393518
    colours = 1097610035548393519
    intros = 1097610035548393520
    birthdays = 1097610036026548284
    polls = 1097610036026548285
    activity_reports = 1097610036026548286

    general = 1097610036026548288
    venting = 1097610036026548290
    nsfw = 1097610036026548291

    bots = 1097610036026548293
    memes = 1097610036445974650
    anime = 1097610036445974651
    animals = 1097610036445974652
    gaming = 1097610036445974653

    selfies = 1097610036445974657
    artwork = 1097610036685054032
    photos = 1097610036685054033
    videos = 1097610036685054034
    outfit_showcase = 1097614351860506694

    recommendations = 1097610037289025637
    # confessions = 1089494283863736320
    quotes = 1097610037289025639
    self_ad = 1097610037289025640

    no_mic_chat = 1097610037289025644
    music_commands = 1097610037767180459
    music = 1097610037767180460
    lobby_1 = 1097610037767180461
    lobby_2 = 1097610037767180462
    sleep = 1097610037767180463

    staff_chat = 1097610038270500875
    bot_commands = 1097610038270500880

    logs = 1097610038270500876
    messages_logs = 1097610038270500877
    moderation_logs = 1097610038270500878
    github = 1097610038270500879
    discord_news = 1081314042368512072
    discord_safety = 1081670414406795445

    all = (
        tickets, news, boosts, rules, welcome, intros,
        roles, colours, birthdays, general, venting,
        nsfw, bots, memes, anime, animals,
        gaming, selfies, artwork, photos, videos,
        no_mic_chat, music_commands, music,
        lobby_1, lobby_2, sleep, staff_chat, logs,
        messages_logs, moderation_logs, github, bot_commands, verify,
        recommendations, self_ad, polls, activity_reports, outfit_showcase,
        discord_news, discord_safety
    )


class Categories(NamedTuple):
    server = 1097610035548393513
    general = 1097610036026548287
    fun = 1097610036026548292
    media = 1097610036445974654
    extra = 1097610036685054035
    music = 1097610037289025643
    staff = 1097610037767180464
    tickets = 1097610038270500881

    all = (server, general, fun, media, extra, music, staff, tickets)


class StaffRoles(NamedTuple):
    owner = 1097610034998935568
    admin = 1097610034998935567
    moderator = 1097610034998935566

    all = (owner, admin, moderator)


class ExtraRoles(NamedTuple):
    muted = 1097610034998935564
    blocked = 1097610034998935565
    unverified = 1097610034701144147
    bot = 1097610034701144146
    server_booster = 1078313465392943125
    special_booster = 1078368293297066074

    all = (muted, blocked, unverified, bot)
