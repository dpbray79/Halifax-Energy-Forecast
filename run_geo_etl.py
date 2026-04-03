import subprocess
import os
import sys

def run_script(script_path):
    print(f"\n>>> Running {script_path}...")
    try:
        # Use the virtual environment's python
        python_exe = os.path.join(".venv", "bin", "python3")
        if not os.path.exists(python_exe):
            python_exe = sys.executable
            
        result = subprocess.run([python_exe, script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}:")
        print(e.stderr)
        return False
    return True

def main():
    print("=" * 60)
    print("HALIFAX ENERGY GEO - MASTER ETL PIPELINE")
    print("=" * 60)
    
    scripts = [
        "scripts/step6_geo_extract.py",
        "scripts/step7_geo_transform.py",
        "scripts/step8_zone_predict.py"
    ]
    
    for script in scripts:
        if not run_script(script):
            print("\nPipeline failed.")
            sys.exit(1)
            
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    main()
