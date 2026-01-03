import click
import os

@click.command()
def setup_wizard():
    click.secho("\n🚀 CubePlus SDK: Quick Configuration Wizard", fg="cyan", bold=True)
    click.echo("This will generate a .env file for your trading environment.\n")
    
    # User Inputs
    api_key = click.prompt("1. Enter your API Key (Client ID)")
    password = click.prompt("2. Enter your CubePlus Password", hide_input=True)
    totp_secret = click.prompt("3. Enter your TOTP Secret Key")
    
    # .env Content
    env_content = (
        f"TRADEJINI_API_KEY={api_key}\n"
        f"TRADEJINI_PASSWORD={password}\n"
        f"TRADEJINI_TOTP_SECRET={totp_secret}\n"
    )
    
    # Save to the current working directory
    with open(".env", "w") as f:
        f.write(env_content)
    
    click.secho("\n✅ .env file created successfully!", fg="green")
    click.echo("You are now ready to trade with CubePlus.")