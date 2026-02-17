"""Issue storage service backed by storage-provider."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import Any

from storage_provider import StorageProvider
from storage_provider.exceptions import StorageNotFoundError

# Default user for all operations (no real user system).
DEFAULT_USER = {
    "login": "local-user",
    "id": 1,
    "node_id": "U_local1",
    "avatar_url": "",
    "gravatar_id": "",
    "url": "",
    "html_url": "",
    "followers_url": "",
    "following_url": "",
    "gists_url": "",
    "starred_url": "",
    "subscriptions_url": "",
    "organizations_url": "",
    "repos_url": "",
    "events_url": "",
    "received_events_url": "",
    "type": "User",
    "site_admin": False,
}


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_user(login: str, base_url: str) -> dict[str, Any]:
    """Build a simple-user dict for a given login."""
    return {
        "login": login,
        "id": abs(hash(login)) % 10_000_000,
        "node_id": f"U_{login}",
        "avatar_url": "",
        "gravatar_id": "",
        "url": f"{base_url}/users/{login}",
        "html_url": f"{base_url}/users/{login}",
        "followers_url": f"{base_url}/users/{login}/followers",
        "following_url": f"{base_url}/users/{login}/following{{/other_user}}",
        "gists_url": f"{base_url}/users/{login}/gists{{/gist_id}}",
        "starred_url": f"{base_url}/users/{login}/starred{{/owner}}{{/repo}}",
        "subscriptions_url": f"{base_url}/users/{login}/subscriptions",
        "organizations_url": f"{base_url}/users/{login}/orgs",
        "repos_url": f"{base_url}/users/{login}/repos",
        "events_url": f"{base_url}/users/{login}/events{{/privacy}}",
        "received_events_url": f"{base_url}/users/{login}/received_events",
        "type": "User",
        "site_admin": False,
    }


def _make_label(name: str, label_id: int, base_url: str, owner: str, repo: str) -> dict[str, Any]:
    """Build a label object from a name string."""
    return {
        "id": label_id,
        "node_id": f"LA_{label_id}",
        "url": f"{base_url}/repos/{owner}/{repo}/labels/{name}",
        "name": name,
        "description": None,
        "color": "ededed",
        "default": False,
    }


def _issue_urls(base_url: str, owner: str, repo: str, number: int) -> dict[str, str]:
    """Generate all URL fields for an issue."""
    repo_url = f"{base_url}/repos/{owner}/{repo}"
    issue_url = f"{repo_url}/issues/{number}"
    return {
        "url": issue_url,
        "repository_url": repo_url,
        "labels_url": f"{issue_url}/labels{{/name}}",
        "comments_url": f"{issue_url}/comments",
        "events_url": f"{issue_url}/events",
        "html_url": issue_url,
    }


class IssueStore:
    """CRUD operations for issues, persisted via a StorageProvider."""

    def __init__(self, storage: StorageProvider) -> None:
        self._storage = storage

    # -- path helpers -------------------------------------------------------

    @staticmethod
    def _issue_path(owner: str, repo: str, number: int) -> str:
        return f"repos/{owner}/{repo}/issues/{number}/issue.json"

    @staticmethod
    def _counter_path(owner: str, repo: str) -> str:
        return f"repos/{owner}/{repo}/counter.txt"

    @staticmethod
    def _comment_path(owner: str, repo: str, comment_id: int) -> str:
        return f"repos/{owner}/{repo}/comments/{comment_id}/comment.json"

    @staticmethod
    def _comment_counter_path(owner: str, repo: str) -> str:
        return f"repos/{owner}/{repo}/comment_counter.txt"

    # -- internal helpers ---------------------------------------------------

    def _next_number(self, owner: str, repo: str) -> int:
        path = self._counter_path(owner, repo)
        current = 0
        if self._storage.exists(path):
            current = int(self._storage.read(path).decode().strip())
        next_num = current + 1
        self._storage.write(path, str(next_num).encode())
        return next_num

    def _read_issue(self, owner: str, repo: str, number: int) -> dict[str, Any] | None:
        path = self._issue_path(owner, repo, number)
        try:
            data = self._storage.read(path)
        except StorageNotFoundError:
            return None
        return json.loads(data)

    def _write_issue(self, owner: str, repo: str, number: int, issue: dict[str, Any]) -> None:
        path = self._issue_path(owner, repo, number)
        self._storage.write(path, json.dumps(issue, ensure_ascii=False).encode())

    def _list_repos(self) -> list[tuple[str, str]]:
        """Return all (owner, repo) pairs that have issues."""
        repos: list[tuple[str, str]] = []
        try:
            owners = self._storage.list("repos/")
        except StorageNotFoundError:
            return repos
        for owner_entry in owners:
            owner = owner_entry.rstrip("/")
            try:
                repo_entries = self._storage.list(f"repos/{owner}/")
            except StorageNotFoundError:
                continue
            for repo_entry in repo_entries:
                repos.append((owner, repo_entry.rstrip("/")))
        return repos

    def _list_issue_numbers(self, owner: str, repo: str) -> list[int]:
        """Return all issue numbers for a repo, sorted ascending."""
        try:
            entries = self._storage.list(f"repos/{owner}/{repo}/issues/")
        except StorageNotFoundError:
            return []
        numbers: list[int] = []
        for entry in entries:
            name = entry.rstrip("/")
            if name.isdigit():
                numbers.append(int(name))
        numbers.sort()
        return numbers

    def _next_comment_id(self, owner: str, repo: str) -> int:
        path = self._comment_counter_path(owner, repo)
        current = 0
        if self._storage.exists(path):
            current = int(self._storage.read(path).decode().strip())
        next_id = current + 1
        self._storage.write(path, str(next_id).encode())
        return next_id

    def _read_comment(self, owner: str, repo: str, comment_id: int) -> dict[str, Any] | None:
        path = self._comment_path(owner, repo, comment_id)
        try:
            data = self._storage.read(path)
        except StorageNotFoundError:
            return None
        return json.loads(data)

    def _write_comment(self, owner: str, repo: str, comment_id: int, comment: dict[str, Any]) -> None:
        path = self._comment_path(owner, repo, comment_id)
        self._storage.write(path, json.dumps(comment, ensure_ascii=False).encode())

    def _list_comment_ids(self, owner: str, repo: str) -> list[int]:
        """Return all comment IDs for a repo, sorted ascending."""
        try:
            entries = self._storage.list(f"repos/{owner}/{repo}/comments/")
        except StorageNotFoundError:
            return []
        ids: list[int] = []
        for entry in entries:
            name = entry.rstrip("/")
            if name.isdigit():
                ids.append(int(name))
        ids.sort()
        return ids

    # -- public API ---------------------------------------------------------

    def create(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str | None,
        labels: list[str] | None,
        assignee: str | None,
        assignees: list[str] | None,
        base_url: str,
    ) -> dict[str, Any]:
        """Create an issue and return the full issue dict."""
        number = self._next_number(owner, repo)
        now = _now_iso()

        urls = _issue_urls(base_url, owner, repo, number)
        user = {
            **DEFAULT_USER,
            "url": f"{base_url}/users/local-user",
            "html_url": f"{base_url}/users/local-user",
        }

        # Build label objects.
        label_objects: list[dict[str, Any]] = []
        if labels:
            for i, name in enumerate(labels):
                label_objects.append(_make_label(name, number * 100 + i, base_url, owner, repo))

        # Build assignee objects.
        assignee_objects: list[dict[str, Any]] = []
        if assignees:
            assignee_objects = [_make_user(a, base_url) for a in assignees]
        elif assignee:
            assignee_objects = [_make_user(assignee, base_url)]

        issue: dict[str, Any] = {
            "id": number,
            "node_id": f"I_{number}",
            "number": number,
            **urls,
            "state": "open",
            "state_reason": None,
            "title": title,
            "body": body,
            "user": user,
            "labels": label_objects,
            "assignee": assignee_objects[0] if assignee_objects else None,
            "assignees": assignee_objects or [],
            "milestone": None,
            "locked": False,
            "active_lock_reason": None,
            "comments": 0,
            "created_at": now,
            "updated_at": now,
            "closed_at": None,
            "closed_by": None,
            "author_association": "OWNER",
        }

        self._write_issue(owner, repo, number, issue)
        return issue

    def get(self, owner: str, repo: str, number: int) -> dict[str, Any] | None:
        """Get a single issue, or None if not found."""
        return self._read_issue(owner, repo, number)

    def update(
        self,
        owner: str,
        repo: str,
        number: int,
        changes: dict[str, Any],
        base_url: str,
    ) -> dict[str, Any] | None:
        """Update an issue from a dict of changed fields.

        ``changes`` should contain only the keys that were explicitly provided
        in the PATCH request body.  Keys not present are left untouched.
        """
        issue = self._read_issue(owner, repo, number)
        if issue is None:
            return None

        if "title" in changes and changes["title"] is not None:
            issue["title"] = str(changes["title"])

        if "body" in changes:
            issue["body"] = changes["body"]

        if "state" in changes and changes["state"] is not None:
            old_state = issue["state"]
            new_state = changes["state"]
            issue["state"] = new_state

            if "state_reason" in changes:
                issue["state_reason"] = changes["state_reason"]
            elif new_state == "closed" and old_state != "closed":
                issue["state_reason"] = "completed"
            elif new_state == "open" and old_state != "open":
                issue["state_reason"] = "reopened"

            if new_state == "closed" and old_state != "closed":
                issue["closed_at"] = _now_iso()
                issue["closed_by"] = issue.get("user")
            elif new_state == "open" and old_state != "open":
                issue["closed_at"] = None
                issue["closed_by"] = None
        elif "state_reason" in changes:
            issue["state_reason"] = changes["state_reason"]

        if "labels" in changes:
            raw_labels = changes["labels"]
            if raw_labels is None:
                issue["labels"] = []
            else:
                issue["labels"] = [
                    _make_label(name, number * 100 + i, base_url, owner, repo) for i, name in enumerate(raw_labels)
                ]

        if "assignees" in changes:
            raw = changes["assignees"]
            if raw is None:
                issue["assignees"] = []
                issue["assignee"] = None
            else:
                issue["assignees"] = [_make_user(a, base_url) for a in raw]
                issue["assignee"] = issue["assignees"][0] if issue["assignees"] else None
        elif "assignee" in changes:
            raw = changes["assignee"]
            if raw is None:
                issue["assignees"] = []
                issue["assignee"] = None
            else:
                user_obj = _make_user(raw, base_url)
                issue["assignee"] = user_obj
                issue["assignees"] = [user_obj]

        issue["updated_at"] = _now_iso()
        self._write_issue(owner, repo, number, issue)
        return issue

    def list_for_repo(
        self,
        owner: str,
        repo: str,
        *,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        labels: str | None = None,
        since: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """List issues for a specific repo with filtering, sorting, pagination."""
        numbers = self._list_issue_numbers(owner, repo)
        issues: list[dict[str, Any]] = []
        for num in numbers:
            issue = self._read_issue(owner, repo, num)
            if issue is None:
                continue
            # State filter.
            if state != "all" and issue.get("state") != state:
                continue
            # Labels filter (comma-separated label names, all must match).
            if labels:
                required = {lbl_name.strip() for lbl_name in labels.split(",")}
                issue_labels = {
                    lbl.get("name", "") if isinstance(lbl, dict) else str(lbl) for lbl in issue.get("labels", [])
                }
                if not required.issubset(issue_labels):
                    continue
            # Since filter.
            if since and issue.get("updated_at", "") < since:
                continue
            issues.append(issue)

        # Sort.
        sort_key = sort if sort in ("created", "updated", "comments") else "created"
        key_map = {
            "created": "created_at",
            "updated": "updated_at",
            "comments": "comments",
        }
        issues.sort(
            key=lambda i: i.get(key_map[sort_key], ""),
            reverse=(direction == "desc"),
        )

        # Paginate.
        start = (page - 1) * per_page
        return issues[start : start + per_page]

    def list_all(
        self,
        *,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        labels: str | None = None,
        since: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """List issues across all repos."""
        all_issues: list[dict[str, Any]] = []
        for owner, repo in self._list_repos():
            all_issues.extend(
                self.list_for_repo(
                    owner,
                    repo,
                    state=state,
                    sort=sort,
                    direction=direction,
                    labels=labels,
                    since=since,
                    per_page=999_999,
                    page=1,
                )
            )

        # Re-sort the combined list.
        sort_key = sort if sort in ("created", "updated", "comments") else "created"
        key_map = {
            "created": "created_at",
            "updated": "updated_at",
            "comments": "comments",
        }
        all_issues.sort(
            key=lambda i: i.get(key_map[sort_key], ""),
            reverse=(direction == "desc"),
        )

        start = (page - 1) * per_page
        return all_issues[start : start + per_page]

    def list_for_org(
        self,
        org: str,
        *,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        labels: str | None = None,
        since: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """List issues for repos owned by a given org."""
        all_issues: list[dict[str, Any]] = []
        for owner, repo in self._list_repos():
            if owner != org:
                continue
            all_issues.extend(
                self.list_for_repo(
                    owner,
                    repo,
                    state=state,
                    sort=sort,
                    direction=direction,
                    labels=labels,
                    since=since,
                    per_page=999_999,
                    page=1,
                )
            )

        sort_key = sort if sort in ("created", "updated", "comments") else "created"
        key_map = {
            "created": "created_at",
            "updated": "updated_at",
            "comments": "comments",
        }
        all_issues.sort(
            key=lambda i: i.get(key_map[sort_key], ""),
            reverse=(direction == "desc"),
        )

        start = (page - 1) * per_page
        return all_issues[start : start + per_page]

    def search(
        self,
        query: str,
        *,
        sort: str | None = None,
        order: str = "desc",
        per_page: int = 30,
        page: int = 1,
    ) -> dict[str, Any]:
        """Basic text search across all issues. Returns search-result envelope."""
        q_lower = query.lower()
        matches: list[dict[str, Any]] = []
        for owner, repo in self._list_repos():
            for num in self._list_issue_numbers(owner, repo):
                issue = self._read_issue(owner, repo, num)
                if issue is None:
                    continue
                title = (issue.get("title") or "").lower()
                body = (issue.get("body") or "").lower()
                if q_lower in title or q_lower in body:
                    result = {**issue, "score": 1.0}
                    matches.append(result)

        # Sort if requested.
        if sort == "created":
            matches.sort(
                key=lambda i: i.get("created_at", ""),
                reverse=(order == "desc"),
            )
        elif sort == "updated":
            matches.sort(
                key=lambda i: i.get("updated_at", ""),
                reverse=(order == "desc"),
            )
        elif sort == "comments":
            matches.sort(
                key=lambda i: i.get("comments", 0),
                reverse=(order == "desc"),
            )

        total = len(matches)
        start = (page - 1) * per_page
        items = matches[start : start + per_page]

        return {
            "total_count": total,
            "incomplete_results": False,
            "items": items,
        }

    # -- Comment API --------------------------------------------------------

    def create_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
        base_url: str,
    ) -> dict[str, Any] | None:
        """Create a comment on an issue. Returns None if the issue doesn't exist."""
        issue = self._read_issue(owner, repo, issue_number)
        if issue is None:
            return None

        comment_id = self._next_comment_id(owner, repo)
        now = _now_iso()
        user = {
            **DEFAULT_USER,
            "url": f"{base_url}/users/local-user",
            "html_url": f"{base_url}/users/local-user",
        }

        comment: dict[str, Any] = {
            "id": comment_id,
            "node_id": f"IC_{comment_id}",
            "url": f"{base_url}/repos/{owner}/{repo}/issues/comments/{comment_id}",
            "html_url": f"{base_url}/repos/{owner}/{repo}/issues/comments/{comment_id}",
            "issue_url": f"{base_url}/repos/{owner}/{repo}/issues/{issue_number}",
            "user": user,
            "created_at": now,
            "updated_at": now,
            "body": body,
            "author_association": "OWNER",
            "performed_via_github_app": None,
            "reactions": None,
            # Internal field for filtering by issue.
            "issue_number": issue_number,
        }

        self._write_comment(owner, repo, comment_id, comment)

        # Increment the issue's comment count.
        issue["comments"] = issue.get("comments", 0) + 1
        issue["updated_at"] = now
        self._write_issue(owner, repo, issue_number, issue)

        return comment

    def get_comment(self, owner: str, repo: str, comment_id: int) -> dict[str, Any] | None:
        """Get a single comment, or None if not found."""
        return self._read_comment(owner, repo, comment_id)

    def update_comment(
        self,
        owner: str,
        repo: str,
        comment_id: int,
        body: str,
        base_url: str,
    ) -> dict[str, Any] | None:
        """Update a comment's body. Returns None if not found."""
        comment = self._read_comment(owner, repo, comment_id)
        if comment is None:
            return None

        comment["body"] = body
        comment["updated_at"] = _now_iso()
        self._write_comment(owner, repo, comment_id, comment)
        return comment

    def delete_comment(self, owner: str, repo: str, comment_id: int) -> bool:
        """Delete a comment. Returns False if not found."""
        comment = self._read_comment(owner, repo, comment_id)
        if comment is None:
            return False

        # Decrement the parent issue's comment count.
        issue_number = comment.get("issue_number")
        if issue_number is not None:
            issue = self._read_issue(owner, repo, issue_number)
            if issue is not None:
                issue["comments"] = max(0, issue.get("comments", 0) - 1)
                issue["updated_at"] = _now_iso()
                self._write_issue(owner, repo, issue_number, issue)

        self._storage.delete(self._comment_path(owner, repo, comment_id))
        return True

    def list_comments_for_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        *,
        since: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]] | None:
        """List comments for a specific issue. Returns None if the issue doesn't exist."""
        issue = self._read_issue(owner, repo, issue_number)
        if issue is None:
            return None

        comments: list[dict[str, Any]] = []
        for cid in self._list_comment_ids(owner, repo):
            comment = self._read_comment(owner, repo, cid)
            if comment is None:
                continue
            if comment.get("issue_number") != issue_number:
                continue
            if since and comment.get("updated_at", "") < since:
                continue
            comments.append(comment)

        # Comments for an issue are always sorted by created_at ascending.
        comments.sort(key=lambda c: c.get("created_at", ""))

        start = (page - 1) * per_page
        return comments[start : start + per_page]

    def list_comments_for_repo(
        self,
        owner: str,
        repo: str,
        *,
        sort: str = "created",
        direction: str = "desc",
        since: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """List all comments for a repo with sorting and pagination."""
        comments: list[dict[str, Any]] = []
        for cid in self._list_comment_ids(owner, repo):
            comment = self._read_comment(owner, repo, cid)
            if comment is None:
                continue
            if since and comment.get("updated_at", "") < since:
                continue
            comments.append(comment)

        sort_field = "updated_at" if sort == "updated" else "created_at"
        comments.sort(
            key=lambda c: c.get(sort_field, ""),
            reverse=(direction == "desc"),
        )

        start = (page - 1) * per_page
        return comments[start : start + per_page]

    def pin_comment(self, owner: str, repo: str, comment_id: int) -> dict[str, Any] | None:
        """Pin a comment. Returns None if not found."""
        comment = self._read_comment(owner, repo, comment_id)
        if comment is None:
            return None

        comment["pinned"] = True
        comment["updated_at"] = _now_iso()
        self._write_comment(owner, repo, comment_id, comment)
        return comment

    def unpin_comment(self, owner: str, repo: str, comment_id: int) -> bool:
        """Unpin a comment. Returns False if not found."""
        comment = self._read_comment(owner, repo, comment_id)
        if comment is None:
            return False

        comment["pinned"] = False
        comment["updated_at"] = _now_iso()
        self._write_comment(owner, repo, comment_id, comment)
        return True
