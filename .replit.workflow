[job_board_app]
name = "Remote Work Job Board"
entrypoint = "python job_api.py"
language = "python"
run = "python job_api.py"
environment = {}
ports = [
  { port=8080, name="Web App", visibility="public" }
]