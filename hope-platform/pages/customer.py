"""The detail page: read one row, edit it, and delete it after asking."""
from workpeg.ui import (
    App, State, Padding, Column, Row, Container, ConstrainedBox, Expanded,
    Spacer, Text, Button, Input, TextInput, Select, Divider, Link, Modal,
    biz_url, dates, navigate, route, set_title, store, toast, workpeg,
)

from components import ErrorState, LoadingState, StatusTag

TABLE_NAMESPACE = "customers"


class CustomerPage(App):
    table = State("")
    customer_id = State(0)
    row = State({})
    loading = State(True)
    error = State("")
    email_address = State("")
    status = State("lead")
    saving = State(False)
    confirming = State(False)
    deleting = State(False)

    async def on_mount(self):
        store.page_title = "Customer"
        # route.* is a live read of the URL: capture it before any await.
        self.customer_id = int(route.customer_id)
        try:
            tables = await workpeg.get_tables(TABLE_NAMESPACE)
            if len(tables) == 0:
                self.error = ("This business has no customer list, or you "
                              "cannot see it.")
            else:
                self.table = tables[0]["uuid"]
                self.show(await workpeg.get_row(self.table, self.customer_id))
        except Exception as e:
            self.error = e.message
        self.loading = False

    def show(self, row):
        self.row = row
        self.email_address = row["data"].get("email", "")
        self.status = row["data"].get("status", "lead")
        set_title(row["data"]["name"])

    def set_email(self, value):
        self.email_address = value

    def set_status(self, value):
        self.status = value

    async def save(self):
        if self.saving:
            return
        self.saving = True
        before = self.row
        # update_row replaces `data` whole, so copy every column the row
        # has (including ones this page does not know) and change yours.
        data = {}
        for key in self.row["data"]:
            data[key] = self.row["data"][key]
        data["email"] = self.email_address
        data["status"] = self.status
        try:
            self.show(await workpeg.update_row(
                self.table, self.customer_id, {"data": data}))
            toast("Saved", kind="success")
        except Exception as e:
            self.show(before)          # a failed write restores server state
            toast(e.message, kind="danger")
        self.saving = False

    def ask_delete(self):
        self.confirming = True

    def cancel_delete(self):
        self.confirming = False

    async def remove(self):
        if self.deleting:
            return
        self.deleting = True
        try:
            await workpeg.delete_row(self.table, self.customer_id)
            self.confirming = False
            toast("Customer deleted", kind="success")
            navigate(biz_url("/customers"))
        except Exception as e:
            toast(e.message, kind="danger")
        self.deleting = False

    def back(self):
        navigate(biz_url("/customers"))

    def build(self):
        if self.loading:
            return LoadingState("Loading customer...")
        elif self.error != "":
            return Padding(
                ErrorState(
                    self.error,
                    Button("Back to customers", variant="outline-gray",
                           icon="arrow-left", on_click=self.back),
                ),
                all=24,
            )
        else:
            return Padding(
                # A readable width for a form; never maxWidth in style=.
                ConstrainedBox(
                    Column(
                        Link("Customers", href=biz_url("/customers"),
                             icon="arrow-left"),
                        Row(
                            Expanded(
                                Column(
                                    Row(
                                        Text(self.row["data"]["name"],
                                             variant="heading"),
                                        StatusTag(self.status),
                                        align="center", gap=8,
                                    ),
                                    Text("Added " + dates.format(
                                        dates.to_epoch(
                                            self.row["created_at"][:19],
                                            "UTC"),
                                        "medium"), variant="caption"),
                                    gap=4,
                                ),
                            ),
                            Button("Delete", variant="outline-gray",
                                   error=True, icon="trash",
                                   on_click=self.ask_delete),
                            align="center", gap=16,
                        ),
                        Container(
                            Column(
                                Text("Contact", weight="semibold"),
                                Divider(),
                                Input(
                                    TextInput(value=self.email_address,
                                              on_change=self.set_email,
                                              type="email"),
                                    label="Email",
                                    hint="Where invoices go.",
                                ),
                                Select(
                                    options=[
                                        {"value": "lead", "label": "Lead"},
                                        {"value": "active",
                                         "label": "Active"},
                                        {"value": "churned",
                                         "label": "Churned"},
                                    ],
                                    value=self.status,
                                    on_change=self.set_status,
                                    label="Status",
                                ),
                                Row(Spacer(), self.save_button()),
                                gap=16,
                            ),
                            variant="card", padding=24,
                        ),
                        Modal(
                            Column(
                                Text("This deletes the customer for everyone "
                                     "in this business. It cannot be undone."),
                                Row(
                                    Spacer(),
                                    Button("Cancel", variant="outline-gray",
                                           on_click=self.cancel_delete),
                                    self.delete_button(),
                                    gap=8,
                                ),
                                gap=24,
                            ),
                            open=self.confirming, on_close=self.cancel_delete,
                            title="Delete this customer?",
                        ),
                        gap=24,
                    ),
                    max_width=720,
                ),
                all=24,
            )

    def save_button(self):
        if self.saving:
            return Button("Saving...", disabled=True)
        else:
            return Button("Save", on_click=self.save)

    def delete_button(self):
        if self.deleting:
            return Button("Deleting...", error=True, disabled=True)
        else:
            return Button("Delete customer", error=True,
                          on_click=self.remove)
