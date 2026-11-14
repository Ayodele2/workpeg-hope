"""HOPE emergency response history helpers."""

from workpeg.ui import workpeg, user


TABLE_NAMESPACE = "emergency_history"


async def ensure_history_table():
    """Find or create the current business's history table."""

    tables = await workpeg.get_tables(TABLE_NAMESPACE)

    if len(tables) > 0:
        return tables[0]["uuid"]

    try:
        made = await workpeg.create_table({
            "name": "HOPE Emergency Response History",
            "namespace": TABLE_NAMESPACE,
            "permission": "760",
            "columns": [
                {
                    "id": "case_id",
                    "name": "Emergency Case ID",
                    "type": "text",
                    "position": 1000,
                    "required": True,
                },
                {
                    "id": "event_type",
                    "name": "Event Type",
                    "type": "text",
                    "position": 2000,
                    "required": True,
                },
                {
                    "id": "summary",
                    "name": "Event Description",
                    "type": "text",
                    "position": 3000,
                    "required": True,
                },
                {
                    "id": "previous_value",
                    "name": "Previous Value",
                    "type": "text",
                    "position": 4000,
                },
                {
                    "id": "new_value",
                    "name": "New Value",
                    "type": "text",
                    "position": 5000,
                },
                {
                    "id": "actor_name",
                    "name": "Staff Member",
                    "type": "text",
                    "position": 6000,
                },
                {
                    "id": "actor_subject",
                    "name": "Staff Identity",
                    "type": "text",
                    "position": 7000,
                },
            ],
        })

        return made["uuid"]

    except Exception:
        # Another staff member may have created the table.
        tables = await workpeg.get_tables(TABLE_NAMESPACE)

        if len(tables) > 0:
            return tables[0]["uuid"]

        raise


async def record_history(
    case_id,
    event_type,
    summary,
    previous_value="",
    new_value="",
):
    """Record one event without hiding errors from the calling page."""

    try:
        table = await ensure_history_table()

        latest = await workpeg.get_rows(
            table,
            limit=1,
        )

        top = (
            latest[0].get("position", 0)
            if len(latest) > 0
            else 0
        )

        await workpeg.add_row(table, {
            "data": {
                "case_id": str(case_id),
                "event_type": event_type,
                "summary": summary,
                "previous_value": str(previous_value),
                "new_value": str(new_value),
                "actor_name": user.name or "Staff member",
                "actor_subject": user.subject or "",
            },
            "position": top + 1000,
        })

        return ""

    except Exception as e:
        return str(e)


async def get_case_history(case_id):
    """Return history events belonging to one emergency case."""

    table = await ensure_history_table()

    rows = await workpeg.get_rows(
        table,
        limit=100,
    )

    return [
        row for row in rows
        if row["data"].get("case_id", "") == str(case_id)
    ]