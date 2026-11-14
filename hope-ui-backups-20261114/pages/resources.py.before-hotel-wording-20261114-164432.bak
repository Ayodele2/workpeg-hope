
"""HOPE Response Resources: hospitals and ambulances."""

from workpeg.ui import (
    App, State, Padding, Column, Row, Spacer, Text, Button,
    Table, TableHeader, TableRow, TableCell, Modal, Form,
    Field, TextInput, Select, on_table_change, set_title,
    store, toast, workpeg, required,
)

from components import (
    EmptyState, ErrorState, LoadingState, PageHeader,
)

TABLE_NAMESPACE = "response_resources"
PAGE = 100


class ResourcesPage(App):

    table = State("")
    rows = State([])
    limit = State(100)
    more = State(False)

    loading = State(True)
    ready = State(False)
    needs_setup = State(False)
    setting_up = State(False)
    error = State("")

    adding = State(False)
    saving = State(False)

    resource_type = State("hospital")
    status = State("available")

    async def on_mount(self):
        store.page_title = "Response Resources"
        set_title("HOPE | Response Resources")
        on_table_change(self.changed)
        await self.load()

    async def changed(self, event):
        await self.load()

    async def find_table(self):
        tables = await workpeg.get_tables(TABLE_NAMESPACE)

        if len(tables) > 0:
            self.table = tables[0]["uuid"]
        else:
            self.table = ""

        self.ready = self.table != ""
        self.needs_setup = not self.ready

    async def load(self):
        try:
            if self.table == "":
                await self.find_table()

            if self.table != "":
                rows = await workpeg.get_rows(
                    self.table,
                    limit=self.limit,
                )
                self.rows = rows
                self.more = len(rows) == self.limit

            self.error = ""

        except Exception as e:
            self.error = e.message

        self.loading = False

    async def retry(self):
        self.loading = True
        await self.load()

    async def show_more(self):
        self.limit += PAGE
        await self.load()

    async def set_up(self):
        if self.setting_up or not self.needs_setup:
            return

        self.setting_up = True

        try:
            made = await workpeg.create_table({
                "name": "HOPE Response Resources",
                "namespace": TABLE_NAMESPACE,
                "permission": "760",
                "columns": [
                    {
                        "id": "resource_type",
                        "name": "Resource Type",
                        "type": "text",
                        "position": 1000,
                        "required": True,
                    },
                    {
                        "id": "name",
                        "name": "Resource Name",
                        "type": "text",
                        "position": 2000,
                        "required": True,
                    },
                    {
                        "id": "identifier",
                        "name": "Vehicle or Facility ID",
                        "type": "text",
                        "position": 3000,
                    },
                    {
                        "id": "contact_person",
                        "name": "Contact Person",
                        "type": "text",
                        "position": 4000,
                    },
                    {
                        "id": "phone",
                        "name": "Contact Phone",
                        "type": "text",
                        "position": 5000,
                    },
                    {
                        "id": "location",
                        "name": "Location",
                        "type": "text",
                        "position": 6000,
                        "required": True,
                    },
                    {
                        "id": "status",
                        "name": "Operational Status",
                        "type": "text",
                        "position": 7000,
                    },
                    {
                        "id": "notes",
                        "name": "Notes",
                        "type": "text",
                        "position": 8000,
                    },
                ],
            })

            self.table = made["uuid"]
            self.ready = True
            self.needs_setup = False
            toast("Response resources register created", kind="success")

        except Exception as e:
            await self.find_table()

            if self.table == "":
                toast(e.message, kind="danger")

        self.setting_up = False

    def open_add(self):
        self.resource_type = "hospital"
        self.status = "available"
        self.adding = True

    def close_add(self):
        self.adding = False

    def set_resource_type(self, value):
        self.resource_type = value

    def set_status(self, value):
        self.status = value

    async def save(self, values):
        if self.saving or not self.ready:
            return

        self.saving = True
        top = self.rows[0]["position"] if len(self.rows) > 0 else 0

        try:
            await workpeg.add_row(self.table, {
                "data": {
                    "resource_type": self.resource_type,
                    "name": values["name"],
                    "identifier": values["identifier"],
                    "contact_person": values["contact_person"],
                    "phone": values["phone"],
                    "location": values["location"],
                    "status": self.status,
                    "notes": values["notes"],
                },
                "position": top + 1000,
            })

            self.adding = False
            toast("Resource registered successfully", kind="success")
            await self.load()

        except Exception as e:
            toast(e.message, kind="danger")

        self.saving = False

    def submit_button(self):
        if self.saving:
            return Button("Saving...", disabled=True)

        return Button("Register resource", kind="submit")

    def add_form(self):
        return Form(
            Select(
                options=[
                    {"value": "hospital", "label": "Hospital"},
                    {"value": "ambulance", "label": "Ambulance"},
                ],
                value=self.resource_type,
                on_change=self.set_resource_type,
                label="Resource type",
            ),
            Field(
                "name",
                TextInput(autofocus=True),
                label="Hospital or ambulance name",
                validators=[required],
            ),
            Field(
                "identifier",
                TextInput(),
                label="Vehicle registration or facility ID",
            ),
            Field(
                "contact_person",
                TextInput(),
                label="Contact person",
            ),
            Field(
                "phone",
                TextInput(),
                label="Contact phone number",
            ),
            Field(
                "location",
                TextInput(),
                label="Address or current location",
                validators=[required],
            ),
            Select(
                options=[
                    {"value": "available", "label": "Available"},
                    {"value": "busy", "label": "Busy"},
                    {"value": "offline", "label": "Offline"},
                ],
                value=self.status,
                on_change=self.set_status,
                label="Operational status",
            ),
            Field(
                "notes",
                TextInput(),
                label="Additional information",
            ),
            Row(
                Spacer(),
                Button(
                    "Cancel",
                    variant="outline-gray",
                    on_click=self.close_add,
                ),
                self.submit_button(),
                gap=8,
            ),
            on_submit=self.save,
        )

    def body(self):
        if self.loading:
            return LoadingState("Loading response resources...")

        elif self.error != "":
            return ErrorState(
                self.error,
                Button(
                    "Try again",
                    icon="refresh",
                    variant="outline-gray",
                    on_click=self.retry,
                ),
            )

        elif self.needs_setup and self.setting_up:
            return EmptyState(
                "building-2",
                "Preparing resource register",
                "Creating the hospital and ambulance register.",
                Button("Setting up...", disabled=True),
            )

        elif self.needs_setup:
            return EmptyState(
                "building-2",
                "Resource register not set up",
                "Create the register to start adding hospitals and ambulances.",
                Button(
                    "Set up resources",
                    icon="plus",
                    on_click=self.set_up,
                ),
            )

        elif len(self.rows) == 0:
            return EmptyState(
                "building-2",
                "No response resources registered",
                "Add your first hospital or ambulance.",
                Button(
                    "Register resource",
                    icon="plus",
                    on_click=self.open_add,
                ),
            )

        else:
            return Table(
                TableHeader(
                    TableCell(title="Resource"),
                    TableCell(title="Name"),
                    TableCell(title="Contact"),
                    TableCell(title="Location"),
                    TableCell(title="Status"),
                ),
                *[
                    TableRow(
                        TableCell(
                            Text(
                                r["data"].get("resource_type", "").upper(),
                                weight="medium",
                            )
                        ),
                        TableCell(
                            Text(r["data"].get("name", "Unnamed"))
                        ),
                        TableCell(
                            Text(
                                r["data"].get("phone", ""),
                                variant="muted",
                            )
                        ),
                        TableCell(
                            Text(
                                r["data"].get("location", ""),
                                variant="muted",
                            )
                        ),
                        TableCell(
                            Text(
                                r["data"].get("status", "offline").upper()
                            )
                        ),
                    )
                    for r in self.rows
                ],
                search="Search response resources",
                sortable=True,
                footer=self.footer(),
            )

    def footer(self):
        if self.more:
            return Row(
                Text(
                    "Showing the first " + str(len(self.rows)) + " resources",
                    variant="caption",
                ),
                Spacer(),
                Button(
                    "Show more",
                    variant="outline-gray",
                    size="sm",
                    on_click=self.show_more,
                ),
                align="center",
            )

        return Text(
            str(len(self.rows)) + " registered resources",
            variant="caption",
        )

    def build(self):
        return Padding(
            Column(
                PageHeader(
                    "Response Resources",
                    "Manage hospitals and ambulance resources.",
                    Button(
                        "Register resource",
                        icon="plus",
                        on_click=self.open_add,
                        visible=self.ready,
                    ),
                ),
                Text(
                    "Operational statuses are maintained manually. "
                    "They do not represent verified live availability.",
                    variant="muted",
                ),
                self.body(),
                Modal(
                    self.add_form(),
                    open=self.adding,
                    on_close=self.close_add,
                    title="Register a response resource",
                ),
                gap=24,
            ),
            all=24,
        )
