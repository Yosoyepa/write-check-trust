.PHONY: bootstrap fast check full harden doctor rules

bootstrap:
	uv sync --group dev --group quality
	uv run wct rules build
	test -f governance/integrity.lock || uv run wct integrity lock
	uv run pre-commit install --install-hooks

fast:
	uv run wct gate --tier fast

check:
	uv run wct gate --tier commit

full:
	uv run wct gate --tier full

harden:
	uv run wct mutate run
	uv run wct accept mutate
	uv run wct gate --tier full

doctor:
	uv run wct doctor

rules:
	uv run wct rules build
