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
import zipfile
from pathlib import Path


AGENT_RUNTIME_DIR = "agent_runtime"
PID_FILE = os.path.join(AGENT_RUNTIME_DIR, "agent.pid")
LOG_FILE = os.path.join(AGENT_RUNTIME_DIR, "agent.log")
CONFIG_FILE = "agent.toml"




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
   click.echo(" Welcome to Agent Deploy!")
   click.echo("Let's set up your new agent.\n")


   agent_name = Prompt.ask("What is the name of your agent?", default="my-agent")
   agent_file = Prompt.ask("What is the path to your agent's Python file?", default="main.py")
   agent_callable = Prompt.ask("What is the function or class to call?", default="my_agent_func")
   python_version = Prompt.ask("What Python version for the agent's environment?", default="3.12")
   requirements_file = Prompt.ask("Path to your agent's requirements.txt file (if you use one)", default="requirements.txt")




   config = {
       "agent": {
           "name": agent_name,
           "file": agent_file,
           "callable": agent_callable,
       },
       "api": {
           "port": 8000,
           "host": "127.0.0.1",
       },
       "build": {
           "python_version": python_version,
           "requirements": requirements_file,
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
   click.echo("\n Initialization complete! You can now run this tool to deploy your agent.")




@cli.command()
def deploy():
   """
   Deploys the agent as a background process locally.
   """
   click.echo(" Starting local agent deployment...")
   config = get_config()
   if not config:
       click.secho(f" Error: `{CONFIG_FILE}` not found. Please run `python main.py init` first.", fg="red")
       return


   if os.path.exists(PID_FILE):
       click.secho("Agent is already running. Use `stop` or `restart`.", fg="yellow")
       return


   _generate_api_wrapper(config)


   api_config = config.get("api", {})
   host = api_config.get("host", "127.0.0.1")
   port = api_config.get("port", 8000)


   command = [
       sys.executable, "-u", "-m", "uvicorn", "agent_runtime.api_wrapper:app",
       f"--host={host}", f"--port={port}",
   ]
   with open(LOG_FILE, "wb") as log:
       process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
   with open(PID_FILE, "w") as f:
       f.write(str(process.pid))


   click.secho(f" Agent deployed successfully!", fg="green")
   click.echo(f"   - PID: {process.pid}")
   click.echo(f"   - Log: {LOG_FILE}")
   click.echo(f"   - API running at: http://{host}:{port}")


def _generate_api_wrapper(config):
   """Generates the FastAPI wrapper for the agent."""
   agent_config = config.get("agent", {})
   agent_file = agent_config.get("file")
   agent_callable = agent_config.get("callable")


   if not all([agent_file, agent_callable]):
       click.secho(" Error: Agent file or callable not configured in `agent.toml`.", fg="red")
       raise click.Abort()


   os.makedirs(AGENT_RUNTIME_DIR, exist_ok=True)
   # Create __init__.py to make it a package
   Path(os.path.join(AGENT_RUNTIME_DIR, "__init__.py")).touch()




   api_wrapper_template = '''
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import sys, os
from importlib import util


# Load .env from the project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


file_path = "{agent_file_path}"
callable_name = "{callable_name}"


# Add project root to sys.path to allow imports within the agent code
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
   sys.path.insert(0, project_root)


spec = util.spec_from_file_location("agent_module", file_path)
agent_module = util.module_from_spec(spec)
sys.modules["agent_module"] = agent_module
spec.loader.exec_module(agent_module)
agent_callable = getattr(agent_module, callable_name)


app = FastAPI()


@app.post("/invoke")
async def invoke(request: Request):
   body = await request.json()
   result = await agent_callable(body)
   return result


@app.get("/")
def health_check():
   return {{"status": "ok"}}
'''
   wrapper_code = api_wrapper_template.format(
       agent_file_path=agent_file, # Use the relative path directly
       callable_name=agent_callable
   )
   with open(os.path.join(AGENT_RUNTIME_DIR, "api_wrapper.py"), "w") as f:
       f.write(wrapper_code)
   click.echo(" Generated API wrapper.")


def _generate_dockerfile(config, path):
   """Generates the Dockerfile for the agent's cloud deployment."""
   build_config = config.get("build", {})
   python_version = build_config.get("python_version", "3.12")
  
   # Flexible dependency handling
   if os.path.exists("pyproject.toml"):
       click.echo(" Found `pyproject.toml`, using it for dependencies.")
       dep_copy_line = "COPY pyproject.toml uv.lock* ./"
       dep_install_line = "RUN uv pip install --system --no-cache ."
   else:
       requirements_file = build_config.get("requirements")
       if not requirements_file or not os.path.exists(requirements_file):
           click.secho(" `pyproject.toml` not found and `requirements.txt` is missing or not specified.", fg="yellow")
           click.secho("Your container may fail to build if it has dependencies.", fg="yellow")
           dep_copy_line = "# No dependency file found"
           dep_install_line = "# No dependency file found"
       else:
           click.echo(f" Found `{requirements_file}`, using it for dependencies.")
           dep_copy_line = f"COPY {requirements_file} requirements.txt"
           dep_install_line = "RUN uv pip install --system --no-cache -r requirements.txt"




   dockerfile_template = f'''
FROM python:{python_version}-slim
WORKDIR /app
RUN pip install uv


{dep_copy_line}
{dep_install_line}


COPY . .


EXPOSE 8080
CMD ["uvicorn", "agent_runtime.api_wrapper:app", "--host", "0.0.0.0", "--port", "8080"]
'''
   with open(path, "w") as f:
       f.write(dockerfile_template)
   click.echo(f" Generated temporary Dockerfile at '{path}'.")




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




@click.group()
def cloud():
   """Manage cloud deployments via a central backend."""
   pass


@cloud.command(name="deploy")
def cloud_deploy():
   """
   Packages and deploys the agent via the management backend.
   """
   click.echo(" Starting cloud deployment...")
   config = get_config()
   if not config:
       click.secho(" Error: `agent.toml` not found. Please run `init` first.", fg="red")
       return
  
   backend_url = "https://agent-deploy-backend-460024322232.us-central1.run.app"
   deploy_endpoint = f"{backend_url.rstrip('/')}/deploy"
  
   temp_dockerfile_path = "Dockerfile"


   try:
       _generate_api_wrapper(config)
       _generate_dockerfile(config, temp_dockerfile_path)


       with tempfile.TemporaryDirectory() as temp_dir:
           zip_path = os.path.join(temp_dir, "agent_project.zip")
           click.echo(f" Creating archive at: {zip_path}")


           with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
               for root, dirs, files in os.walk("."):
                   dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.git']]
                  
                   for file in files:
                       file_path = os.path.join(root, file)
                       arcname = os.path.relpath(file_path, ".")
                       zf.write(file_path, arcname)


           click.echo(f" Project zipped. Uploading to management backend...")
          
           with open(zip_path, 'rb') as f:
               files = {'file': ('agent_project.zip', f, 'application/zip')}
               response = requests.post(deploy_endpoint, files=files, timeout=300)


           click.echo("--- SERVER RESPONSE (START) ---")
           click.echo(response.text)
           click.echo("--- SERVER RESPONSE (END) ---")


           if response.status_code == 200:
               data = response.json()
               click.secho(" Deployment successful!", fg="green")
               click.echo(f"   Service Name: {data.get('service_name')}")
               click.echo(f"   Public URL: {data.get('url')}")
           else:
               try:
                   error_detail = response.json().get('detail', response.text)
               except requests.exceptions.JSONDecodeError:
                   error_detail = "Could not parse JSON from error response."
               click.secho(f" Deployment failed (HTTP {response.status_code}): {error_detail}", fg="red")


   except FileNotFoundError as e:
       click.secho(f" Error: Could not find project file to zip: {e}. Ensure you are in the project root.", fg="red")
   except requests.exceptions.RequestException as e:
       click.secho(f" Error: Could not connect to the management backend: {e}", fg="red")
   except Exception as e:
       click.secho(f" An unexpected error occurred: {e}", fg="red")
   finally:
       if os.path.exists(temp_dockerfile_path):
           os.remove(temp_dockerfile_path)
           click.echo(f" Cleaned up temporary Dockerfile.")
       if os.path.exists(AGENT_RUNTIME_DIR):
           shutil.rmtree(AGENT_RUNTIME_DIR)
           click.echo(f" Cleaned up temporary runtime directory.")




cli.add_command(cloud)




if __name__ == "__main__":
   cli()