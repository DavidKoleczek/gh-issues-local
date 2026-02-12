# API Spec

Endpoints to implement from the GitHub Issues REST API.
Reference: `ai_working/rest-api-description/descriptions/api.github.com/api.github.com.2022-11-28.json`
The Ref column (e.g., L50633) is the line number in the reference file where the method's OpenAPI definition starts.

## Issues -- Core

| Method | Path | operationId | Summary | Ref |
|--------|------|-------------|---------|-----|
| `GET` | `/issues` | `issues/list` | List issues assigned to the authenticated user | L6019 |
| `GET` | `/orgs/{org}/issues` | `issues/list-for-org` | List organization issues assigned to the authenticated user | L21016 |
| `GET` | `/user/issues` | `issues/list-for-authenticated-user` | List user account issues assigned to the authenticated user | L68646 |
| `GET` | `/repos/{owner}/{repo}/issues` | `issues/list-for-repo` | List repository issues | L50633 |
| `POST` | `/repos/{owner}/{repo}/issues` | `issues/create` | Create an issue | L50783 |
| `GET` | `/repos/{owner}/{repo}/issues/{issue_number}` | `issues/get` | Get an issue | L51663 |
| `PATCH` | `/repos/{owner}/{repo}/issues/{issue_number}` | `issues/update` | Update an issue | L51721 |
| `GET` | `/search/issues` | `search/issues-and-pull-requests` | Search issues and pull requests | L64215 |

## Comments

| Method | Path | operationId | Summary | Ref |
|--------|------|-------------|---------|-----|
| `GET` | `/repos/{owner}/{repo}/issues/comments` | `issues/list-comments-for-repo` | List issue comments for a repository | L50960 |
| `GET` | `/repos/{owner}/{repo}/issues/comments/{comment_id}` | `issues/get-comment` | Get an issue comment | L51044 |
| `PATCH` | `/repos/{owner}/{repo}/issues/comments/{comment_id}` | `issues/update-comment` | Update an issue comment | L51093 |
| `DELETE` | `/repos/{owner}/{repo}/issues/comments/{comment_id}` | `issues/delete-comment` | Delete an issue comment | L51168 |
| `PUT` | `/repos/{owner}/{repo}/issues/comments/{comment_id}/pin` | `issues/pin-comment` | Pin an issue comment | L51204 |
| `DELETE` | `/repos/{owner}/{repo}/issues/comments/{comment_id}/pin` | `issues/unpin-comment` | Unpin an issue comment | L51265 |
| `GET` | `/repos/{owner}/{repo}/issues/{issue_number}/comments` | `issues/list-comments` | List issue comments | L52117 |
| `POST` | `/repos/{owner}/{repo}/issues/{issue_number}/comments` | `issues/create-comment` | Create an issue comment | L52186 |

## Assignees

| Method | Path | operationId | Summary | Ref |
|--------|------|-------------|---------|-----|
| `GET` | `/repos/{owner}/{repo}/assignees` | `issues/list-assignees` | List assignees | L35014 |
| `GET` | `/repos/{owner}/{repo}/assignees/{assignee}` | `issues/check-user-can-be-assigned` | Check if a user can be assigned | L35076 |
| `POST` | `/repos/{owner}/{repo}/issues/{issue_number}/assignees` | `issues/add-assignees` | Add assignees to an issue | L51912 |
| `DELETE` | `/repos/{owner}/{repo}/issues/{issue_number}/assignees` | `issues/remove-assignees` | Remove assignees from an issue | L51987 |
| `GET` | `/repos/{owner}/{repo}/issues/{issue_number}/assignees/{assignee}` | `issues/check-user-can-be-assigned-to-issue` | Check if a user can be assigned to an issue | L52063 |

## Labels

| Method | Path | operationId | Summary | Ref |
|--------|------|-------------|---------|-----|
| `GET` | `/repos/{owner}/{repo}/labels` | `issues/list-labels-for-repo` | List labels for a repository | L54175 |
| `POST` | `/repos/{owner}/{repo}/labels` | `issues/create-label` | Create a label | L54235 |
| `GET` | `/repos/{owner}/{repo}/labels/{name}` | `issues/get-label` | Get a label | L54330 |
| `PATCH` | `/repos/{owner}/{repo}/labels/{name}` | `issues/update-label` | Update a label | L54384 |
| `DELETE` | `/repos/{owner}/{repo}/labels/{name}` | `issues/delete-label` | Delete a label | L54468 |
| `GET` | `/repos/{owner}/{repo}/issues/{issue_number}/labels` | `issues/list-labels-on-issue` | List labels for an issue | L52660 |
| `POST` | `/repos/{owner}/{repo}/issues/{issue_number}/labels` | `issues/add-labels` | Add labels to an issue | L52729 |
| `PUT` | `/repos/{owner}/{repo}/issues/{issue_number}/labels` | `issues/set-labels` | Set labels for an issue | L52869 |
| `DELETE` | `/repos/{owner}/{repo}/issues/{issue_number}/labels/{name}` | `issues/remove-label` | Remove a label from an issue | L53054 |
| `DELETE` | `/repos/{owner}/{repo}/issues/{issue_number}/labels` | `issues/remove-all-labels` | Remove all labels from an issue | L53009 |

## Lock

| Method | Path | operationId | Summary | Ref |
|--------|------|-------------|---------|-----|
| `PUT` | `/repos/{owner}/{repo}/issues/{issue_number}/lock` | `issues/lock` | Lock an issue | L53122 |
| `DELETE` | `/repos/{owner}/{repo}/issues/{issue_number}/lock` | `issues/unlock` | Unlock an issue | L53199 |

## Not Included

The following endpoint categories from the GitHub Issues API are not covered:
Events, Timeline, Milestones, Sub-Issues/Parent, Dependencies, Reactions.
