from app.utils.di import create_backlog_context
from app.utils.ultils import get_user_task

from app.server_settings import settings


async def get_user_issue_list(
    project_ids: list[int] | None = None,
    assignee_ids: list[int] | None = None,
    status_ids: list[int] | None = None,
    milestone_ids: list[int] | None = None,
    parent_issue_ids: list[int] | None = None,
    created_since: str | None = None,
    created_until: str | None = None,
    updated_since: str | None = None,
    updated_until: str | None = None,
    start_date_since: str | None = None,
    start_date_until: str | None = None,
    due_date_since: str | None = None,
    due_date_until: str | None = None,
):
    """
    Retrieves a filtered list of issues from Backlog for the users.

    Args:
        project_ids (list[int], optional): List of project IDs to filter issues.
        assignee_ids (list[int], optional): List of assignee IDs to filter issues (defaults to current user).
        status_ids (list[int], optional): List of status IDs to filter issues (defaults to all non-closed statuses).
        milestone_ids (list[int], optional): List of milestone IDs to filter issues.
        parent_issue_ids (list[int], optional): List of parent issue IDs to filter issues.

        created_since (str, optional): Created since (YYYY-MM-DD).
        created_until (str, optional): Created until (YYYY-MM-DD).

        updated_since (str, optional): Updated since (YYYY-MM-DD).
        updated_until (str, optional): Updated until (YYYY-MM-DD).

        start_date_since (str, optional): Start Date since (YYYY-MM-DD).
        start_date_until (str, optional): Start Date until (YYYY-MM-DD).

        due_date_since (str, optional): Due Date since (YYYY-MM-DD).
        due_date_until (str, optional): Due Date until (YYYY-MM-DD).
    """

    try:
        ctx = create_backlog_context()

        if assignee_ids is None:
            assignee_ids = [settings.USER_ID]

        issue_list = await get_user_task(
            backlog_domain=ctx.backlog_domain,
            api_key=ctx.api_key,
            project_ids=project_ids,
            assignee_ids=assignee_ids,
            status_ids=status_ids,
            milestone_ids=milestone_ids,
            parent_issue_ids=parent_issue_ids,
            created_since=created_since,
            created_until=created_until,
            updated_since=updated_since,
            updated_until=updated_until,
            start_date_since=start_date_since,
            start_date_until=start_date_until,
            due_date_since=due_date_since,
            due_date_until=due_date_until
        )
        return issue_list
    except Exception as e:
        raise e
