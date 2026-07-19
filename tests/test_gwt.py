import unittest
import os
import subprocess
import shutil
import tempfile

# Get absolute path to gwt-cli
GWT_CLI_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "bin", "gwt-cli")
)


class TestGitWorktreeTool(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.remote_path = os.path.join(self.test_dir, "remote-repo")
        os.makedirs(self.remote_path)

        # Initialize remote repository
        self.run_cmd(["git", "init"], cwd=self.remote_path)
        self.run_cmd(["git", "config", "user.name", "Test User"], cwd=self.remote_path)
        self.run_cmd(
            ["git", "config", "user.email", "test@example.com"], cwd=self.remote_path
        )

        # Create initial commit on main
        readme_path = os.path.join(self.remote_path, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Remote Repo\n")
        self.run_cmd(["git", "add", "README.md"], cwd=self.remote_path)
        self.run_cmd(["git", "commit", "-m", "Initial commit"], cwd=self.remote_path)
        self.run_cmd(["git", "branch", "-M", "main"], cwd=self.remote_path)

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def run_cmd(self, args, cwd=None, input_str=None):
        res = subprocess.run(
            args, cwd=cwd, input=input_str, capture_output=True, text=True
        )
        return res

    def init_project(self, project_path):
        res = self.run_cmd([GWT_CLI_PATH, "init", self.remote_path, project_path])
        if res.returncode == 0:
            main_path = os.path.join(project_path, "main")
            if os.path.exists(main_path):
                self.run_cmd(["git", "config", "user.name", "Test User"], cwd=main_path)
                self.run_cmd(
                    ["git", "config", "user.email", "test@example.com"], cwd=main_path
                )
        return res

    def test_init_success(self):
        project_path = os.path.join(self.test_dir, "project")

        # Run gwt-cli init
        res = self.init_project(project_path)
        self.assertEqual(res.returncode, 0, f"init failed: {res.stderr}")

        # Verify structure
        self.assertTrue(os.path.isdir(os.path.join(project_path, ".bare")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, ".git")))
        with open(os.path.join(project_path, ".git"), "r") as f:
            self.assertEqual(f.read().strip(), "gitdir: ./.bare")

        # Verify main worktree directory exists and is check out
        main_path = os.path.join(project_path, "main")
        self.assertTrue(os.path.isdir(main_path))
        self.assertTrue(os.path.isfile(os.path.join(main_path, "README.md")))

        # Verify upstream tracking is set up
        branch_info = self.run_cmd(["git", "branch", "-vv"], cwd=main_path).stdout
        self.assertIn("[origin/main]", branch_info)

    def test_new_worktree_success(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        # Run gwt-cli new from main directory (simulating being in project repo)
        main_path = os.path.join(project_path, "main")
        res = self.run_cmd([GWT_CLI_PATH, "new", "feature/my-feat"], cwd=main_path)

        self.assertEqual(res.returncode, 0, f"new failed: {res.stderr}")

        # The tool should output the directory path to stdout
        expected_path = os.path.join(project_path, "feature-my-feat")
        self.assertEqual(
            os.path.realpath(res.stdout.strip()), os.path.realpath(expected_path)
        )

        # Verify directories
        self.assertTrue(os.path.isdir(expected_path))
        self.assertTrue(os.path.isfile(os.path.join(expected_path, "README.md")))

        # Verify Git branch inside the new worktree
        branch_name = self.run_cmd(
            ["git", "branch", "--show-current"], cwd=expected_path
        ).stdout.strip()
        self.assertEqual(branch_name, "feature/my-feat")

    def test_new_already_exists_fails(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        # Create once
        self.run_cmd([GWT_CLI_PATH, "new", "feature/my-feat"], cwd=main_path)

        # Try creating again (same name)
        res = self.run_cmd([GWT_CLI_PATH, "new", "feature/my-feat"], cwd=main_path)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("already exists", res.stderr)

    def test_cleanup_clean_worktree(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        feat_path = os.path.join(project_path, "feature-my-feat")

        # Create worktree
        self.run_cmd([GWT_CLI_PATH, "new", "feature/my-feat"], cwd=main_path)

        # Make a commit in feature worktree and merge it to main
        with open(os.path.join(feat_path, "feat.txt"), "w") as f:
            f.write("feat\n")
        self.run_cmd(["git", "add", "feat.txt"], cwd=feat_path)
        self.run_cmd(["git", "commit", "-m", "add feat"], cwd=feat_path)

        # Merge it into main
        self.run_cmd(["git", "merge", "feature/my-feat"], cwd=main_path)

        # Check that it exists before clean
        self.assertTrue(os.path.isdir(feat_path))

        # Run clean from main
        res = self.run_cmd([GWT_CLI_PATH, "clean"], cwd=main_path)
        self.assertEqual(res.returncode, 0, f"clean failed: {res.stderr}")

        # Verify worktree is removed
        self.assertFalse(os.path.exists(feat_path))

        # Verify branch is deleted
        branches = self.run_cmd(["git", "branch"], cwd=main_path).stdout
        self.assertNotIn("feature/my-feat", branches)

    def test_cleanup_squash_merged_worktree(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        feat_path = os.path.join(project_path, "feature-my-feat")

        # Create worktree
        self.run_cmd([GWT_CLI_PATH, "new", "feature/my-feat"], cwd=main_path)

        # Make a commit in feature worktree
        with open(os.path.join(feat_path, "feat.txt"), "w") as f:
            f.write("feat\n")
        self.run_cmd(["git", "add", "feat.txt"], cwd=feat_path)
        self.run_cmd(["git", "commit", "-m", "add feat"], cwd=feat_path)

        # Squash merge it into main manually
        self.run_cmd(["git", "merge", "--squash", "feature/my-feat"], cwd=main_path)
        self.run_cmd(["git", "commit", "-m", "squash merge of my-feat"], cwd=main_path)

        # Check that it exists before clean
        self.assertTrue(os.path.isdir(feat_path))

        # Run clean from main
        res = self.run_cmd([GWT_CLI_PATH, "clean"], cwd=main_path)
        self.assertEqual(res.returncode, 0, f"clean failed: {res.stderr}")

        # Verify worktree is removed
        self.assertFalse(os.path.exists(feat_path))

        # Verify branch is deleted
        branches = self.run_cmd(["git", "branch"], cwd=main_path).stdout
        self.assertNotIn("feature/my-feat", branches)

    def test_cleanup_dirty_worktree_rejected(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        feat_path = os.path.join(project_path, "feature-my-feat")

        self.run_cmd([GWT_CLI_PATH, "new", "feature/my-feat"], cwd=main_path)

        # Merge it without making a commit (so it has no diff, but we add a dirty file)
        # Wait, if there's no commits on feature/my-feat, it is technically merged.
        # Let's add an untracked, unignored file to make it dirty
        dirty_file = os.path.join(feat_path, "dirty.txt")
        with open(dirty_file, "w") as f:
            f.write("some state\n")

        # Let's stage it to make it a staged change
        self.run_cmd(["git", "add", "dirty.txt"], cwd=feat_path)

        # Add another untracked file to make it unstaged change
        dirty_file_2 = os.path.join(feat_path, "dirty2.txt")
        with open(dirty_file_2, "w") as f:
            f.write("another state\n")

        # Run clean and reject deletion (input "n")
        res = self.run_cmd([GWT_CLI_PATH, "clean"], cwd=main_path, input_str="n\n")
        self.assertEqual(res.returncode, 0)
        self.assertIn("NOT clean", res.stderr)
        self.assertIn("Staged changes:", res.stderr)
        self.assertIn("Unstaged changes:", res.stderr)
        self.assertIn("Skipping deletion", res.stderr)

        # Verify worktree still exists
        self.assertTrue(os.path.exists(feat_path))
        self.assertTrue(os.path.exists(dirty_file))
        self.assertTrue(os.path.exists(dirty_file_2))

    def test_cleanup_dirty_worktree_approved(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        feat_path = os.path.join(project_path, "feature-my-feat")

        self.run_cmd([GWT_CLI_PATH, "new", "feature/my-feat"], cwd=main_path)

        dirty_file = os.path.join(feat_path, "dirty.txt")
        with open(dirty_file, "w") as f:
            f.write("some state\n")

        # Run clean and approve deletion (input "y")
        res = self.run_cmd([GWT_CLI_PATH, "clean"], cwd=main_path, input_str="y\n")
        self.assertEqual(res.returncode, 0, f"clean failed: {res.stderr}")
        self.assertIn("Deleting...", res.stderr)

        # Verify worktree is removed
        self.assertFalse(os.path.exists(feat_path))

    def test_list_command(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        self.run_cmd([GWT_CLI_PATH, "new", "feature/my-feat"], cwd=main_path)

        # Test listing
        res = self.run_cmd([GWT_CLI_PATH, "list"], cwd=main_path)
        self.assertEqual(res.returncode, 0, f"list failed: {res.stderr}")

        # Verify columns in stdout
        stdout = res.stdout
        self.assertIn("WORKTREE", stdout)
        self.assertIn("BRANCH", stdout)
        self.assertIn("MERGE STATUS", stdout)
        self.assertIn("FILE STATUS", stdout)

        # Verify main status
        self.assertIn("main", stdout)
        self.assertIn("Main", stdout)

        # Verify feature status (is clean)
        self.assertIn("feature-my-feat", stdout)
        self.assertIn("feature/my-feat", stdout)
        self.assertIn("Merged", stdout)
        self.assertIn("Clean", stdout)

        # Create a dirty file in feature worktree (unstaged)
        feat_path = os.path.join(project_path, "feature-my-feat")
        dirty_file = os.path.join(feat_path, "dirty.txt")
        with open(dirty_file, "w") as f:
            f.write("state\n")

        # List again and verify it reports unstaged dirty status
        res2 = self.run_cmd([GWT_CLI_PATH, "list"], cwd=main_path)
        self.assertIn("Dirty (1 unstaged)", res2.stdout)

        # Stage the file and check list again
        self.run_cmd(["git", "add", "dirty.txt"], cwd=feat_path)
        res3 = self.run_cmd([GWT_CLI_PATH, "list"], cwd=main_path)
        self.assertIn("Dirty (1 staged)", res3.stdout)

        # Add another untracked file to verify mixed status
        dirty_file_2 = os.path.join(feat_path, "dirty2.txt")
        with open(dirty_file_2, "w") as f:
            f.write("state2\n")

        res4 = self.run_cmd([GWT_CLI_PATH, "list"], cwd=main_path)
        self.assertIn("Dirty (1 staged, 1 unstaged)", res4.stdout)

        # Commit the staged file to make it tracked
        self.run_cmd(["git", "commit", "-m", "commit dirty.txt"], cwd=feat_path)
        # Remove the second untracked file to return to clean state
        os.remove(dirty_file_2)

        # Modify the tracked file (will output ' M' in git status --porcelain)
        with open(dirty_file, "a") as f:
            f.write("more modifications\n")

        # Verify it reports as unstaged only and does not contain "staged" in the status
        res5 = self.run_cmd([GWT_CLI_PATH, "list"], cwd=main_path)
        self.assertIn("Dirty (1 unstaged)", res5.stdout)
        self.assertNotIn("staged", res5.stdout.splitlines()[2].lower())

    def test_repair_command(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        res = self.run_cmd([GWT_CLI_PATH, "repair"], cwd=main_path)
        self.assertEqual(res.returncode, 0, f"repair failed: {res.stderr}")
        self.assertIn("repair", res.stderr.lower() + res.stdout.lower())

    def test_init_custom_main_branch(self):
        project_path = os.path.join(self.test_dir, "project")

        res = self.run_cmd(
            [
                GWT_CLI_PATH,
                "init",
                self.remote_path,
                project_path,
                "--main",
                "custom-main",
            ]
        )
        self.assertEqual(res.returncode, 0, f"init failed: {res.stderr}")

        main_path = os.path.join(project_path, "custom-main")
        self.assertTrue(os.path.isdir(main_path))
        self.assertTrue(os.path.isfile(os.path.join(main_path, "README.md")))

    def test_go_command_success(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        # Create a feature worktree
        self.run_cmd([GWT_CLI_PATH, "new", "feature/test"], cwd=main_path)

        # Test going to main worktree
        res = self.run_cmd([GWT_CLI_PATH, "go", "main"], cwd=main_path)
        self.assertEqual(res.returncode, 0, f"go failed: {res.stderr}")
        self.assertEqual(
            os.path.realpath(res.stdout.strip()), os.path.realpath(main_path)
        )

        # Test going to feature worktree by directory name
        feature_path = os.path.join(project_path, "feature-test")
        res = self.run_cmd([GWT_CLI_PATH, "go", "feature-test"], cwd=main_path)
        self.assertEqual(res.returncode, 0, f"go failed: {res.stderr}")
        self.assertEqual(
            os.path.realpath(res.stdout.strip()), os.path.realpath(feature_path)
        )

        # Test going to feature worktree by branch name
        res = self.run_cmd([GWT_CLI_PATH, "go", "feature/test"], cwd=main_path)
        self.assertEqual(res.returncode, 0, f"go failed: {res.stderr}")
        self.assertEqual(
            os.path.realpath(res.stdout.strip()), os.path.realpath(feature_path)
        )

    def test_go_command_not_found(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        # Test going to non-existent worktree
        res = self.run_cmd([GWT_CLI_PATH, "go", "nonexistent"], cwd=main_path)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("not found", res.stderr)

    def test_init_shell_output(self):
        res_zsh = self.run_cmd([GWT_CLI_PATH, "init-shell", "zsh"])
        self.assertEqual(res_zsh.returncode, 0)
        self.assertIn("function wt", res_zsh.stdout)
        self.assertIn("_wt_zsh()", res_zsh.stdout)
        self.assertIn("compdef _wt_zsh wt", res_zsh.stdout)

        res_bash = self.run_cmd([GWT_CLI_PATH, "init-shell", "bash"])
        self.assertEqual(res_bash.returncode, 0)
        self.assertIn("function wt", res_bash.stdout)
        self.assertIn("_wt_bash()", res_bash.stdout)
        self.assertIn("complete -F _wt_bash wt", res_bash.stdout)

    def test_version_output(self):
        res = self.run_cmd([GWT_CLI_PATH, "--version"])
        self.assertEqual(res.returncode, 0)
        output = res.stdout + res.stderr
        self.assertRegex(output, r"\d+\.\d+\.\d+")

        res_v = self.run_cmd([GWT_CLI_PATH, "-v"])
        self.assertEqual(res_v.returncode, 0)
        output_v = res_v.stdout + res_v.stderr
        self.assertRegex(output_v, r"\d+\.\d+\.\d+")

    def test_delete_clean_merged_worktree(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        feat_path = os.path.join(project_path, "feature-test-delete")

        # Create worktree
        self.run_cmd([GWT_CLI_PATH, "new", "feature/test-delete"], cwd=main_path)

        # Merge it into main (clean and merged)
        self.run_cmd(["git", "merge", "feature/test-delete"], cwd=main_path)

        # Run delete
        res = self.run_cmd(
            [GWT_CLI_PATH, "delete", "feature/test-delete"], cwd=main_path
        )
        self.assertEqual(res.returncode, 0, f"delete failed: {res.stderr}")
        self.assertIn("Successfully deleted", res.stderr)

        # Verify worktree is removed
        self.assertFalse(os.path.exists(feat_path))

        # Verify branch is deleted
        branches = self.run_cmd(["git", "branch"], cwd=main_path).stdout
        self.assertNotIn("feature/test-delete", branches)

    def test_delete_dirty_worktree_aborted_or_approved(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        feat_path = os.path.join(project_path, "feature-test-delete")

        # Create worktree
        self.run_cmd([GWT_CLI_PATH, "new", "feature/test-delete"], cwd=main_path)

        # Make dirty
        dirty_file = os.path.join(feat_path, "dirty.txt")
        with open(dirty_file, "w") as f:
            f.write("uncommitted state\n")

        # Run delete and abort (input "n")
        res = self.run_cmd(
            [GWT_CLI_PATH, "delete", "feature/test-delete"],
            cwd=main_path,
            input_str="n\n",
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("has uncommitted changes", res.stderr)
        self.assertIn("Deletion aborted", res.stderr)
        self.assertTrue(os.path.exists(feat_path))

        # Run delete and approve (input "y")
        res2 = self.run_cmd(
            [GWT_CLI_PATH, "delete", "feature/test-delete"],
            cwd=main_path,
            input_str="y\n",
        )
        self.assertEqual(res2.returncode, 0, f"delete failed: {res2.stderr}")
        self.assertIn("Successfully deleted", res2.stderr)
        self.assertFalse(os.path.exists(feat_path))

    def test_delete_unmerged_worktree_aborted_or_approved(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        feat_path = os.path.join(project_path, "feature-test-delete")

        # Create worktree
        self.run_cmd([GWT_CLI_PATH, "new", "feature/test-delete"], cwd=main_path)

        # Make a commit in feature worktree to make it unmerged
        with open(os.path.join(feat_path, "feat.txt"), "w") as f:
            f.write("feat\n")
        self.run_cmd(["git", "add", "feat.txt"], cwd=feat_path)
        self.run_cmd(["git", "commit", "-m", "add feat"], cwd=feat_path)

        # Run delete and abort (input "n")
        res = self.run_cmd(
            [GWT_CLI_PATH, "delete", "feature/test-delete"],
            cwd=main_path,
            input_str="n\n",
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("is not merged into main", res.stderr)
        self.assertIn("Deletion aborted", res.stderr)
        self.assertTrue(os.path.exists(feat_path))

        # Run delete and approve (input "y")
        res2 = self.run_cmd(
            [GWT_CLI_PATH, "delete", "feature/test-delete"],
            cwd=main_path,
            input_str="y\n",
        )
        self.assertEqual(res2.returncode, 0, f"delete failed: {res2.stderr}")
        self.assertIn("Successfully deleted", res2.stderr)
        self.assertFalse(os.path.exists(feat_path))

    def test_delete_with_force_flag(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")
        feat_path = os.path.join(project_path, "feature-test-delete")

        # Create worktree
        self.run_cmd([GWT_CLI_PATH, "new", "feature/test-delete"], cwd=main_path)

        # Add commit (unmerged) and dirty file
        with open(os.path.join(feat_path, "feat.txt"), "w") as f:
            f.write("feat\n")
        self.run_cmd(["git", "add", "feat.txt"], cwd=feat_path)
        self.run_cmd(["git", "commit", "-m", "add feat"], cwd=feat_path)

        with open(os.path.join(feat_path, "dirty.txt"), "w") as f:
            f.write("dirty\n")

        # Run delete with force flag -- no prompts
        res = self.run_cmd(
            [GWT_CLI_PATH, "delete", "feature/test-delete", "--force"], cwd=main_path
        )
        self.assertEqual(res.returncode, 0, f"delete failed: {res.stderr}")
        self.assertIn("Successfully deleted", res.stderr)
        self.assertFalse(os.path.exists(feat_path))

        # Test rm alias as well
        self.run_cmd([GWT_CLI_PATH, "new", "feature/test-rm"], cwd=main_path)
        res_rm = self.run_cmd(
            [GWT_CLI_PATH, "rm", "feature/test-rm", "-f"], cwd=main_path
        )
        self.assertEqual(res_rm.returncode, 0, f"rm failed: {res_rm.stderr}")
        self.assertFalse(os.path.exists(os.path.join(project_path, "feature-test-rm")))

    def test_delete_prevent_main_or_active(self):
        project_path = os.path.join(self.test_dir, "project")
        self.init_project(project_path)

        main_path = os.path.join(project_path, "main")

        # Try to delete main
        res = self.run_cmd([GWT_CLI_PATH, "delete", "main"], cwd=main_path)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Cannot delete the main branch worktree", res.stderr)

        # Create a feature worktree
        self.run_cmd([GWT_CLI_PATH, "new", "feature/test-delete"], cwd=main_path)
        feat_path = os.path.join(project_path, "feature-test-delete")

        # Run command from inside feature worktree and try to delete it
        res2 = self.run_cmd(
            [GWT_CLI_PATH, "delete", "feature-test-delete"], cwd=feat_path
        )
        self.assertNotEqual(res2.returncode, 0)
        self.assertIn("Cannot delete the active worktree", res2.stderr)


if __name__ == "__main__":
    unittest.main()
