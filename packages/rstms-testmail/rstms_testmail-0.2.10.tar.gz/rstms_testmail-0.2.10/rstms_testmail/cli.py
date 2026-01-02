"""Console script for rstms_testmail."""

import json
import subprocess
import sys
from pathlib import Path
from pprint import pformat

import click
import click.core

from .counter import Counter
from .exception_handler import ExceptionHandler
from .gmail import Gmail
from .sendgrid_server import SendGrid
from .settings import Settings
from .shell import _shell_completion
from .smtp_server import SMTPServer
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug
    return debug


def fail(msg):
    click.echo("testmail: " + msg, err=True)
    sys.exit(-1)


@click.command("testmail")
@click.version_option(message=header)
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.option("-q", "--quiet", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-f", "--from", "from_addr", envvar="TESTMAIL_FROM")
@click.option("-t", "--to", "to_addr", envvar="TESTMAIL_TO")
@click.option("-s", "--subject", default="test{}")
@click.option("-c", "--set-counter", type=int)
@click.option("-S", "--system", envvar="TESTMAIL_SYSTEM")
@click.option("-e", "--exec", "exec_command", envvar="TESTMAIL_EXEC")
@click.option("-k", "--api-key", envvar="TESTMAIL_API_KEY")
@click.option("-u", "--username", envvar="TESTMAIL_USERNAME")
@click.option("-p", "--password", envvar="TESTMAIL_PASSWORD")
@click.option("-P", "--port", default=465, envvar="TESTMAIL_PORT")
@click.option("-m", "--message", help="message to send or - to read from stdin")
@click.option("--profile", "profile_option", default="default", show_envvar=True, envvar="TESTMAIL_PROFILE")
@click.option("--dryrun", is_flag=True)
@click.option("--reset-token", is_flag=True)
@click.option("--set-default", is_flag=True)
@click.option("--show-password", is_flag=True, help="unmask password in dryrun output")
@click.option("-W", "--write-profile", help="write current profile")
@click.option("-D", "--delete", "delete_profile", is_flag=True, help="profile name to delete")
@click.option("-L", "--list", "list_profiles", is_flag=True, help="list available profiles")
@click.argument("profile", required=False)
@click.pass_context
def cli(  # noqa:
    ctx,
    debug,
    shell_completion,
    quiet,
    verbose,
    dryrun,
    to_addr,
    from_addr,
    set_counter,
    subject,
    message,
    system,
    exec_command,
    username,
    password,
    port,
    api_key,
    profile,
    write_profile,
    reset_token,
    delete_profile,
    list_profiles,
    profile_option,
    show_password,
    set_default,
):
    """send a test email"""

    if set_default:
        write_profile = "default"
        dryrun = True

    config_dir = Path.home() / ".testmail"

    if profile is None:
        profile = profile_option

    if "{}" in subject:
        counter = Counter(label="testmail", dir=config_dir)
        count = counter.bump(set_counter)
        subject = subject.replace("{}", str(count))
    else:
        counter = None

    settings = Settings(
        label="testmail",
        dir=config_dir,
        profile=profile,
        from_addr=from_addr,
        to_addr=to_addr,
        system=system,
        exec_command=exec_command,
        username=username,
        password=password,
        port=port,
        api_key=api_key,
        write_profile=write_profile,
    )

    if delete_profile:
        settings.delete()
        sys.exit(0)

    profiles = settings.profiles()

    if profile not in profiles:
        fail(f"unknown profile '{profile}'")

    if list_profiles:
        click.echo("\n".join(profiles))
        sys.exit(0)

    if message in profiles:
        message is None

    if debug:
        click.echo(json.dumps({"config": settings.dict()}, indent=2))

    if settings.exec_command is not None:
        message = subprocess.check_output(settings.exec_command, shell=True).decode()

    if message == "-":
        message = sys.stdin.read()
    elif message is None:
        message = subject

    system = settings.system or ""

    if system == "gmail":
        server = Gmail(settings.password, reset_token)
    elif system == "sendgrid":
        server = SendGrid(settings.api_key)
    elif system.startswith("smtp:") or system.startswith("smtps:"):
        server = SMTPServer(settings.system, settings.port, settings.username, settings.password, verbose)
    else:
        fail(f"unknown system: {repr(system)}")

    if dryrun:
        output = settings.dict()
        if not show_password:
            output["password"] = "***************"
        click.echo(pformat({profile: output}))
        if counter is not None:
            counter.rewind()
        sys.exit(0)
    else:
        error = server.send(settings.from_addr, settings.to_addr, subject, message)

    if error:
        fail(pformat(error))

    if not quiet:
        click.echo(f"sent {subject} to {settings.to_addr}")

    if verbose:
        click.echo(pformat(server.result))

    sys.exit(0)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
