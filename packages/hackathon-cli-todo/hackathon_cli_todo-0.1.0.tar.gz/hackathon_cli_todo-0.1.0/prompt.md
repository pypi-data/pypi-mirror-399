
# constitution: 
Generate a Constitution file for a command-line Todo application.
The project is a Python 3.13+ and uv console-based todo app that stores tasks in memory.
It follows spec-driven development using Claude Code and Spec-Kit Plus.
The Constitution should define:
- Project purpose and scope (console-only, in-memory)
- Core principles (clean code, simplicity)
- Allowed and disallowed features 
- Coding standards and structure rules
- Specification-first workflow expectations
Keep it concise, formal, and suitable for an educational software project.
Output only the Constitution content in markdown format.

# specification: 
Write a short Spec-Kit Plus specification for a Phase-1 command-line Todo app.
Context:
- Python 3.13+
- uv
- Console-based
- In-memory tasks only
- No database, files, UI, or cloud
- Built with Claude Code and Spec-Kit Plus
Include:
- Problem statement
- CRUD + mark complete requirements
- Non-functional requirements
- Task data model (fields only)
- Command-line flow
- application runs using while loop until user exits
- Acceptance criteria
- Out-of-scope features
Use markdown, clear testable language, no code, output only the 
/claer

# Interactive mode
  python -m src

  # Command-line mode
  python -m src add "Buy milk"
  python -m src list
  python -m src complete 1
  python -m src delete 1

  # Publishing as a Package:
  You will act as expert python developer and will complete the task carefeully according to the        
  project structure and code files . I want to package this application so that:
  - It can be installed globally using pip or uv
  - It exposes a command named `todo`
  - Running `todo` launches the CLI menu
  - No database, UI, or cloud services are used   -- Make the changes in app that will work
  effectively also add steps to installation and using steps for global user in
  d:\Agentic-Hackthon\Hackthon-II-Todo-App\PHASE-I-CLI-Todo-app\specs\001-cli-todo-app\quickstart.md    
  -- and guide proper what should i do next