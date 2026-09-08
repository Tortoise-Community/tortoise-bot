from aenum import Enum, NoAlias

from discord import Color

tortoise_guild_id = 1520372691448889364
ban_appeal_server_id = 1523653436757770330
website_url = "https://www.tyxc.org/"
privacy_url = "https://www.tyxc.org/privacy"
rules_url = "https://www.tyxc.org/rules"
github_repo_link = "https://github.com/Tortoise-Community/Tortoise-BOT"
line_img_url = "https://www.animatedimages.org/data/media/562/animated-line-image-0015.gif"
infraction_img_url = "https://www.animatedimages.org/data/media/562/animated-line-image-0538.gif"
banner_url = "https://lairesit.sirv.com/Tortoise/banner.jpg"
github_repo_stats_endpoint = "https://api.github.com/repos/Tortoise-Community/"
project_url = "https://www.tyxc.org/projects/"
events_url = "https://www.tyxc.org/events/"
default_avatar_url = "https://cdn.discordapp.com/embed/avatars/4.png"
appeal_server_link = "https://discord.com/invite/YxEzEqMNY8"
server_link = "https://discord.com/invite/Ex8xeWD"
online_compiler_link = "https://execute.tyxc.org"
runtime_bot_link = "https://runtime-bot.tyxc.org"
online_viewer_url = "https://viewer.tyxc.org"
bot_avatar_url = "https://lairesit.sirv.com/Tortoise/tortoise.png"

# Channel IDs
announcements_channel_id = 1522906040662757416

# Log Channel IDs
deterrence_log_channel_id = 1522646380462608434
bot_log_channel_id = 1522646330663764061
message_log_channel_id = 1522646466643099820
user_log_channel_id = 1522646515477119077
team_log_channel_id = 1522646585039913240
challenge_log_channel_id = 1522646623967117333
role_progression_log_channel_id = 1522646678899916831

mod_mail_log_channel_id = bot_log_channel_id
bug_reports_log_channel_id = bot_log_channel_id
code_submissions_log_channel_id = bot_log_channel_id

bot_dev_channel_id = 1520372693155971105
general_channel_id = 1520372692446871668
today_i_did_channel_id = 1535663240015519755
resume_roasting_channel = 1520372692446871669
staff_channel_id = 1520372692090359890
rules_channel_id = 1522180967136231445

#Tortoise Guild channels
leetcode_channel_id = 1520372692446871674
programming_channel_id = 1520372692820426862
opensource_channel_id = 1520372692820426863
discussion_voice_channel_id = 1520372692820426864
bot_cmd_channel_id = 1520372692446871671
focus_music_channel_id = 1520372692446871672
project_showcase_channel_id = 1520372692446871670
resources_channel_id = 1520372692090359895
challenge_submission_channel_id = 1520372692820426866
challenge_discussion_channel_id = 1520372692820426867
challenges_channel_id = 1522906649973751898
challenge_logs_public_channel_id = 1524679248219213864
bait_channel_id = 1520372693294125167
introduction_channel_id = 1520372692090359897
join_a_team_channel_id = 1520372692446871665
mod_mail_thread_channel_id = 1546921962339835914

# Marketplace channels
job_board_channel_id = 1520372693067632693
dev_board_channel_id = 1520372693126348848

# Ban Appeal Channels
ban_appeal_channel_id = 1520372693155971106

# Message id
teams_dashboard_message_id = 1523585450311417876

# Roles
trusted_role_id = 1520372691469729955
moderator_role_id = 1520372691469729959
admin_role_id = 1520372691486638113
new_member_role_id = 1520372691448889372
challenger_role_id = 1520372691457020016
wizard_role_id = 1520372691469729956
contributor_role_id = 1520372691469729952
accepting_team_invites_role_id = 1520372691448889369
jr_moderator_role_id = 1520372691469729958


active_role_id = 1520372691457020017
active_plus_role_id = 1520372691457020018
chronically_online_role_id = 1520372691457020019
needs_to_touch_grass_role_id = 1520372691457020020
boot_role_id = 1520372691457020023
apprentice_role_id = 1520372691457020024
fellow_role_id = 1520372691469729953
elite_role_id = 1520372691469729957

mod_mail_ping_role_id = 1520372691448889367
bot_trap_role_id = 1520372691448889365

promotable_roles = {
    wizard_role_id: "You are currently **#1 on the Challenges Leaderboard**, placing you at the top "
                         "of the server's competitive coding ranks.\n\n"
                         "This is the **highest non-staff role** and represents exceptional skill, "
                         "consistency, and mastery in solving challenges.\n\n"
                         "Keep pushing the limits and setting the bar for others!",

    trusted_role_id:  "This role is given to members who have been part of the community for a long "
                         "time and have consistently shown they can be trusted.\n\n"
                         "This is the **2nd highest non-staff role** and it's exempt from certain auto-mod restrictions.\n\n"
                         "Thank you for being a reliable and respected member of the community.",

    contributor_role_id:  "This role recognizes members who actively contribute to our **GitHub repositories** "
                         "through code, improvements, bug fixes, or other development efforts.\n\n"
                         "Your work helps strengthen our projects and supports the wider **open-source community**.\n\n"
                         "Thank you for contributing and helping move the project forward!",
    jr_moderator_role_id: "This is a **trial staff role** for members stepping into moderation.\n\n"
                          "As a **Junior Moderator**, you’ll help keep the server clean, assist members, "
                          "and get hands-on experience with how moderation works.\n\n"
                          "This is the **3rd highest role in the staff hierarchy** and lasts for about "
                          "**1 month**.\n\n"
                          "Do well during this period, make fair decisions, and help the community "
                          "and you can be promoted to **Moderator**.\n\n"
                          "Take initiative, be approachable, and set a good example.",
    elite_role_id:        "This role is given to appreciate and honor the **most experienced person on this server**.\n\n"
                          "This is now the **highest non-staff role** and stands as a testament to your exceptional "
                          "real-world expertise, seasoned perspective, and industry background.\n\n"
                          "We are incredibly grateful to have you in our community."

}

progression_roles = {
    boot_role_id: (
        "This role marks the beginning of your progression in the community. "
        "It is given to members who actively participate and are recognized "
        "by others for their helpfulness and engagement.\n\n"
        "Keep contributing, helping others, and sharing your knowledge to "
        "continue progressing through the ranks."
    ),

    apprentice_role_id: (
        "This role represents members who have demonstrated consistent "
        "participation and a willingness to help others in the community.\n\n"
        "Apprentices play an important role in maintaining a welcoming and "
        "knowledge-sharing environment.\n\n### Apprentice Powers\n\n"
        "You can now nominate other members of the server for **Boot role**.\n"
        "Use `/nominate` command to nominate a member in the server.\n"
        "Make sure you nominate only the deserving candidates, so they get the visibility.\n\n"
        "Keep up the great work!"
    ),

    fellow_role_id: (
        "This role is given to members who have earned strong recognition "
        "from the community for their knowledge, contributions, and support "
        "for others.\n\n### Fellow Powers\n\n"
        "You can nominate other members of the server for **Apprentice role** or below.\n"
        "Use `/nominate` command to nominate a member in the server.\n\n"
        "Thank you for setting a positive example. Your presence helps guide "
        "and improve the community."
    )
}

automatically_assigned_roles = {
    active_role_id: (
        "Thank you for staying active and engaging in the server.\n\n"
        "Next milestone: **Active+**"
    ),
    active_plus_role_id: (
        "Your activity and engagement place you among the server's top contributors.\n"
        "We appreciate the energy you bring to the community\n"
        "Next milestone: Is there one?"
    ),
    chronically_online_role_id: (
        "Congratulations... I guess? Your message count has breached the event horizon.\n"
        "You are now officially certified as **Chronically Online**.\n"
        "Your eyes have adapted to pure dark mode. Blue light filters have no power here.\n\n"
        "Next milestone: **The Ultimate Threat.**"
    ),
    needs_to_touch_grass_role_id: (
        "🚨 EMERGENCY EVENT DETECTED 🚨\n"
        "You have unlocked the final hidden evolution: **Needs to Touch Grass**.\n"
        "The server database is begging you to close Discord. The turtles are worried.\n"
        "Please step outside, locate a photosynthetic plant organism, and make physical skin contact with it immediately.\n\n"
        "Next milestone: **Seriously, go outside.**"
    )
}


# Emoji IDs
mod_mail_emoji_id = 1546914838733791362
event_emoji_id = 611403448750964746
bug_emoji_id = 1546914803988177077
verified_emoji_id = 610713784268357632
upvote_emoji_id = 741202481090002994
staff_application_emoji_id = 1485325243043283075

# mod_mail_emoji_id = 1546903141671239680
# bug_emoji_id = 1546906168742518854

# Auto mod rulesets
racial_and_transphobic_rule_id = 1461221874540347577
discord_advertisement_rule_id = 1443953991217057843

# Badges
partner = "<:partner:753957703155449916>"
staff = "<:staff:753957681336942673>"
nitro = "<:nitro:753957661912989747>"
hs_bal = "<:balance:753957264460873728>"
hs_bril = "<:brilliance:753957311537479750>"
hs_brav = "<:bravery:753957296475996234>"
hs_ev = "<:events:753957640069185637>"
verified_bot_dev = "<:dev:753957609328869384>"
bg_1 = "<:bug1:753957385844031538>"
bg_2 = "<:bug2:753957425664753754>"
ear_supp = "<:early:753957626097696888>"

# Emotes
idle = "🌙"
game_emoji = "🎮"
online = "<:online:753999406562410536>"
offline = "<:offline:753999424446922782>"
dnd = "<:dnd:753999445728952503>"
spotify_emoji = "<:spotify:754238046123196467>"
pin_emoji = "<:pinunread:754233175244537976>"
user_emoji = "<:user:754234411922227250>"
git_start_emoji = "<:git_star:758616139646763064>"
git_fork_emoji = "<:git_fork:758616130780004362>"
git_commit_emoji = "<:git_commit:758616123590574090>"
git_repo_emoji = "<:repo:758616137977561119>"
success_emoji = "<:success:1524706961172463646>"
info_emoji = "<:info:1546914814796763166>"
failure_emoji = "<:failure:1524706674550767706>"
warning_low_emoji = "<:warninglow:1524706548301959199>"
warning_high_emoji = "<:warninghigh:1524706535073120297>"
poker_face_emoji = "<:pokerface:689918352512254035>"
stonks_emoji = "<:stonks:689918347596660824>"
sadcat_emoji = "<:sadcat:689913330516754584>"

# Icons
google_icon = "https://www.freepnglogos.com/uploads/google-logo-png/" \
              "google-logo-png-google-icon-logo-png-transparent-svg-vector-bie-supply-14.png"
stack_overflow_icon = "https://cdn2.iconfinder.com/data/icons/social-icons-color/512/stackoverflow-512.png"


# Special
tortoise_developers = (612349409736392928, 529290942306320384, 1157899519422378034)

# Embeds are not monospaced so we need to use spaces to make different lines "align"
# But discord doesn't like spaces and strips them down.
# Using a combination of zero width space + regular space solves stripping problem.
embed_space = "\u200b "


# Discord constants
everyone_mention = "@​everyone"
here_mention = "@​here"

# After this is exceeded the link to tortoise paste service should be sent
max_message_length = 1000

# Tortoise brand
default_color = 0xffb101


class Infraction(Enum):
    _settings_ = NoAlias

    warning = Color.gold()
    kick = Color.gold()
    ban = Color.red()
    timeout = Color.orange()

# These are allowed and will not get auto-deleted by bot nor will they get a paste link.
allowed_file_extensions = (
    # Audio
    "aif",
    "mid", "midi",
    "mp3",
    "mpa",
    "ogg",
    "wav",
    "wma",

    # Images
    "bmp",
    "gif",
    "jpg", "jpeg",
    "png",
    "svg",
    "tif", "tiff",
    "webp",

    # Video
    "3g2",
    "3gp",
    "avi",
    "h264",
    "mkv",
    "mov", "qt",
    "mp4", "m4v",
    "mpg", "m2v", "mp2", "mpe", "mpeg", "mpv",
    "ogv",
    "webm",
    "wmv",

    # Document/misc
    "doc", "docx",
    "odt",
    "pdf",
    "rtf",
    "txt",
)

rate_limit_minutes = 10

defcon_lockable_channels = [
    general_channel_id,
    leetcode_channel_id,
    bot_cmd_channel_id,
    project_showcase_channel_id,
    resources_channel_id,
    challenge_discussion_channel_id,
    challenge_submission_channel_id
]

RULES = {
    1: {
        "title": "Discord TOS",
        "text": "Follow the Discord Community Guidelines and Terms of Service.",
        "aliases": ["tos", "guidelines", "terms"],
    },
    2: {
        "title": "Just ask",
        "text": "Do not ask to ask. Just ask!",
        "aliases": ["ask"],
    },
    3: {
        "title": "Respect everyone",
        "text": "Do not use Racist, Homophobic or Transphobic slurs that are abusive. "
                "Respect all members and staffs.",
        "aliases": ["racial", "homophobic", "homo", "slurs", "slur"],
    },
    4: {
        "title": "No advertisement",
        "text": "No unapproved advertising, including requests for paid work. "
                "Projects can be showcased in #project-showcase.",
        "aliases": ["ad", "advertise", "advertising", "projects", "project", "paid work"],
    },
    5: {
        "title": "No selfbots",
        "text": "Do not spam or use self-bots inside the server.",
        "aliases": ["spam", "selfbot"],
    },
    6: {
        "title": "No pings",
        "text": "Do not try to mention @everyone, or unnecessarily ping members/roles. "
                "You should mostly never ping members who are not present in the current discussion "
                "unless they’ve previously given you permission.",
        "aliases": ["mention", "mentions", "ping", "noping"],
    },
    7: {
        "title": "Contacting staff",
        "text": "Don't mention staff unless its an emergency or serious rule break. "
                "If you wish to ask them a question use mod mail (DM @Tortoise Bot)",
        "aliases": ["staff", "emergency", "modmail", "mail"],
    },
    8: {
        "title": "Relevancy",
        "text": "Keep discussions relevant to channel topics.",
        "aliases": ["relevant", "discussion", "discussions", "channels", "topic"],
    },
    9: {
        "title": "No NSFW",
        "text": "No NSFW contents are allowed inside the server. Use of them will result in an Infraction.",
        "aliases": ["nsfw"],
    },
    10: {
        "title": "No DM",
        "text": "Do not DM members without getting their permission first. "
                "If you want coding help, use the help channels.",
        "aliases": ["dm", "nodm"],
    },
}

introduction_format = """
```
Name / Nickname:
Location:
What you do:
Interests: 
Hobbies:
What you’re looking for here:
Fun fact (optional):
```
"""