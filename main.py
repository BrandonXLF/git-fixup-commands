import os
import subprocess
import sys


def internal_insert_todo_break() -> None:
	file = sys.argv[1]
	lines = []

	with open(file) as f:
		lines = f.readlines()

		i = 0
		while not lines[i].startswith("pick"):
			i += 1

		i += 1
		while lines[i].startswith("fixup ") or lines[i].startswith("squash "):
			i += 1

		lines.insert(i, "break\n")

	with open(file, "w") as f:
		f.writelines(lines)

def git_run(args, capture_stdout=None, env=None) -> None:
	res = subprocess.run(["git", *args], stdout=capture_stdout, stderr=None, text=True, env=env, check=False)

	if res.returncode != 0:
		sys.exit(res.returncode)

	return res.stdout

def core(fixup_prefix = "") -> None:
	args = sys.argv[1:]
	flags = []
	pause = False
	interactive = False
	commit = ""

	for arg in args:
		if arg in ("-p", "--pause"):
			pause = True
		elif arg in ("-i", "--interactive"):
			interactive = True
			flags.append(arg)
		elif arg.startswith("-"):
			flags.append(arg)
		else:
			commit = arg

	if pause and interactive:
		sys.exit("Cannot use both --pause and --interactive")

	parent_list = git_run(["rev-list", "-n1", "--parents", commit, "--"], subprocess.PIPE).strip().split()[1:]
	parent_ref = parent_list[0] if len(parent_list) > 0 else "--root"

	rebase_env = None
	if pause or not interactive:
		rebase_env = {
			**dict(**os.environ),
			"GIT_SEQUENCE_EDITOR": "\"" + sys.executable + "\" \"" + os.path.abspath(__file__) + "\" internal_insert_todo_break" if pause else "true"
		}

		flags.append("--interactive")

	git_run(["commit", "--fixup=" + fixup_prefix + commit])
	git_run(["rebase", "--autosquash", "--autostash", "--rebase-merges", *flags, parent_ref], env=rebase_env, capture_stdout=True)

def fixup() -> None:
	core()

def amend() -> None:
	core("amend:")

def reword() -> None:
	core("reword:")

if __name__ == "__main__":
	sys.argv = sys.argv[1:]

	if len(sys.argv) == 0:
		sys.exit("No command specified")

	globals()[sys.argv[0]]()
