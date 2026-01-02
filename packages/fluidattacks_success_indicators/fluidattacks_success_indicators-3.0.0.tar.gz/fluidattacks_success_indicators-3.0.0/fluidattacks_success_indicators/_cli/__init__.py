import click

from . import (
    _sub_cmds,
)


@click.group()
def main() -> None:
    # main entrypoint group
    pass


main.add_command(_sub_cmds.single_job)
main.add_command(_sub_cmds.compound_job)
