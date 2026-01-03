import click
import os

@click.command()
def setup_wizard():
    click.secho("\n🚀 Tradejini API: Setup Wizard", fg="blue", bold=True)
    api_key     = click.prompt("1. Enter your API Key")
    client_id   = click.prompt("2. Enter your Client ID")
    password    = click.prompt("3. Enter your Password", hide_input=True)
    otp_secret  = click.prompt("4. Enter your TOTP Secret Key")
    
    env_content = (
        f"TRADEJINI_API_KEY={api_key}\n"
        f"TRADEJINI_CLIENT_ID={client_id}\n"
        f"TRADEJINI_PASSWORD={password}\n"
        f"TRADEJINI_TOTP_SECRET={otp_secret}\n"
    )
    
    with open(".env", "w") as f:
        f.write(env_content)
    click.secho("\n✅ Configuration Successful! .env created locally.", fg="green")