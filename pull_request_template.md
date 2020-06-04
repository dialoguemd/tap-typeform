## Description
<!-- Short summary of your changes. -->
<!-- Add screenshots if needed (simple copy/paste or drag-n-drop will work). -->
<!-- You can also leave notes for code reviewers here. -->

## Author Checklist

- [ ] PR title follows [Commit Convention](https://www.notion.so/godialogue/Commit-Convention-84fd9a4c149e48c998d760f1c9176df0) <!-- `feat(lang): add German language` -->
- [ ] PR title ends with a JIRA issue ID  <!-- `fix: signup error [DIA-000]` -->
- [ ] PR title includes `REFACTOR` if it requires a full validation, such as for the introduction of a new endpoint
- [ ] Discovery mode succeeds locally
- [ ] Sync mode succeeds when pointed at the DEV analytics DB (credentials in 1Password)
- [ ] Updated properties file is committed to the PR, for ease of testing and development
- [ ] PR review requested from groups not individuals <!-- It's better to add whole teams rather than specific people; i.e.: `@dialoguemd/maestro` or `@dialoguemd/s-team`. -->
- [ ] PR link is posted to the corresponding Slack channel <!-- This will quickly draw attention to your PR. -->

## Validator Checklist

- If `REFACTOR`:
	- [ ] Discovery mode succeeds locally
	- [ ] Sync mode succeeds against dev DB
	- [ ] New table in dev DB is well-typed and all columns are properly populated (e.g. some `null` is ok, all `null` for a column is not)
- Else:
	- [ ] New column(s) in dev DB are well-typed and are properly populated (e.g. some `null` is ok, all `null` for a column is not)
