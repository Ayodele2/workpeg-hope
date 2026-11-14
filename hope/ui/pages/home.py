
"""HOPE Hotel Emergency Response Centre."""

from workpeg.ui import (
    App, State, Padding, Column, Row, Container, Expanded,
    Text, Icon, Link, store, set_title, workpeg,
    on_table_change, biz_url,
)

from components import (
    PageHeader,
    SectionHeading,
    MetricCard,
    LoadingState,
    ErrorState,
)

TABLE_NAMESPACE = "emergencies"
RESOURCE_NAMESPACE = "response_resources"


class HomePage(App):

    rows = State([])
    loading = State(True)
    error = State("")

    total = State(0)
    awaiting = State(0)
    assigned = State(0)
    responding = State(0)
    arrived = State(0)
    active = State(0)
    completed = State(0)

    hospital_count = State(0)
    ambulance_count = State(0)

    async def on_mount(self):
        store.page_title = "Hotel Response Centre"
        set_title("HOPE | Hotel Response Centre")
        on_table_change(self.changed)
        await self.load()

    async def changed(self, event):
        await self.load()

    async def load(self):
        self.loading = True

        try:
            tables = await workpeg.get_tables(TABLE_NAMESPACE)

            if len(tables) == 0:
                records = []
            else:
                records = await workpeg.get_rows(
                    tables[0]["uuid"],
                    limit=100,
                )

            total = len(records)
            awaiting = 0
            assigned = 0
            responding = 0
            arrived = 0
            completed = 0

            for record in records:
                data = record.get("data", {})
                status = data.get("status", "received")

                if status == "received":
                    awaiting += 1
                    data["display_status"] = "Received"

                elif status == "assigned":
                    assigned += 1
                    data["display_status"] = "Assigned"

                elif status == "responding":
                    responding += 1
                    data["display_status"] = "Responding"

                elif status == "arrived":
                    arrived += 1
                    data["display_status"] = "Arrived"

                elif status == "completed":
                    completed += 1
                    data["display_status"] = "Completed"

                else:
                    data["display_status"] = "Other"

            self.rows = records
            self.total = total
            self.awaiting = awaiting
            self.assigned = assigned
            self.responding = responding
            self.arrived = arrived
            self.active = assigned + responding + arrived
            self.completed = completed

            resource_tables = await workpeg.get_tables(
                RESOURCE_NAMESPACE
            )

            hospitals = 0
            ambulances = 0

            if len(resource_tables) > 0:
                resources = await workpeg.get_rows(
                    resource_tables[0]["uuid"],
                    limit=100,
                )

                for resource in resources:
                    resource_type = resource.get(
                        "data", {}
                    ).get("resource_type", "")

                    if resource_type == "hospital":
                        hospitals += 1

                    elif resource_type == "ambulance":
                        ambulances += 1

            self.hospital_count = hospitals
            self.ambulance_count = ambulances
            self.error = ""

        except Exception as e:
            self.error = str(e)

        self.loading = False

    def overview(self):
        return Column(
            SectionHeading(
                "Emergency response tracking",
                "Live status figures from the emergency register.",
            ),
            Row(
                Expanded(
                    MetricCard(
                        "alert-circle",
                        "Total emergencies",
                        str(self.total),
                        "Cases recorded",
                    )
                ),
                Expanded(
                    MetricCard(
                        "clock",
                        "Awaiting assignment",
                        str(self.awaiting),
                        "Require coordination",
                    )
                ),
                gap=16,
            ),
            Row(
                Expanded(
                    MetricCard(
                        "clipboard-check",
                        "Assigned",
                        str(self.assigned),
                        "Resources allocated",
                    )
                ),
                Expanded(
                    MetricCard(
                        "activity",
                        "Responding",
                        str(self.responding),
                        "Response in progress",
                    )
                ),
                gap=16,
            ),
            Row(
                Expanded(
                    MetricCard(
                        "map-pin",
                        "Arrived",
                        str(self.arrived),
                        "Responder at location",
                    )
                ),
                Expanded(
                    MetricCard(
                        "check-circle",
                        "Completed",
                        str(self.completed),
                        "Cases marked complete",
                    )
                ),
                gap=16,
            ),
            gap=14,
        )

    def resources(self):
        return Column(
            SectionHeading(
                "Registered response resources",
                "Resources available in this business workspace.",
            ),
            Row(
                Expanded(
                    Container(
                        Column(
                            Icon("truck", size=26),
                            Text("Ambulances", weight="semibold"),
                            Text(
                                str(self.ambulance_count),
                                variant="heading",
                            ),
                            Text(
                                "Registered ambulances",
                                variant="muted",
                            ),
                            Link(
                                "Manage resources",
                                href=biz_url("/resources"),
                            ),
                            gap=8,
                        ),
                        variant="card",
                        padding=20,
                    ),
                ),
                Expanded(
                    Container(
                        Column(
                            Icon("building-2", size=26),
                            Text("Hospitals", weight="semibold"),
                            Text(
                                str(self.hospital_count),
                                variant="heading",
                            ),
                            Text(
                                "Registered hospitals",
                                variant="muted",
                            ),
                            Link(
                                "Manage resources",
                                href=biz_url("/resources"),
                            ),
                            gap=8,
                        ),
                        variant="card",
                        padding=20,
                    ),
                ),
                gap=16,
            ),
            gap=12,
        )

    
    def recent_activity(self):
        if len(self.rows) == 0:
            return Container(
                Column(
                    Icon("activity", size=28),
                    Text(
                        "No emergency activity yet",
                        weight="semibold",
                    ),
                    Text(
                        "New emergency reports will appear here.",
                        variant="muted",
                    ),
                    Link(
                        "Open Emergency Dispatch",
                        href=biz_url("/dispatch"),
                    ),
                    gap=8,
                    align="center",
                ),
                variant="card",
                padding=32,
            )

        return Container(
            Column(
                Row(
                    Icon("alert-circle", size=24),
                    Expanded(
                        Column(
                            Text(
                                self.rows[0].get("data", {}).get(
                                    "guest_name", "Unnamed case"
                                ),
                                weight="semibold",
                            ),
                            Text(
                                self.rows[0].get("data", {}).get(
                                    "emergency_type", "Emergency"
                                ),
                                variant="muted",
                            ),
                            Text(
                                self.rows[0].get("data", {}).get(
                                    "location", "Location not provided"
                                ),
                                variant="caption",
                            ),
                            gap=4,
                        ),
                    ),
                    Column(
                        Text(
                            self.rows[0].get("data", {}).get(
                                "display_status", "Received"
                            ),
                            weight="semibold",
                        ),
                        Link(
                            "View case",
                            href=biz_url(
                                "/dispatch/"
                                + str(self.rows[0].get("id", ""))
                            ),
                        ),
                        gap=4,
                    ),
                    align="center",
                    gap=12,
                ),
                Divider(),
                Text(
                    "Assigned hospital: "
                    + str(
                        self.rows[0].get("data", {}).get(
                            "hospital_name", "Not assigned"
                        )
                    ),
                    weight="medium",
                ),
                Text(
                    "Assigned ambulance: "
                    + str(
                        self.rows[0].get("data", {}).get(
                            "ambulance_name", "Not assigned"
                        )
                    ),
                    weight="medium",
                ),
                gap=10,
            ),
            variant="card",
            padding=20,
        )


    def build(self):
        if self.loading:
            return LoadingState("Loading Hotel Response Centre...")

        elif self.error != "":
            return Padding(
                ErrorState(
                    self.error,
                    Link(
                        "Open Emergency Dispatch",
                        href=biz_url("/dispatch"),
                    ),
                ),
                all=24,
            )

        else:
            return Padding(
                Column(
                    PageHeader(
                        "Hotel Emergency Response Centre",
                        "Monitor guest emergencies, staff response and available medical resources.",
                        Link(
                            "View emergency register",
                            href=biz_url("/dispatch"),
                        ),
                    ),
                    Container(
                        Row(
                            Icon("shield-check", size=24),
                            Expanded(
                                Column(
                                    Text(
                                        "HOPE hotel-response demonstration",
                                        weight="semibold",
                                    ),
                                    Text(
                                        "Emergency figures reflect records "
                                        "in this business. Resource "
                                        "assignments are for demonstration; "
                                        "no real dispatch integrations "
                                        "are connected.",
                                        variant="caption",
                                    ),
                                    gap=4,
                                ),
                            ),
                            align="center",
                            gap=12,
                        ),
                        variant="card",
                        padding=20,
                    ),
                    self.overview(),
                    self.resources(),
                    Column(
                        SectionHeading(
                            "Recent emergency activity",
                            "Latest case and its assigned response resources.",
                        ),
                        self.recent_activity(),
                        gap=12,
                    ),
                    gap=24,
                ),
                all=24,
            )
