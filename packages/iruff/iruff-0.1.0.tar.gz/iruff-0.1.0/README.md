# iruff

A small wrapper CLI for [Ruff](https://github.com/astral-sh/ruff) that sorts imports and formats Python code in one command.


## What iruff does

Running:

```bash
iruff <PATH>
````

is equivalent to:

```bash
ruff check --select I --fix <PATH>
ruff format <PATH>
```

That’s it.


## Configuration

`iruff` uses Ruff’s configuration directly.

All settings are read from:

* `pyproject.toml`
* `ruff.toml`
* `.ruff.toml`

Configuration discovery behaves exactly the same as `ruff`.


## Installation and Usage

```bash
uvx iruff .
uvx iruff src/
uvx iruff file.py
```


## Scope

`iruff` intentionally does only two things:

* Sort imports (`I` rules)
* Format code

No extra options. No new config. No behavior changes.


## License

MIT
