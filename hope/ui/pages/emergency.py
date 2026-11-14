
"""HOPE Emergency Case Details and Demo Resource Assignment."""

from workpeg.ui import (
    App, State, Padding, Column, Row, Container, Spacer,
    Text, Button, Select, Divider, Link, ListView,
    biz_url, route, navigate, set_title, store, toast, workpeg,
)

from components import ErrorState, LoadingState

TABLE_NAMESPACE = "emergencies"
RESOURCE_NAMESPACE = "response_resources"


class EmergencyCasePage(App):
    table = State("")
    emergency_id = State(0)
    row = State({})
    loading = State(True)
    error = State("")
    status = State("received")
    saving = State(False)
    additional_notes = State("None provided")

    resource_rows = State([])
    resource_error = State("")

    hospital_options = State([
        {"value": "", "label": "Select a hospital"}
    ])
    ambulance_options = State([
        {"value": "", "label": "Select an ambulance"}
    ])

    selected_hospital = State("")
    selected_ambulance = State("")
    hospital_name = State("")
    ambulance_name = State("")

    async def on_mount(self):
        store.page_title = "Emergency Case"
        self.loading = True
        self.error = ""

        try:
            self.emergency_id = int(route.emergency_id)
            tables = await workpeg.get_tables(TABLE_NAMESPACE)

            if len(tables) == 0:
                self.error = "Emergency register not found."
            else:
                self.table = tables[0]["uuid"]
                record = await workpeg.get_row(
                    self.table,
                    self.emergency_id,
                )

                if not record:
                    self.error = (
                        "No emergency case was found for case ID "
                        + str(self.emergency_id)
                        + "."
                    )
                elif "data" not in record:
                    self.error = "The emergency record has no data field."
                else:
                    self.show(record)

        except Exception as e:
            self.error = str(e)

        await self.load_resources()
        self.loading = False

    def show(self, row):
        self.row = row
        data = row["data"]

        self.status = data.get("status", "received")
        self.additional_notes = (
            data.get("notes", "") or "None provided"
        )

        self.selected_hospital = str(
            data.get("hospital_id", "") or ""
        )
        self.selected_ambulance = str(
            data.get("ambulance_id", "") or ""
        )

        self.hospital_name = data.get("hospital_name", "")
        self.ambulance_name = data.get("ambulance_name", "")

        set_title("Emergency case " + str(self.emergency_id))

    async def load_resources(self):
        try:
            tables = await workpeg.get_tables(RESOURCE_NAMESPACE)

            if len(tables) == 0:
                self.resource_error = (
                    "The response resources register was not found."
                )
                return

            resource_table = tables[0]["uuid"]

            self.resource_rows = await workpeg.get_rows(
                resource_table,
                limit=100,
            )

            hospitals = [
                {"value": "", "label": "Select a hospital"}
            ]

            ambulances = [
                {"value": "", "label": "Select an ambulance"}
            ]

            for resource in self.resource_rows:
                data = resource["data"]
                resource_id = str(resource["id"])
                name = data.get("name", "Unnamed resource")
                resource_type = data.get("resource_type", "")
                resource_status = data.get("status", "offline")

                label = (
                    name + " (" + resource_status.upper() + ")"
                )

                if resource_type == "hospital":
                    hospitals.append({
                        "value": resource_id,
                        "label": label,
                    })

                elif resource_type == "ambulance":
                    ambulances.append({
                        "value": resource_id,
                        "label": label,
                    })

            self.hospital_options = hospitals
            self.ambulance_options = ambulances
            self.resource_error = ""

        except Exception as e:
            self.resource_error = str(e)

    def set_hospital(self, value):
        self.selected_hospital = value
        self.hospital_name = ""

        for resource in self.resource_rows:
            if str(resource["id"]) == value:
                self.hospital_name = resource["data"].get(
                    "name", ""
                )

    def set_ambulance(self, value):
        self.selected_ambulance = value
        self.ambulance_name = ""

        for resource in self.resource_rows:
            if str(resource["id"]) == value:
                self.ambulance_name = resource["data"].get(
                    "name", ""
                )

    def set_status(self, value):
        self.status = value

    async def save_assignment(self):
        if self.saving or not self.row:
            return

        if self.selected_hospital == "":
            toast("Please select a hospital.", kind="danger")
            return

        if self.selected_ambulance == "":
            toast("Please select an ambulance.", kind="danger")
            return

        self.saving = True
        data = {}

        for key in self.row["data"]:
            data[key] = self.row["data"][key]

        data["hospital_id"] = self.selected_hospital
        data["hospital_name"] = self.hospital_name
        data["ambulance_id"] = self.selected_ambulance
        data["ambulance_name"] = self.ambulance_name
        data["assignment_type"] = "demo"

        if data.get("status", "received") == "received":
            data["status"] = "assigned"

        try:
            updated = await workpeg.update_row(
                self.table,
                self.emergency_id,
                {"data": data},
            )

            self.show(updated)
            toast(
                "Demo hospital and ambulance assigned successfully",
                kind="success",
            )

        except Exception as e:
            toast(str(e), kind="danger")

        self.saving = False

    async def save(self):
        if self.saving or not self.row:
            return

        self.saving = True
        data = {}

        for key in self.row["data"]:
            data[key] = self.row["data"][key]

        data["status"] = self.status

        try:
            updated = await workpeg.update_row(
                self.table,
                self.emergency_id,
                {"data": data},
            )

            self.show(updated)
            toast("Emergency status updated", kind="success")

        except Exception as e:
            toast(str(e), kind="danger")

        self.saving = False

    def back(self):
        navigate(biz_url("/dispatch"))

    def save_button(self):
        if self.saving:
            return Button("Saving...", disabled=True)

        return Button(
            "Update case status",
            on_click=self.save,
        )

    def assignment_button(self):
        if self.saving:
            return Button("Saving assignment...", disabled=True)

        return Button(
            "Save resource assignment",
            on_click=self.save_assignment,
        )

    def guest_panel(self):
        return Container(
            Column(
                Text("Guest information", weight="semibold"),
                Divider(),
                Text("Guest / Patient", variant="muted"),
                Text(
                    str(
                        self.row["data"].get(
                            "guest_name", "Not provided"
                        )
                    )
                ),
                Text("Guest contact phone", variant="muted"),
                Text(
                    str(
                        self.row["data"].get(
                            "phone", "Not provided"
                        )
                    )
                ),
                gap=8,
            ),
            variant="card",
            padding=24,
        )

    def next_of_kin_panel(self):
        return Container(
            Column(
                Text(
                    "Guest and next-of-kin details",
                    weight="semibold",
                ),
                Divider(),
                Text(
                    "Room number, next-of-kin name, relationship, "
                    "phone number, preferred language and consent "
                    "information are recorded below.",
                    variant="muted",
                ),
                Text(str(self.additional_notes)),
                Divider(),
                Text(
                    "Verify the required permission before contacting "
                    "the next of kin. No notification is sent by this page.",
                    variant="muted",
                ),
                gap=8,
            ),
            variant="card",
            padding=24,
        )

    def emergency_panel(self):
        return Container(
            Column(
                Text("Emergency information", weight="semibold"),
                Divider(),
                Text("Emergency type", variant="muted"),
                Text(
                    str(
                        self.row["data"].get(
                            "emergency_type", "Not provided"
                        )
                    )
                ),
                Text("Incident location", variant="muted"),
                Text(
                    str(
                        self.row["data"].get(
                            "location", "Not provided"
                        )
                    )
                ),
                Text("Priority", variant="muted"),
                Text(
                    str(
                        self.row["data"].get(
                            "priority", "Not provided"
                        )
                    )
                ),
                gap=8,
            ),
            variant="card",
            padding=24,
        )

    def assignment_panel(self):
        return Container(
            Column(
                Text(
                    "Hospital and ambulance assignment",
                    weight="semibold",
                ),
                Text(
                    "Select the demo hospital and ambulance "
                    "for this emergency case.",
                    variant="muted",
                ),
                Divider(),
                Text("Select hospital", variant="muted"),
                Select(
                    options=self.hospital_options,
                    value=self.selected_hospital,
                    on_change=self.set_hospital,
                ),
                Text("Select ambulance", variant="muted"),
                Select(
                    options=self.ambulance_options,
                    value=self.selected_ambulance,
                    on_change=self.set_ambulance,
                ),
                Text(
                    "Currently assigned hospital: "
                    + (self.hospital_name or "Not assigned"),
                    weight="medium",
                ),
                Text(
                    "Currently assigned ambulance: "
                    + (self.ambulance_name or "Not assigned"),
                    weight="medium",
                ),
                self.assignment_button(),
                Text(
                    "BETA DEMO: Assignments are saved inside HOPE. "
                    "No hospital or ambulance is contacted or dispatched.",
                    variant="muted",
                ),
                gap=12,
            ),
            variant="card",
            padding=24,
        )

    def status_panel(self):
        return Container(
            Column(
                Text("Response management", weight="semibold"),
                Text(
                    "Update the current stage of this emergency response.",
                    variant="muted",
                ),
                Select(
                    options=[
                        {"value": "received", "label": "Received"},
                        {"value": "assigned", "label": "Assigned"},
                        {"value": "responding", "label": "Responding"},
                        {"value": "arrived", "label": "Arrived"},
                        {"value": "completed", "label": "Completed"},
                    ],
                    value=self.status,
                    on_change=self.set_status,
                    label="Emergency status",
                ),
                Row(Spacer(), self.save_button()),
                gap=16,
            ),
            variant="card",
            padding=24,
        )

    def build(self):
        if self.loading:
            return LoadingState("Loading emergency case...")

        elif self.error != "":
            return Padding(
                ErrorState(
                    self.error,
                    Button(
                        "Back to dispatch",
                        variant="outline-gray",
                        icon="arrow-left",
                        on_click=self.back,
                    ),
                ),
                all=24,
            )

        elif not self.row:
            return Padding(
                ErrorState(
                    "The emergency record is empty.",
                    Button(
                        "Back to dispatch",
                        variant="outline-gray",
                        on_click=self.back,
                    ),
                ),
                all=24,
            )

        else:
            return ListView(
                Link(
                    "Emergency Dispatch",
                    href=biz_url("/dispatch"),
                    icon="arrow-left",
                ),
                Row(
                    Column(
                        Text("Emergency Case", variant="heading"),
                        Text(
                            "Case ID: " + str(self.emergency_id),
                            variant="muted",
                        ),
                        gap=4,
                    ),
                    Spacer(),
                    Button(
                        "Back to list",
                        variant="outline-gray",
                        on_click=self.back,
                    ),
                    align="center",
                ),
                self.guest_panel(),
                self.next_of_kin_panel(),
                self.emergency_panel(),
                self.assignment_panel(),
                self.status_panel(),
                height="100%",
                padding=24,
                gap=24,
            )
