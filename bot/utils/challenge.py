from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp
import discord

from bot.constants import challenge_supported_language_values


CHALLENGE_ATTACHMENT_FILENAMES = (
    "statement.md",
    "python-boilerplate.py",
    "javascript-boilerplate.js",
    "cpp-boilerplate.cpp",
    "java-boilerplate.java",
    "test-inputs.json",
    "expected-outputs.json",
)


@dataclass(slots=True)
class TestCase:
    name: str
    input: str
    expected: str


@dataclass(slots=True)
class Problem:
    guild_id: int
    slug: str
    title: str
    statement: str
    points: int
    boilerplates: dict[str, str]
    tests: list[TestCase]


@dataclass(slots=True)
class ExecutionResult:
    exit_code: int
    stdout: str
    stderr: str


@dataclass(slots=True)
class JudgeResult:
    accepted: bool
    passed: int
    total: int
    failed_test: Optional[str] = None
    error: Optional[str] = None
    diagnostic: Optional[str] = None


class ExecutionApiClient:
    def __init__(
        self,
        *,
        url: str,
        api_token: Optional[str],
        timeout_seconds: float,
    ):
        self.url = url
        self.api_token = api_token
        self.timeout_seconds = timeout_seconds

    async def execute(self, language: str, code: str) -> ExecutionResult:
        if language not in challenge_supported_language_values:
            raise ValueError(f"Unsupported language: {language}")

        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                self.url,
                json={"language": language, "code": code},
                headers=headers,
            ) as response:
                if response.status == 403:
                    body = await response.text()
                    raise RuntimeError(f"Execution API returned HTTP 403: {body[:200]}")
                if response.status < 200 or response.status >= 300:
                    body = await response.text()
                    raise RuntimeError(f"Execution API returned HTTP {response.status}: {body[:200]}")
                payload = await response.json()

        return ExecutionResult(
            exit_code=int(payload.get("code", payload.get("exit_code", -1))),
            stdout=str(payload.get("output", payload.get("stdout", ""))),
            stderr=str(payload.get("std_log", payload.get("stderr", ""))),
        )


async def download_text(attachment: discord.Attachment, *, max_bytes: int) -> str:
    if attachment.size is not None and attachment.size > max_bytes:
        raise ValueError(f"{attachment.filename} is too large (max {max_bytes // 1024} KB).")

    data = await attachment.read()
    if len(data) > max_bytes:
        raise ValueError(f"{attachment.filename} is too large (max {max_bytes // 1024} KB).")

    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{attachment.filename} must be UTF-8 text.") from exc


def arrange_challenge_attachments(
    attachments: list[discord.Attachment],
) -> dict[str, discord.Attachment]:
    arranged = {attachment.filename: attachment for attachment in attachments}
    duplicates = sorted(
        filename for filename in arranged if sum(a.filename == filename for a in attachments) > 1
    )
    missing = sorted(set(CHALLENGE_ATTACHMENT_FILENAMES) - arranged.keys())
    unexpected = sorted(arranged.keys() - set(CHALLENGE_ATTACHMENT_FILENAMES))
    problems = []
    if missing:
        problems.append(f"missing: {', '.join(missing)}")
    if unexpected:
        problems.append(f"unexpected: {', '.join(unexpected)}")
    if duplicates:
        problems.append(f"duplicated: {', '.join(duplicates)}")
    if problems:
        raise ValueError("Invalid challenge files (" + "; ".join(problems) + ").")
    return {filename: arranged[filename] for filename in CHALLENGE_ATTACHMENT_FILENAMES}


def positive_integer_env(name: str, fallback: int) -> int:
    raw_value = os.getenv(name, str(fallback))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a positive integer.") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be a positive integer.")
    return value


def parse_jsonish(value: Any) -> Any:
    if isinstance(value, str):
        return json.loads(value)
    return value


def slug_from_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower().strip()).strip("-")[:40]
    if len(slug) < 2:
        raise ValueError("The title must contain at least two letters or numbers.")
    return slug


def clean_slug(value: str) -> str:
    slug = value.lower().strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,39}", slug):
        raise ValueError("Slug must be 2–40 lowercase letters, numbers, _ or -.")
    return slug


def parse_test_files(inputs_text: str, outputs_text: str, max_tests: int) -> list[TestCase]:
    try:
        inputs = json.loads(inputs_text)
        outputs = json.loads(outputs_text)
    except json.JSONDecodeError as exc:
        raise ValueError("The tests attachment is not valid JSON.") from exc

    if not isinstance(inputs, list) or not isinstance(outputs, list):
        raise ValueError("Both test files must be JSON arrays.")
    if not inputs:
        raise ValueError("At least one test case is required.")
    if len(inputs) != len(outputs):
        raise ValueError("Input and expected-output files must have the same number of entries.")
    if len(inputs) > max_tests:
        raise ValueError(f"A problem may have at most {max_tests} tests.")

    tests = []
    for index, (test_input, expected_output) in enumerate(zip(inputs, outputs), start=1):
        if not isinstance(test_input, str) or not isinstance(expected_output, str):
            raise ValueError("Every test input and output must be a JSON string.")
        tests.append(TestCase(name=f"Test {index}", input=test_input, expected=expected_output))
    return tests


def normalize_output(value: str) -> str:
    return str(value or "").replace("\r\n", "\n").rstrip()


def encoded_input(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def build_executable(language: str, solution: str, test_input: str) -> str:
    encoded = encoded_input(test_input)

    if language == "python":
        return (
            "import sys as __judge_sys, io as __judge_io, base64 as __judge_b64\n"
            f"__judge_sys.stdin = __judge_io.StringIO(__judge_b64.b64decode('{encoded}').decode('utf-8'))\n"
            f"{solution}"
        )

    if language == "javascript":
        return (
            "const __judgeFs = require('fs');\n"
            f"const __judgeInput = Buffer.from('{encoded}', 'base64');\n"
            "const __judgeRead = __judgeFs.readFileSync;\n"
            "__judgeFs.readFileSync = function(path, options) {\n"
            "  if (path === 0 || path === '/dev/stdin') "
            "return options && String(options).includes('utf') "
            "? __judgeInput.toString('utf8') : __judgeInput;\n"
            "  return __judgeRead.apply(this, arguments);\n"
            "};\n"
            f"{solution}"
        )

    if language == "cpp":
        return (
            "#define main __submitted_main\n"
            f"{solution}\n"
            "#undef main\n"
            "#include <sstream>\n"
            "#include <iostream>\n"
            "#include <string>\n"
            "#include <cstdlib>\n"
            "int main() {\n"
            "  std::string __data;\n"
            f'  const std::string __b64 = "{encoded}";\n'
            '  const std::string __chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            'abcdefghijklmnopqrstuvwxyz0123456789+/";\n'
            "  int __val=0, __bits=-8;\n"
            "  for (unsigned char __c : __b64) { if (__c=='=') break; "
            "auto __p=__chars.find(__c); if (__p==std::string::npos) continue; "
            "__val=(__val<<6)+int(__p); __bits+=6; if (__bits>=0) { "
            "__data.push_back(char((__val>>__bits)&0xFF)); __bits-=8; } }\n"
            "  std::istringstream __input(__data); std::cin.rdbuf(__input.rdbuf());\n"
            "  return __submitted_main();\n"
            "}"
        )

    if language == "java":
        renamed = re.sub(r"public\s+class\s+Main\b", "class SubmittedMain", solution, count=1)
        if renamed == solution:
            raise ValueError("Java submissions must contain `public class Main`.")
        return (
            "import java.io.*;\n"
            "import java.util.Base64;\n"
            f"{renamed}\n"
            "public class Main { public static void main(String[] args) throws Exception { "
            f'System.setIn(new ByteArrayInputStream(Base64.getDecoder().decode("{encoded}"))); '
            "SubmittedMain.main(args); } }"
        )

    raise ValueError(f"Unsupported language: {language}")


async def judge_submission(
    *,
    hermes: ExecutionApiClient,
    language: str,
    solution: str,
    boilerplate: str,
    tests: list[TestCase],
) -> JudgeResult:
    if "{{SOLUTION}}" not in boilerplate:
        return JudgeResult(
            accepted=False,
            passed=0,
            total=len(tests),
            failed_test="judge setup",
            error="Problem boilerplate is missing {{SOLUTION}}.",
        )

    complete_program = boilerplate.replace("{{SOLUTION}}", solution)
    passed = 0

    for test in tests:
        try:
            code = build_executable(language, complete_program, test.input)
        except Exception as exc:
            return JudgeResult(
                accepted=False,
                passed=passed,
                total=len(tests),
                failed_test=test.name,
                error=str(exc),
            )

        try:
            execution = await hermes.execute(language, code)
        except Exception as exc:
            return JudgeResult(
                accepted=False,
                passed=passed,
                total=len(tests),
                failed_test=test.name,
                error=f"Judge unavailable: {exc}",
            )

        if execution.exit_code != 0:
            if execution.exit_code == 401:
                return JudgeResult(
                    accepted=False,
                    passed=passed,
                    total=len(tests),
                    failed_test=test.name,
                    error="Judge authentication failed. Ask an administrator to synchronize the Hermes API token.",
                )

            if re.search(r"seccomp_load|rosetta error", execution.stderr, flags=re.IGNORECASE):
                return JudgeResult(
                    accepted=False,
                    passed=passed,
                    total=len(tests),
                    failed_test=test.name,
                    error=(
                        "Judge sandbox is unavailable on this host architecture. "
                        "This is an engine failure, not a wrong answer."
                    ),
                    diagnostic=execution.stderr[:2000],
                )

            return JudgeResult(
                accepted=False,
                passed=passed,
                total=len(tests),
                failed_test=test.name,
                error=f"Runtime or compilation error (exit code {execution.exit_code})",
                diagnostic=execution.stderr[:2000],
            )

        if normalize_output(execution.stdout) != normalize_output(test.expected):
            return JudgeResult(
                accepted=False,
                passed=passed,
                total=len(tests),
                failed_test=test.name,
                error="Wrong answer",
            )

        passed += 1

    return JudgeResult(accepted=True, passed=passed, total=len(tests))
