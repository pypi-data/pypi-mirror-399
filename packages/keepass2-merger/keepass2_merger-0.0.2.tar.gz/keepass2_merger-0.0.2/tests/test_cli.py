from datetime import datetime, timedelta

from keepass2_merger.cli import DiffItem, apply_entry_change, diff_databases, ensure_group


class DummyGroup:
    def __init__(self, name, parent=None, notes="", uuid=None, last_modified=None):
        self.name = name
        self.parent = parent
        self.notes = notes
        self.uuid = uuid or name
        self.last_modification_time = last_modified
        self.subgroups = []
        if parent is not None:
            parent.subgroups.append(self)


class DummyEntry:
    def __init__(
        self,
        title,
        username,
        password,
        group,
        url="",
        notes="",
        uuid=None,
        last_modified=None,
    ):
        self.title = title
        self.username = username
        self.password = password
        self.group = group
        self.url = url
        self.notes = notes
        self.uuid = uuid or title
        self.last_modification_time = last_modified
        self._deleted = False

    def __repr__(self):
        return f"<DummyEntry {self.title}>"


class DummyKeePass:
    def __init__(self, root_group, entries):
        self.root_group = root_group
        self.entries = list(entries)

    def move_entry(self, entry, destination):
        entry.group = destination
        return entry

    def delete_entry(self, entry):
        entry._deleted = True

    def add_group(self, parent, name):
        return DummyGroup(name, parent, uuid=f"{parent.name}/{name}")

    def add_entry(self, group, title, username, password, url="", notes=""):
        entry = DummyEntry(title, username, password, group, url=url, notes=notes)
        self.entries.append(entry)
        return entry


def test_diff_detects_entry_changes_and_orders_them():
    now = datetime.utcnow()
    earlier = now - timedelta(days=1)

    root1 = DummyGroup("Root", None, uuid="root")
    group1 = DummyGroup("Personal", root1, uuid="group-1", last_modified=earlier)
    entry_shared_old = DummyEntry(
        "Shared",
        "old_user",
        "old_pass",
        group1,
        uuid="entry-shared",
        last_modified=earlier,
    )
    entry_only_left = DummyEntry(
        "Left Only",
        "left",
        "pass",
        group1,
        uuid="entry-left",
        last_modified=earlier,
    )
    kp_left = DummyKeePass(root1, [entry_shared_old, entry_only_left])

    root2 = DummyGroup("Root", None, uuid="root")
    group2 = DummyGroup("Personal", root2, uuid="group-1", last_modified=now)
    entry_shared_new = DummyEntry(
        "Shared",
        "new_user",
        "new_pass",
        group2,
        uuid="entry-shared",
        last_modified=now,
    )
    entry_only_right = DummyEntry(
        "Right Only",
        "right",
        "pass",
        group2,
        uuid="entry-right",
        last_modified=now,
    )
    kp_right = DummyKeePass(root2, [entry_shared_new, entry_only_right])

    diffs = diff_databases(kp_left, kp_right)
    kinds = [(d.category, d.change, d.label) for d in diffs]

    assert kinds == [
        ("entry", "add", "Right Only"),
        ("entry", "modify", "Shared"),
    ]

    add_diff = diffs[0]
    modify_diff = diffs[1]
    assert add_diff.recommendation() is True
    assert modify_diff.recommendation() is True


def test_apply_entry_change_handles_none_fields():
    root = DummyGroup("Root", None, uuid="root")
    group_old = DummyGroup("Old", root, uuid="g-old")
    group_new = DummyGroup("New", root, uuid="g-new")
    entry_left = DummyEntry("Title", "user", "pass", group_old, url="http://old", notes="old")
    entry_right = DummyEntry("Title", "user", "pass", group_new, url=None, notes=None)
    kp = DummyKeePass(root, [entry_left])

    diff = DiffItem(
        category="entry",
        change="modify",
        left=entry_left,
        right=entry_right,
        path="/Old",
        label="Title",
        left_modified=None,
        right_modified=None,
    )

    apply_entry_change(kp, diff)
    assert entry_left.group == group_new
    assert entry_left.url == ""
    assert entry_left.notes == ""


def test_apply_entry_change_moves_entry_group():
    root = DummyGroup("Root", None, uuid="root")
    group_old = DummyGroup("Old", root, uuid="g-old")
    group_new = DummyGroup("New", root, uuid="g-new")
    entry_left = DummyEntry("Title", "user", "pass", group_old)
    entry_right = DummyEntry("Title", "user", "pass", group_new)
    kp = DummyKeePass(root, [entry_left])

    diff = DiffItem(
        category="entry",
        change="modify",
        left=entry_left,
        right=entry_right,
        path="/Old",
        label="Title",
        left_modified=None,
        right_modified=None,
    )

    apply_entry_change(kp, diff)
    assert entry_left.group == group_new
