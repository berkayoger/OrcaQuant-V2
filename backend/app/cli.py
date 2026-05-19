import click
from flask import Flask

from app.seeds.seed_assets import seed_assets
from app.services.plans.seed_plans import seed_plans


def register_cli(app: Flask) -> None:
    @app.cli.command("seed-assets")
    def seed_assets_command() -> None:
        assets = seed_assets()
        click.echo(f"Seeded assets: {len(assets)}")

    @app.cli.command("seed-plans")
    def seed_plans_command() -> None:
        result = seed_plans()
        click.echo(f"Seeded plans: {result['plans']}, limits: {result['limits']}")
