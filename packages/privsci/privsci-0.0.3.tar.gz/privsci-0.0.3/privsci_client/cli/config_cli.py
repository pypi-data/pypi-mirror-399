import click
from ..database import init_db
from ..config_store import load_config, save_config

@click.group()
@click.pass_context
def config(ctx):
    pass

@config.command("set")
@click.option("--default_db", is_flag=True, help="True will use default, client-side DB storage.")
@click.option("--org", help="Name of the organization.")
@click.option("--domain", help="Target domain.")
@click.option("--rep", help="Data representation format.")
@click.pass_context
def config_cmd(ctx, default_db, org, domain, rep):    
    try:
        cfg = load_config()
    except Exception as e:
        click.secho(f"Error loading config: {e}", fg="red")
        ctx.exit(1)

    updates = {}

    if default_db:
        cfg["DEFAULT_DB"] = default_db
        updates["DEFAULT_DB"] = default_db
    
    if org: 
        cfg["ORG_NAME"] = org
        updates["ORG_NAME"] = org

    if domain:
        cfg["DOMAIN"] = domain
        updates["DOMAIN"] = domain

    if rep:
        cfg["REPRESENTATION"] = rep
        updates["REPRESENTATION"] = rep

    if not updates:
        click.secho("No options provided. Nothing to update.", fg="yellow")
        click.echo("Try: cli config set --help")
        return
    
    save_config(cfg)

    click.secho("Configuration updated successfully:", fg="green")
    for key, val in updates.items():
        click.echo(f"  {key} = {val}")

@config.command("init")
@click.option("--reset", is_flag=True, help="Reset client side SQLite database.")
@click.pass_context
def init_cmd(ctx, reset):
    if reset:
        click.confirm(
            "WARNING: You are about to reset the database. \n"
            "This will PERMANENTLY DELETE all local data. \n"
            "Do you want to continue?",
            abort=True 
        )

    cfg = load_config()
    db_url = cfg.get("DB_URL")
        
    init_db(db_path=db_url, reset=reset)

    if reset:
        click.secho("Success: Fresh database initialized.", fg="green")
    else:
        click.echo("Database connection verified and tables ensured.")