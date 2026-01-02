# vmux

Run any command in the cloud. Like tmux, but virtual.

## Install

```bash
# Install globally
uv tool install vmux-cli

# Or run without installing
uvx --from vmux-cli vmux run python train.py
```

## Usage

```bash
# Login with GitHub
vmux login

# Run a command (streams output)
vmux run python train.py

# Run in background
vmux run --detach python long_job.py

# Run a web server with preview URL
vmux run --preview uvicorn main:app
# → Preview: https://abc123.purr.ge

# Attach to running job
vmux attach <job_id>

# View logs
vmux logs <job_id>

# List jobs
vmux ps
```

## Features

- **Cloud execution**: Run Python scripts on Cloudflare containers
- **Automatic dependencies**: Uses `uv` for instant package installs
- **Interactive terminal**: Attach to running jobs via tmux
- **Background jobs**: Detach and reattach anytime
- **Preview URLs**: Share web apps instantly with `--preview` (port 8000)

## License

MIT
