# postmodern-mono

This is an example repo of how to use a [uv Workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) effectively.

## Structure
There are three packages split into libs and apps:
- **libs**: importable packages, never run independently, do not have entry points
- **apps**: have entry points, never imported

Note that neither of these definitions are enforced by anything in Python or `uv`.

```bash
> tree
.
├── pyproject.toml              # root pyproject
├── uv.lock
├── libs
│   └── greeter
│       ├── pyproject.toml      # package dependencies here
│       └── postmodern          # all packages are namespaced
│           └── greeter
│               └── __init__.py
└── apps
    ├── server
    │   ├── pyproject.toml      # this one depends on libs/greeter
    │   ├── Dockerfile          # this one gets a Dockerfile
    │   └── postmodern
    │       └── server
    │           └── __init__.py
    └── mycli
        ├── pyproject.toml      # this one has a cli entrypoint
        └── postmodern
            └── mycli
                └── __init__.py
```

## Important notes
### Syncing
To make life easier while you're working across the workspace, you should run:
```bash
uv sync --all-packages
```

uv's sync behaviour is as follows:
- If you're in the workspace root and you run `uv sync`, it will sync only the
dependencies of the root workspace, which for this kind of monorepo should be bare.
This is not very useful.
- If you're in eg `apps/myserver` and run `uv sync`, it will sync only that package.
- You can run `uv sync --package=postmodern-server` to sync only that package.
- You can run `uv sync --all-packages` to sync all packages.

You can add an alias to your `.bashrc`/`.zshrc` if you like:
```bash
alias uvs="uv sync --all-packages
```

### Dependencies
You'll notice that `apps/mycli` has `urllib3` as a dependency.
Because of this, _every_ package in the workspace is able to import `urllib3` **in local development**,
even though they don't include it as a direct or transitive dependency.

This can make it possible to import stuff and write passing tests, only to have stuff fail
in production, where presumably you've only got the necessary dependencies installed.

There are two ways to guard against this:

1. If you're working _only_ on eg `libs/server`, you can sync only that package (see above).
This will make your LSP shout and your tests fail, if you try to import something that isn't
available to that package.

2. Your CI (see example in [.github/workflows](.github/workflows)) should do the same.

### Dev dependencies
This repo has all the global dev dependencies (`pyright`, `pytest`, `ruff` etc) in the root
pyproject.toml, and then repeated again in each package _without_ their version specifiers.

It's annoying to have to duplicate them, but at least excluding the versions makes it easier
to keep things in sync.

The reason they have to be repeated, is that if you follow the example above and install only
a specific package, it won't include anything specified in the root package.

### Testing
This repo includes a simple pytest test for each package.

I haven't yet found a good way to to run all tests from the root (short of more
avant-garde approaches like Polylith).

To test a package:
```bash
cd apps/server
uv sync
uv run pytest
```

### Pyright
You'll need to add the following to every package `pyproject.toml`:
```toml
[tool.pyright]
venvPath = "../.."       # point to the workspace root where the venv is
venv = ".venv"
strict = ["**/*.py"]
pythonVersion = "3.13"
```

## Docker
The Dockerfile is at [apps/server/Dockerfile](apps/server/Dockerfile).

Build the Docker image from the workspace root, so that it has access to all libraries:
```bash
docker build --tag=postmodern-server -f apps/server/Dockerfile .
```

And run it:
```bash
docker run --rm -it postmodern-server
```
