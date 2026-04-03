import subprocess
import os
import sys

def run_step(script_name):
    print(f"\n--- Running {script_name} ---")
    try:
        # Use our local venv
        python_exe = os.path.join(".venv", "bin", "python3")
        if not os.path.exists(python_exe):
            python_exe = sys.executable
            
        result = subprocess.run([python_exe, os.path.join("etl", script_name)], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error in {script_name}:")
        print(e.stderr)
        return False
    return True

def main():
    print("=" * 60)
    print("HALIFAX ENERGY CLOUD ETL PIPELINE v2.0")
    print("=" * 60)
    
    steps = [
        "extract_weather.py",
        "extract_energy.py",
        "transform.py",
        "predict.py",
        "export_json.py"
    ]
    
    for step in steps:
        if not run_step(step):
            print("\nPipeline failed!")
            sys.exit(1)
            
    print("\n" + "=" * 60)
    print("PIPELINE SUCCESSFUL")
    print("=" * 60)

if __name__ == "__main__":
    main()
