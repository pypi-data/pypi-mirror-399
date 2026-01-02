import toml
import click
from rich.prompt import Prompt
import os
import subprocess
import sys
import signal
import time
import requests
import shutil
import tempfile
import json


AGENT_DIR = ".agent"
PID_FILE = os.path.join(AGENT_DIR, "agent.pid")
LOG_FILE = os.path.join(AGENT_DIR, "agent.log")
CONFIG_FILE = "agent.toml"
CLOUD_DEPLOYMENT_FILE = os.path.join(AGENT_DIR, "cloud_deployment.json")




def get_config():
   try:
       with open(CONFIG_FILE, "r") as f:
           return toml.load(f)
   except FileNotFoundError:
       return None


def is_process_running(pid):
   try:
       os.kill(pid, 0)
   except OSError:
       return False
   else:
       return True


@click.group()
def cli():
   """
   A simple deployment tool for AI agents.
   """
   pass


@cli.command()
def init():
   """
   Initialize a new agent configuration.
   """
   click.echo(" Welcome to Agentctlx!")
   click.echo("Let's set up your new agent.\n")


   agent_name = Prompt.ask("What is the name of your agent?", default="my-agent")
   agent_file = Prompt.ask("What is the path to your agent's Python file?", default="src/agent.py")
   agent_callable = Prompt.ask("What is the function or class to call?", default="my_agent_func")


   config = {
       "agent": {
           "name": agent_name,
           "file": agent_file,
           "callable": agent_callable,
       },
       "api": {
           "port": 8000,
           "host": "127.0.0.1",
       }
   }


   with open(CONFIG_FILE, "w") as f:
       toml.dump(config, f)
  
   click.echo(f"\n Created `{CONFIG_FILE}` configuration file.")


   click.echo("\nNow, let's add your API keys. Leave blank if not needed.")
   openai_key = Prompt.ask("[Optional] OpenAI API Key")
   anthropic_key = Prompt.ask("[Optional] Anthropic API Key")
   gemini_key = Prompt.ask("[Optional] Gemini API Key")


   with open(".env", "w") as f:
       if openai_key: f.write(f'OPENAI_API_KEY="{openai_key}"\n')
       if anthropic_key: f.write(f'ANTHROPIC_API_KEY="{anthropic_key}"\n')
       if gemini_key: f.write(f'GEMINI_API_KEY="{gemini_key}"\n')


   click.echo(" Created `.env` file for your secrets.")
   click.echo("\n Initialization complete! You can now run `agentctlx deploy`.")




@cli.command()
def deploy():
   """
   Deploys the agent as a background process.
   """
   click.echo(" Starting agent deployment...")
   config = get_config()
   if not config:
       click.secho(f" Error: `{CONFIG_FILE}` not found. Please run `agentctlx init` first.", fg="red")
       return


   if os.path.exists(PID_FILE):
       click.secho("Agent is already running. Use `stop` or `restart`.", fg="yellow")
       return


   agent_config = config.get("agent", {})
   api_config = config.get("api", {})
   agent_file = agent_config.get("file")
   agent_callable = agent_config.get("callable")
   host = api_config.get("host", "127.0.0.1")
   port = api_config.get("port", 8000)


   if not all([agent_file, agent_callable]):
       click.secho(" Error: Agent file or callable not configured in `agent.toml`.", fg="red")
       return


   os.makedirs(AGENT_DIR, exist_ok=True)


   api_wrapper_template = """
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import sys, os
from importlib import util


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


file_path = "{agent_file_path}"
callable_name = "{callable_name}"


spec = util.spec_from_file_location("agent_module", file_path)
agent_module = util.module_from_spec(spec)
sys.modules["agent_module"] = agent_module
spec.loader.exec_module(agent_module)
agent_callable = getattr(agent_module, callable_name)


app = FastAPI()


@app.post("/invoke")
async def invoke(request: Request):
   body = await request.json()
   prompt = body.get("prompt")
   if prompt is None:
       return {{"error": "Missing 'prompt' in request body"}}, 400
   result = await agent_callable(prompt)
   return {{"data": result}}


@app.get("/")
def health_check():
   return {{"status": "ok"}}
"""
   wrapper_code = api_wrapper_template.format(
       agent_file_path=os.path.abspath(agent_file),
       callable_name=agent_callable
   )
   with open(os.path.join(AGENT_DIR, "api_wrapper.py"), "w") as f:
       f.write(wrapper_code)
   click.echo(" Generated API wrapper.")


   command = [
       sys.executable, "-u", "-m", "uvicorn", "api_wrapper:app",
       f"--host={host}", f"--port={port}",
       "--app-dir", os.path.abspath(AGENT_DIR),
   ]
   with open(LOG_FILE, "wb") as log:
       process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
   with open(PID_FILE, "w") as f:
       f.write(str(process.pid))


   click.secho(f" Agent deployed successfully!", fg="green")
   click.echo(f"   - PID: {process.pid}")
   click.echo(f"   - Log: {LOG_FILE}")
   click.echo(f"   - API running at: http://{host}:{port}")


@cli.command()
def status():
   """
   Checks the status of the deployed agent.
   """
   config = get_config()
   if not os.path.exists(PID_FILE) or not config:
       click.secho(" Agent is STOPPED.", fg="red")
       return


   with open(PID_FILE, "r") as f:
       pid = int(f.read())


   if not is_process_running(pid):
       click.secho(" Agent is STOPPED (stale PID file).", fg="red")
       os.remove(PID_FILE)
       return


   api_config = config.get("api", {})
   host = api_config.get("host", "127.0.0.1")
   port = api_config.get("port", 8000)
   url = f"http://{host}:{port}/"


   try:
       response = requests.get(url, timeout=5)
       if response.status_code == 200:
           click.secho(f" Agent is RUNNING", fg="green")
           click.echo(f"   - PID: {pid}")
           click.echo(f"   - URL: {url}")
       else:
           click.secho(f" Agent is UNHEALTHY (status code {response.status_code}).", fg="yellow")
   except requests.exceptions.RequestException:
       click.secho(" Agent is UNRESPONSIVE (health check failed).", fg="yellow")


@cli.command()
def stop():
   """
   Stops the deployed agent.
   """
   if not os.path.exists(PID_FILE):
       click.secho(" Agent is already stopped.", fg="yellow")
       return


   with open(PID_FILE, "r") as f:
       pid = int(f.read())


   click.echo(f"Stopping agent process (PID: {pid})...")
   try:
       os.kill(pid, signal.SIGTERM)
       # Wait a moment for the process to terminate
       time.sleep(1)
       if is_process_running(pid):
           click.secho("Process did not terminate gracefully, forcing...", fg="yellow")
           os.kill(pid, signal.SIGKILL)
   except OSError:
       click.secho("Process not found (already stopped?).", fg="yellow")


   os.remove(PID_FILE)
   click.secho(" Agent stopped.", fg="green")


@cli.command()
@click.pass_context
def restart(ctx):
   """
   Restarts the deployed agent.
   """
   click.echo(" Restarting agent...")
   ctx.invoke(stop)
   time.sleep(2) # Give OS time to free up the port
   ctx.invoke(deploy)


@cli.command()
@click.option("-f", "--follow", is_flag=True, help="Follow the log output.")
def logs(follow):
   """
   Shows the agent's logs.
   """
   if not os.path.exists(LOG_FILE):
       click.echo("No log file found.")
       return


   with open(LOG_FILE, "r") as f:
       if not follow:
           click.echo(f.read())
           return
      
       # Follow logic
       f.seek(0, 2) # Go to the end of the file
       while True:
           line = f.readline()
           if not line:
               time.sleep(0.1)
               continue
           click.echo(line, nl=False)


def get_cloud_deployment():
   """Reads cloud deployment info (service_name, token) from the local file."""
   if not os.path.exists(CLOUD_DEPLOYMENT_FILE):
       return None
   with open(CLOUD_DEPLOYMENT_FILE, "r") as f:
       try:
           return json.load(f)
       except json.JSONDecodeError:
           return None


@click.group()
def cloud():
   """Manage cloud deployments via a central backend."""
   pass


@cloud.command()
def deploy():
   """
   Packages and deploys the agent.
   """
   click.echo(" Starting cloud deployment...")
   backend_url="https://agent-deploy-backend-460024322232.us-central1.run.app"


   deploy_endpoint = f"{backend_url.rstrip('/')}/deploy"
  

   try:
       with tempfile.TemporaryDirectory() as temp_dir:
           zip_base_name = os.path.join(temp_dir, "agent_project")

           zip_path = shutil.make_archive(zip_base_name, 'zip', root_dir=".")
          
           click.echo(" Project zipped. Uploading to management backend...")


           with open(zip_path, 'rb') as f:
               files = {'file': ('agent_project.zip', f, 'application/zip')}
               response = requests.post(deploy_endpoint, files=files, timeout=300)


           if response.status_code == 200:
               data = response.json()
               deployment_info = {
                   "service_name": data.get("service_name"),
                   "url": data.get("url"),
                   "auth_token": data.get("auth_token"),
               }
               os.makedirs(AGENT_DIR, exist_ok=True)
               with open(CLOUD_DEPLOYMENT_FILE, "w") as f:
                   json.dump(deployment_info, f)

               click.secho(" Deployment successful!", fg="green")
               click.echo(f"   Service Name: {deployment_info['service_name']}")
               click.echo(f"   Public URL: {deployment_info['url']}")
               click.echo(" Run `agentcltx cloud status` or `agentcltx cloud logs` to see details.")
           else:
               error_detail = response.json().get('detail', response.text)
               click.secho(f" Deployment failed (HTTP {response.status_code}):", fg="red")
               click.secho(error_detail, fg="red")

   except Exception as e:
       click.secho(f" An unexpected error occurred: {e}", fg="red")


@cloud.command(name="status")
def cloud_status():
   """Gets the status of the deployed cloud agent."""
   deployment = get_cloud_deployment()
   if not deployment:
       click.secho(" No cloud deployment found. Run `cloud deploy` first.", fg="red")
       return


   backend_url = "https://agent-deploy-backend-460024322232.us-central1.run.app" # Must be the same as in deploy
   service_name = deployment["service_name"]
   token = deployment["auth_token"]
  
   status_url = f"{backend_url.rstrip('/')}/status/{service_name}"
   headers = {"Authorization": f"Bearer {token}"}


   try:
       response = requests.get(status_url, headers=headers, timeout=30)
       if response.status_code == 200:
           data = response.json()
           click.secho(f" Agent '{service_name}' is available.", fg="green")
           click.echo(f"   URL: {data.get('url')}")
           click.echo(f"   Latest Ready Revision: {data.get('latest_ready_revision')}")
           click.echo(f"   Last Updated: {data.get('update_time')}")
       else:
           error_detail = response.json().get('detail', response.text)
           click.secho(f" Could not get status (HTTP {response.status_code}):", fg="red")
           click.secho(error_detail, fg="red")
   except requests.exceptions.RequestException as e:
       click.secho(f" Error connecting to the backend: {e}", fg="red")


@cloud.command(name="logs")
@click.option("--limit", default=50, help="Number of log entries to fetch.")
def cloud_logs(limit):
   """Fetches the latest logs for the deployed cloud agent."""
   deployment = get_cloud_deployment()
   if not deployment:
       click.secho(" No cloud deployment found. Run `cloud deploy` first.", fg="red")
       return


   backend_url = "https://agent-deploy-backend-460024322232.us-central1.run.app" # Must be the same as in deploy
   service_name = deployment["service_name"]
   token = deployment["auth_token"]
  
   logs_url = f"{backend_url.rstrip('/')}/logs/{service_name}?limit={limit}"
   headers = {"Authorization": f"Bearer {token}"}


   try:
       response = requests.get(logs_url, headers=headers, timeout=60)
       if response.status_code == 200:
           data = response.json()
           logs = data.get("logs", [])
           if not logs:
               click.echo("No logs found for this service yet.")
               return
          
           click.secho(f" Showing last {len(logs)} log entries for '{service_name}':", bold=True)
           for log in logs:
               click.echo(f"[{log['timestamp']}] [{log['severity']}] {log['message']}")
       else:
           error_detail = response.json().get('detail', response.text)
           click.secho(f" Could not get logs (HTTP {response.status_code}):", fg="red")
           click.secho(error_detail, fg="red")
   except requests.exceptions.RequestException as e:
       click.secho(f" Error connecting to the backend: {e}", fg="red")


cli.add_command(cloud)




if __name__ == "__main__":
   cli()