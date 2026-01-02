# PyAttackForge

A lightweight Python library for interacting with the AttackForge API.

---

## Features

- Create and fetch projects
- Manage users (create, update, activate/deactivate, access, audit logs)
- Manage assets
- Submit vulnerabilities
- Create findings from existing writeups by passing a `writeup_id`
- Upload evidence to findings or testcases
- Update/assign testcases to link findings or add notes
- Link vulnerabilities to testcases via the client
- Dry-run mode for testing

---

## Install

   ```bash
   mkdir PyAttackForgeEnv
   cd PyAttackForgeEnv
   virtualenv venv
   source ./venv/bin/activate
   pip install git+https://github.com/Tantalum-Labs/PyAttackForge.git
   ```

## Use

   ```python
   from pyattackforge import PyAttackForgeClient

   # Initialize client - Note: Make sure to set your AttackForge URL and API Key
   client = PyAttackForgeClient(api_key="your-api-key", base_url="https://demo.attackforge.com", dry_run=False)

   # Create a project
   project = client.create_project("My Project", scope=["Asset1", "Asset2"])

   ## Create a security finding (vulnerability)
   client.create_vulnerability(
       project_id="abc123",
       title="Open SSH Port",
       affected_assets=[{"name": "ssh-prod-1"}],
       priority="High",
       likelihood_of_exploitation=10,
       description="SSH port 22 is open to the internet.",
       attack_scenario="An attacker can brute-force SSH credentials.",
       remediation_recommendation="Restrict SSH access to trusted IPs.",
       steps_to_reproduce="1. Scan the host\n2. Observe port 22 is open",
       writeup_id="68e92c7a821c05c8405a8003",  # optional: use an existing writeup
       tags=["ssh", "exposure"],
       notes=["Observed on 2025-09-09"],
       is_zeroday=False,
       is_visible=True
   )

   ```

---

## Creating Security Findings

To create a security finding (vulnerability) in AttackForge, use the `create_vulnerability` method:

```python
client.create_vulnerability(
    project_id="abc123",
    title="Open SSH Port",
    affected_assets=[{"name": "ssh-prod-1"}],
    priority="High",
    likelihood_of_exploitation=10,
    description="SSH port 22 is open to the internet.",
    attack_scenario="An attacker can brute-force SSH credentials.",
    remediation_recommendation="Restrict SSH access to trusted IPs.",
    steps_to_reproduce="1. Scan the host\n2. Observe port 22 is open",
    writeup_id="68e92c7a821c05c8405a8003",  # optional: reuse an existing writeup
    tags=["ssh", "exposure"],
    notes=["Observed on 2025-09-09"],
    is_zeroday=False,
    is_visible=True
)
```

### Creating a finding from an existing writeup

If you already have a writeup/library entry and just need to create a finding bound to it, you can either pass `writeup_id` to `create_vulnerability` (as above) or call `create_finding_from_writeup` directly. Prefer the 24-character writeup id (`id` / `_id`); if only a numeric `reference_id` is available, use that. You can also specify the library key (e.g., `approved_writeups`, `Main Vulnerabilities`):

```python
client.create_finding_from_writeup(
    project_id="abc123",
    writeup_id="68e92c7a821c05c8405a8003",  # writeup id
    library="approved_writeups",             # optional: library key/name
    priority="High",
    affected_assets=[{"name": "ssh-prod-1"}],
    linked_testcases=["5e8017d2e1385f0c58e8f4f8"],  # optional: link testcases at creation
    likelihood_of_exploitation=5,
    steps_to_reproduce="1. Do something\n2. Observe result",
    notes=[{"note": "Created via API", "type": "PLAINTEXT"}],
    tags=["automation"]
)
```

## User Management

Create a user:
```python
client.create_user(
    first_name="John",
    last_name="Citizen",
    username="john.citizen@attackforge.com",
    email="john.citizen@attackforge.com",
    password="ThisIsASuperLongPassword",
    role="client",
    mfa="Yes",
)
```

Activate or deactivate a user:
```python
client.activate_user("5eacb8450c8d520a8281e539")
client.deactivate_user("5eacb8450c8d520a8281e539")
```

Fetch users:
```python
users = client.get_users(email="john.citizen@attackforge.com")
user = client.get_user_by_email("john.citizen@attackforge.com")
```

Invite users to a project:
```python
client.invite_user_to_project(
    project_id="abc123",
    username="user@attackforge.com",
    access_level="Edit",
    role="Pentester",
)
```

### Evidence and testcase helpers

Upload evidence to an existing finding:
```python
client.upload_finding_evidence(
    vulnerability_id="6768d29db1782d7362a2df5f",
    file_path="evidence.png"
)
```

Upload evidence to a testcase:
```python
client.upload_testcase_evidence(
    project_id="abc123",
    testcase_id="5e8017d2e1385f0c58e8f4f8",
    file_path="testcase-evidence.png"
)
```

Add a note to a finding (deduplicates by note text):
```python
client.add_note_to_finding(
    vulnerability_id="6768d29db1782d7362a2df5f",
    note="Observed during retest on 2025-09-19."
)
```

Add a note/update to a testcase (PUT to the testcase endpoint):
```python
client.add_note_to_testcase(
    project_id="abc123",
    testcase_id="5e8017d2e1385f0c58e8f4f8",
    note="Observed during retest on 2025-09-19.",
    status="Tested"  # optional
)
```

Associate findings to a testcase:
```python
client.assign_findings_to_testcase(
    project_id="abc123",
    testcase_id="5e8017d2e1385f0c58e8f4f8",
    vulnerability_ids=["66849b77950ab45e68fc7b48", "6768d29db1782d7362a2df5f"],
    additional_fields={"status": "Tested"} # optional
)
```
Or link from the vulnerability side using its update endpoint:
```python
client.link_vulnerability_to_testcases(
    vulnerability_id="69273ef0f4a7c85d03930667",
    testcase_ids=["5e8017d2e1385f0c58e8f4f8"],
    project_id="abc123",  # optional
)
```

Fetch project testcases:
```python
testcases = client.get_testcases("abc123")
```

Fetch a single testcase (if supported in your tenant):
```python
testcase = client.get_testcase("abc123", "5e8017d2e1385f0c58e8f4f8")
```

Merge and add findings to a testcase in one call:
```python
client.add_findings_to_testcase(
    project_id="abc123",
    testcase_id="5e8017d2e1385f0c58e8f4f8",
    vulnerability_ids=["69273ef0f4a7c85d03930667"],
    additional_fields={"status": "Tested"} # optional
)
```

**Parameters:**
- `project_id` (str): The project ID.
- `title` (str): The title of the finding.
- `affected_assets` (list): List of affected assets (e.g., `[{"name": "host1"}]`).
- `priority` (str): The priority (e.g., "Critical", "High", "Medium", "Low").
- `likelihood_of_exploitation` (int): Likelihood of exploitation (e.g., 10).
- `description` (str): Description of the finding.
- `attack_scenario` (str): Attack scenario details.
- `remediation_recommendation` (str): Remediation recommendation.
- `steps_to_reproduce` (str): Steps to reproduce the finding.
- `writeup_id` (str, optional): Existing writeup/library reference ID to use directly.
- `tags` (list, optional): List of tags.
- `notes` (list, optional): List of notes.
- `is_zeroday` (bool, optional): Whether this is a zero-day finding.
- `is_visible` (bool, optional): Whether the finding is visible.
- `import_to_library` (str, optional): Library to import to.
- `import_source` (str, optional): Source of import.
- `import_source_id` (str, optional): Source ID for import.
- `custom_fields` (list, optional): List of custom fields.
- `linked_testcases` (list, optional): List of linked testcases.
- `custom_tags` (list, optional): List of custom tags.

See the source code for full details and docstrings.

---

## API Reference

### `PyAttackForgeClient`

- `__init__(api_key: str, base_url: str = ..., dry_run: bool = False)`
- `get_assets() -> dict`
- `get_asset_by_name(name: str) -> dict or None`
- `create_asset(asset_data: dict) -> dict`
- `get_project_by_name(name: str) -> dict or None`
- `get_project_scope(project_id: str) -> set`
- `update_project_scope(project_id: str, new_assets: list) -> dict`
- `create_project(name: str, **kwargs) -> dict`
- `update_project(project_id: str, update_fields: dict) -> dict`
- `create_vulnerability(
      project_id: str,
      title: str,
      affected_assets: list,
      priority: str,
      likelihood_of_exploitation: int,
      description: str,
      attack_scenario: str,
      remediation_recommendation: str,
      steps_to_reproduce: str,
      tags: Optional[list] = None,
      notes: Optional[list] = None,
      is_zeroday: bool = False,
      is_visible: bool = True,
      import_to_library: Optional[str] = None,
      import_source: Optional[str] = None,
      import_source_id: Optional[str] = None,
      custom_fields: Optional[list] = None,
      linked_testcases: Optional[list] = None,
      custom_tags: Optional[list] = None,
      writeup_custom_fields: Optional[list] = None,
  ) -> dict`
- `create_finding_from_writeup(project_id: str, writeup_id: str, priority: str, affected_assets: Optional[list] = None, linked_testcases: Optional[list] = None, **kwargs) -> dict`
- `create_user(first_name: str, last_name: str, username: str, email: str, password: str, role: str, mfa: str) -> dict`
- `create_users(users: List[Dict[str, Any]]) -> Any`
- `get_findings_for_project(project_id: str, priority: Optional[str] = None) -> list`
- `upsert_finding_for_project(...)`
- `get_user(user_id: str) -> dict`
- `get_user_by_email(email: str) -> dict`
- `get_user_by_username(username: str) -> dict`
- `get_users(first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None, username: Optional[str] = None) -> list`
- `get_vulnerability(vulnerability_id: str) -> dict`
- `add_note_to_finding(vulnerability_id: str, note: Any, note_type: str = "PLAINTEXT") -> dict`
- `upload_finding_evidence(vulnerability_id: str, file_path: str) -> dict`
- `upload_testcase_evidence(project_id: str, testcase_id: str, file_path: str) -> dict`
- `get_testcases(project_id: str) -> list`
- `get_testcase(project_id: str, testcase_id: str) -> dict or None`
- `link_vulnerability_to_testcases(vulnerability_id: str, testcase_ids: List[str], project_id: Optional[str] = None) -> dict`
- `assign_findings_to_testcase(project_id: str, testcase_id: str, vulnerability_ids: List[str], existing_linked_vulnerabilities: Optional[List[str]] = None, additional_fields: Optional[Dict[str, Any]] = None) -> dict`
- `add_findings_to_testcase(project_id: str, testcase_id: str, vulnerability_ids: List[str], additional_fields: Optional[Dict[str, Any]] = None) -> dict`
- `add_note_to_testcase(project_id: str, testcase_id: str, note: str, status: Optional[str] = None) -> dict`
- `update_user(user_id: str, first_name: Optional[str] = None, last_name: Optional[str] = None, email_address: Optional[str] = None, username: Optional[str] = None, is_deleted: Optional[bool] = None) -> dict`
- `activate_user(user_id: str) -> dict`
- `deactivate_user(user_id: str) -> dict`
- `add_user_to_group(group_id: str, user_id: str, access_level: str) -> dict`
- `update_user_access_on_group(group_id: str, user_id: str, access_level: str) -> dict`
- `update_user_access_on_project(project_id: str, user_id: str, update_action: str) -> dict`
- `invite_user_to_project(project_id: str, username: str, access_level: str, role: Optional[str] = None) -> dict`
- `invite_users_to_project_team(project_id: str, users: List[Dict[str, Any]]) -> dict`
- `get_user_groups(user_id: str) -> list`
- `get_user_projects(user_id: str) -> list`
- `get_user_audit_logs(user_id: str, skip: Optional[int] = None, limit: Optional[int] = None, include_request_body: Optional[bool] = None, endpoint: Optional[str] = None, method: Optional[str] = None) -> list`
- `get_user_login_history(user_id: str, skip: Optional[int] = None, limit: Optional[int] = None) -> list`

See the source code for full details and docstrings.

---

## Versioning and Changelog

- Current release: `0.1.9`
- See `CHANGELOG.md` for release notes.

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests via GitHub.

- Ensure code is PEP8-compliant and includes docstrings and type hints.
- Add or update tests for new features or bugfixes.
- Do **not** commit API keys or other secrets.

---

## Security

**Never commit your API keys or other sensitive information to version control.**

---

## License

This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html).
