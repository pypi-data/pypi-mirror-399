from ..config_store import load_config, save_config
import click

@click.group()
@click.pass_context
def keys(ctx):
    pass

@keys.command("generate")
@click.argument("key_name", required=True)
@click.option("--activate", is_flag=True, help="Set the new key as the active API key")
@click.pass_context
def generate_key(ctx, key_name, activate):
    client = ctx.obj

    response = client.keys.generate_key(key_name)
    api_key = response.get("api_key")

    click.echo("Generated API key:")
    click.echo(api_key)
    click.echo(response.get("message", ""))

    if activate and api_key:
        cfg = load_config()
        cfg["api_key"] = api_key
        save_config(cfg)

        client.set_api_key(api_key)
        click.echo("This key has been saved as the active API key.")

@keys.command("switch")
@click.argument("api_key", required=True)
@click.pass_context
def switch_key(ctx, api_key):
    client = ctx.obj

    cfg = load_config()
    cfg["api_key"] = api_key
    save_config(cfg)

    client.set_api_key(api_key)
    click.echo(f"Switched active key to {api_key}")

@keys.command("revoke")
@click.argument("api_key", required=True)
@click.pass_context
def revoke_key(ctx, api_key):
    client = ctx.obj
    
    response = client.keys.revoke_key(api_key)
    click.echo(response.get("message", f"Revoked {api_key}."))