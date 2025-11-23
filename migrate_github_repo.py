import os
import subprocess
import shutil

# ==============================================================================
#                       HOW TO GENERATE A GITHUB TOKEN
# ==============================================================================
# You need a Personal Access Token (PAT) because passwords don't work for scripts.
#
# 1. Log in to the GitHub account you need access to.
# 2. Go to: https://github.com/settings/tokens
# 3. Click "Generate new token (classic)".
# 4. Note: "Migration Script".
# 5. Expiration: Set to "7 days" (since you only need it now).
# 6. Select Scopes: Check the [x] repo box (this gives full read/write access).
# 7. Click "Generate token".
# 8. COPY the token (starts with ghp_...) and paste it below.
#
# *Repeat this for the second account if Source and Dest are different users.*
# ==============================================================================


# ==============================================================================
#                               CONFIGURATION
# ==============================================================================
# https://github.com/rqz123/speaker_identification.git
# https://github.com/rqz123/class-qa-starter.git
# https://github.com/rqz123/talk2-openai.git
# https://github.com/rqz123/question_dedup.git

# --- 1. SOURCE ACCOUNT (Where we copy FROM) ---
SOURCE_REPO_URL = "https://github.com/rqz123/class-qa-starter.git" 
SOURCE_USER     = "rqz123"
# Needs 'repo' scope (READ access)
SOURCE_TOKEN    = "REDACTED" 

# --- 2. DESTINATION ACCOUNT (Where we copy TO) ---
# IMPORTANT: Make sure this repo exists and is EMPTY (No README, No License)
DEST_REPO_URL   = "https://github.com/ta1cy/class-qa-starter.git"
DEST_USER       = "ta1cy"
# Needs 'repo' scope (WRITE access)
DEST_TOKEN      = "REDACTED"

# --- 3. HISTORY REWRITE (Change Commit Authors) ---
# This finds every commit by 'OLD_EMAIL' and changes it to your new details.
# If you don't want to rewrite history, just leave these as they are (it won't break).
OLD_EMAIL_TO_MATCH = "qz123@yahoo.com"
NEW_AUTHOR_NAME    = "Joseph Zhang"
NEW_AUTHOR_EMAIL   = "jazz24313@gmail.com"

# --- 4. SETTINGS ---
TEMP_DIR = "repo_migration_temp"

# ==============================================================================
#                            END OF CONFIGURATION
# ==============================================================================

def get_auth_url(url, user, token):
    """Injects credentials into the URL for authentication."""
    # Strip existing protocol to avoid double https://
    clean_url = url.replace("https://", "").replace("http://", "")
    return f"https://{user}:{token}@{clean_url}"

def run_command(command, cwd=None, description="command"):
    """Runs a shell command and handles errors gracefully."""
    try:
        # We use subprocess to execute git commands
        subprocess.run(
            command, 
            cwd=cwd, 
            check=True, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        print(f"✅ Success: {description}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during: {description}")
        err_msg = e.stderr.decode()
        
        if "403" in err_msg:
            print(f"   -> PERMISSION DENIED. Check the token scopes for this user.")
        elif "404" in err_msg:
            print("   -> REPO NOT FOUND. Check the URL or Token validity.")
        elif "remote: Repository not found" in err_msg:
            print("   -> GitHub says repository not found (or token is invalid).")
        else:
            print(f"   -> Detailed Error: {err_msg.strip()}")
        exit(1)

def main():
    print("🚀 Starting Repository Migration...")
    print(f"   From: {SOURCE_USER}  ->  To: {DEST_USER}")

    # 1. Clean up previous temp folders if they exist
    if os.path.exists(TEMP_DIR):
        # Helper to delete read-only git files on Windows
        def remove_readonly(func, path, excinfo):
            os.chmod(path, 0o777)
            func(path)
        shutil.rmtree(TEMP_DIR, onerror=remove_readonly)

    # 2. Clone Source
    print(f"\nStep 1/4: Cloning source repository...")
    auth_source_url = get_auth_url(SOURCE_REPO_URL, SOURCE_USER, SOURCE_TOKEN)
    run_command(f"git clone --bare {auth_source_url} {TEMP_DIR}", description="Cloning Source")

    # 3. Prepare Mailmap
    print(f"Step 2/4: Configuring history rewrite...")
    # Format: New Name <New Email> <Old Name> <Old Email>
    mailmap_content = f"{NEW_AUTHOR_NAME} <{NEW_AUTHOR_EMAIL}> <{OLD_EMAIL_TO_MATCH}>"
    
    mailmap_path = os.path.join(TEMP_DIR, "mailmap")
    with open(mailmap_path, "w") as f:
        f.write(mailmap_content)

    # 4. Run Filter-Repo
    print(f"Step 3/4: Rewriting history (Author: {NEW_AUTHOR_NAME})...")
    try:
        # git-filter-repo must be run inside the repo folder
        subprocess.run(
            f"git filter-repo --mailmap mailmap --force", 
            cwd=TEMP_DIR, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Success: History rewritten")
    except FileNotFoundError:
        print("\n❌ FATAL ERROR: 'git-filter-repo' is not installed.")
        print("   Please run: pip install git-filter-repo")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error rewriting history: {e.stderr.decode()}")
        exit(1)

    # 5. Push to Destination
    print(f"Step 4/4: Pushing to new repository...")
    auth_dest_url = get_auth_url(DEST_REPO_URL, DEST_USER, DEST_TOKEN)
    run_command(f"git push --mirror {auth_dest_url}", cwd=TEMP_DIR, description="Pushing to Destination")

    # 6. Cleanup
    print("\n🧹 Cleaning up temporary files...")
    if os.path.exists(TEMP_DIR):
        # Helper to delete read-only git files on Windows
        def remove_readonly(func, path, excinfo):
            os.chmod(path, 0o777)
            func(path)
        shutil.rmtree(TEMP_DIR, onerror=remove_readonly)

    print("\n🎉 MIGRATION COMPLETE!")
    print("   You can now verify the repo at: " + DEST_REPO_URL)

if __name__ == "__main__":
    main()