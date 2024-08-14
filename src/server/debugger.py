import os

def initialize_debug_server_if_needed(wait_for_client=False, break_on_attach=False):
    if os.getenv("DEBUGGER") == "True":
        import psutil

        current_process = psutil.Process()
        parent_process = current_process.parent()

        # Flask in debug mode will fork() and have the child process handle requests.
        # If we don't check, we'll try to listen on the same port from both processes.
        # To avoid that, we only listen on debugpy from the child process. We identify
        # the parent process by checking its name for 'flask'
        if parent_process is not None and parent_process.name() == "flask":
            import debugpy

            debugpy.listen(("0.0.0.0", 5678))
            print("⏳ VS Code debugger can now be attached, press F5 in VS Code ⏳", flush=True)
            if wait_for_client:
                debugpy.wait_for_client()
                if break_on_attach:
                    breakpoint()
                else:
                    print("🎉 VS Code debugger attached, enjoy debugging 🎉", flush=True)
