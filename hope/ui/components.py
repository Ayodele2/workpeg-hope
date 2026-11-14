
"""Reusable visual components for HOPE."""

from workpeg.ui import (
    Component, Center, Column, Container, Expanded,
    Icon, Row, Spinner, Tag, Text,
)


class PageHeader(Component):
    def __init__(self, title, subtitle, action=None):
        self.title = title
        self.subtitle = subtitle
        self.action = action

    def build(self):
        if self.action is None:
            return Column(
                Text(self.title, variant="heading"),
                Text(self.subtitle, variant="muted"),
                gap=6,
            )

        return Row(
            Expanded(
                Column(
                    Text(self.title, variant="heading"),
                    Text(self.subtitle, variant="muted"),
                    gap=6,
                ),
            ),
            self.action,
            align="center",
            gap=16,
        )


class SectionHeading(Component):
    def __init__(self, title, subtitle=""):
        self.title = title
        self.subtitle = subtitle

    def build(self):
        if self.subtitle == "":
            return Text(self.title, weight="semibold")

        return Column(
            Text(self.title, weight="semibold"),
            Text(self.subtitle, variant="muted"),
            gap=4,
        )


class MetricCard(Component):
    def __init__(self, icon, label, value, description):
        self.icon = icon
        self.label = label
        self.value = value
        self.description = description

    def build(self):
        return Container(
            Row(
                Icon(self.icon, size=26),
                Expanded(
                    Column(
                        Text(self.label, variant="muted"),
                        Text(self.value, variant="heading"),
                        Text(self.description, variant="caption"),
                        gap=6,
                    ),
                ),
                align="center",
                gap=16,
            ),
            variant="card",
            padding=20,
        )


class LoadingState(Component):
    def __init__(self, label):
        self.label = label

    def build(self):
        return Center(
            Column(
                Spinner(size=24),
                Text(self.label, variant="muted"),
                gap=16,
                align="center",
            ),
        )


class EmptyState(Component):
    def __init__(self, icon, title, detail, action):
        self.icon = icon
        self.title = title
        self.detail = detail
        self.action = action

    def build(self):
        return Container(
            Column(
                Icon(self.icon, size=32),
                Text(self.title, weight="semibold"),
                Text(self.detail, variant="muted"),
                self.action,
                gap=8,
                align="center",
            ),
            variant="card",
            padding=40,
        )


class ErrorState(Component):
    def __init__(self, message, action):
        self.message = message
        self.action = action

    def build(self):
        return Container(
            Column(
                Icon("alert-triangle", size=32),
                Text("Something went wrong", weight="semibold"),
                Text(self.message, tone="danger"),
                self.action,
                gap=8,
                align="center",
            ),
            variant="card",
            padding=40,
        )


class StatusTag(Component):
    def __init__(self, status):
        self.status = status

    def build(self):
        if self.status == "active":
            return Tag("Active", tone="success", dot=True)

        elif self.status == "churned":
            return Tag("Churned", tone="neutral", dot=True)

        else:
            return Tag("Lead", tone="info", dot=True)
