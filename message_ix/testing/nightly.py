import logging
import os
import tarfile
from asyncio import get_event_loop
from pathlib import Path
from subprocess import check_output

import click
import ixmp
import requests
import yaml
from asyncssh import connect, scp

import message_ix

log = logging.getLogger(__name__)

HERE = Path(__file__).parent.resolve()
DEFAULT_WORKDIR = HERE.parent / "tests" / "data" / "nightly"


def _config():
    with open(HERE.parents[1] / "ci" / "nightly.yaml") as f:
        return yaml.safe_load(f)


def download(path, cli=False):
    auth = (os.environ["MESSAGE_IX_CI_USER"], os.environ["MESSAGE_IX_CI_PW"])

    cfg = _config()

    # Download database
    fn = cfg["filename"]["data"]
    url = cfg["http base"] + cfg["path"] + fn
    log.info("Downloading from {}".format(url))

    r = requests.get(url, auth=auth, stream=True)
    r.raise_for_status()

    data_path = path / fn
    with open(data_path, "wb") as out:
        for bits in r.iter_content(None):
            out.write(bits)

    log.info("Extracting from {}".format(fn))
    with tarfile.open(data_path, "r:gz") as tf:
        tf.extractall(path)

    # Download license
    if cli:
        gams_dir = path
        log.info("Downloading GAMS license to {}".format(gams_dir))
    else:
        which_gams = check_output(["which", "gams"], universal_newlines=True)
        gams_dir = Path(which_gams.strip()).parent
        log.info("Located GAMS executable in {}".format(gams_dir))

    fn = cfg["filename"]["license"]
    url = cfg["http base"] + cfg["path"] + fn
    log.info("Downloading from {}".format(url))

    r = requests.get(url, auth=auth)
    r.raise_for_status()
    (gams_dir / fn).write_text(r.text)


def fetch_scenarios(path, dbprops):
    mp = ixmp.Platform(dbprops=dbprops)
    for id, data in iter_scenarios():
        scen = message_ix.Scenario(mp, data["model"], data["scenario"])
        scen.to_excel((path / id).with_suffix(".xlsx"))


def iter_scenarios():
    try:
        with open(HERE.parent / "tests" / "data" / "scenarios.yaml", "r") as f:
            scenarios = yaml.safe_load(f)

    except FileNotFoundError as e:
        msg = (
            "Caught error: {}. Did you install message_ix using `$ pip "
            "install --editable`?".format(str(e))
        )
        raise FileNotFoundError(msg)

    for id, data in scenarios.items():
        yield id, (
            data["model"],
            data["scenario"],
            data["solve"],
            data.get("solve_options", {}),
            data["cases"],
        )


def make_db(path):
    mp = ixmp.Platform(backend="jdbc", driver="hsqldb", path=path / "scenarios")
    for id, data in iter_scenarios():
        scen = message_ix.Scenario(mp, data["model"], data["scenario"], version="new")
        message_ix.macro.init(scen)
        scen.read_excel(id + ".xlsx", add_units=True)
        scen.commit("saving")
    mp.close_db()

    # Pack the HSQLDB files into an archive
    cfg = _config()
    with tarfile.open(path / cfg["filename"]["data"], "w:gz") as tf:
        for fn in path.glob("scenarios*"):
            tf.add(fn)


def upload(path, username, password):
    get_event_loop().run_until_complete(_upload(path, username, password))


async def _upload(path, username, password):
    cfg = _config()
    async with connect(
        cfg["ssh"]["host"], username=username, password=password
    ) as conn:
        target = (conn, cfg["ssh"]["base"] + cfg["path"])
        await scp(path / cfg["filename"]["data"], target)
        await scp(path / cfg["filename"]["license"], target)


@click.group("nightly")
@click.option(
    "--path",
    type=click.Path(file_okay=False),
    default=str(DEFAULT_WORKDIR),
    help="Directory for file input/output.",
)
@click.pass_context
def cli(context, path):
    """Tools for slow-running/nightly continuous integration (CI) tests.

    These tools generate a test database used by tests/test_nightly.py to
    execute slow-running tests on large MESSAGEix scenarios. These tests are
    run nightly on CI infrastructure.

    To generate and upload the database, run the following commands. Read the
    --help for each command *before* running!

    \b
    1. message-ix nightly fetch
    2. message-ix nightly make
    3. message-ix nightly upload

    To test the download procedure that is executed for CI jobs:

    message-ix nightly download

    OTHER FILES

    ci/nightly.yaml: defines paths for the 'upload' and 'download' commands.

    tests/data/scenarios.yaml: defines the particular scenarios to be solved,
      and the checks to run on the solved scenarios.

    tests/test_nightly.yaml: executes the tests.
    """
    path = Path(path)
    if path == DEFAULT_WORKDIR:
        path.mkdir(parents=True, exist_ok=True)
    else:
        assert path.exists()
    context.obj = dict(path=path)


@cli.command()
@click.option("--dbprops", type=click.File())
@click.pass_obj
def fetch(context, dbprops):
    """Fetch scenarios from a master database to Excel files."""
    fetch_scenarios(context["path"], dbprops)


@cli.command()
@click.pass_obj
def make(context):
    """Generate the test database from the Excel files."""
    make_db(context["path"])


@cli.command("upload")
@click.argument("username")
@click.password_option(confirmation_prompt=False)
@click.pass_obj
def upload_cmd(context, username, password):
    """Upload the test database and license file.

    The two files are uploaded using SCP to a location that is also accessible
    via HTTP. You must provide your SSH USERNAME; and will be prompted for your
    password.
    """
    upload(context["path"], username, password)


@cli.command("download")
@click.pass_obj
def download_cmd(context):
    """Download the test database and license file.

    The following environment variables are required to download:

    \b
    - MESSAGE_IX_CI_USER
    - MESSAGE_IX_CI_PW

    The values for these variables can be found in an internal IIASA document.
    """
    download(context["path"], cli=True)
