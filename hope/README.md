# hope

A Workpeg peg: a UI and a function, described by one manifest.

```text
AGENTS.md        how a coding agent should build this peg (CLAUDE.md imports it)
workpeg.json     the manifest: namespace, function entrypoint, runtime
ui/              the interface, a Scaffold app (workpeg ui serve ui/ --fake-cloud)
function/        the backend (workpeg function test .)
```

## Working on it

```bash
workpeg ui build ui/                         # compile the UI into ui/dist/
workpeg ui serve ui/ --fake-cloud            # see it signed in, as a dev install
workpeg doctor ui/ --offline                 # check the project
workpeg function test .                      # run the function once, offline
workpeg project serve . --fake-cloud         # the page, and the function for your own saves
```

`ui/` starts as a working app: the Workpeg Scaffold, a home page, and a
customer list with its detail page. Keep the shape, replace the example.
`AGENTS.md` explains why each file is the way it is.

`workpeg project submit main:1.0.0` checks the peg's source and uploads it
as one version, never a build: Workpeg is to build and review the whole peg
itself, and `workpeg project status` says where it stands. `--dry-run`
shows what it would send.
