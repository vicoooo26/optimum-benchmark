import argparse
import os
import re
import subprocess
import sys

EXTERNAL_REPOS_DIR = "external_repos"


def process_setup_file(setup_file_path):
    with open(setup_file_path, "r") as file:
        setup_content = file.read()

    # Use a regular expression to remove any line containing "torch=="
    setup_content = re.sub(r'"torch==[^\"]+",', "", setup_content)

    # Set IS_CPU_ONLY to False
    setup_content = setup_content.replace(
        "IS_CPU_ONLY = not torch.backends.mps.is_available() and not torch.cuda.is_available()", "IS_CPU_ONLY = False"
    )

    # Write the modified content back to setup.py
    with open(setup_file_path, "w") as file:
        file.write(setup_content)


def clone_or_pull_repo(repo_url, repo_location_path):
    """Clone the repo if it doesn't exist; otherwise, pull the latest changes."""
    if os.path.exists(repo_location_path):
        print(f"Directory {repo_location_path} already exists. Pulling the latest changes.")
        subprocess.run(f"cd {repo_location_path} && git pull", shell=True, check=True)
    else:
        repo_name = repo_location_path.split("/")[-1]
        print(f"Cloning {repo_name} into {repo_location_path}")
        subprocess.run(f"git clone {repo_url} {repo_location_path}", shell=True, check=True)


def install_autoawq_from_source():
    """Install the AutoAWQ and AutoAWQ_kernels packages from GitHub."""
    print("Installing AutoAWQ and AutoAWQ_kernels packages.")

    autoawq_repo_name = "AutoAWQ"
    autoawq_kernels_repo_name = "AutoAWQ_kernels"

    autoawq_repo_path = os.path.join(EXTERNAL_REPOS_DIR, autoawq_repo_name)
    kernels_repo_path = os.path.join(EXTERNAL_REPOS_DIR, autoawq_kernels_repo_name)

    clone_or_pull_repo(f"https://github.com/casper-hansen/{autoawq_kernels_repo_name}", kernels_repo_path)
    kernels_setup_file_path = os.path.join(kernels_repo_path, "setup.py")
    process_setup_file(kernels_setup_file_path)
    subprocess.run(
        f"cd {kernels_repo_path} && {sys.executable} -m pip install .",
        shell=True,
        check=True,
        env=os.environ,
    )

    clone_or_pull_repo(f"https://github.com/casper-hansen/{autoawq_repo_name}", autoawq_repo_path)
    autoawq_setup_file_path = os.path.join(autoawq_repo_path, "setup.py")
    process_setup_file(autoawq_setup_file_path)
    subprocess.run(
        f"cd {autoawq_repo_path} && {sys.executable} -m pip install .",
        shell=True,
        check=True,
        env=os.environ,
    )

    print("AutoAWQ and AutoAWQ_kernels packages installed.")


def install_autogptq_from_source():
    """Install the AutoGPTQ package from GitHub."""
    print("Installing AutoGPTQ package.")
    autogptq_repo_path = os.path.join(EXTERNAL_REPOS_DIR, "AutoGPTQ")

    clone_or_pull_repo("https://github.com/PanQiWei/AutoGPTQ.git", autogptq_repo_path)
    subprocess.run("pip install numpy gekko pandas", shell=True, check=True, env=os.environ)
    autogptq_setup_file_path = os.path.join(autogptq_repo_path, "setup.py")
    process_setup_file(autogptq_setup_file_path)
    subprocess.run(
        f"cd {autogptq_repo_path} && {sys.executable} -m pip install .",
        shell=True,
        check=True,
        env=os.environ,
    )

    print("AutoGPTQ package installed.")


def main():
    parser = argparse.ArgumentParser(description="Install AutoAWQ or AutoGPTQ from source.")
    parser.add_argument(
        "--install-autoawq-from-source",
        action="store_true",
        help="Install AutoAWQ and AutoAWQ_kernels packages from source.",
    )
    parser.add_argument(
        "--install-autogptq-from-source",
        action="store_true",
        help="Install AutoGPTQ package from source.",
    )

    args = parser.parse_args()

    if args.install_autoawq_from_source:
        install_autoawq_from_source()
    if args.install_autogptq_from_source:
        install_autogptq_from_source()

    if not args.install_autoawq_from_source and not args.install_autogptq_from_source:
        print(
            "Please specify an installation option. Use --install-autoawq-from-source or --install-autogptq-from-source."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()