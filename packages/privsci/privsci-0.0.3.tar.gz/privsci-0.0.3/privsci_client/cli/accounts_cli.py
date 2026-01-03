import click
import getpass

@click.group()
@click.pass_context
def accounts(ctx):
    pass

@accounts.command("login")
@click.argument("email")
@click.pass_context
def login_cmd(ctx, email):
    password = getpass.getpass(prompt="Password: ")

    client = ctx.obj
    response = client.accounts.login(email, password)
    click.echo(response.get("message", "Logged in."))

@accounts.command("logout")
@click.pass_context
def logout_cmd(ctx):
    client = ctx.obj
    response = client.accounts.logout()
    click.echo(response.get("message", "Logged out."))
