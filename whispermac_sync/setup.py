#!/usr/bin/env python3
"""
Simple script to generate plist file from Jinja2 template
"""

import os
from jinja2 import Environment, FileSystemLoader


import subprocess


def run_launchctl_command(command_args):
    """
    Executes a launchctl command and prints its output.

    Args:
        command_args (list): A list of strings representing the launchctl command
                             and its arguments, e.g., ['load', '~/Library/LaunchAgents/com.example.myagent.plist'].
    """
    try:
        # Construct the full command
        full_command = ["launchctl"] + command_args

        # Execute the command
        process = subprocess.run(
            full_command,
            capture_output=True,
            text=True,  # Capture output as text
            check=True,  # Raise an exception if the command returns a non-zero exit code
        )

        # Print the standard output and standard error
        stdout = process.stdout
        stderr = process.stderr
        if stdout:
            print("STDOUT:")
            print(stdout)
        if stderr:
            print("STDERR:")
            print(stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error executing launchctl command: {e}")
        print(f"Command: {e.cmd}")
        print(f"Return Code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
    except FileNotFoundError:
        print("Error: 'launchctl' command not found. Ensure it's in your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Calculate repo root (two levels up from whispermac_sync/)
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))

    # Get user input for source and destination directories
    default_source = os.path.join(os.environ["HOME"], "Library/Application Support/MacWhisper/GlobalRecordings/")
    default_dest = os.path.join(repo_root, "global_recordings_sync_watched")

    print("\nConfigure WhisperMac sync directories:")
    print(f"Default source: {default_source}")
    source_dir = input(f"Source directory (press Enter for default): ").strip()
    if not source_dir:
        source_dir = default_source

    print(f"Default destination: {default_dest}")
    dest_dir = input(f"Destination directory (press Enter for default): ").strip()
    if not dest_dir:
        dest_dir = default_dest

    # Resolve paths to absolute paths
    source_dir = os.path.abspath(source_dir)
    dest_dir = os.path.abspath(dest_dir)

    print(f"\nUsing source: {source_dir}")
    print(f"Using destination: {dest_dir}")

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(script_dir))

    # If the destination directory doesn't exist, create it
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created destination directory: {dest_dir}")
    else:
        print(f"Destination directory already exists: {dest_dir}")

    # Load the template
    template = env.get_template("TEMPLATE.com.user.whispermacsync.plist")

    # Render the template with environment variables and user-provided paths
    rendered = template.render(env=os.environ, source_dir=source_dir, dest_dir=dest_dir)

    # Write the output to the plist file
    output_path = os.path.join(script_dir, "com.user.whispermacsync.plist")
    with open(output_path, "w") as f:
        f.write(rendered)

    print(f"Generated plist file: {output_path}")

    sync_script_src_path = os.path.join(script_dir, "whispermac_sync.sh")
    sync_script_dest_path = os.path.join(os.environ["HOME"], "bin", "whispermac_sync.sh")
    plist_src_path = os.path.join(script_dir, "com.user.whispermacsync.plist")
    plist_dest_path = os.path.join(os.environ["HOME"], "Library", "LaunchAgents", "com.user.whispermacsync.plist")

    # Check if symlinks already exist for the script
    if os.path.exists(sync_script_dest_path):
        print("Symlink already exists for the sync script")
    else:
        print("Symlink does not exist for the sync script")
        # Ask the user if they want to create symlinks to the script
        create_symlinks = input("Do you want to create symlinks to the script? (y/n): ")
        if create_symlinks == "y":
            # Create symlinks to the script and plist file
            os.makedirs(os.path.dirname(sync_script_dest_path), exist_ok=True)
            os.symlink(sync_script_src_path, sync_script_dest_path)
            print(f"Created symlink: {sync_script_dest_path}")

    # Check if symlinks already exist for the plist file
    if os.path.exists(plist_dest_path):
        print("Symlink already exists for the plist file")
    else:
        print("Symlink does not exist for the plist file")
        # Ask the user if they want to create symlinks to the plist file
        create_symlinks = input("Do you want to create symlinks to the plist file? (y/n): ")
        if create_symlinks == "y":
            # Create symlinks to the script and plist file
            os.makedirs(os.path.dirname(plist_dest_path), exist_ok=True)
            os.symlink(plist_src_path, plist_dest_path)
            print(f"Created symlink: {plist_dest_path}")

    # Check if the user wants to load the launch agent
    load_launch_agent = input("Do you want to load/reload the launch agent? (y/n): ")
    if load_launch_agent == "y":
        # First unload the launch agent
        run_launchctl_command(["unload", plist_dest_path])
        # print(f"Unloaded launch agent: {plist_dest_path}")

        # Then load the launch agent
        run_launchctl_command(["load", plist_dest_path])
        print(f"Loaded launch agent: {plist_dest_path}")
    else:
        print("Launch agent not loaded/reloaded")


if __name__ == "__main__":
    main()
