#!/usr/bin/env python3

import os
import subprocess
import json
import shutil

CONFIG_FILE = os.path.expanduser("~/.backup_tool_jobs.json")
SCRIPT_DIR = os.path.expanduser("~/backup_scripts/")
TEMP_DIR = "/var/tmp/backupbuddy_temp"

#PREPARE TEMP#

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def prepare_temp_directory():
    """Create a dedicated temporary directory for backups."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR, exist_ok=True)
    os.chmod(TEMP_DIR, 0o777)

#CONFIG#

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def load_config():
    """Load configuration data from the JSON file and validate it."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        # Add default values for missing keys
        for job in config.values():
            job.setdefault("encrypt", False)  # Default: no encryption
            job.setdefault("compress", False)
            job.setdefault("compression_level", None)
            job.setdefault("split_files", False)
            job.setdefault("split_size", None)
            job.setdefault("cores", 4)  # Default: 4 cores
        return config
    return {}

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def save_config(config):
    """Save configuration data to the JSON file."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

#LISTINGS AND REMOTES"

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def list_jobs(config):
    """List all backup and transfer jobs."""
    if not config:
        print("No jobs found.")
        return
    print("\nConfigured jobs:")
    for i, job in enumerate(config.keys(), start=1):
        job_data = config.get(job, {})
        job_type = job_data.get("type", "backup")
        if job_type == "transfer":
            print(f"{i}. [Transfer] Source: {job_data.get('source', 'N/A')}, Destination: {job_data.get('destination', 'N/A')}")
        else:
            print(f"{i}. [Backup] Source: {job_data.get('source_dir', 'N/A')}, Destination: {job_data.get('destination', 'N/A')}, "
                  f"Encrypted: {job_data.get('encrypt', False)}, Compressed: {job_data.get('compress', False)}, "
                  f"Split: {job_data.get('split_files', False)}")

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def list_remotes():
    """List configured rclone remotes."""
    try:
        result = subprocess.run("rclone listremotes", shell=True, text=True, capture_output=True, check=True)
        remotes = result.stdout.strip().splitlines()
        if remotes:
            print("\nAvailable remotes:")
            for i, remote in enumerate(remotes, start=1):
                print(f"{i}. {remote}")
            return remotes
        else:
            print("No remotes found. Please configure a remote first.")
            subprocess.run("rclone config", shell=True)
            return list_remotes()
    except subprocess.CalledProcessError as e:
        print(f"Failed to retrieve remotes: {e}")
        return []

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def manage_remotes_and_paths():
    """Add new remotes or local paths."""
    print("\nManage Remotes and Local Paths")
    print("1. Add a new remote")
    print("2. Add a new local shortcut")
    print("3. View existing remotes")
    print("4. View local shortcuts")
    print("5. Back to main menu")

    choice = input("Enter your choice (1/2/3/4/5): ").strip()

    if choice == "1":
        print("\nAdding a new remote...")
        try:
            subprocess.run("rclone config", shell=True, check=True)
            print("New remote added successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error adding remote: {e.stderr}")
    elif choice == "2":
        print("\nAdding a new local shortcut...")
        shortcut_path = input("Enter the path for the new local shortcut: ").strip()
        if os.path.exists(shortcut_path):
            with open("local_shortcuts.txt", "a") as file:
                file.write(shortcut_path + "\n")
            print(f"New local shortcut '{shortcut_path}' added successfully.")
        else:
            print(f"Error: The path '{shortcut_path}' does not exist.")
    elif choice == "3":
        print("\nExisting remotes:")
        try:
            result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, check=True)
            remotes = result.stdout.strip().splitlines()
            if remotes:
                for remote in remotes:
                    print(f"- {remote}")
            else:
                print("No remotes configured yet.")
        except subprocess.CalledProcessError as e:
            print(f"Error listing remotes: {e.stderr}")
    elif choice == "4":
        print("\nExisting local shortcuts:")
        try:
            with open("local_shortcuts.txt", "r") as file:
                shortcuts = file.readlines()
                if shortcuts:
                    for shortcut in shortcuts:
                        print(f"- {shortcut.strip()}")
                else:
                    print("No local shortcuts configured yet.")
        except FileNotFoundError:
            print("No local shortcuts configured yet.")
    elif choice == "5":
        print("Returning to main menu.")
    else:
        print("Invalid choice. Returning to main menu.")


#CHECK AND INSTALL DEPENDENCIES#

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def check_and_install_dependencies():
    """
    Kontrollera och installera nödvändiga beroenden.
    Installera rclone alltid via curl och använd apt som fallback om det inte går.
    Om curl saknas, installera curl först.
    """
    DEPENDENCY_FLAG_FILE = os.path.expanduser("~/.backupbuddy_dependencies_checked")
    INSTALLED_PACKAGES_LOG = os.path.expanduser("~/.backupbuddy_installed_packages.log")
    dependencies = ["curl", "pigz", "tar", "pv", "cron"]

    # Kontrollera om alla beroenden finns installerade
    missing_dependencies = [dep for dep in dependencies if not shutil.which(dep)]

    if not missing_dependencies and os.path.exists(DEPENDENCY_FLAG_FILE):
        print("All dependencies are already installed.")
        return

    print("\nInstalling missing dependencies...")

    def install_dependency(package_manager, packages):
        command = f"{package_manager} install -y {' '.join(packages)}"
        if os.geteuid() != 0:
            command = f"sudo {command}"
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Successfully installed: {' '.join(packages)}")
            with open(INSTALLED_PACKAGES_LOG, "a") as log_file:
                for package in packages:
                    log_file.write(f"{package}\n")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {packages} using {package_manager}: {e}")

    # Installera curl om det saknas
    if "curl" in missing_dependencies:
        print("curl not found. Installing curl...")
        install_dependency("apt", ["curl"])
        missing_dependencies.remove("curl")

    # Installera andra beroenden om de saknas
    if missing_dependencies:
        print("Installing missing dependencies...")
        install_dependency("apt", missing_dependencies)

    # Installera rclone via curl, med fallback till apt
    print("\nAttempting to install rclone via curl...")
    try:
        subprocess.run("curl https://rclone.org/install.sh | sudo bash", shell=True, check=True)
        print("rclone installed successfully via curl.")
    except subprocess.CalledProcessError:
        print("Failed to install rclone via curl. Falling back to apt.")
        install_dependency("apt", ["rclone"])

    # Uppdatera flaggfilen om alla beroenden nu är installerade
    if all(shutil.which(dep) for dep in dependencies + ["rclone"]):
        with open(DEPENDENCY_FLAG_FILE, "w") as flag_file:
            flag_file.write("Dependencies checked and installed.")
        print("All dependencies are installed and ready to use.")
    else:
        print("Some dependencies are still missing. Please resolve them manually.")
        if os.path.exists(DEPENDENCY_FLAG_FILE):
            os.remove(DEPENDENCY_FLAG_FILE)

#REMOTES#

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def select_remote():
    """Select a remote from the list or configure a new one."""
    while True:
        try:
            # Försök lista konfigurerade remotes
            result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, check=True)
            remotes = result.stdout.strip().splitlines()
        except subprocess.CalledProcessError:
            remotes = []

        if not remotes:
            print("No remotes found. You need to configure one.")
            create_new = input("Would you like to create a new remote? (y/n): ").strip().lower()
            if create_new == "y":
                print("\nStarting rclone configuration...")
                subprocess.run(["rclone", "config"], check=True)
                continue  # Återgå och ladda om listan
            else:
                print("Operation canceled.")
                return None

        # Lista befintliga remotes
        print("\nAvailable remotes:")
        for i, remote in enumerate(remotes, start=1):
            print(f"{i}. {remote}")
        print("0. Create a new remote")

        choice = input("Enter the number of the remote to use (or 'b' to go back): ").strip()

        if choice.lower() == "b":
            return None
        elif choice == "0":
            print("\nStarting rclone configuration to create a new remote...")
            subprocess.run(["rclone", "config"], check=True)
            # Efter att en ny remote skapats, återgå och ladda om listan
            continue
        else:
            try:
                choice = int(choice)
                if 1 <= choice <= len(remotes):
                    return remotes[choice - 1]
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")


#NAVIGATE#

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def navigate_remote_directories(remote_name):
    """Navigate remote directories"""
    current_path = remote_name  # Start from the root of the selected remote
    YELLOW = '\033[33m'
    RED = '\033[31m'
    RESET = '\033[0m'

    while True:
        print(f"\n{YELLOW}Current remote directory: {current_path}{RESET}")

        # Försök lista kataloger i den aktuella sökvägen
        try:
            result = subprocess.run(
                ["rclone", "lsd", current_path],
                capture_output=True,
                text=True,
                check=True
            )
            remote_directories = [
                line.split()[-1] for line in result.stdout.strip().splitlines()
                if line.strip()
            ]  # Extrahera katalognamn
        except subprocess.CalledProcessError as e:
            print(f"{RED}Error listing directories: {e.stderr}{RESET}")
            remote_directories = []

        # Visa vilken katalog vi är i
        print(f"\n{YELLOW}You are currently in:{RESET} {current_path}")

        # Hantera tomma kataloger eller fel
        if not remote_directories:
            print(f"{RED}No directories found in this location.{RESET}")
        else:
            # Lista kataloger
            print(f"\n{RED}Remote Directories:{RESET}")
            for idx, directory in enumerate(remote_directories, start=1):
                print(f"{RED}{idx}. {directory}{RESET}")

        # Alternativ
        print(f"\n{YELLOW}0.{RESET} Select this location")
        print(f"{YELLOW}b.{RESET} Go back")
        print(f"{YELLOW}c.{RESET} Enter a custom remote directory path")
        print(f"{YELLOW}d.{RESET} Create a new directory")
        print(f"{YELLOW}e.{RESET} Copy files to this location")

        choice = input("\nEnter your choice: ").strip()

        if choice == "0":
            # Bekräfta valet av den aktuella katalogen
            print(f"{YELLOW}You have selected the current location: {current_path}{RESET}")
            return current_path
        elif choice.lower() == "b":
            # Gå tillbaka till föregående katalog
            if "/" in current_path:
                current_path = "/".join(current_path.rstrip("/").split("/")[:-1])
            else:
                print("You are already at the root remote directory.")
        elif choice.lower() == "c":
            # Ange en anpassad sökväg
            custom_path = input("Enter the custom remote directory path: ").strip()
            if custom_path.startswith(remote_name):
                current_path = custom_path
            else:
                current_path = f"{remote_name}/{custom_path}".rstrip("/")
        elif choice.lower() == "d":
            # Skapa en ny katalog direkt på remote
            new_dir = input("Enter the name for the new directory: ").strip()
            if new_dir:
                try:
                    new_dir_path = f"{current_path.rstrip('/')}/{new_dir}".lstrip("/")
                    subprocess.run(["rclone", "mkdir", new_dir_path], check=True)
                    print(f"{YELLOW}New directory '{new_dir}' created successfully at {new_dir_path}.{RESET}")
                    
                    # Uppdatera current_path till den nyskapade katalogen
                    current_path = new_dir_path
                    print(f"{YELLOW}Now in the new directory: {current_path}{RESET}")
                except subprocess.CalledProcessError as e:
                    print(f"{RED}Error creating directory: {e.stderr}{RESET}")
            else:
                print(f"{RED}Directory name cannot be empty.{RESET}")
        elif choice.lower() == "e":
            # Kopiera filer till den aktuella katalogen
            source_path = input("Enter the local path of the files to copy: ").strip()
            if source_path:
                try:
                    print(f"{YELLOW}Copying files from {source_path} to {current_path}{RESET}")
                    subprocess.run(["rclone", "copy", source_path, current_path], check=True)
                    print(f"{YELLOW}Files successfully copied to {current_path}.{RESET}")
                except subprocess.CalledProcessError as e:
                    print(f"{RED}Error copying files: {e.stderr}{RESET}")
            else:
                print(f"{RED}Source path cannot be empty.{RESET}")
        else:
            try:
                choice = int(choice)
                if 1 <= choice <= len(remote_directories):
                    # Navigera till vald katalog
                    selected_directory = remote_directories[choice - 1]
                    current_path = f"{current_path.rstrip('/')}/{selected_directory}".rstrip("/")
                    print(f"{YELLOW}Now in the directory: {current_path}{RESET}")
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")


import subprocess
import os

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def navigate_local_directories():
    """Let the user navigate local directories."""
    current_path = "/"   # Start from the / directory
    YELLOW = '\033[33m'  # ANSI escape code for yellow text
    GREEN = '\033[32m'   # ANSI escape code for green text
    RED = '\033[31m'     # ANSI escape code for red text
    RESET = '\033[0m'    # Reset to default color

    while True:
        print(f"\n{YELLOW}Current local directory: {current_path}{RESET}")  # Show current directory

        try:
            # List all directories in the current path
            current_directories = [d for d in os.listdir(current_path) 
                                   if os.path.isdir(os.path.join(current_path, d))]

            # List all files in the current path, but only the first 3 files
            current_files = [f for f in os.listdir(current_path) 
                             if os.path.isfile(os.path.join(current_path, f))]
            current_files = current_files[:3]  # Show only the first 3 files

            # Check if there are more than 3 files
            more_files = len(os.listdir(current_path)) > 3

            # Merge the current directories with the common directories list
            # Add the current directory (.) and root directory (/) as options
            directories = current_directories
            directories.insert(0, '..')  # Go back to the parent directory
            directories.insert(0, '/')   # Add root directory as an option

            # Always include /root in the list if not already included
            if current_path != "/root":
                directories.insert(0, 'root')  # Show root as an option

            if not directories:
                print(f"{RED}No valid directories found in {current_path}.{RESET}")
                return current_path

            # Display Directories section first
            print(f"\n{RED}Directories:{RESET}")
            for idx, directory in enumerate(directories, start=1):
                print(f"{RED}{idx}. {directory}{RESET}")  # Mark directories as red

            # List the files in the current directory in green (only 3 files)
            print(f"\n{GREEN}Files:{RESET}")
            if current_files:
                for file in current_files:
                    print(f"{GREEN}{file}{RESET}")  # Mark files as green
                # If there are more than 3 files, show "[ ... ]"
                if more_files:
                    print(f"{GREEN}[ ... ]{RESET}")
            else:
                print(f"{GREEN}No files to display.{RESET}")  # If there are no files

            # Display options
            print(f"\n{YELLOW}0.{RESET} Select this location")
            print(f"{YELLOW}b.{RESET} Go back")
            print(f"{YELLOW}c.{RESET} Enter a custom local directory path")
            print(f"{YELLOW}d.{RESET} Create a new directory")

            # Print the current directory
            print(f"\n{YELLOW}Current directory: {current_path}{RESET}")  # Show current directory under options

            choice = input("\nEnter your choice: ").strip()
            if choice == "0":
                # Select the current location
                print(f"{YELLOW}You have selected the current location: {current_path}{RESET}")
                return current_path
            elif choice.lower() == "b":
                # Go back one level
                if current_path != "/":  # Check if we are at the root
                    current_path = os.path.dirname(current_path)  # Go back to the parent directory
                    print(f"Now in the directory: {current_path}")
                else:
                    print("You are already at the root local directory.")
            elif choice.lower() == "c":
                # Enter a custom path and set it as the current path
                custom_path = input("Enter the custom local directory path: ").strip()
                if os.path.exists(custom_path) and os.path.isdir(custom_path):
                    current_path = custom_path
                    print(f"Now in the directory: {current_path}")
                    continue  # Skip the rest of the loop, no need to list directories
                else:
                    print(f"{RED}Invalid path or the directory '{custom_path}' does not exist.{RESET}")
            elif choice.lower() == "d":
                # Create a new directory
                new_dir = input("Enter the name for the new directory: ").strip()
                if new_dir:
                    try:
                        new_dir_path = os.path.join(current_path, new_dir)
                        os.makedirs(new_dir_path, exist_ok=True)
                        print(f"New directory '{new_dir}' created successfully at {new_dir_path}.")
                        
                        # Update the current path to the newly created directory
                        current_path = new_dir_path
                        print(f"Now in the directory: {current_path}")
                    except Exception as e:
                        print(f"Error creating directory: {e}")
                else:
                    print("Directory name cannot be empty.")
            else:
                try:
                    choice = int(choice)
                    if 1 <= choice <= len(directories):
                        selected_directory = directories[choice - 1]
                        selected_path = os.path.join(current_path, selected_directory)
                        if os.path.exists(selected_path) and os.path.isdir(selected_path):
                            current_path = selected_path
                            print(f"Now in the directory: {current_path}")
                        else:
                            print(f"{RED}The directory '{selected_directory}' does not exist or is invalid.{RESET}")
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"Error retrieving local directories: {e}")
            return None

#CREATE#

import os

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

import os
import subprocess

def create_backup_job(config):
    """
    Guide user through creating a new backup job.
    "split files" ONLY if compression is enabled.
    """
    print("\nCreating a new backup job.")
    job_id = input("Enter a unique ID for the backup job: ").strip()

    # Välj source directory
    print("\nNavigate to select the source directory (local).")
    source_dir = navigate_local_directories()

    # Välj remote destination
    print("\nNavigate to select the destination directory (remote).")
    remote_name = select_remote()
    if remote_name is None:
        print("Operation canceled.")
        return
    destination_path = navigate_remote_directories(remote_name)

    # Fråga om kompression
    compress = input("Do you want to compress files? (yes/no): ").strip().lower() == "yes"
    compression_level = None
    cores = None
    split_files = False
    split_size = None

    if compress:
        compression_level = int(input("Enter compression level (1=low, 9=high, default: 6): ").strip() or 6)
        cores = int(input("Enter the number of CPU cores to use (default: 4): ").strip() or 4)

        # Fråga om split-filer (BARA om komprimering är aktivt)
        split_files = input("Do you want to split the compressed archive? (yes/no): ").strip().lower() == "yes"
        if split_files:
            split_size = input("Enter maximum size per part (e.g., 10M, 1G, default: 100M): ").strip() or "100M"

    # Konfigurera rclone flaggor
    print("\nConfigure rclone flags for this job (Press Enter to use default values):")
    default_flags = {
        "--tpslimit": "2",
        "--tpslimit-burst": "1",
        "--transfers": "2",
        "--checkers": "1",
        "--low-level-retries": "3",
        "--retries": "5",
        "--log-file": f"{job_id}_rclone.log",
        "--log-level": "INFO",
    }

    for flag, value in default_flags.items():
        new_value = input(f"{flag} (default: {value}): ").strip()
        if new_value:
            default_flags[flag] = new_value

    # Fråga om --progress ska inkluderas
    add_progress = input("Do you want to enable progress output (--progress)? (yes/no, default: no): ").strip().lower()
    if add_progress == "yes":
        default_flags["--progress"] = ""

    # Spara konfigurationen
    config[job_id] = {
        "source_dir": source_dir,
        "destination": destination_path,
        "compress": compress,
        "compression_level": compression_level,
        "split_files": split_files,
        "split_size": split_size,
        "cores": cores,
        "rclone_flags": default_flags,
    }
    save_config(config)

    # Generera och kör backup-skript
    script_path = generate_backup_script(config, job_id)
    print(f"Backup script generated: {script_path}")

    try:
        print(f"Running the backup job {job_id}...")
        subprocess.run([script_path], shell=True, check=True)
        print("Backup job completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the backup job: {e}")
        return

    # Fråga om cron-jobb
    setup_cron = input("Do you want to schedule this job with a cron job? (yes/no, default: no): ").strip().lower()
    if setup_cron == "yes":
        schedule_cron(config[job_id])
    else:
        print("Skipping cron job setup.")


def create_transfer(config):
    """Guide user through creating a new transfer job with compression and split options."""
    print("\nCreating a new transfer job.")
    job_id = input("Enter a unique ID for the transfer job: ").strip()

    # Välj source (lokal eller remote)
    print("\nSelect the source:")
    print("1. Local directory")
    print("2. Remote")
    source_type = input("Enter your choice (1/2): ").strip()

    if source_type == "1":
        print("\nNavigate to select the source directory (local).")
        source = navigate_local_directories()
    elif source_type == "2":
        print("\nSelect the source remote:")
        source_remote = select_remote()
        if source_remote is None:
            print("Operation canceled.")
            return
        source = navigate_remote_directories(source_remote)
    else:
        print("Invalid choice. Returning to main menu.")
        return

    # Välj destination (lokal eller remote)
    print("\nSelect the destination:")
    print("1. Local directory")
    print("2. Remote")
    destination_type = input("Enter your choice (1/2): ").strip()

    if destination_type == "1":
        print("\nNavigate to select the destination directory (local).")
        destination = navigate_local_directories()
    elif destination_type == "2":
        print("\nSelect the destination remote:")
        destination_remote = select_remote()
        if destination_remote is None:
            print("Operation canceled.")
            return
        destination = navigate_remote_directories(destination_remote)
    else:
        print("Invalid choice. Returning to main menu.")
        return

    # Fråga om komprimering
    compress = input("Do you want to compress files before transfer? (yes/no): ").strip().lower() == "yes"
    compression_level = None
    cores = None
    split_files = False
    split_size = None

    if compress:
        compression_level = int(input("Enter compression level (1=low, 9=high, default: 6): ").strip() or 6)
        cores = int(input("Enter the number of CPU cores to use (default: 4): ").strip() or 4)

        # Fråga om split-filer (BARA om komprimering är aktivt)
        split_files = input("Do you want to split the compressed archive? (yes/no): ").strip().lower() == "yes"
        if split_files:
            split_size = input("Enter maximum size per part (e.g., 10M, 1G, default: 100M): ").strip() or "100M"

    # Konfigurera rclone flaggor
    print("\nConfigure rclone flags for this job (Press Enter to use default values):")
    default_flags = {
        "--transfers": "4",
        "--checkers": "2",
        "--retries": "5",
        "--log-file": f"{job_id}_rclone.log",
        "--log-level": "INFO",
    }

    for flag, value in default_flags.items():
        new_value = input(f"{flag} (default: {value}): ").strip()
        if new_value:
            default_flags[flag] = new_value

    # Fråga om --progress ska inkluderas
    add_progress = input("Do you want to enable progress output (--progress)? (yes/no, default: no): ").strip().lower()
    if add_progress == "yes":
        default_flags["--progress"] = ""

    # Spara konfigurationen
    config[job_id] = {
        "source": source,
        "destination": destination,
        "type": "transfer",
        "compress": compress,
        "compression_level": compression_level,
        "split_files": split_files,
        "split_size": split_size,
        "cores": cores,
        "rclone_flags": default_flags,
    }
    save_config(config)

    # Generera och kör överföringsskript
    script_path = generate_transfer_script(config, job_id)
    print(f"Transfer script generated: {script_path}")

    try:
        print(f"Running the transfer job {job_id}...")
        subprocess.run([script_path], shell=True, check=True)
        print("Transfer job completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the transfer job: {e}")
        return

    # Fråga om cron-jobb
    setup_cron = input("Do you want to schedule this job with a cron job? (yes/no, default: no): ").strip().lower()
    if setup_cron == "yes":
        schedule_cron(config[job_id])
    else:
        print("Skipping cron job setup.")



import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

#GENERATE#

def generate_transfer_script(config, job_id):
    """Generate a transfer script."""
    job = config[job_id]
    script_path = os.path.join(SCRIPT_DIR, f"transfer_{job_id}.sh")
    os.makedirs(SCRIPT_DIR, exist_ok=True)

    rclone_flags = " ".join(f"{flag} {value}" for flag, value in job.get("rclone_flags", {}).items())
    use_progress = "--progress" in rclone_flags
    log_file = job.get("rclone_flags", {}).get("--log-file", None)

    with open(script_path, "w") as script:
        script.write("#!/bin/bash\n")
        script.write("set -e\n")
        script.write(f"echo 'Starting transfer process for job {job_id}...'\n")

        source = job["source"]
        destination = job["destination"]

        # Skapa TEMP_DIR om det inte finns
        script.write(f"if [ ! -d \"{TEMP_DIR}\" ]; then\n")
        script.write(f"    echo 'Creating temporary directory: {TEMP_DIR}'\n")
        script.write(f"    mkdir -p {TEMP_DIR}\n")
        script.write("else\n")
        script.write("    echo 'Temporary directory already exists.'\n")
        script.write("fi\n")

        script.write(f"chmod 777 {TEMP_DIR}\n")  # Säkerställer skrivbarhet

        if job["compress"]:
            compression_level = job.get("compression_level", 6)
            cores = job.get("cores", 4)

            script.write(f"echo 'Compressing files with pigz -{compression_level}, using {cores} cores...'\n")

            if use_progress:
                script.write(f"tar -cf - -C {source} . | pv -cN 'Compressing' | pigz -{compression_level} -p {cores} > {TEMP_DIR}/transfer.tar.gz\n")
            else:
                script.write(f"tar -cf - -C {source} . | pigz -{compression_level} -p {cores} > {TEMP_DIR}/transfer.tar.gz\n")

            if job["split_files"]:
                split_size = job.get("split_size", "100M")
                script.write("echo 'Splitting compressed file...'\n")
                if use_progress:
                    script.write(f"pv -cN 'Splitting' {TEMP_DIR}/transfer.tar.gz | split -b {split_size} - {TEMP_DIR}/transfer-part-\n")
                else:
                    script.write(f"split -b {split_size} {TEMP_DIR}/transfer.tar.gz {TEMP_DIR}/transfer-part-\n")
                script.write(f"rm {TEMP_DIR}/transfer.tar.gz\n")

            script.write(f"rclone copy {TEMP_DIR}/ {destination} {rclone_flags}\n")

        else:
            script.write(f"rclone copy {source} {destination} {rclone_flags}\n")

        script.write("echo 'Transfer completed.'\n")

        if log_file:
            script.write(f"if ! grep -qE 'ERROR|FATAL' {log_file}; then\n")
            script.write(f"    echo 'No errors found in log. Deleting {log_file}...'\n")
            script.write(f"    rm -f {log_file}\n")
            script.write("else\n")
            script.write("    echo 'Errors detected in log. Keeping it for review.'\n")
            script.write("fi\n")

    os.chmod(script_path, 0o755)
    return script_path


import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def generate_backup_script(config, job_id):
    """
    Generate a backup script for the specified job.
    
    """
    job = config[job_id]
    script_path = os.path.join(SCRIPT_DIR, f"backup_{job_id}.sh")
    os.makedirs(SCRIPT_DIR, exist_ok=True)

    rclone_flags = " ".join(f"{flag} {value}" for flag, value in job.get("rclone_flags", {}).items())
    use_progress = "--progress" in rclone_flags
    log_file = job.get("rclone_flags", {}).get("--log-file", None)

    with open(script_path, "w") as script:
        script.write("#!/bin/bash\n")
        script.write("set -e\n")
        script.write("echo 'Starting backup process...'\n")

        # Skapa TEMP_DIR om det inte finns
        script.write(f"if [ ! -d \"{TEMP_DIR}\" ]; then\n")
        script.write(f"    echo 'Creating temporary directory: {TEMP_DIR}'\n")
        script.write(f"    mkdir -p {TEMP_DIR}\n")
        script.write("else\n")
        script.write("    echo 'Temporary directory already exists.'\n")
        script.write("fi\n")

        script.write(f"chmod 777 {TEMP_DIR}\n")  # Säkerställer skrivbarhet

        if job["compress"]:
            compression_level = job.get("compression_level", 6)
            cores = job.get("cores", 4)

            script.write(f"echo 'Compressing files with pigz -{compression_level}, using {cores} cores...'\n")

            if use_progress:
                script.write(f"tar -cf - -C {job['source_dir']} . | pv -cN 'Compressing' | pigz -{compression_level} -p {cores} > {TEMP_DIR}/backup.tar.gz\n")
            else:
                script.write(f"tar -cf - -C {job['source_dir']} . | pigz -{compression_level} -p {cores} > {TEMP_DIR}/backup.tar.gz\n")

            if job["split_files"]:
                split_size = job.get("split_size", "100M")
                script.write("echo 'Splitting compressed file...'\n")
                if use_progress:
                    script.write(f"pv -cN 'Splitting' {TEMP_DIR}/backup.tar.gz | split -b {split_size} - {TEMP_DIR}/backup-part-\n")
                else:
                    script.write(f"split -b {split_size} {TEMP_DIR}/backup.tar.gz {TEMP_DIR}/backup-part-\n")
                script.write(f"rm {TEMP_DIR}/backup.tar.gz\n")

            script.write(f"rclone copy {TEMP_DIR}/ {job['destination']} {rclone_flags}\n")

        else:
            script.write("echo 'Copying files without compression or splitting...'\n")
            script.write(f"rclone copy {job['source_dir']} {job['destination']} {rclone_flags}\n")

        script.write("echo 'Backup completed.'\n")

        if log_file:
            script.write(f"if ! grep -qE 'ERROR|FATAL' {log_file}; then\n")
            script.write(f"    echo 'No errors found in log. Deleting {log_file}...'\n")
            script.write(f"    rm -f {log_file}\n")
            script.write("else\n")
            script.write("    echo 'Errors detected in log. Keeping it for review.'\n")
            script.write("fi\n")

    os.chmod(script_path, 0o755)
    return script_path


import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def generate_restore_script(config, job_id):
    """Generate a restore script for the specified job."""
    job = config[job_id]
    target_dir = job["source_dir"]
    script_path = os.path.join(SCRIPT_DIR, f"restore_{job_id}.sh")
    os.makedirs(SCRIPT_DIR, exist_ok=True)

    # Bygg rclone-flaggor baserat på användarval
    rclone_flags = " ".join(f"{flag} {value}" for flag, value in job.get("rclone_flags", {}).items())

    # Kontrollera om --progress är aktiverat
    use_progress = "--progress" in rclone_flags

    with open(script_path, "w") as script:
        script.write("#!/bin/bash\n")
        script.write("set -e\n")
        script.write("echo 'Starting restore process...'\n")

        # Hämta från remote
        script.write("echo 'Downloading files from remote...'\n")
        script.write(f"rclone copy {job['destination']} {TEMP_DIR} {rclone_flags}\n")

        if job.get("split_files"):
            script.write("echo 'Checking for split files...'\n")
            script.write(f"if ls {TEMP_DIR}/backup-part-* 1> /dev/null 2>&1; then\n")
            script.write("    echo 'Split files found. Reassembling...'\n")
            script.write(f"    cat {TEMP_DIR}/backup-part-* {'| pv -cN Reassembling' if use_progress else ''} > {TEMP_DIR}/backup.tar.gz\n")
            script.write(f"    rm {TEMP_DIR}/backup-part-* || true\n")
            script.write("else\n")
            script.write("    echo 'Error: No split files found!'\n")
            script.write("    exit 1\n")
            script.write("fi\n")

        # Extrahera om komprimering används
        if job.get("compress"):
            script.write("echo 'Extracting compressed files...'\n")
            script.write(f"mkdir -p {target_dir}\n")
            if use_progress:
                script.write(f"pv -cN Extracting {TEMP_DIR}/backup.tar.gz | tar -xz -C {target_dir}\n")
            else:
                script.write(f"tar -xzf {TEMP_DIR}/backup.tar.gz -C {target_dir}\n")
            script.write(f"rm {TEMP_DIR}/backup.tar.gz\n")
        else:
            script.write("echo 'Restoring files without compression...'\n")
            script.write(f"rclone copy {TEMP_DIR} {target_dir} {rclone_flags}\n")

        script.write("echo 'Cleaning up temporary files...'\n")
        script.write(f"rm -rf {TEMP_DIR}/*\n")
        script.write("echo 'Restore completed.'\n")

    os.chmod(script_path, 0o755)
    return script_path


import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def generate_transfer_script(config, job_id):
    """Generate a transfer script for the specified job."""
    job = config[job_id]
    script_path = os.path.join(SCRIPT_DIR, f"transfer_{job_id}.sh")
    os.makedirs(SCRIPT_DIR, exist_ok=True)

    rclone_flags = " ".join(f"{flag} {value}" for flag, value in job.get("rclone_flags", {}).items())

    log_file = job.get("rclone_flags", {}).get("--log-file", None)

    with open(script_path, "w") as script:
        script.write("#!/bin/bash\n")
        script.write("set -e\n")
        script.write(f"echo 'Starting transfer process for job {job_id}...'\n")

        source = job["source"]
        destination = job["destination"]

        script.write(f"rclone copy {source} {destination} {rclone_flags}\n")

        script.write("echo 'Transfer completed.'\n")

        if log_file:
            script.write(f"if ! grep -qE 'ERROR|FATAL' {log_file}; then\n")
            script.write(f"    echo 'No errors found in log. Deleting {log_file}...'\n")
            script.write(f"    rm -f {log_file}\n")
            script.write("else\n")
            script.write("    echo 'Errors detected in log. Keeping it for review.'\n")
            script.write("fi\n")

    os.chmod(script_path, 0o755)
    return script_path


#RESTORE#

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def restore_backup_job(config):
    """Guide user through restoring a backup job."""
    while True:
        if not config:
            print("No backup jobs are configured. Create a backup job first.")
            return

        print("\nAvailable backup jobs: (Enter 'b' to go back)")
        for i, job_id in enumerate(config.keys(), start=1):
            print(f"{i}. {job_id}")
        selected_job = input("Select a job to restore from: ").strip()
        if selected_job.lower() == "b":
            return

        try:
            selected_job = int(selected_job) - 1
            if selected_job < 0 or selected_job >= len(config):
                print("Invalid choice. Try again.")
                continue
            job_id = list(config.keys())[selected_job]

            job_data = config[job_id]
            print(f"\nRestoring job '{job_id}':")
            print(f"- Source directory: {job_data['source_dir']}")
            print(f"- Destination: {job_data['destination']}")
            print(f"- Encrypted: {job_data.get('encrypt', False)}")
            print(f"- Compressed: {job_data.get('compress', False)}")
            print(f"- Split files: {job_data.get('split_files', False)}")

            if job_data.get("encrypt"):
                print("Note: This job is encrypted. You will need to provide the decryption password during restore.")

            # Generate and run the restore script
            script_path = generate_restore_script(config, job_id)
            print(f"Restore script generated: {script_path}")
            try:
                subprocess.run([script_path], shell=True, check=True)
                print("Restore completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while running the restore job: {e}")
            return
        except ValueError:
            print("Invalid input. Enter a number.")

#CRON-JOBS#

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def configure_cron_job(config, job_id):
    """Prompt user to set up a cron job for the specified job."""
    setup_cron = input("Do you want to schedule this job with a cron job? (yes/no): ").strip().lower()
    if setup_cron != "yes":
        print("Skipping cron job setup.")
        return

    print("\nCron Job Mode:")
    print("1. `copy`: Ensures files in the source are copied to the destination. Doesn't remove extra files from the destination.")
    print("2. `sync`: Synchronizes the source -> destination. Extra files in the destination will be removed.")
    cron_mode = input("Do you want to use 'copy' or 'sync' for the cron job? (default: copy): ").strip().lower()
    if cron_mode not in ["copy", "sync"]:
        cron_mode = "copy"

    print("\nSet up your cron schedule:")
    minute = input("Enter the minute (0-59, default: 0): ").strip() or "0"
    hour = input("Enter the hour (0-23, default: 0): ").strip() or "0"
    day_of_month = input("Enter the day of the month (1-31, default: * for every day): ").strip() or "*"
    month = input("Enter the month (1-12, default: * for every month): ").strip() or "*"
    day_of_week = input("Enter the day of the week (0=Sunday, 6=Saturday, default: * for every day): ").strip() or "*"

    schedule = f"{minute} {hour} {day_of_month} {month} {day_of_week}"
    job = config[job_id]

    source = job.get("source") or job.get("source_dir")
    destination = job["destination"]
    cron_command = f"rclone {cron_mode} {source} {destination} --progress --log-level INFO"
    cron_job = f"{schedule} {cron_command}"

    print(f"\nAdding the following cron job:\n{cron_job}")
    subprocess.run(f"(crontab -l 2>/dev/null; echo \"{cron_job}\") | crontab -", shell=True, check=True)
    print("Cron job added successfully.")


import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def edit_cron_jobs():
    """
    List, edit, or delete existing cron jobs with colored menu.
    """
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    RESET = "\033[0m"

    print("\nManaging cron jobs...\n")

    try:
        result = subprocess.run("crontab -l", shell=True, text=True, capture_output=True, check=True)
        cron_jobs = result.stdout.strip().split("\n")
    except subprocess.CalledProcessError:
        print("No cron jobs found.")
        return

    if not cron_jobs:
        print("No cron jobs found.")
        return

    print("\nExisting cron jobs:")
    for i, job in enumerate(cron_jobs, start=1):
        print(f"{YELLOW}{i}.{RESET} {GREEN}{job}{RESET}")

    print("\nWhat would you like to do:")
    print(f"{YELLOW}1.{RESET} {GREEN}Edit a cron job{RESET}")
    print(f"{YELLOW}2.{RESET} {GREEN}Delete a cron job{RESET}")
    print(f"{YELLOW}3.{RESET} {GREEN}Cancel{RESET}")

    choice = input("Enter your choice (1/2/3): ").strip()


import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def validate_flag_value(flag, value):
    """
    Validera inmatade värden för rclone-flaggor.
    """
    try:
        if flag in ["--tpslimit", "--tpslimit-burst", "--transfers", "--checkers", "--low-level-retries", "--retries"]:
            value = int(value)
            if value < 1:
                raise ValueError(f"{flag} must be greater than 0.")
        return value
    except ValueError as e:
        print(f"Invalid value for {flag}: {e}")
        return None

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def schedule_cron(job):
    """
    Add a cron job to root's crontab, reusing the rclone flags stored in the job configuration.
    Now only asks for day of the week, removing "day of the month".
    """
    print("\nSetting up a cron job for your task...")

    # Retrieve rclone flags from the job configuration
    rclone_flags = " ".join(f"{flag} {value}" for flag, value in job.get("rclone_flags", {}).items())

    # Build cron command
    source = job.get("source") or job.get("source_dir")
    destination = job["destination"]
    cron_command = f"rclone copy {source} {destination} {rclone_flags}"

    # Collect cron schedule
    print("\nSet up your cron schedule:")
    minute = input("Minute (0-59, default: 0): ").strip() or "0"
    hour = input("Hour (0-23, default: 0): ").strip() or "0"
    month = input("Month (1-12, default: * for every month): ").strip() or "*"
    day_of_week = input("Day of the week (0=Sunday, 6=Saturday, * for every day, default: *): ").strip() or "*"

    # Combine cron schedule (REMOVED day_of_month)
    schedule = f"{minute} {hour} * {month} {day_of_week}"

    # Add the cron job
    print(f"\nAdding the following cron job:\n{schedule} {cron_command}")
    try:
        subprocess.run(f"(crontab -l 2>/dev/null; echo \"{schedule} {cron_command}\") | crontab -", shell=True, check=True)
        print("Cron job added successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add cron job: {e}")



#MISCS#

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def run_command(command):
    """
    Kör ett kommando med eller utan sudo beroende på om scriptet körs som root.
    """
    if os.geteuid() != 0:
        command = f"sudo {command}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e}")
        raise

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def rerun_job(config):
    """Rerun an existing backup or transfer job."""
    if not config:
        print("No jobs found to rerun.")
        return

    print("\nExisting jobs:")
    for i, job_id in enumerate(config.keys(), start=1):
        job = config[job_id]
        job_type = "Transfer" if job.get("type") == "transfer" else "Backup"
        print(f"{i}. [{job_type}] {job_id} - Source: {job.get('source_dir', job.get('source'))}, Destination: {job['destination']}")

    try:
        choice = int(input("\nEnter the number of the job to rerun: ").strip()) - 1
        if choice < 0 or choice >= len(config):
            print("Invalid choice. Returning to main menu.")
            return

        job_id = list(config.keys())[choice]
        print(f"Rerunning job: {job_id}")
        script_path = os.path.join(SCRIPT_DIR, f"{'transfer' if config[job_id].get('type') == 'transfer' else 'backup'}_{job_id}.sh")
        
        if not os.path.exists(script_path):
            print(f"Error: Script for job {job_id} does not exist. Please recreate the job.")
            return

        try:
            print(f"Running the job {job_id}...")
            subprocess.run([script_path], shell=True, check=True)
            print("Job completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running the job: {e}")
    except ValueError:
        print("Invalid input. Returning to main menu.")

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def clear_configurations():
    """Clear configurations: Backup jobs, remotes, or all data."""
    config = load_config()

    print("\nWhat do you want to clear?")
    print("1. Clear all remotes (rclone config)")
    print("2. Clear a specific job")
    print("3. Clear all jobs")
    print("4. Clear temporary files")
    print("5. Cancel")
    choice = input("Enter your choice (1/2/3/4/5): ").strip()

    if choice == "1":
        print("\nClearing all remotes using rclone config...")
        subprocess.run("rclone config", shell=True)
        print("Remotes cleared. You can now configure new remotes.")
    elif choice == "2":
        if not config:
            print("No jobs found to clear.")
            return
        print("\nConfigured jobs:")
        for i, job_id in enumerate(config.keys(), start=1):
            print(f"{i}. {job_id}")
        try:
            job_choice = int(input("\nEnter the number of the job to delete: ").strip()) - 1
            if job_choice < 0 or job_choice >= len(config):
                print("Invalid choice. Returning to main menu.")
                return
            job_id = list(config.keys())[job_choice]
            print(f"\nDeleting job: {job_id}")
            del config[job_id]
            save_config(config)
            print(f"Job '{job_id}' deleted successfully.")
        except (ValueError, IndexError):
            print("Invalid input. Returning to main menu.")
    elif choice == "3":
        confirm = input("Are you sure you want to clear all jobs? (yes/no): ").strip().lower()
        if confirm == "yes":
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
                print("All jobs cleared.")
            else:
                print("Configuration file not found. No jobs to clear.")
        else:
            print("Operation canceled.")
    elif choice == "4":
        confirm = input("Are you sure you want to clear all temporary files? (yes/no): ").strip().lower()
        if confirm == "yes":
            subprocess.run(f"rm -rf {TEMP_DIR}/*", shell=True, check=True)
            print("Temporary files cleared.")
        else:
            print("Operation canceled.")
    elif choice == "5":
        print("Returning to main menu.")
    else:
        print("Invalid choice. Returning to main menu.")
        
import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def remove_dependencies():
    """
    Avinstallera endast verktyg och beroenden som installerades av BackupBuddy.
    Kör avinstallation i sekvens och hantera varje paket individuellt.
    """
    INSTALLED_PACKAGES_LOG = os.path.expanduser("~/.backupbuddy_installed_packages.log")
    if not os.path.exists(INSTALLED_PACKAGES_LOG):
        print("\nNo dependencies installed by BackupBuddy to remove.")
        return

    with open(INSTALLED_PACKAGES_LOG, "r") as log_file:
        dependencies = [line.strip() for line in log_file.readlines()]

    if not dependencies:
        print("\nNo dependencies installed by BackupBuddy to remove.")
        return

    print("\nRemoving dependencies installed by BackupBuddy...")

    def uninstall_package(package_manager, package):
        command = f"{package_manager} remove -y {package}"
        if os.geteuid() != 0:
            command = f"sudo {command}"
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Successfully removed: {package}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove {package} using {package_manager}: {e}")

    package_manager = None
    if shutil.which("apt"):
        package_manager = "apt"
        print("Detected Debian/Ubuntu-based distribution.")
    elif shutil.which("yum"):
        package_manager = "yum"
        print("Detected RedHat/CentOS-based distribution.")
    elif shutil.which("dnf"):
        package_manager = "dnf"
        print("Detected Fedora-based distribution.")
    elif shutil.which("pacman"):
        package_manager = "pacman"
        print("Detected Arch-based distribution.")
    else:
        print("Unknown Linux distribution. Please remove dependencies manually.")
        return

    # Kör avinstallation för varje paket
    for dependency in dependencies:
        print(f"\nAttempting to remove: {dependency}")
        uninstall_package(package_manager, dependency)

    # Hantera specifikt rclone om det installerades via ett skript
    if "rclone" in dependencies:
        print("\nChecking for manually installed rclone...")
        try:
            rclone_path = shutil.which("rclone")
            if rclone_path:
                os.remove(rclone_path)
                print(f"Manually installed rclone binary removed: {rclone_path}")
            else:
                print("rclone binary not found. Skipping manual removal.")
        except Exception as e:
            print(f"Failed to remove rclone binary: {e}")

    # Ta bort loggfilen efter avinstallation
    try:
        os.remove(INSTALLED_PACKAGES_LOG)
        print("Removed log of installed packages.")
    except Exception as e:
        print(f"Failed to remove package log file: {e}")

#REMOVE#
import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def remove_cron_jobs():
    """
    Ta bort endast de cron-jobb som skapats av BackupBuddy.
    Identifieras genom kommentaren "# backupbuddy".
    """
    print("\nRemoving BackupBuddy cron jobs...")

    try:
        # Hämta nuvarande cron-jobb
        if os.geteuid() != 0:
            print("Requesting sudo to manage cron jobs.")
            result = subprocess.run("sudo crontab -l", shell=True, text=True, capture_output=True)
        else:
            result = subprocess.run("crontab -l", shell=True, text=True, capture_output=True)

        # Kontrollera om crontab innehåller jobb
        if result.returncode != 0 or not result.stdout.strip():
            print("No cron jobs found.")
            return

        # Filtrera bort endast BackupBuddy-jobb
        current_cron_jobs = result.stdout.strip().split("\n")
        updated_cron_jobs = [job for job in current_cron_jobs if "# backupbuddy" not in job.lower()]

        # Uppdatera crontab utan BackupBuddy-jobb
        if len(updated_cron_jobs) == len(current_cron_jobs):
            print("No BackupBuddy cron jobs found to remove.")
            return

        command = "crontab -" if os.geteuid() == 0 else "sudo crontab -"
        cron_data = "\n".join(updated_cron_jobs) + "\n"
        subprocess.run(f"echo '{cron_data}' | {command}", shell=True, check=True)

        print("BackupBuddy cron jobs removed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove cron jobs: {e}")

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def remove_temp_files():
    """
    Ta bort alla temporära filer som används av BackupBuddy.
    """
    print("\nRemoving temporary files...")

    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            print(f"Temporary files removed from {TEMP_DIR}")
        else:
            print("No temporary files found.")
    except Exception as e:
        print(f"Failed to remove temporary files: {e}")

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def remove_configurations():
    """
    Remove all configurations, including rclone configuration files.
    """
    print("\nRemoving configurations...")

    # Ta bort BackupBuddy-konfigurationsfil
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
            print(f"BackupBuddy configuration file removed: {CONFIG_FILE}")
        except Exception as e:
            print(f"Failed to remove BackupBuddy configuration file: {e}")
    else:
        print("No BackupBuddy configuration file found.")

    # Ta bort rclone-konfigurationsfil
    rclone_config_path = os.path.expanduser("~/.config/rclone/rclone.conf")
    if os.path.exists(rclone_config_path):
        try:
            os.remove(rclone_config_path)
            print(f"rclone configuration file removed: {rclone_config_path}")
        except Exception as e:
            print(f"Failed to remove rclone configuration file: {e}")
    else:
        print("No rclone configuration file found.")

    # Rensa hela rclone-konfigurationsmappen om den är tom
    rclone_config_dir = os.path.expanduser("~/.config/rclone")
    if os.path.exists(rclone_config_dir) and not os.listdir(rclone_config_dir):
        try:
            os.rmdir(rclone_config_dir)
            print(f"Empty rclone configuration directory removed: {rclone_config_dir}")
        except Exception as e:
            print(f"Failed to remove rclone configuration directory: {e}")

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

import sys  # Lägg till sys-modulen för att använda sys.exit()

def uninstall_backupbuddy():
    """
    Uninstall BackupBuddy and all related components.
    Allow the user to choose whether to remove only tools and dependencies
    or everything, including logs, configs, jobs, and cronjobs.
    """
    print("\nUninstall BackupBuddy")
    print("1. Remove tools and dependencies only")
    print("2. Remove everything (tools, dependencies, temp, configs, jobs, cronjobs)")
    print("3. Cancel")

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        # Remove only tools and dependencies
        remove_dependencies()
    elif choice == "2":
        # Full uninstallation
        remove_cron_jobs()
        remove_temp_files()
        remove_configurations()
        remove_dependencies()
        print("\nBackupBuddy and all related components have been fully removed.")
        validate_removal()  # Run validation
        print("Exiting BackupBuddy. Goodbye!")
        sys.exit(0)  # Avsluta programmet direkt efter avinstallation
    elif choice == "3":
        print("Uninstallation canceled.")
    else:
        print("Invalid choice. Returning to main menu.")

import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess

def validate_removal():
    """
    Kontrollera att alla förväntade filer, mappar och cron-jobb har tagits bort.
    """
    print("\nValidating removal of BackupBuddy components...")

    # Kontrollera mappen TEMP_DIR
    if os.path.exists(TEMP_DIR):
        print(f"Temporary directory still exists: {TEMP_DIR}")
    else:
        print(f"Temporary directory successfully removed: {TEMP_DIR}")

    # Kontrollera konfigurationsfilen
    if os.path.exists(CONFIG_FILE):
        print(f"Configuration file still exists: {CONFIG_FILE}")
    else:
        print(f"Configuration file successfully removed: {CONFIG_FILE}")

    # Kontrollera backup-skriptmappen
    if os.path.exists(SCRIPT_DIR):
        print(f"Backup scripts directory still exists: {SCRIPT_DIR}")
    else:
        print(f"Backup scripts directory successfully removed: {SCRIPT_DIR}")

    # Kontrollera om cron-jobb finns kvar
    try:
        if os.geteuid() != 0:
            result = subprocess.run("sudo crontab -l", shell=True, text=True, capture_output=True)
        else:
            result = subprocess.run("crontab -l", shell=True, text=True, capture_output=True)

        if result.returncode == 0 and "backupbuddy" in result.stdout.lower():
            print("Some BackupBuddy cron jobs still exist:")
            print(result.stdout)
        else:
            print("All BackupBuddy cron jobs successfully removed.")
    except subprocess.CalledProcessError:
        print("No cron jobs found, or crontab is empty.")

    print("\nValidation completed.")
    

#HELP#
import subprocess
import time  # Importera time-modulen för att använda sleep
import subprocess


def show_help():
    """
    Display an overview of BackupBuddy and its features.
    """
    print("\n========================================")
    print("Welcome to the BackupBuddy Help Section!")
    print("========================================\n")
    print("BackupBuddy is a powerful tool for backing up, restoring, and transferring files "
          "between local and cloud-based systems.")
    print("It supports task scheduling using cron jobs and provides flexible settings "
          "to minimize API requests to cloud providers.\n")
    
    print("Key Features:")
    print("1. **Create Backups:**")
    print("   Back up local files or folders to cloud storage or another local destination.")
    print("2. **Restore Backups:**")
    print("   Restore files from a backup to your desired destination.")
    print("3. **Schedule Tasks:**")
    print("   Set up cron jobs to automate backups and transfers.")
    print("4. **Configure rclone Remotes:**")
    print("   Manage cloud storage accounts and connections via rclone.")
    print("5. **Optimize API Requests:**")
    print("   Customize rclone flags such as `--tpslimit` and `--transfers` to avoid exceeding API limits.\n")
    
    print("Available Commands:")
    print("1. **Create a Backup:** Guides you through creating a new backup task.")
    print("2. **Create a Transfer Task:** Set up a task to transfer files between two destinations.")
    print("3. **Restore a Backup:** Restore files from a previous backup.")
    print("4. **Schedule Cron Jobs:** Create automated schedules to run backup and transfer tasks.")
    print("5. **Manage Configurations:** View, edit, or delete existing settings and tasks.")
    print("6. **Uninstall BackupBuddy:** Removes all files, logs, and settings related to BackupBuddy.\n")
    
    print("Example Customizable rclone Flags:")
    print("  --tpslimit <number>: Limits the number of API requests per second (default: 2).")
    print("  --tpslimit-burst <number>: Allows a short burst of requests above the limit (default: 1).")
    print("  --transfers <number>: Sets the number of concurrent file transfers (default: 2).")
    print("  --checkers <number>: Sets the number of file checkers to verify file integrity (default: 1).")
    print("  --low-level-retries <number>: Number of retries for low-level errors (default: 3).")
    print("  --retries <number>: Number of retries for the entire operation (default: 5).")
    print("  --log-file <file>: Specifies the log file for rclone operations (default: rclone.log).")
    print("  --log-level <level>: Sets the verbosity level for logging (default: INFO).\n")
    
    print("Tips:")
    print("1. Use reasonable values for flags to avoid hitting API limits imposed by cloud providers.")
    print("2. Review log files (`rclone.log`) to troubleshoot issues or monitor operations.")
    print("3. Use `Manage Configurations` to update existing tasks or clean up unnecessary data.\n")
    
    print("For more information, visit the rclone documentation or contact support!")

#MAIN#


def display_logo():
    """
    Display a green ASCII logo next to the welcome message, with red HTTP links and yellow numbers in the menu.
    """
    # ANSI Escape Codes for colors
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"  # Reset to default color

    ascii_logo = rf"""
     {RED} _________________
    | | ____My_____ |o|
    | | ____Old____ | |
    | | _Pictures__ | |
    | | _____&_____ | |
    | |____Taxes____| |
    |     _______     |
    |    |       |   ||
    | DD |       |   V|
    |____|_______|____|{RESET}
    """
    print(f"{GREEN}.............................................................{RESET}")
    print(f"{YELLOW}psst, look here:{RESET}")
    print(f"Have you considered trying out Parrot OS Sec/Home or HTB edition?")
    print(f"Find them here: {RED}https://www.parrotsec.org{RESET}\n")
    print(f"\n{GREEN}===============================================\n{RESET}")
    print(f"{GREEN}Welcome to BackupBuddy!                      ||{RESET}")
    print(f"{GREEN}Let's back up your files and keep them safe. ||{RESET}")
    print(f"{GREEN}===============================================\n{RESET}")
    print(ascii_logo)
    print(f"For help regarding BackupBuddy, check: {GREEN}https://github.com/TubalQ/BackupBuddy{RESET}")
    print(f"Good Luck & check option 9 for help // Best regards T-Q {GREEN}https://t-vault.se{RESET}")

def main():
    """
    Main program to handle backup and restore operations.
    """
    # Define color variables at the top of the main function
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"  # Reset to default color

    check_and_install_dependencies()

    # Display the ASCII logo and welcome message
    display_logo()

    while True:
        config = load_config()
        list_jobs(config)

        print("\nWhat would you like to do:")
        print(f"{YELLOW}1.{RESET} Create a new backup job")
        print(f"{YELLOW}2.{RESET} Create a new transfer job")
        print(f"{YELLOW}3.{RESET} Restore from an existing backup job")
        print(f"{YELLOW}4.{RESET} Rerun an existing job")
        print(f"{YELLOW}5.{RESET} Manage cron jobs")
        print(f"{YELLOW}6.{RESET} Clear configurations and data")
        print(f"{YELLOW}7.{RESET} Add a new remote or local path")
        print(f"{YELLOW}8.{RESET} Uninstall BackupBuddy")
        print(f"{YELLOW}9.{RESET} Help")
        print(f"{YELLOW}10.{RESET} Exit")
        
        choice = input("Enter your choice (1-10): ").strip()

        if choice == "1":
            create_backup_job(config)
        elif choice == "2":
            create_transfer(config)
        elif choice == "3":
            restore_backup_job(config)
        elif choice == "4":
            rerun_job(config)
        elif choice == "5":
            edit_cron_jobs()
        elif choice == "6":
            clear_configurations()
        elif choice == "7":
            manage_remotes_and_paths()
        elif choice == "8":
            uninstall_backupbuddy()
        elif choice == "9":
            show_help()
        elif choice == "10":
            print("Goodbye! Thanks for using BackupBuddy.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
