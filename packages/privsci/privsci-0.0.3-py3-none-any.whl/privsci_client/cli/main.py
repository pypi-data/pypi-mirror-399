import click
from ..client import Client
from .keys_cli import keys
from .groups_cli import groups
from .accounts_cli import accounts
from .config_cli import config
from ..config_store import load_config, save_config

@click.group()
@click.option("--base-url", default=None)
@click.pass_context
def cli(ctx, base_url):
    cfg = load_config()
    base_url = (base_url or cfg.get("base_url"))

    if base_url and base_url != cfg.get("base_url"):
        cfg["base_url"] = base_url
        save_config(cfg)

    client = Client(base_url)

    token = cfg.get("token")
    api_key = cfg.get("api_key")

    if token:
        client.set_token(token)
    if api_key:
        client.set_api_key(api_key)

    ctx.obj = client

cli.add_command(config)
cli.add_command(accounts)
cli.add_command(keys)
cli.add_command(groups)
