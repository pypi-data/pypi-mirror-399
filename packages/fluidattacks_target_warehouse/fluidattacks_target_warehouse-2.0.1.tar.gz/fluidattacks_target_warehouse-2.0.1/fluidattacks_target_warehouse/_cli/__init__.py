import click

from . import (
    _append,
    _recreate,
)


@click.group()
def main() -> None:
    # main cli entrypoint
    pass


main.add_command(_append.only_append)
main.add_command(_recreate.destroy_and_upload)
