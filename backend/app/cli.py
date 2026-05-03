import click
from flask import Flask

from app.seeds.seed_assets import seed_assets


def register_cli(app: Flask) -> None:
    @app.cli.command("seed-assets")
    def seed_assets_command() -> None:
        assets = seed_assets()
        click.echo(f"Seeded assets: {len(assets)}")
