
# Add to the VERY TOP of .zshrc
if [ -z "$SCRIPT_LOG_FILE" ]; then
    # 1. Use $$ to create a unique file for THIS specific tab/window
    export SCRIPT_LOG_FILE="/tmp/session_$$.log"
    
    # 2. Start recording
    # We remove 'exec' so we can run the cleanup command afterwards
    script -q -F "$SCRIPT_LOG_FILE" /bin/zsh
    
    # 3. Cleanup: When you type 'exit' or close the tab, delete the file
    rm -f "$SCRIPT_LOG_FILE"
    
    # 4. Close the parent terminal too so it doesn't hang around
    exit
fi

