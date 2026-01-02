**What changes are proposed in this pull request?**
<< Insert text here that can be directly copied into CHANGELOG.md by your reviewer. >>

**If there is an GitHub issue associated with this pull request, please provide link.**


--------------------------------------------------------------------------------

Reviewer Checklist (if item does not apply, mark is complete)

- [ ] PR branch has pulled the most recent updates from main branch.
- [ ] If a bug was fixed, a unit test was added.
- [ ] Code coverage is suitable for any new functions/features: `pytest --cov=<package_name> --cov-report=term-missing`
- [ ] Documentation builds without errors: `uv run quartodoc build` (artpack-py uses quartodoc)
- [ ] Code is formatted consistently: `black .`
- [ ] **All** GitHub Action workflows pass with a :white_check_mark:

When the branch is ready to be merged into main:
- [ ] Update `CHANGELOG.qmd` with the changes from this pull request under the heading "`## [Unreleased]`". If there is an issue associated with the pull request, reference it in parentheses at the end of the update (see `CHANGELOG.qmd` for examples).
- [ ] Increment the version number in `pyproject.toml` (or `setup.py`/`__version__.py`) and `CHANGELOG.md` if releasing
- [ ] Run final checks: `pytest`
- [ ] Approve Pull Request
- [ ] Merge the PR. Please use "Squash and merge".