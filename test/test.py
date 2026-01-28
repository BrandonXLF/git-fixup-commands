import json
import os
import subprocess
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
tests_folder = os.path.join(current_folder, "tests")
repos_folder = os.path.join(current_folder, "repos")
patches_folder = os.path.join(current_folder, "patches")

tests = [name for name in os.listdir(tests_folder) if os.path.isdir(os.path.join(tests_folder, name))]
shell_self = "\"" + sys.executable + "\""

def run(args, cwd, env=None, input=None, capture=False):
	return subprocess.run(
		[*args],
		stdout=subprocess.PIPE if capture else None,
		stderr=subprocess.STDOUT if capture else None,
		text=True,
		cwd=cwd,
		env=env,
		input=input, check=False
	)

def git(args, cwd, env=None, input=None, capture=False):
	return run(["git", *args], cwd, env, input, capture)

def compare_expected(name, expected_path, actual):
	if os.path.exists(expected_path):
		with open(expected_path) as f:
			expected = f.read()

		if actual != expected:
			print(f"Test \"{test}\" failed: {name} does not match expected output.")

			diff = git(
				["diff", "--no-index", "--word-diff=color", expected_path, "-"],
				cwd=current_folder,
				input=actual
			).stdout

			print()
			print(diff)
			sys.exit(1)

		return

	with open(expected_path, "w") as f:
		f.write(actual)

	print(f"Test \"{test}\": created expected {name} output.")

for test in tests:
	print(f"\n** {test} **")

	test_folder = os.path.join(current_folder, "tests", test)

	info = False
	with open(f"{test_folder}/test.json") as f:
		info = json.load(f)

	git(["clone", info["repo"] + ".bundle", info["repo"]], cwd=repos_folder)
	repo_folder = os.path.join(repos_folder, info["repo"])

	git(["config", "commit.gpgsign", "false"], cwd=repo_folder)
	git(["config", "fixupCommands.rebaseMerges", "true"], cwd=repo_folder)
	git(["config", "user.name", "Tester"], cwd=repo_folder)
	git(["config", "user.email", "test@invalid"], cwd=repo_folder)

	if "config" in info:
		for key, value in info["config"].items():
			if key == "sequence.editor":
				value = shell_self + " ../../append.py \"" + value + "\""

			git(["config", key, value], cwd=repo_folder)

	git(["rebase", "--abort"], cwd=repo_folder)
	git(["checkout", "main"], cwd=repo_folder)
	git(["reset", "--hard", "origin/HEAD"], cwd=repo_folder)

	git(["apply", os.path.join(patches_folder, info["patch"])], cwd=repo_folder)
	git(["add", "."], cwd=repo_folder)

	test_out = info.get("test_out", False)
	test_env = {
		**dict(**os.environ),
		"GIT_EDITOR": shell_self + " ../../append.py \"LINE ADDED BY REWORD\"",
		"GIT_COMMITTER_NAME": "Tester",
		"GIT_COMMITTER_EMAIL": "test@invalid",
		"GIT_COMMITTER_DATE": "2026-01-01 12:00:00 +0000"
	}
	res = run(
		[sys.executable, os.path.join(os.path.dirname(current_folder), "main.py"), info["type"], *info["args"]],
		cwd=repo_folder,
		env=test_env,
		capture=test_out
	)

	if test_out:
		actual = res.stdout.strip()
		compare_expected("command output", os.path.join(test_folder, "out.txt"), actual)

	actual = git(
		["log", "-p", "-U0",  "--diff-merges=separate", "--author-date-order", "--graph", "--format=fuller", "origin/HEAD"],
		cwd=repo_folder,
		capture=True
	).stdout.strip()
	compare_expected("old log", os.path.join(test_folder, "log_old.txt"), actual)

	actual = git(
		["log", "-p", "-U0", "--diff-merges=separate", "--author-date-order", "--graph", "--format=fuller"],
		cwd=repo_folder,
		capture=True
	).stdout.strip()
	compare_expected("new log", os.path.join(test_folder, "log_new.txt"), actual)

	actual = git(["diff", "--no-index", "-U1", "log_old.txt", "log_new.txt"], cwd=test_folder, capture=True).stdout
	actual = "\n".join(actual.splitlines()[4:]) # Remove header
	compare_expected("log diff", os.path.join(test_folder, "log.diff"), actual)

	actual = git(["diff"], cwd=repo_folder, capture=True).stdout
	compare_expected("changes", os.path.join(test_folder, "diff.txt"), actual)

	actual = git(["diff", "--staged"], cwd=repo_folder, capture=True).stdout
	compare_expected("staged", os.path.join(test_folder, "diff_staged.txt"), actual)

	print(f"Test \"{test}\" passed.")
