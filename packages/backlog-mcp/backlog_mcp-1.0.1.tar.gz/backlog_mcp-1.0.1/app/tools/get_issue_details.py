from app.utils.di import create_backlog_context
from app.utils.ultils import get_issue_detail_handler


async def get_issue_details(
    issue_key: str,
    issue_title: str | None,
    timezone: str = "UTC"
):
    """
    Get details of a Backlog issue by its key.

    Args:
        issue_key (str): The key of the Backlog issue to retrieve.
        issue_title (str): The title of the Backlog issue, used for logging or reference purposes.
        timezone (str, optional): The timezone to format datetime fields. Defaults to "UTC".
    """
    try:
        if not issue_key and not issue_title:
            raise ValueError("Please provide an issue key.")
        elif issue_title and not issue_key:
            raise ValueError(
                "Cannot retrieve task information with only the issue title. "
                "Please provide an issue key. Searching by title is not supported yet."
            )
        ctx = create_backlog_context()
        result = await get_issue_detail_handler(
            backlog_domain=ctx.backlog_domain,
            api_key=ctx.api_key,
            issue_key=issue_key,
            timezone=timezone,
        )
        return result
    except Exception as e:
        raise e
