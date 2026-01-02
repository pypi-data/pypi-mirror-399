import click
import glob
from pathlib import Path
from rich import print
from rich.panel import Panel
from rich.console import Group
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.live import Live

@click.group()
def app():
    """
    Get files from GoPro and organise in folders
    """
    pass


def list_prefixes(input_folder):
    prefixes = [i.name[:4] for i in list((input_folder.glob("*GOPRO/*.JPG")))]
    prefixes = list(set(prefixes))
    prefixes.sort()
    print("[green]Found these sub-folders with GoPro specific prefixes[/green]: {}".format(prefixes))
    return prefixes


@app.command("show-files")
@click.option("--input-folder",
              default=".",
              type=click.Path())
def show_files(input_folder):
    """
    Show which prefixes/series of images are found
    and how many of them per series
    """
    print(Panel(
        "[bold]Trying to find GoPro-prefixed files in {}".format(input_folder),
        title="Task"))
    input_folder = (Path.cwd() / input_folder).resolve()
    prefixes = list_prefixes(input_folder)
    for prefix in prefixes:
        num_files = len(list(input_folder.glob("*GOPRO/{}*.JPG".format(prefix))))
        print("[yellow]Prefix [italic]{}[/italic] has {} images[/yellow]".format(prefix, num_files))


@app.command("copy-files")
@click.option("--input-folder",
              default=".",
              type=click.Path())
@click.option("--output-folder",
              required=True,
              type=click.Path())
def copy_files(input_folder, output_folder):
    """
    Give an input & output folder to copy unsorted
    GoPro files into sub-folders organised by
    image prefix/series in the destination folder
    """
    input_folder = (Path.cwd() / input_folder).resolve()
    output_folder = (Path.cwd() / output_folder).resolve()
    print(Panel("[bold]Preparing to copy files from[/bold] [italic]{}[/italic] to [italic]{}[/italic]".format(input_folder, output_folder),
                title="Task"))
    prefixes = list_prefixes(input_folder=input_folder)
   
   # make progress bars
    total_files = len(list((input_folder.glob("*GOPRO/*.JPG"))))

    uploading_progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            TextColumn("[{task.completed}/{task.total}]"))

    tf_progress = uploading_progress.add_task("[red]Total progress of files copied[/red]:",total=total_files)

    pf_progress = uploading_progress.add_task("[green]Progress by prefix:[/green]:",total=len(prefixes))


  #   uploading_progress.start()

    progress_group = Panel(uploading_progress, title="Copy progress")
    with Live(progress_group) as live_render:
        for prefix in prefixes:
            p = (Path(output_folder) / prefix).resolve()
            print("[green]Copying files with prefix {} to {}[/green] ".format(prefix, p))
            p.mkdir(parents=True, exist_ok=True)
            per_prefix_progress = uploading_progress.add_task("[yellow]Copy progress for {} prefix[/yellow]".format(prefix),
                                                     total=len(list(
                                                         input_folder.glob("*GOPRO/{}*.JPG".format(prefix))
                                                         )))

            for f in input_folder.glob("*GOPRO/{}*.JPG".format(prefix)):
                f.copy((p / f.name).resolve())
                uploading_progress.advance(tf_progress)
                uploading_progress.advance(per_prefix_progress)
            uploading_progress.update(per_prefix_progress, visible=False)
            uploading_progress.advance(pf_progress)
    uploading_progress.stop()
