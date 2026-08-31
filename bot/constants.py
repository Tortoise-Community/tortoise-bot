from aenum import Enum, NoAlias

from discord import Color
from decouple import config


tortoise_guild_id = 577192344529404154
ban_appeal_server_id = 1464188109364396169
website_url = "https://www.tyxc.org/"
privacy_url = "https://www.tyxc.org/privacy"
rules_url = "https://www.tyxc.org/rules"
github_repo_link = "https://github.com/Tortoise-Community/Tortoise-BOT"
line_img_url = "https://www.animatedimages.org/data/media/562/animated-line-image-0015.gif"
infraction_img_url = "https://www.animatedimages.org/data/media/562/animated-line-image-0538.gif"
banner_url = "https://lairesit.sirv.com/Tortoise/banner.jpg"
info_banner_url = "https://lairesit.sirv.com/Tortoise/tortoise-info.jpg"
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
announcements_channel_id = 578197131526144024

# Log Channel IDs
deterrence_log_channel_id = 1521908452837036104
bot_log_channel_id = 1521907692745265343
message_log_channel_id = 1521908191858917477
user_log_channel_id = 1521910276272816138
team_log_channel_id = 1521951592189001768
challenge_log_channel_id = 1521954677770420245
role_progression_log_channel_id = 1522592723331190965

mod_mail_log_channel_id = bot_log_channel_id
bug_reports_log_channel_id = bot_log_channel_id
code_submissions_log_channel_id = bot_log_channel_id

bot_dev_channel_id = 692851221223964822
general_channel_id = 577192344533598472
today_i_did_channel_id = 1527705624073474169
resume_roasting_channel = 1507008205232935122
staff_channel_id = 580809054067097600
rules_channel_id = 738986778396196935

# Tortoise Guild channels
leetcode_channel_id = 726403782740541470
programming_channel_id = 577195845376802826
opensource_channel_id = 581483558410125372
discussion_voice_channel_id = 1457383811406102762
bot_cmd_channel_id = 581726653710073858
focus_music_channel_id = 1515440479636820169
project_showcase_channel_id = 581156991557304330
resources_channel_id = 577195878620725251
challenge_submission_channel_id = 780842875901575228
challenge_discussion_channel_id = 781129674860003336
challenges_channel_id = 780841435712716800
challenge_logs_public_channel_id = 1524682332005728257
bait_channel_id = 1461666781612740750
introduction_channel_id = 1487413734056923236
join_a_team_channel_id = 1489264049983197246

# Team channels
team_plan_channel_id = 1498315759506686115
team_forum_channel_id = 1498316149035896874
team_chat_channel_id = 1497109933001543740
team_discussion_channel_id = 1506559418555174932
team_voice_channel_id = 1497109934029144074

# Marketplace channels
job_board_channel_id = 1472363495608815852
dev_board_channel_id = 1472363116296933448

# Ban Appeal Channels
ban_appeal_channel_id = 1464188530396893336

# Message id
teams_dashboard_message_id = 1489264468168016054

# Roles
muted_role_id = 707007421066772530
verified_role_id = 599647985198039050
trusted_role_id = 703657957438652476
moderator_role_id = 577368219875278849
admin_role_id = 577196762691928065
new_member_role_id = 1441848294828670978
challenger_role_id = 781210603997757471
wizard_role_id = 1472794198053879809
contributor_role_id = 649630145304461312
accepting_team_invites_role_id = 1488893079053144184
jr_moderator_role_id = 1510378507450974351


active_role_id = 1482843939978481889
active_plus_role_id = 1482844032488050921
chronically_online_role_id = 1511005709653770242
needs_to_touch_grass_role_id = 1511006001623470120
boot_role_id = 1472793802740596839
apprentice_role_id = 1472725760723648522
fellow_role_id = 1472793939630358731
elite_role_id = 1515787455184240722

rules_emoji_id = 1534128065104576522
roles_emoji_id = 1534127242081206322
channels_emoji_id = 1534124243640385536

mod_mail_ping_role_id = 1493890424518086807
bot_trap_role_id = 1505158956811685908

promotable_roles = {
    wizard_role_id:      "You are currently **#1 on the Challenges Leaderboard**, placing you at the top "
                         "of the server's competitive coding ranks.\n\n"
                         "This is the **highest non-staff role** and represents exceptional skill, "
                         "consistency, and mastery in solving challenges.\n\n"
                         "Keep pushing the limits and setting the bar for others!",

    trusted_role_id:  "This role is given to members who have been part of the community for a long "
                         "time and have consistently shown they can be trusted.\n\n"
                         "This is the **2nd highest non-staff role** and it's exempt "
                      "from certain auto-mod restrictions.\n\n"
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
    elite_role_id:        "This role is given to appreciate and honor the **most experienced person on this server**.\n"
                          "\nThis is now the **highest non-staff role** and stands as a testament to your exceptional "
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
        "Please step outside, locate a photosynthetic plant organism, "
        "and make physical skin contact with it immediately.\n\n"
        "Next milestone: **Seriously, go outside.**"
    )
}


# Emoji IDs
mod_mail_emoji_id = 706195614857297970
event_emoji_id = 611403448750964746
bug_emoji_id = 723274927968354364
verified_emoji_id = 610713784268357632
upvote_emoji_id = 741202481090002994
staff_application_emoji_id = 1485325243043283075

# Challenge system
challenge_supported_languages = (
    ("Python", "python"),
    ("JavaScript", "javascript"),
    ("C++", "cpp"),
    ("Java", "java"),
)
challenge_supported_language_values = tuple(
    language_value for _, language_value in challenge_supported_languages
)
challenge_default_points = 100
challenge_optimal_solution_bonus = 50
challenge_test_reveal_cost = 50
challenge_default_max_tests = 30
challenge_problem_title_min_length = 2
challenge_problem_title_max_length = 100
challenge_autocomplete_choice_max_length = 100
challenge_statement_max_bytes = 100_000
challenge_boilerplate_max_bytes = 100_000
challenge_submission_max_bytes = 100_000
challenge_tests_max_bytes = 500_000
challenge_modal_submission_max_length = 4000
challenge_execution_api_default_url = "http://127.0.0.1:8000/execute"
challenge_execution_api_default_timeout_ms = 15000
challenge_pipeline_smoke_tests = {
    "python": {
        "name": "Python",
        "solution": "def add(a, b):\n    return a + b\n",
        "boilerplate": "{{SOLUTION}}\na, b = map(int, input().split())\nprint(add(a, b))\n",
    },
    "javascript": {
        "name": "JavaScript",
        "solution": "function add(a, b) {\n  return a + b;\n}\n",
        "boilerplate": (
            "{{SOLUTION}}\n"
            "const fs = require('fs');\n"
            "const [a, b] = fs.readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
            "console.log(add(a, b));\n"
        ),
    },
    "cpp": {
        "name": "C++",
        "solution": "int add(int a, int b) {\n    return a + b;\n}\n",
        "boilerplate": (
            "#include <iostream>\n"
            "using namespace std;\n"
            "{{SOLUTION}}\n"
            "int main() {\n"
            "    int a, b;\n"
            "    cin >> a >> b;\n"
            "    cout << add(a, b);\n"
            "    return 0;\n"
            "}\n"
        ),
    },
    "java": {
        "name": "Java",
        "solution": "public static int add(int a, int b) {\n    return a + b;\n}\n",
        "boilerplate": (
            "public class Main {\n"
            "    {{SOLUTION}}\n"
            "    public static void main(String[] args) throws Exception {\n"
            "        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n"
            "        String[] parts = br.readLine().trim().split(\"\\\\s+\");\n"
            "        System.out.print(add(Integer.parseInt(parts[0]), Integer.parseInt(parts[1])));\n"
            "    }\n"
            "}\n"
        ),
    },
}
challenge_pipeline_smoke_test_cases = (
    ("Smoke Test 1", "2 3\n", "5"),
    ("Smoke Test 2", "-10 7\n", "-3"),
)

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
success_emoji = "<:success:1522613769094693048>"
failure_emoji = "<:failure:1522613811033538681>"
warning_low_emoji = "<:warninglow:1524707529416769596>"
warning_high_emoji = "<:warninghigh:1524707516636991528>"
poker_face_emoji = "<:pokerface:689918352512254035>"
stonks_emoji = "<:stonks:689918347596660824>"
sadcat_emoji = "<:sadcat:689913330516754584>"

# Icons
google_icon = "https://www.freepnglogos.com/uploads/google-logo-png/" \
              "google-logo-png-google-icon-logo-png-transparent-svg-vector-bie-supply-14.png"
stack_overflow_icon = "https://cdn2.iconfinder.com/data/icons/social-icons-color/512/stackoverflow-512.png"


# Special
tortoise_developers = (197918569894379520, 612349409736392928)

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


DEVELOPMENT_MODE = config("DEVELOPMENT_MODE", cast=bool, default=False)

if DEVELOPMENT_MODE:
    from dev.constants import * # noqa

channel_description_info = (
    "- 🌟 **Getting Started**\n"
    f"  - **<#{introduction_channel_id}>**: Introduce yourself here, so like minded people can find you.\n"
    f"  - **<#{join_a_team_channel_id}>**: Join a DSA team, view all teams using the channel utility.\n\n"
    "- 💭 **General**\n"
    f"  - **<#{general_channel_id}>**: Casual conversations and main community chat.\n"
    f"  - **<#{today_i_did_channel_id}>**: Log your daily progress or anything productive you did that day.\n"
    f"  - **<#{resume_roasting_channel}>**: Post your resume here and get roasted!\n"
    f"  - **<#{project_showcase_channel_id}>**: Showcase your project here that you are really proud of.\n"
    f"  - **<#{bot_cmd_channel_id}>**: Use all bots and bot commands here, both Tortoise and Runtime.\n"
    f"  - **<#{focus_music_channel_id}>**: Listen to lo-fi beats and focus music 24/7 365.\n\n"
    "- ❓ **Help & discussion**\n"
    f"  - **<#{leetcode_channel_id}>**: All discussions related to Leetcode/DS-Algo and Competitive Programming.\n"
    f"  - **<#{programming_channel_id}>**: General programming discussions, All languages welcome.\n"
    f"  - **<#{opensource_channel_id}>**: Discussions about opensource projects, Homelab and Self-hosting.\n"
    f"  - **<#{discussion_voice_channel_id}>**: Common voice channel for all topics.\n\n"
    "- 👨‍💻 **Leetcode challenges**\n"
    f"  - **<#{challenges_channel_id}>**: Weekly Leetcode Challenge will be posted here!\n"
    f"  - **<#{challenge_log_channel_id}>**: Challenge auto-submission logs will be visible here.\n"
    f"  - **<#{challenge_submission_channel_id}>**: Post your challenge solutions here so others can refer it.\n"
    f"  - **<#{challenge_discussion_channel_id}>**: Discussion related to current or previous challenges.\n\n"
    "- 🎓 **DSA Prep Team - Tortoise**\n"
    f"  - **<#{team_plan_channel_id}>**: Weekly team plan posted here with list of problems for you to solve daily.\n"
    f"  - **<#{team_forum_channel_id}>**: Post your daily solutions in the designated forum channels.\n"
    f"  - **<#{team_chat_channel_id}>**: All casual conversation with team members happens here.\n"
    f"  - **<#{team_discussion_channel_id}>**: Discussions related to daily problems, approaches and patterns.\n"
    f"  - **<#{team_voice_channel_id}>**: Common voice channel for all team activity.\n\n"
    "- 💳 **Developer Marketplace**\n"
    f"  - **<#{job_board_channel_id}>**: Use this channel for posting job/paid work requests.\n"
    f"  - **<#{dev_board_channel_id}>**: Use this channel if you are a developer / service provider "
    f"who want's to advertise their service. \n\n"
)


role_description_info = (
    "# Server Roles\n"
    "Roles in this server recognize activity, contribution, and trust within the community. "
    "Some roles are earned automatically through participation, some are awarded through "
    "community nominations, and a few are granted directly for special achievements.\n\n"

    "## Activity Roles\n"
    "Earn these automatically by being active in chat.\n"
    f"- <@&{active_role_id}>: marks you as an active community member.\n"
    f"- <@&{active_plus_role_id}>: Shows consistent participation in discussions.\n"
    f"- <@&{chronically_online_role_id}>: Your message count has breached the event horizon.\n"
    f"- <@&{needs_to_touch_grass_role_id}>: The final hidden evolution. Please step outside.\n\n"

    "## Community Progression Roles\n"
    "Awarded through community nominations (`/nominate`).\n"
    f"- <@&{boot_role_id}> 👦🏻: **Boot** - Requires <@&{active_role_id}>. "
    f"Nominated by 2 Apprentices, 1 Fellow, or 1 Mod.\n"
    f"- <@&{apprentice_role_id}> 👨‍💻: **Apprentice** - Requires Boot. Nominated by 2 Fellows or 1 Mod.\n"
    f"- <@&{fellow_role_id}> 👨🏻‍🎓: **Fellow** - Requires Apprentice. Nominated by 2 Mods.\n\n"

    "## Special Recognition Roles\n"
    "Awarded directly by staff for notable achievements.\n"
    f"- <@&{wizard_role_id}> ⚡︎: Awarded to the member currently #1 on the challenges leaderboard.\n"
    f"- <@&{trusted_role_id}> ✔: Given to long-standing members demonstrating reliability.\n"
    f"- <@&{contributor_role_id}> 🛠️: Recognizes contributions to our GitHub repositories."
)
