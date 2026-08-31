import io
import json
import logging
import time
from typing import Optional

import discord
from decouple import config
from discord import app_commands
from discord.ext import commands

from bot.constants import (
    challenge_boilerplate_max_bytes,
    challenge_default_max_tests,
    challenge_default_points,
    challenge_execution_api_default_timeout_ms,
    challenge_execution_api_default_url,
    challenge_modal_submission_max_length,
    challenge_optimal_solution_bonus,
    challenge_pipeline_smoke_test_cases,
    challenge_pipeline_smoke_tests,
    challenge_problem_title_max_length,
    challenge_problem_title_min_length,
    challenge_statement_max_bytes,
    challenge_supported_languages,
    challenge_test_reveal_cost,
    challenge_tests_max_bytes,
    challenge_autocomplete_choice_max_length,
    challenge_log_channel_id,
    success_emoji,
    failure_emoji, challenge_logs_public_channel_id,
)
from bot.utils.checks import check_if_tortoise_mod, check_if_tortoise_staff
from bot.utils.challenge import (
    CHALLENGE_ATTACHMENT_FILENAMES,
    ExecutionApiClient,
    Problem,
    TestCase,
    arrange_challenge_attachments,
    clean_slug,
    download_text,
    judge_submission,
    parse_test_files,
    positive_integer_env,
    slug_from_title,
)
from bot.utils.embed_handler import (
    build_rules_embed,
    failure,
    info,
    success,
    warning,
)
from bot.utils.exceptions import TortoiseStaffCheckFailure


logger = logging.getLogger(__name__)

CHALLENGE_INFO_CHOICES = [
    app_commands.Choice(name="View a problem statement", value="view"),
    app_commands.Choice(name="Submit a problem statement", value="submit"),
]

LANGUAGE_CHOICES = [
    app_commands.Choice(name=name, value=value)
    for name, value in challenge_supported_languages
]

PIPELINE_LANGUAGE_CHOICES = [
    app_commands.Choice(name="All languages", value="all"),
    *LANGUAGE_CHOICES,
]


def submission_log_view(
    submission_id: int,
    *,
    moderator: bool = False,
    optimal_awarded: bool = False,
) -> discord.ui.View:
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(
        label="See solution",
        style=discord.ButtonStyle.primary,
        emoji="👀",
        custom_id=f"challenge_solution:{submission_id}",
    ))
    if moderator:
        view.add_item(discord.ui.Button(
            label="Optimal solution (+50)",
            style=discord.ButtonStyle.success,
            emoji="✅",
            custom_id=f"challenge_optimal:{submission_id}",
            disabled=optimal_awarded,
        ))
    return view


async def challenge_problem_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    cog = interaction.client.get_cog("Challenges")
    if cog is None:
        return []
    return await cog.autocomplete_problem(interaction, current)


class SolutionSubmissionModal(discord.ui.Modal):
    def __init__(
        self,
        *,
        cog: "Challenges",
        problem_slug: str,
        language_value: str,
        language_name: str,
    ):
        super().__init__(title="Submit solution")
        self.cog = cog
        self.problem_slug = problem_slug
        self.language_value = language_value
        self.language_name = language_name
        self.solution = discord.ui.TextInput(
            label="Function implementation",
            style=discord.TextStyle.paragraph,
            placeholder="Paste only the function implementation here.",
            required=True,
            max_length=challenge_modal_submission_max_length,
        )
        self.add_item(self.solution)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.cog.process_submission(
            interaction=interaction,
            problem_slug=self.problem_slug,
            language_value=self.language_value,
            language_name=self.language_name,
            submitted_code=str(self.solution.value),
        )


class RevealTestsConfirmView(discord.ui.View):
    def __init__(self, *, cog: "Challenges", user_id: int, problem: Problem):
        super().__init__(timeout=120)
        self.cog = cog
        self.user_id = user_id
        self.problem = problem
        self.confirmation_step = 1

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True

        await interaction.response.send_message(
            embed=failure("Only the user who requested the reveal can confirm it."),
            ephemeral=True,
        )
        return False

    @discord.ui.button(label="Reveal test cases", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.confirmation_step == 1:
            self.confirmation_step = 2
            button.label = "Yes, reveal and deduct points"
            button.style = discord.ButtonStyle.danger
            await interaction.response.edit_message(
                embed=warning(
                    "Second confirmation required.\n\n"
                    f"Revealing these hidden test cases costs **{challenge_test_reveal_cost} points** the first time "
                    "you reveal this problem. Press the red button again to continue."
                ),
                view=self,
            )
            return

        self.disable_all_buttons()
        await interaction.response.edit_message(view=self)
        await self.cog.reveal_tests_for_user(interaction, self.problem)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.disable_all_buttons()
        await interaction.response.edit_message(embed=warning("Test case reveal cancelled."), view=self)


class Challenges(commands.Cog):
    """Automated coding challenges powered by Hermes Engine."""

    challenge_group = app_commands.Group(
        name="challenge",
        description="Coding challenge commands.",
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.challenge_manager = bot.challenge_manager
        self.max_tests = challenge_default_max_tests
        self.hermes = ExecutionApiClient(
            url=config("EXECUTION_API_URL", default=challenge_execution_api_default_url),
            api_token=config("EXECUTION_API_KEY", default=None),
            timeout_seconds=positive_integer_env(
                "EXECUTION_API_TIMEOUT_MS",
                challenge_execution_api_default_timeout_ms,
            ) / 1000,
        )
        self._challenge_log_channel = None
        self._challenge_log_public_channel = None

    @property
    def challenge_log_channel(self) -> discord.TextChannel:
        if self._challenge_log_channel is None:
            self._challenge_log_channel = self.bot.get_channel(challenge_log_channel_id)
        return self._challenge_log_channel

    @property
    def challenge_log_public_channel(self) -> discord.TextChannel:
        if self._challenge_log_public_channel is None:
            self._challenge_log_public_channel = self.bot.get_channel(challenge_logs_public_channel_id)
        return self._challenge_log_public_channel

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component or not interaction.data:
            return

        custom_id = interaction.data.get("custom_id", "")
        if not custom_id.startswith(("challenge_solution:", "challenge_optimal:")):
            return

        try:
            submission_id = int(custom_id.rsplit(":", 1)[1])
        except (IndexError, ValueError):
            return

        if custom_id.startswith("challenge_solution:"):
            await interaction.response.defer(ephemeral=True)
            submission = await self.challenge_manager.get_submission_solution(submission_id)
            if submission is None:
                await interaction.followup.send(
                    embed=failure("This accepted solution is no longer available."),
                    ephemeral=True,
                )
                return

            file = discord.File(
                io.BytesIO(submission["solution"].encode("utf-8")),
                filename=f"{submission['problem_slug']}-{submission['language']}-solution.txt",
                spoiler=True,
            )
            await interaction.followup.send(
                content=f"Accepted solution from <@{submission['user_id']}>.",
                file=file,
                ephemeral=True,
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        try:
            await check_if_tortoise_mod(interaction)
        except TortoiseStaffCheckFailure:
            await interaction.response.send_message(
                embed=failure("Only moderators can award the optimal-solution bonus."),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        status, user_id, total_points = await self.challenge_manager.award_optimal_solution(
            submission_id,
            interaction.user.id,
        )
        if status != "awarded":
            message = {
                "missing": "Submission not found.",
                "not_accepted": "Only accepted submissions can receive this bonus.",
                "already_awarded": "The optimal-solution bonus was already awarded.",
            }[status]
            await interaction.followup.send(embed=warning(message), ephemeral=True)
            return

        if interaction.message and interaction.message.embeds:
            embed = discord.Embed.from_dict(interaction.message.embeds[0].to_dict())
            embed.add_field(
                name="Optimal solution",
                value=f"+{challenge_optimal_solution_bonus} points awarded by {interaction.user.mention}",
                inline=False,
            )
            await interaction.message.edit(
                embed=embed,
                view=submission_log_view(submission_id, moderator=True, optimal_awarded=True),
            )

        await interaction.followup.send(
            embed=success(
                f"Awarded <@{user_id}> **{challenge_optimal_solution_bonus} points**. "
                f"New total: **{total_points}**."
            ),
            ephemeral=True,
        )

    @challenge_group.command(name="rules", description="Show challenge guidelines.")
    async def challenge_rules(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=build_rules_embed(self.bot.user))

    @challenge_group.command(name="info", description="Show how coding challenges work.")
    @app_commands.choices(action=CHALLENGE_INFO_CHOICES)
    @app_commands.describe(action="Choose the guide to display.")
    async def challenge_info(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
    ):
        embed = discord.Embed(title=action.name, color=discord.Color.green())
        embed.set_image(url=f"https://lairesit.sirv.com/Tortoise/{action.value}.gif")
        await interaction.response.send_message(
            embed=embed,
            ephemeral=False,
        )

    @challenge_group.command(name="add-points", description="Give points to a user.")
    @app_commands.check(check_if_tortoise_staff)
    @app_commands.describe(
        member="Member receiving points.",
        amount="Number of points to add.",
        reason="Optional reason shown in the log and DM.",
        silent="Whether to skip DMing the member.",
    )
    async def challenge_add_points(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: app_commands.Range[int, 1, 10_000],
        reason: Optional[str] = None,
        silent: bool = False,
    ):
        await interaction.response.defer(ephemeral=True)

        new_total = await self.bot.points_manager.add_points(interaction.guild.id, member.id, amount)
        desc = (
            f"{member.mention} received **{amount}** points.\n"
            f"New total: **{new_total}** points."
        )
        dm_desc = (
            f"You were awarded **{amount}** points.\n"
            f"New total: **{new_total}** points."
        )
        if reason:
            desc += f"\n\n**Reason:** {reason}"
            dm_desc += f"\n\n**Comment:** {reason}"

        await self.challenge_log_channel.send(
            embed=info(desc, self.bot.user, "Points Awarded", f"Given by {interaction.user.display_name}")
        )

        if not silent:
            try:
                await member.send(embed=info(dm_desc, self.bot.user, "Congratulations 🌟"))
            except discord.Forbidden:
                pass

        await interaction.followup.send(
            embed=success(f"{amount} points awarded. New total: {new_total}"),
            ephemeral=True,
        )

    @challenge_group.command(name="remove-points", description="Remove points from a user.")
    @app_commands.check(check_if_tortoise_staff)
    @app_commands.describe(
        member="Member losing points.",
        amount="Number of points to remove.",
        silent="Whether to skip DMing the member.",
    )
    async def challenge_remove_points(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: app_commands.Range[int, 1, 10_000],
        silent: bool = True,
    ):
        await interaction.response.defer(ephemeral=True)

        new_total = await self.bot.points_manager.remove_points(interaction.guild.id, member.id, amount)

        await self.challenge_log_channel.send(
            embed=info(
                (
                    f"**{amount}** points removed from {member.mention}\n"
                    f"New total: **{new_total}** points."
                ),
                self.bot.user,
                "Points Removed",
                f"Removed by: {interaction.user.display_name}",
            )
        )

        if not silent:
            try:
                await member.send(
                    embed=info(
                        (
                            f"**{amount}** points removed\n"
                            f"New total: **{new_total}** points."
                        ),
                        self.bot.user,
                        "Points Removed ;(",
                    )
                )
            except discord.Forbidden:
                pass

        await interaction.followup.send(
            embed=success(f"{amount} points removed. New total: {new_total}"),
            ephemeral=True,
        )

    @challenge_group.command(name="leaderboard", description="Show the points leaderboard.")
    async def challenge_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        entries = await self.bot.points_manager.get_leaderboard(
            interaction.guild.id,
            min_points=1,
            limit=10,
        )

        if not entries:
            await interaction.followup.send(embed=warning("No one has any points yet."), ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🏆 {interaction.guild.name} Leaderboard",
            color=discord.Color.gold(),
        )
        medals = ["🥇", "🥈", "🥉"]
        for idx, (user_id, points) in enumerate(entries, start=1):
            member = interaction.guild.get_member(user_id)
            name = member.mention if member else f"<@{user_id}>"
            rank = medals[idx - 1] if idx <= 3 else f"#{idx}"
            embed.add_field(
                name=f"**{points}** points",
                value=f"{rank} {name}",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @challenge_group.command(name="points", description="Check points.")
    @app_commands.describe(member="Member to check. Defaults to you.")
    async def challenge_points(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None,
    ):
        target = member or interaction.user
        pts = await self.bot.points_manager.get_points(interaction.guild.id, target.id)
        await interaction.response.send_message(
            embed=info(f"{target.mention} has **{pts}** points.", self.bot.user, "Points"),
            ephemeral=True,
        )

    @challenge_group.command(name="add", description="Create or update a coding problem.")
    @app_commands.check(check_if_tortoise_staff)
    @app_commands.describe(
        title="Problem title.",
        bulk="True to upload all seven files in one follow-up message.",
        statement="Markdown/text file containing the full problem statement.",
        python_boilerplate="Python driver/starter file containing {{SOLUTION}}.",
        javascript_boilerplate="JavaScript driver/starter file containing {{SOLUTION}}.",
        cpp_boilerplate="C++ driver/starter file containing {{SOLUTION}}.",
        java_boilerplate="Java driver/starter file containing {{SOLUTION}}.",
        test_inputs="JSON array of private input strings.",
        expected_outputs="JSON array of expected output strings.",
    )
    async def challenge_add(
        self,
        interaction: discord.Interaction,
        title: app_commands.Range[str, challenge_problem_title_min_length, challenge_problem_title_max_length],
        bulk: bool,
        statement: Optional[discord.Attachment] = None,
        python_boilerplate: Optional[discord.Attachment] = None,
        javascript_boilerplate: Optional[discord.Attachment] = None,
        cpp_boilerplate: Optional[discord.Attachment] = None,
        java_boilerplate: Optional[discord.Attachment] = None,
        test_inputs: Optional[discord.Attachment] = None,
        expected_outputs: Optional[discord.Attachment] = None,
    ):
        try:
            if bulk:
                filenames = "\n".join(f"`{name}`" for name in CHALLENGE_ATTACHMENT_FILENAMES)
                await interaction.response.send_message(
                    embed=info(
                        "Send one message in this channel with these seven files attached:\n\n"
                        f"{filenames}\n\nThis upload expires in 3 minutes.",
                        interaction.user,
                    ),
                    ephemeral=True,
                )

                def is_upload(message: discord.Message) -> bool:
                    return (
                        message.author.id == interaction.user.id
                        and message.channel.id == interaction.channel_id
                        and message.guild is not None
                        and message.guild.id == interaction.guild_id
                    )

                message = await self.bot.wait_for("message", check=is_upload, timeout=180)
                attachments = arrange_challenge_attachments(message.attachments)
            else:
                await interaction.response.defer(ephemeral=True)
                attachments = {
                    "statement.md": statement,
                    "python-boilerplate.py": python_boilerplate,
                    "javascript-boilerplate.js": javascript_boilerplate,
                    "cpp-boilerplate.cpp": cpp_boilerplate,
                    "java-boilerplate.java": java_boilerplate,
                    "test-inputs.json": test_inputs,
                    "expected-outputs.json": expected_outputs,
                }
                missing = [name for name, attachment in attachments.items() if attachment is None]
                if missing:
                    raise ValueError(f"Manual mode requires: {', '.join(missing)}.")

            tests = await self._save_problem(interaction, str(title), attachments)
        except TimeoutError:
            await interaction.followup.send(embed=warning("Bulk challenge upload timed out."), ephemeral=True)
            return
        except Exception as exc:
            logger.exception("Could not add challenge problem")
            await interaction.followup.send(embed=failure(f"Could not save problem: {exc}"), ephemeral=True)
            return

        await interaction.followup.send(
            embed=success(
                f"Saved **{title}** for Python, JavaScript, C++, and Java "
                f"with **{len(tests)}** hidden test(s). A full pass awards **{challenge_default_points} points**."
            ),
            ephemeral=True,
        )

    async def _save_problem(
        self,
        interaction: discord.Interaction,
        title: str,
        attachments: dict[str, discord.Attachment],
    ) -> list[TestCase]:
        problem_statement = await download_text(
            attachments["statement.md"], max_bytes=challenge_statement_max_bytes
        )
        if not problem_statement.strip():
            raise ValueError("problem statement cannot be empty.")

        boilerplates = {
            "python": await download_text(
                attachments["python-boilerplate.py"], max_bytes=challenge_boilerplate_max_bytes
            ),
            "javascript": await download_text(
                attachments["javascript-boilerplate.js"], max_bytes=challenge_boilerplate_max_bytes
            ),
            "cpp": await download_text(
                attachments["cpp-boilerplate.cpp"], max_bytes=challenge_boilerplate_max_bytes
            ),
            "java": await download_text(
                attachments["java-boilerplate.java"], max_bytes=challenge_boilerplate_max_bytes
            ),
        }
        for language, boilerplate in boilerplates.items():
            if "{{SOLUTION}}" not in boilerplate:
                raise ValueError(f"{language} boilerplate must contain a {{SOLUTION}} marker.")

        tests = parse_test_files(
            await download_text(attachments["test-inputs.json"], max_bytes=challenge_tests_max_bytes),
            await download_text(attachments["expected-outputs.json"], max_bytes=challenge_tests_max_bytes),
            self.max_tests,
        )
        await self.challenge_manager.upsert_problem(
            guild_id=interaction.guild_id,
            slug=slug_from_title(title),
            title=title,
            statement=problem_statement,
            boilerplates=boilerplates,
            tests=tests,
            created_by=interaction.user.id,
        )
        return tests

    @challenge_group.command(name="remove", description="Deactivate a coding problem.")
    @app_commands.check(check_if_tortoise_staff)
    @app_commands.autocomplete(problem=challenge_problem_autocomplete)
    @app_commands.describe(problem="Problem title.")
    async def challenge_remove(self, interaction: discord.Interaction, problem: str):
        await interaction.response.defer(ephemeral=True)

        removed = await self.challenge_manager.deactivate_problem(interaction.guild_id, clean_slug(problem))
        if not removed:
            await interaction.followup.send(embed=failure("Problem not found."), ephemeral=True)
            return

        await interaction.followup.send(embed=success(f"Removed problem `{problem}`."), ephemeral=True)

    @challenge_group.command(name="view", description="List problems or download a selected problem starter.")
    @app_commands.autocomplete(problem=challenge_problem_autocomplete)
    @app_commands.choices(language=LANGUAGE_CHOICES)
    @app_commands.describe(
        problem="Problem title. Leave empty to list active problems.",
        language="Language starter file to download when viewing one problem.",
    )
    async def challenge_view(
        self,
        interaction: discord.Interaction,
        problem: Optional[str] = None,
        language: Optional[app_commands.Choice[str]] = None,
    ):
        if problem is None:
            await self.send_problem_list(interaction)
            return

        if language is None:
            await interaction.response.send_message(
                embed=failure("Please choose a language when viewing a specific problem."),
                ephemeral=True,
            )
            return

        selected = await self.challenge_manager.get_problem(interaction.guild_id, clean_slug(problem))
        if selected is None:
            await interaction.response.send_message(embed=failure("Problem not found."), ephemeral=True)
            return

        boilerplate = selected.boilerplates.get(language.value)
        if boilerplate is None:
            await interaction.response.send_message(
                embed=failure(f"No `{language.name}` boilerplate is configured for this problem."),
                ephemeral=True,
            )
            return

        statement_file = discord.File(
            io.BytesIO(selected.statement.encode("utf-8")),
            filename=f"{selected.slug}-statement.md",
        )
        starter_file = discord.File(
            io.BytesIO(boilerplate.encode("utf-8")),
            filename=f"{selected.slug}-{language.value}-starter.txt",
        )
        preview = selected.statement.strip()
        if len(preview) > 3800:
            preview = f"{preview[:3800].rstrip()}\n\n… full statement attached."
        embed = discord.Embed(
            title=selected.title,
            description=preview or "Problem statement attached.",
            color=discord.Color.green(),
        )
        embed.add_field(name="Points", value=str(selected.points), inline=True)
        embed.add_field(name="Language", value=language.name, inline=True)
        embed.set_footer(
            text="Download the starter file, implement the requested function, then use /challenge submit."
        )
        await interaction.response.send_message(
            embed=embed,
            files=[statement_file, starter_file],
            ephemeral=True,
        )

    async def send_problem_list(self, interaction: discord.Interaction, *, ephemeral: bool = True):
        rows = await self.challenge_manager.list_problems(interaction.guild_id)
        if not rows:
            await interaction.response.send_message(
                embed=warning("No active problems yet."),
                ephemeral=ephemeral,
            )
            return

        body = "\n".join(
            f"`{row['slug']}` — **{row['title']}** ({row['points']} pts)"
            for row in rows
        )
        embed = info(body, self.bot.user, "View a Problem Statement")
        embed.set_image(url="https://lairesit.sirv.com/Tortoise/view.gif")
        await interaction.response.send_message(
            embed=embed,
            ephemeral=ephemeral,
        )

    @challenge_group.command(name="submit", description="Submit a solution by pasting code into a popup form.")
    @app_commands.autocomplete(problem=challenge_problem_autocomplete)
    @app_commands.choices(language=LANGUAGE_CHOICES)
    @app_commands.describe(
        problem="Problem title.",
        language="Language of your submitted function.",
    )
    async def challenge_submit(
        self,
        interaction: discord.Interaction,
        problem: str,
        language: app_commands.Choice[str],
    ):
        await interaction.response.send_modal(
            SolutionSubmissionModal(
                cog=self,
                problem_slug=clean_slug(problem),
                language_value=language.value,
                language_name=language.name,
            )
        )

    @challenge_group.command(
        name="test-pipeline",
        description="Run a mod-only smoke test of the challenge submission pipeline.",
    )
    @app_commands.check(check_if_tortoise_staff)
    @app_commands.choices(language=PIPELINE_LANGUAGE_CHOICES)
    @app_commands.describe(language="Language to test. Leave blank or choose All languages for full coverage.")
    async def challenge_test_pipeline(
        self,
        interaction: discord.Interaction,
        language: Optional[app_commands.Choice[str]] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        tests = [
            TestCase(name=name, input=test_input, expected=expected)
            for name, test_input, expected in challenge_pipeline_smoke_test_cases
        ]
        language_values = (
            list(challenge_pipeline_smoke_tests.keys())
            if language is None or language.value == "all"
            else [language.value]
        )

        results = []
        total_started_at = time.perf_counter()
        for language_value in language_values:
            sample = challenge_pipeline_smoke_tests[language_value]
            started_at = time.perf_counter()
            result = await judge_submission(
                hermes=self.hermes,
                language=language_value,
                solution=sample["solution"],
                boilerplate=sample["boilerplate"],
                tests=tests,
            )
            elapsed_ms = round((time.perf_counter() - started_at) * 1000)
            results.append((language_value, sample, result, elapsed_ms))

        total_elapsed_ms = round((time.perf_counter() - total_started_at) * 1000)
        all_accepted = all(result.accepted for _, _, result, _ in results)
        status_lines = []
        diagnostics = []

        for _, sample, result, elapsed_ms in results:
            icon = success_emoji if result.accepted else failure_emoji
            status = "passed" if result.accepted else f"failed on {result.failed_test}: {result.error}"
            status_lines.append(
                f"{icon} **{sample['name']}** — {status} "
                f"({result.passed}/{result.total}, {elapsed_ms} ms)"
            )
            if result.diagnostic:
                diagnostics.append(f"{sample['name']}: {result.diagnostic[:700]}")

        test_details = "\n".join(
            f"- {test.name}: input `{test.input.strip()}` → expected `{test.expected}`"
            for test in tests
        )
        summary = (
            "This smoke test injects a tiny `add(a, b)` implementation into each language's "
            "`{{SOLUTION}}` boilerplate, feeds stdin through the same judge wrapper, sends it to "
            "Hermes, compares stdout, and does not write submissions/solves or change points."
        )
        description = (
            f"{summary}\n\n"
            f"**Hermes endpoint:** `{self.hermes.url}`\n"
            f"**Tests:**\n{test_details}\n\n"
            f"**Results:**\n" + "\n".join(status_lines) + f"\n\nTotal time: **{total_elapsed_ms} ms**"
        )
        if diagnostics:
            description += "\n\n**Diagnostics:**\n```text\n" + "\n\n".join(diagnostics)[:1400] + "\n```"

        embed_factory = success if all_accepted else failure
        await interaction.followup.send(
            embed=embed_factory(
                description,
            ),
            ephemeral=True,
        )

    @challenge_group.command(name="reveal-tests", description="Reveal hidden test cases for a problem for points.")
    @app_commands.autocomplete(problem=challenge_problem_autocomplete)
    @app_commands.describe(problem="Problem title.")
    async def challenge_reveal_tests(self, interaction: discord.Interaction, problem: str):
        selected = await self.challenge_manager.get_problem(interaction.guild_id, clean_slug(problem))
        if selected is None:
            await interaction.response.send_message(embed=failure("Problem not found."), ephemeral=True)
            return

        already_revealed = await self.challenge_manager.has_revealed_tests(
            guild_id=interaction.guild_id,
            slug=selected.slug,
            user_id=interaction.user.id,
        )
        cost_message = (
            "You have already revealed this problem before, so revealing it again costs **0 points**."
            if already_revealed
            else f"This will deduct **{challenge_test_reveal_cost} points** from your score."
        )

        await interaction.response.send_message(
            embed=warning(
                f"You are about to reveal all hidden test cases for **{selected.title}**.\n\n"
                f"{cost_message}\n\n"
                "This can spoil the challenge. Confirm twice to continue."
            ),
            view=RevealTestsConfirmView(cog=self, user_id=interaction.user.id, problem=selected),
            ephemeral=True,
        )

    async def process_submission(
        self,
        *,
        interaction: discord.Interaction,
        problem_slug: str,
        language_value: str,
        language_name: str,
        submitted_code: str,
    ):
        selected = await self.challenge_manager.get_problem(interaction.guild_id, problem_slug)
        if selected is None:
            await interaction.followup.send(embed=failure("Problem not found."), ephemeral=True)
            return

        boilerplate = selected.boilerplates.get(language_value)
        if boilerplate is None:
            await interaction.followup.send(
                embed=failure(f"No {language_name} boilerplate is configured for this problem."),
                ephemeral=True,
            )
            return

        submission_id = await self.challenge_manager.record_submission(
            guild_id=interaction.guild_id,
            slug=selected.slug,
            user_id=interaction.user.id,
            language=language_value,
            solution=submitted_code,
            status="pending",
            passed=0,
            total=len(selected.tests),
            error=None,
        )

        judge_started_at = time.perf_counter()
        try:
            result = await judge_submission(
                hermes=self.hermes,
                language=language_value,
                solution=submitted_code,
                boilerplate=boilerplate,
                tests=selected.tests,
            )
        except Exception as exc:
            logger.exception("Judge failed after recording submission")
            await self.challenge_manager.update_submission_result(
                submission_id,
                status="error",
                passed=0,
                total=len(selected.tests),
                error=f"Judge unavailable: {exc}",
            )
            await interaction.followup.send(embed=failure(f"Judge unavailable: {exc}"), ephemeral=True)
            return
        judge_elapsed_ms = round((time.perf_counter() - judge_started_at) * 1000)

        if result.diagnostic:
            logger.warning(
                "Submission diagnostic guild=%s slug=%s user=%s: %s",
                interaction.guild_id,
                selected.slug,
                interaction.user.id,
                result.diagnostic,
            )

        await self.challenge_manager.update_submission_result(
            submission_id,
            status="accepted" if result.accepted else "rejected",
            passed=result.passed,
            total=result.total,
            error=result.error,
        )

        if not result.accepted:
            diagnostic = ""
            if result.diagnostic:
                safe_diagnostic = result.diagnostic[:1500].replace("```", "''' ")
                diagnostic = f"\n\n**Compiler/runtime diagnostic:**\n```text\n{safe_diagnostic}\n```"

            await interaction.followup.send(
                embed=failure(
                    f"{result.error} on **{result.failed_test}** "
                    f"({result.passed}/{result.total} passed)."
                    f"{diagnostic}"
                ),
                ephemeral=True,
            )
            return

        previous_rank = await self.challenge_manager.get_points_rank(interaction.guild_id, interaction.user.id)
        newly_solved = await self.challenge_manager.award_solve(
            guild_id=interaction.guild_id,
            slug=selected.slug,
            user_id=interaction.user.id,
            points=selected.points,
        )

        if newly_solved:
            total_points = await self.bot.points_manager.add_points(
                interaction.guild_id,
                interaction.user.id,
                selected.points,
            )
            current_rank = await self.challenge_manager.get_points_rank(interaction.guild_id, interaction.user.id)
            await self.log_accepted_submission(
                interaction=interaction,
                problem=selected,
                language_name=language_name,
                passed=result.passed,
                total=result.total,
                judge_elapsed_ms=judge_elapsed_ms,
                points_awarded=selected.points,
                previous_rank=previous_rank,
                current_rank=current_rank,
                total_points=total_points,
                newly_solved=True,
                submission_id=submission_id,
            )
            await interaction.followup.send(
                embed=success(
                    f"Accepted — {result.total}/{result.total} passed. "
                    f"You earned **{selected.points} points**! New total: **{total_points}**."
                ),
                ephemeral=True,
            )
        else:
            total_points = await self.bot.points_manager.get_points(
                interaction.guild_id,
                interaction.user.id,
            )
            current_rank = await self.challenge_manager.get_points_rank(interaction.guild_id, interaction.user.id)
            await self.log_accepted_submission(
                interaction=interaction,
                problem=selected,
                language_name=language_name,
                passed=result.passed,
                total=result.total,
                judge_elapsed_ms=judge_elapsed_ms,
                points_awarded=0,
                previous_rank=previous_rank,
                current_rank=current_rank,
                total_points=total_points,
                newly_solved=False,
                submission_id=submission_id,
            )
            await interaction.followup.send(
                embed=success(
                    f"Accepted — {result.total}/{result.total} passed. "
                    "You had already solved this problem, so no duplicate points were added."
                ),
                ephemeral=True,
            )

    async def autocomplete_problem(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        if interaction.guild_id is None:
            return []

        query = current.lower()
        rows = await self.challenge_manager.list_problems(interaction.guild_id)
        choices = []
        seen = set()

        for row in rows:
            if query and query not in row["title"].lower() and query not in row["slug"]:
                continue
            if row["slug"] in seen:
                continue
            seen.add(row["slug"])
            choices.append(
                app_commands.Choice(
                    name=row["title"][:challenge_autocomplete_choice_max_length],
                    value=row["slug"],
                )
            )
            if len(choices) >= 25:
                break

        return choices

    async def log_accepted_submission(
        self,
        *,
        interaction: discord.Interaction,
        problem: Problem,
        language_name: str,
        passed: int,
        total: int,
        judge_elapsed_ms: int,
        points_awarded: int,
        previous_rank: Optional[int],
        current_rank: Optional[int],
        total_points: int,
        newly_solved: bool,
        submission_id: int,
    ):
        guild = interaction.guild
        if guild is None:
            return

        previous_rank_text = f"#{previous_rank}" if previous_rank is not None else "unranked"
        current_rank_text = f"#{current_rank}" if current_rank is not None else "unranked"
        if previous_rank != current_rank:
            leaderboard_change = f"{previous_rank_text} → {current_rank_text}"
        else:
            leaderboard_change = f"unchanged ({current_rank_text})"

        embed = discord.Embed(
            title="",
            description=(
                f"## {success_emoji} Correct Submission\n\n"
                f"{interaction.user.mention} solved **{problem.title}**."
                if newly_solved
                else f"{interaction.user.mention} submitted another accepted solution for **{problem.title}**."
            ),
            color=discord.Color.green(),
        )
        embed.add_field(name="Problem", value=f"{problem.title} (`{problem.slug}`)", inline=False)
        embed.add_field(name="Language", value=language_name, inline=True)
        embed.add_field(name="Tests", value=f"{passed}/{total} passed", inline=True)
        embed.add_field(name="Judge time", value=f"{judge_elapsed_ms} ms", inline=True)
        embed.add_field(name="Points awarded", value=str(points_awarded), inline=True)
        embed.add_field(name="Total points", value=str(total_points), inline=True)
        embed.add_field(name="Leaderboard", value=leaderboard_change, inline=True)

        await self.challenge_log_public_channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=submission_log_view(submission_id),
        )
        await self.challenge_log_channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=submission_log_view(submission_id, moderator=True),
        )

    async def reveal_tests_for_user(self, interaction: discord.Interaction, problem: Problem):
        should_deduct = await self.challenge_manager.mark_tests_revealed(
            guild_id=interaction.guild_id,
            slug=problem.slug,
            user_id=interaction.user.id,
        )

        new_total: Optional[int] = None
        if should_deduct:
            new_total = await self.bot.points_manager.remove_points(
                interaction.guild_id,
                interaction.user.id,
                challenge_test_reveal_cost,
            )

        payload = {
            "problem": problem.title,
            "slug": problem.slug,
            "revealed_by": interaction.user.id,
            "points_deducted": challenge_test_reveal_cost if should_deduct else 0,
            "tests": [
                {
                    "name": test.name,
                    "input": test.input,
                    "expected": test.expected,
                }
                for test in problem.tests
            ],
        }
        file = discord.File(
            io.BytesIO(json.dumps(payload, indent=2).encode("utf-8")),
            filename=f"{problem.slug}-test-cases.json",
        )

        if should_deduct:
            message = (
                f"Revealed hidden tests for **{problem.title}**. "
                f"Deducted **{challenge_test_reveal_cost} points**. New total: **{new_total}**."
            )
        else:
            message = (
                f"Revealed hidden tests for **{problem.title}** again. "
                "No points were deducted because you already used this reveal."
            )

        await interaction.followup.send(embed=success(message), file=file, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Challenges(bot))
