
"""HOPE application router."""

from workpeg.ui import (
    App, Router, Route, Shell, State, Store, Padding, Button,
    Authenticated, cookie, navigate, reload, workpeg,
)

from app_shell import AppShell
from components import EmptyState, ErrorState, LoadingState

from pages.home import HomePage
from pages.customers import CustomersPage
from pages.customer import CustomerPage
from pages.dispatch import DispatchPage
from pages.emergency import EmergencyCasePage
from pages.resources import ResourcesPage
from pages.not_found import NotFoundPage


class Landing(App):

    no_business = State(False)
    error = State("")

    async def on_mount(self):
        cached = cookie.get("cachedBusiness")

        if cached:
            navigate("/b/" + cached)
        else:
            try:
                biz = await workpeg.first_business()

                if biz:
                    navigate("/b/" + biz)
                else:
                    self.no_business = True

            except Exception as e:
                self.error = e.message

    def again(self):
        reload()

    def build(self):
        return Authenticated(self.body())

    def body(self):
        if self.error != "":
            return Padding(
                ErrorState(
                    self.error,
                    Button(
                        "Try again",
                        variant="outline-gray",
                        icon="refresh",
                        on_click=self.again,
                    ),
                ),
                all=24,
            )
        elif self.no_business:
            return Padding(
                EmptyState(
                    "building",
                    "You are not in a business yet",
                    "Ask an owner to add you, then check again.",
                    Button(
                        "Check again",
                        variant="outline-gray",
                        icon="refresh",
                        on_click=self.again,
                    ),
                ),
                all=24,
            )
        else:
            return LoadingState("Opening your workspace...")


class Main(Router):

    store = Store(business="", page_title="")

    routes = [
        Route("/", Landing),

        Shell(AppShell, "/b/[business_id]", [
            Route("/", HomePage),
            Route("/customers", CustomersPage),
            Route("/customers/[customer_id]", CustomerPage),
            Route("/dispatch", DispatchPage),
            Route("/dispatch/[emergency_id]", EmergencyCasePage),
            Route("/resources", ResourcesPage),
        ]),
    ]

    not_found = NotFoundPage
