import os
import sys

from git import Repo, InvalidGitRepositoryError

proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.append(proj_root)
from kernel.global_var import GlabalVar as GB

class GitAPI:
    """git コマンドを実行する API"""
    def __init__(self, app_instance):
        self.app = app_instance
        self.editing_path = GB.EDITING_PATH
        if GB.EDITING_PATH:
            abs_path = os.path.abspath(GB.EDITING_PATH)
        else:
            self.git_repo = None
            return

        try:
            repo = Repo(abs_path, search_parent_directories=True)
            repo_root = repo.git_dir.replace('.git', '')
            relative_path = os.path.relpath(abs_path, repo.working_tree_dir)
            is_tracked = any(relative_path in item for item in repo.git.ls_files(relative_path).splitlines())
            if is_tracked:
                self.git_repo = Repo(repo.working_tree_dir, search_parent_directories=True)
            else:
                self.git_repo = None
        except InvalidGitRepositoryError:
            self.git_repo = None

    def add(self, is_all=False, path:list|None=None):
        """git add コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        if is_all:
            self.git_repo.git.add(A=True)
            self.app.log("Git: Added all changes.")
        else:
            target = path if path else [GB.EDITING_PATH]
            self.git_repo.git.add(target)
            self.app.log(f"Git: Added {target}.")

    def commit(self, message="commit from Oriana"):
        """git commit コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        self.git_repo.index.commit(message)
        self.app.log(f"Git: Committed with message: {message}")

    def reset(self):
        """git reset コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        self.git_repo.git.reset()

    def checkout(self, branch, is_force=False):
        """git checkout コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        self.git_repo.git.checkout(branch, force=is_force)
        self.app.log(f"Git: Checked out to {branch}")

    def pull(self, remote="origin", branch="main"):
        """git pull コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        if remote not in [r.name for r in self.git_repo.remotes]:
            self.app.log(f"Error: Remote '{remote}' not found.")
            return
        origin = self.git_repo.remote(name=remote)
        origin.pull(branch)
        self.app.log(f"Git: Pulled from {remote}/{branch}")

    def push(self, remote="origin", branch="main"):
        """git push コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        if remote not in [r.name for r in self.git_repo.remotes]:
            self.app.log(f"Error: Remote '{remote}' not found.")
            return
        origin = self.git_repo.remote(name=remote)
        origin.push(branch)
        self.app.log(f"Git: Pushed to {remote}/{branch}")