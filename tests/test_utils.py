from fusor.utils import is_git_repo

def test_is_git_repo_detects_parent(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    sub = repo / "sub" / "dir"
    sub.mkdir(parents=True)
    assert is_git_repo(str(sub))

def test_is_git_repo_false(tmp_path):
    path = tmp_path / "no_repo"
    path.mkdir()
    assert not is_git_repo(str(path))
