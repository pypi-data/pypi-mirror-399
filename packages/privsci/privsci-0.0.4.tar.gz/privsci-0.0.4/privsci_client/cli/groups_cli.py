import click

@click.group()
@click.pass_context
def groups(ctx):
    pass

@groups.command("create")
@click.argument("group_name", required=True)
@click.pass_context
def create(ctx, group_name):
    client = ctx.obj
    response = client.groups.create(group_name)
    click.echo(response.get("message", ""))


@groups.command("transfer")
@click.argument("group", required=True)
@click.argument("new_owner", required=True)
@click.pass_context
def transfer(ctx, group, new_owner):
    client = ctx.obj
    response = client.groups.transfer(group, new_owner)
    click.echo(response.get("message", ""))

@groups.command("shut")
@click.argument("group", required=True)
@click.pass_context
def shut(ctx, group):
    client = ctx.obj
    response = client.groups.shut(group)
    click.echo(response.get("message", ""))

@groups.command("leave")
@click.argument("group", required=True)
@click.pass_context
def leave(ctx, group):
    client = ctx.obj
    response = client.groups.leave(group)
    click.echo(response.get("message", ""))

@groups.command("promote")
@click.argument("group", required=True)
@click.argument("member", required=True)
@click.pass_context
def promote(ctx, group, member):
    client = ctx.obj
    response = client.groups.promote(group, member)
    click.echo(response.get("message", ""))

@groups.command("demote")
@click.argument("group", required=True)
@click.argument("member", required=True)
@click.pass_context
def demote(ctx, group, member):
    client = ctx.obj
    response = client.groups.demote(group, member)
    click.echo(response.get("message", ""))

@groups.command("revoke")
@click.argument("group", required=True)
@click.argument("member", required=True)
@click.pass_context
def revoke(ctx, group, member):
    client = ctx.obj
    response = client.groups.revoke(group, member)
    click.echo(response.get("message", ""))

@groups.command("invite")
@click.argument("group", required=True)
@click.argument("member", required=True)
@click.argument("duration", required=True)
@click.pass_context
def invite(ctx, group, member, duration):
    client = ctx.obj
    response = client.groups.invite(group, member, duration)
    click.echo(response.get("message", ""))

@groups.command("join")
@click.argument("group", required=True)
@click.pass_context
def join(ctx, group):
    client = ctx.obj
    response = client.groups.join(group)
    click.echo(response.get("message", ""))

@groups.command("adjust_permission")
@click.argument("group", required=True)
@click.argument("member", required=True)
@click.argument("permissions", required=True)
@click.pass_context
def adjust_permission(ctx, group, member, permissions):
    client = ctx.obj
    create_permission = permissions[0].lower() == "c"
    sign_permission = permissions[1].lower() == "s"
    export_permission = permissions[2].lower() == "e"
    response = client.groups.adjust_permissions(
        group, 
        member,
        create_permission,
        sign_permission,
        export_permission
    )
    click.echo(response.get("message", ""))

@groups.command("list")
@click.pass_context
def groups_list(ctx):
    client = ctx.obj
    response = client.groups.groups()

    owned_groups = response["owned_groups"]
    normal_groups = response["normal_groups"]

    max_owned_name_len = max(len(og[0]) for og in owned_groups)
    max_norm_name_len = max(len(og[0]) for og in owned_groups)

    click.echo("\nOwned Groups")
    click.echo(f"{'Group Name':<{max_owned_name_len}} | {'Members':<10}")
    for og in owned_groups:
        click.echo(f"{og[0]:<{max_owned_name_len}} | {og[5]:<10}")
        
    click.echo("\nNormal Groups")
    click.echo(f"{'Group Name':<{max_norm_name_len}} | {'Role':<10} | {'Permissions':<11} | {'Members':<10}")
    for ng in normal_groups: 
        create_permission_character = "C" if ng[2] else "x"
        sign_permission_character = "S" if ng[3] else "x"
        export_permission_character = "E" if ng[4] else "x"
        permission_string = create_permission_character + sign_permission_character + export_permission_character
        click.echo(f"{ng[0]:<{max_norm_name_len}} | {ng[1]:<10} | {permission_string:<11} | {ng[5]:<10}")

    click.echo(response.get("message", ""))

@groups.command("members")
@click.argument("group", required=True)
@click.pass_context
def members_list(ctx, group):
    client = ctx.obj
    click.echo(group)
    response = client.groups.members(group)
    members = response["members"]
    max_email_len = max(len(member[0]) for member in members)
    click.echo(f"{'Email':<{max_email_len}} | {'Role':<10} | {'Permissions':<11}")
    for m in members:
        create_permission_character = "C" if m[2] else "x"
        sign_permission_character = "S" if m[3] else "x"
        export_permission_character = "E" if m[4] else "x"
        permission_string = create_permission_character + sign_permission_character + export_permission_character
        click.echo(f"{m[0]:<{max_email_len}} | {m[1]:<10} | {permission_string:<11}")

    click.echo(response.get("message", ""))

@groups.command("permissions")
@click.argument("group", required=True)
@click.pass_context
def permissions(ctx, group):
    client = ctx.obj
    response = client.groups.permissions(group)

    create_permission_character = "C" if response["create_permission"] else "x"
    sign_permission_character = "S" if response["sign_permission"] else "x"
    export_permission_character = "E" if response["export_permission"] else "x"
    permission_string = create_permission_character + sign_permission_character + export_permission_character
    
    click.echo(permission_string)