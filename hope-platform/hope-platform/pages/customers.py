"""The list page: find this business's table, show a window of its rows,
and add to it. Every state is drawn: loading, error, not set up, empty and
the table itself."""
from workpeg.ui import (
    App, State, Padding, Column, Row, Spacer, Text, Button, Table,
    TableHeader, TableRow, TableCell, Modal, Form, Field, TextInput, Select,
    biz_url, navigate, on_table_change, set_title, store, toast, workpeg,
    required, email,
)

from components import (
    EmptyState, ErrorState, LoadingState, PageHeader, StatusTag,
)

# The table's own label, used to find it with get_tables(). It is not the
# peg's namespace, which comes from workpeg.json.
TABLE_NAMESPACE = "customers"
PAGE = 100


class CustomersPage(App):
    table = State("")          # per page: a table uuid belongs to ONE business
    rows = State([])
    limit = State(100)         # the window of rows this page reads (PAGE)
    more = State(False)        # the window was full, so there may be more
    loading = State(True)
    ready = State(False)       # a table exists and the page can write
    needs_setup = State(False)
    setting_up = State(False)
    error = State("")
    adding = State(False)
    saving = State(False)
    name = State("")
    email_address = State("")
    status = State("lead")

    async def on_mount(self):
        store.page_title = "Customers"
        set_title("Customers")
        on_table_change(self.changed)      # register BEFORE the first await
        await self.load()

    async def changed(self, event):
        await self.load()                  # whatever the kind, fetch again

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
                rows = await workpeg.get_rows(self.table, limit=self.limit)
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
                "name": "Customers",
                "namespace": TABLE_NAMESPACE,
                "permission": "760",
                "columns": [
                    {"id": "name", "name": "Name", "type": "text",
                     "position": 1000, "required": True},
                    {"id": "email", "name": "Email", "type": "text",
                     "position": 2000},
                    {"id": "status", "name": "Status", "type": "text",
                     "position": 3000},
                ],
            })
            self.table = made["uuid"]
            self.ready = True
            self.needs_setup = False
        except Exception as e:
            await self.find_table()        # someone else may have made it
            if self.table == "":
                toast(e.message, kind="danger")
        self.setting_up = False

    def open_add(self):
        self.name = ""
        self.email_address = ""
        self.status = "lead"
        self.adding = True

    def close_add(self):
        self.adding = False

    def set_name(self, value):
        self.name = value

    def set_email(self, value):
        self.email_address = value

    def set_status(self, value):
        self.status = value

    async def save(self, values):
        if self.saving or not self.ready:
            return                 # the button shows the wait; this stops a
        self.saving = True         # second click that lands before it does
        # Rows arrive highest position first; put the new one on top.
        top = self.rows[0]["position"] if len(self.rows) > 0 else 0
        try:
            await workpeg.add_row(self.table, {
                "data": {"name": values["name"], "email": values["email"],
                         "status": self.status},
                "position": top + 1000,
            })
            self.adding = False
            toast("Customer added", kind="success")
            await self.load()
        except Exception as e:
            toast(e.message, kind="danger")
        self.saving = False

    def open_customer(self, row_id):
        navigate(biz_url(f"/customers/{row_id}"))

    def build(self):
        return Padding(
            Column(
                PageHeader(
                    "Customers", "Everyone you sell to, newest first.",
                    # One primary action per view: while the list is empty,
                    # the empty state carries it instead.
                    Button("New customer", icon="plus", on_click=self.open_add,
                           visible=self.ready and len(self.rows) > 0),
                ),
                self.body(),
                Modal(self.add_form(), open=self.adding,
                      on_close=self.close_add, title="New customer"),
                gap=24,
            ),
            all=24,
        )

    def body(self):
        if self.loading:
            return LoadingState("Loading customers...")
        elif self.error != "":
            return ErrorState(
                self.error,
                Button("Try again", variant="outline-gray", icon="refresh",
                       on_click=self.retry),
            )
        elif self.needs_setup and self.setting_up:
            # A Component's argument is a widget, not a helper call, so
            # the busy button is its own branch.
            return EmptyState(
                "users", "Setting up customers",
                "Creating the list for this business.",
                Button("Setting up...", disabled=True),
            )
        elif self.needs_setup:
            return EmptyState(
                "users", "No customer list here yet",
                "It is not set up in this business, or you cannot see it.",
                Button("Set up customers", on_click=self.set_up),
            )
        elif len(self.rows) == 0:
            return EmptyState(
                "users", "No customers yet",
                "Add the first one to start tracking it.",
                Button("New customer", icon="plus", on_click=self.open_add),
            )
        else:
            return Table(
                TableHeader(
                    TableCell(title="Name"),
                    TableCell(title="Email"),
                    TableCell(title="Status"),
                    TableCell(title=""),
                ),
                *[TableRow(
                    TableCell(Text(r["data"]["name"], weight="medium")),
                    # Only a required column is read by subscript: a row
                    # written before a column existed has no such key.
                    TableCell(Text(r["data"].get("email", ""),
                                   variant="muted")),
                    TableCell(StatusTag(r["data"].get("status", "lead"))),
                    TableCell(
                        Button("", icon="chevron-right", variant="ghost-gray",
                               aria_label="Open customer",
                               on_click=lambda: self.open_customer(r["id"])),
                        align="end",
                    ),
                ) for r in self.rows],
                # search and sort act on the rows this page has loaded.
                search="Search customers",
                sortable=True,
                footer=self.footer(),
            )

    def footer(self):
        if self.more:
            return Row(
                Text(f"Showing the first {len(self.rows)}",
                     variant="caption"),
                Spacer(),
                Button("Show more", variant="outline-gray", size="sm",
                       on_click=self.show_more),
                align="center",
            )
        else:
            return Text(f"{len(self.rows)} customers", variant="caption")

    def submit_button(self):
        if self.saving:
            return Button("Adding...", disabled=True)
        else:
            return Button("Add customer", kind="submit")

    def add_form(self):
        return Form(
            Field("name", TextInput(value=self.name, on_change=self.set_name,
                                    autofocus=True),
                  label="Name", validators=[required]),
            Field("email", TextInput(value=self.email_address,
                                     on_change=self.set_email, type="email"),
                  label="Email", validators=[email]),
            Select(
                options=[
                    {"value": "lead", "label": "Lead"},
                    {"value": "active", "label": "Active"},
                    {"value": "churned", "label": "Churned"},
                ],
                value=self.status, on_change=self.set_status,
                label="Status",
            ),
            Row(
                Spacer(),
                Button("Cancel", variant="outline-gray",
                       on_click=self.close_add),
                self.submit_button(),
                gap=8,
            ),
            on_submit=self.save,
        )
