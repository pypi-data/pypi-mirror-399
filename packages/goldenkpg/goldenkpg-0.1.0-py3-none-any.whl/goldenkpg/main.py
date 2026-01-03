import sys
import os
import shutil

# Map keywords to folder names (conceptually, though we can just use the folders directly)
# The user asked for "brain", "heart", "liver" as keywords.
# We will match these to the folder names in 'templates/'

def get_package_root():
    return os.path.dirname(os.path.abspath(__file__))

def get_templates_dir():
    return os.path.join(get_package_root(), 'templates')

def list_available_categories():
    templates_dir = get_templates_dir()
    if not os.path.exists(templates_dir):
        return []
    return [d for d in os.listdir(templates_dir) if os.path.isdir(os.path.join(templates_dir, d))]

def print_help():
    print("Usage: goldenkpg <keyword>")
    print("\nAvailable Keywords:")
    categories = list_available_categories()
    if not categories:
        print("  (No templates found)")
    else:
        # Descriptions could be hardcoded or read from a manifest. 
        # For simplicity and scalability, we'll map known ones and default others.
        descriptions = {
            "cpu_scheduling": "CPU Scheduling Algorithms",
            "disk_scheduling": "Disk Scheduling Algorithms",
            "page_replacement": "Page Replacement Algorithms",
            "memory_allocation": "Memory Allocation Algorithms"
        }
        for cat in categories:
            desc = descriptions.get(cat, "Custom Algorithms")
            print(f"  {cat:<20} → {desc}")
    print("\nExample: goldenkpg cpu_scheduling")

def run():
    argv = sys.argv[1:]
    
    if not argv or argv[0] in ['help', '--help', '-h']:
        print_help()
        return

    keyword = argv[0].lower()
    templates_dir = get_templates_dir()
    category_dir = os.path.join(templates_dir, keyword)

    if not os.path.exists(category_dir):
        print(f"❌ Error: Keyword '{keyword}' not found.")
        print("Run 'goldenkpg help' to see available options.")
        return

    # List py files in the directory
    files = [f for f in os.listdir(category_dir) if f.endswith('.py') and f != '__init__.py']
    
    if not files:
        print(f"⚠️ No templates found in '{keyword}'.")
        return

    print(f"\n📂 Available {keyword} templates:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")

    print("\nSelect a template to generate (enter number): ", end='')
    try:
        choice = input()
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            selected_file = files[idx]
            source_path = os.path.join(category_dir, selected_file)
            dest_path = os.path.join(os.getcwd(), selected_file)
            
            # Check if file exists
            if os.path.exists(dest_path):
                print(f"⚠️ File '{selected_file}' already exists in current directory. Overwrite? (y/n): ", end='')
                if input().lower() != 'y':
                    print("Aborted.")
                    return

            shutil.copy2(source_path, dest_path)
            print(f"✅ Successfully generated '{selected_file}'!")
        else:
            print("❌ Invalid selection.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        print("\nAborted.")

if __name__ == "__main__":
    run()
