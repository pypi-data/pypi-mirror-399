import os.path
from pathlib import Path

import toml
import typer
from rich.console import Console
from rich.table import Table

from heisenberg_cli.command import (
    SubmitCommand,
    JobMetadata,
    JobExecutionSchedule,
    ExecutionMode,
)
from heisenberg_cli.command.code_inspect import CodeInspectCommand
from heisenberg_cli.command.job_status import JobStatusCommand
from heisenberg_cli.command.setup_project import RECOMMENDATION, SetUpProjectCommand
from heisenberg_cli.exceptions import NoConfigSetError, RestClientException
from heisenberg_cli.utils.feature_extractor import extract_features_from_directory

app = typer.Typer(
    name="heisenberg-cli",
    help="Heisenberg CLI - Command line interface for publishing and managing jobs on Heisenberg.",
    add_completion=False,
)
console = Console()
DEFAULT_DATA_SIZE = 1_000_000  # 1 GB
DEFAULT_EXPIRATION = 86400

state = {"verbose": False}


def load_config(config_file: Path = Path.home() / ".codemanager.toml") -> dict:
    try:
        if config_file.exists():
            return toml.load(config_file)
        else:
            raise NoConfigSetError("Config file not found.")
    except toml.TomlDecodeError:
        raise NoConfigSetError("Config file is malformed.")


@app.command(name="create-project")
def create_project(
    name: str = typer.Argument(..., help="Name of the project to create"),
    usecase: str = typer.Option(
        default=RECOMMENDATION,
        help="Project template to use. Available: recommendation",
    ),
):
    """
    Create a new Heisenberg project from a template.

    This command scaffolds a new project directory with all necessary files
    for developing and publishing a Heisenberg job.

    Example:
        heisenberg-cli create-project my-recommender
        heisenberg-cli create-project my-project --usecase recommendation
    """
    command = SetUpProjectCommand(name, usecase, os.getcwd(), report=state["verbose"])
    try:
        command.handle()
    except Exception as exc:
        cli_msg = typer.style(
            f"Setup project in usecase {usecase} failed because of {str(exc)}",
            fg=typer.colors.RED,
            bold=True,
        )
    else:
        cli_msg = typer.style(
            f"Project '{name}' created successfully!\n\n"
            f"To publish your project:\n"
            f"  heisenberg-cli publish {name} --name {name} --version 0.1.0",
            fg=typer.colors.GREEN,
            bold=True,
        )
    typer.echo(cli_msg)


@app.command(name="inspect")
def inspect_code(
    directory: str = typer.Argument(..., help="Directory containing the code to inspect"),
    config_file: Path = typer.Option(
        Path.home() / ".codemanager.toml",
        help="Path to the configuration file",
    ),
):
    """
    Analyze code complexity and update the configuration file.

    This command inspects your project code to calculate a complexity factor,
    which is used for resource allocation when running your job. The complexity
    factor is automatically saved to your config file.

    Example:
        heisenberg-cli inspect ./my-project
    """
    try:
        config = load_config(config_file)
        if not config:
            raise NoConfigSetError()

        manager = CodeInspectCommand(config)
        complexity = manager.handle(directory)
        config["code"] = {**config.get("code", {}), "complexity_factor": complexity}

        with open(config_file, "w") as f:
            toml.dump(config, f)

        typer.echo(f"Configuration updated in {config_file}")
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)


def _display_job_summary(
    package, identifier: str, job_response: dict
) -> None:
    """Display job submission summary in a formatted table."""
    job_response_data = job_response.get("data", {})

    table = Table(title="Publish Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Name", package.name)
    table.add_row("Version", package.version)
    table.add_row("Hash", package.hash)
    table.add_row("S3 Location", identifier)
    table.add_row("Job ID", str(job_response_data.get("id", "N/A")))
    table.add_row("Status", job_response_data.get("status", {}).get("state", "N/A"))

    console.print(table)


@app.command(name="publish")
def publish_job(
    directory: str = typer.Argument(
        ...,
        help="Path to the project directory containing the code to publish",
    ),
    name: str = typer.Option(
        ...,
        "--name", "-n",
        help="Unique name for the job (used to identify it in Heisenberg)",
    ),
    version: str = typer.Option(
        ...,
        "--version", "-v",
        help="Version of the job (e.g., 0.1.0, 1.0.0)",
    ),
    confidential_level: str = typer.Option(
        "default",
        "--confidential-level", "-c",
        help="Security level for the job: default, internal, confidential, or secret",
    ),
    execution_mode: str = typer.Option(
        "single",
        "--execution-mode", "-e",
        help="Execution mode: single (one instance), cluster (distributed), or stream (real-time)",
    ),
    config_file: Path = typer.Option(
        Path.home() / ".codemanager.toml",
        "--config", "-f",
        help="Path to the configuration file containing AWS and API credentials",
    ),
    extract_features: bool = typer.Option(
        False,
        "--extract-features",
        help="Extract features from FeatureView's saver schema and include in the publish payload",
    ),
):
    """
    Publish a job to Heisenberg.

    This command packages your project code, uploads it to S3, and registers
    it with Heisenberg for execution. Before publishing, make sure you have:

    1. Configured your credentials using 'heisenberg-cli configure'
    2. A valid project structure with a main entry point

    The command will:
    - Package all files in the directory (respecting .jobignore)
    - Optionally obfuscate the code (if enabled in config)
    - Upload the package to S3
    - Register the job with Heisenberg API

    Examples:
        # Publish a project with required options
        heisenberg-cli publish ./my-project --name my-job --version 1.0.0

        # Publish with custom execution mode
        heisenberg-cli publish ./my-project -n my-job -v 1.0.0 -e cluster

        # Publish with custom config file
        heisenberg-cli publish ./my-project -n my-job -v 1.0.0 -f ./custom-config.toml

    Configuration:
        The publish command reads settings from ~/.codemanager.toml including:
        - AWS credentials (bucket, access keys, region)
        - API endpoint and authentication token
        - Code settings (main file, env file, ignore patterns)
        - Execution schedule (cron, intervals, etc.)

        Run 'heisenberg-cli configure' to set up these values interactively.
    """
    try:
        config = load_config(config_file)
        if not config:
            raise NoConfigSetError()

        manager = SubmitCommand(config)

        job_execution_schedule = None
        if "execution" in config:
            job_execution_schedule = JobExecutionSchedule(
                **config.get("execution", {}).get("plan", {})
            )

        job_metadata = JobMetadata(
            pipeline_hash="",
            confidential_level=confidential_level,
            execution_mode=ExecutionMode(execution_mode),
            execution_plan=job_execution_schedule,
            main_file_path=config.get("code", {}).get("main_file", "main.py"),
            env_file_path=config.get("code", {}).get("env_file", ".env"),
            data_size=config.get("code", {}).get("data_size", DEFAULT_DATA_SIZE),
            code_size=0,
            complexity_factor=config.get("code", {}).get("complexity_factor", 0),
            requirement_file=None,
            requirements_type=None,
            secret_key=None,
            iv=None,
        )

        package = manager.handle(directory, name, version, metadata=job_metadata)

        # Handle code obfuscation
        obfuscate_code = config.get("code", {}).get("obfuscate_code", "false")
        obfuscate_code = obfuscate_code.lower() == "true"
        if obfuscate_code:
            package = manager.obfuscate_code(package)

        job_metadata.pipeline_hash = package.hash
        identifier = manager.store_code(package)

        # Extract features from FeatureView savers if requested
        features = None
        if extract_features:
            typer.echo("Extracting features from FeatureView savers...")
            main_file = config.get("code", {}).get("main_file", "main.py")
            features = extract_features_from_directory(
                directory,
                main_file=main_file,
                version=version,
                echo_func=typer.echo,
            )
            if features:
                typer.echo(f"Extracted {len(features)} features")
            else:
                typer.echo("No features found in FeatureView savers")

        job_response = manager.publish_job(
            identifier,
            name,
            version,
            job_metadata,
            expiration=config.get("aws", {}).get("expiration", DEFAULT_EXPIRATION),
            features=features,
        )

        _display_job_summary(package, identifier, job_response)

    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)


@app.command(name="configure")
def configure_job(
    bucket: str = typer.Option(..., prompt=True, help="S3 bucket name for storing job packages"),
    prefix: str = typer.Option("code", prompt=True, help="S3 key prefix for uploaded packages"),
    aws_access_key_id: str = typer.Option(..., prompt=True, help="AWS access key ID"),
    aws_secret_access_key: str = typer.Option(
        ..., prompt=True, hide_input=True, help="AWS secret access key"
    ),
    aws_region: str = typer.Option("us-east-1", prompt=True, help="AWS region for S3 bucket"),
    api_base_url: str = typer.Option(
        ..., prompt=True, help="Heisenberg API base URL"
    ),
    api_auth_token: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        prompt_required=True,
        help="Heisenberg API authentication token",
    ),
    main_file_path: str = typer.Option(
        ...,
        prompt=True,
        help="Path to the main entry point file (relative to project root)",
    ),
    env_file_path: str = typer.Option(
        ".env",
        prompt=True,
        help="Path to environment variables file",
    ),
    ignore_file: str = typer.Option(
        ".jobignore",
        prompt=True,
        help="Path to file containing ignore patterns (like .gitignore)",
    ),
    schedule_mode: str = typer.Option(
        "once", prompt=True, help="Schedule mode: 'once' for single run, 'cron' for recurring"
    ),
    start_time: str = typer.Option(
        "", prompt=True, help="Start time in format YYYY-MM-DDTHH:MM (leave empty for immediate)"
    ),
    until: str = typer.Option(
        "", prompt=True, help="End time in format YYYY-MM-DDTHH:MM (leave empty for no end)"
    ),
    interval: int = typer.Option(
        "", prompt=True, help="Interval in minutes between runs (for recurring jobs)"
    ),
    cron_expression: str = typer.Option(
        "",
        prompt=True,
        help="Cron expression (e.g., '0 0 * * *' for daily at midnight)",
    ),
    run_overlap: str = typer.Option(
        "true", prompt=True, help="Allow overlapping job runs (true/false)"
    ),
    data_size: float = typer.Option(
        DEFAULT_DATA_SIZE,
        prompt=True,
        help="Estimated data size in bytes to be processed",
    ),
    complexity_factor: float = typer.Option(
        None,
        prompt=True,
        help="Complexity factor (1-1000) for resource allocation",
    ),
    executor_label: str = typer.Option(
        "",
        prompt=True,
        help="Executor label to run the Data Agent on (leave empty for default)",
    ),
    is_blueprint: bool = typer.Option(
        False,
        prompt=True,
        help="Whether this Data Agent is a blueprint (template for other agents)",
    ),
    table_name: str = typer.Option(
        "",
        prompt=True,
        help="Database table name for the Data Agent output (leave empty if not applicable)",
    ),
    tags: str = typer.Option(
        "",
        prompt=True,
        help="Comma-separated tags for categorizing the Data Agent (e.g., 'ml,recommendation,prod')",
    ),
    filter_statement: str = typer.Option(
        "",
        prompt=True,
        help="SQL-like filter statement for data filtering (leave empty if not applicable)",
    ),
    llm_name: str = typer.Option(
        "",
        prompt=True,
        help="Name for the inference LLM configuration (leave empty to skip LLM config)",
    ),
    llm_system_prompt: str = typer.Option(
        "",
        prompt=True,
        help="System prompt for the LLM (leave empty if not using LLM)",
    ),
    llm_provider: str = typer.Option(
        "",
        prompt=True,
        help="LLM provider (e.g., 'openai', 'anthropic', 'azure')",
    ),
    llm_model_name: str = typer.Option(
        "",
        prompt=True,
        help="Model name for the LLM (e.g., 'gpt-4', 'claude-3-opus')",
    ),
    llm_directives: str = typer.Option(
        "",
        prompt=True,
        help="Additional directives for the LLM (leave empty if not applicable)",
    ),
    config_file: Path = typer.Option(
        Path.home() / ".codemanager.toml", help="Path to save the configuration file"
    ),
):
    """
    Configure Heisenberg CLI credentials and settings interactively.

    This command guides you through setting up all necessary configuration
    for publishing jobs to Heisenberg. Settings are saved to ~/.codemanager.toml
    by default.

    The configuration includes:
    - AWS S3 credentials for package storage
    - Heisenberg API endpoint and authentication
    - Default code settings (main file, env file, ignore patterns)
    - Execution schedule settings

    Example:
        heisenberg-cli configure
        heisenberg-cli configure --config-file ./my-config.toml
    """
    config = {
        "aws": {
            "bucket": bucket,
            "prefix": prefix,
            "access_key_id": aws_access_key_id,
            "secret_access_key": aws_secret_access_key,
            "region": aws_region,
        },
        "api": {
            "base_url": api_base_url,
            "auth_token": api_auth_token,
        },
        "code": {
            "main_file": main_file_path,
            "ignore_file": ignore_file,
            "env_file": env_file_path,
            "data_size": data_size,
            "complexity_factor": complexity_factor,
        },
        "execution": {
            "plan": {
                "schedule_mode": schedule_mode,
                "start_time": start_time,
                "until": until,
                "cron_expression": cron_expression,
                "interval": interval,
                "run_overlap": run_overlap,
            }
        },
        "executor": {
            "label": executor_label,
        },
        "data_agent": {
            "is_blueprint": is_blueprint,
            "table_name": table_name,
            "tags": tags,
            "filter_statement": filter_statement,
            "retrieval_llm": {
                "name": llm_name,
                "system_prompt": llm_system_prompt,
                "provider": llm_provider,
                "model_name": llm_model_name,
                "directives": llm_directives,
            },
        },
    }

    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w") as f:
        toml.dump(config, f)

    typer.echo(f"Configuration saved to {config_file}")


@app.command(name="job-status")
def job_status(
    job_id: str = typer.Argument(..., help="The unique job ID to check"),
    config_file: Path = typer.Option(
        Path.home() / ".codemanager.toml",
        "--config", "-f",
        help="Path to the configuration file",
    ),
    api_base_url: str = typer.Option(
        None,
        "--api-url",
        help="Override API base URL from config",
    ),
    api_auth_token: str = typer.Option(
        None,
        "--api-token",
        help="Override API auth token from config",
    ),
):
    """
    Check the status of a published job.

    Query the Heisenberg API to get the current status of a job by its ID.
    The job ID is returned when you publish a job.

    Example:
        heisenberg-cli job-status abc123-def456
        heisenberg-cli job-status abc123 --api-url https://api.example.com
    """
    try:
        try:
            config = load_config(config_file)
        except NoConfigSetError():
            config = None

        if not config and not (api_base_url and api_auth_token):
            raise NoConfigSetError()
        else:
            base_url = api_base_url or config.get("api", {}).get("base_url")
            auth_token = api_auth_token or config.get("api", {}).get("auth_token")

        if not base_url:
            typer.echo("base_url is not set")
            raise NoConfigSetError(
                "base_url parameter must be set in the config file or as command option"
            )
        if not auth_token:
            typer.echo("auth_token is not set")
            raise NoConfigSetError(
                "auth_token parameter must be set in the config file or as command option"
            )

        manager = JobStatusCommand(base_url=base_url, auth_token=auth_token)
        manager.job_status(job_id)

    except NoConfigSetError as e:
        typer.echo(f"Configuration error: {e}")
        raise typer.Exit(2)
    except RestClientException as e:
        typer.echo(f"API error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        "--verbose", "-V",
        help="Enable verbose output for debugging",
    ),
):
    """
    Heisenberg CLI - Publish and manage jobs on Heisenberg.

    Get started:
        1. Run 'heisenberg-cli configure' to set up your credentials
        2. Run 'heisenberg-cli create-project my-project' to scaffold a new project
        3. Run 'heisenberg-cli publish ./my-project -n my-job -v 1.0.0' to publish

    For more information on a specific command, run:
        heisenberg-cli <command> --help
    """
    state["verbose"] = verbose
