# import os
# import subprocess

# INPUT_DIR = "contracts"
# OUTPUT_DIR = "output"

# os.makedirs(OUTPUT_DIR, exist_ok=True)


# def run_pipeline(sol_file, json_file):
#     try:
#         result = subprocess.run(
#             ["python", "pipeline.py", sol_file, json_file],
#             capture_output=True,
#             text=True,
#             timeout=60   #  add timeout
#         )

#         if result.returncode == 0:
#             print(f"[DONE] Success: {os.path.basename(sol_file)}")
#         else:
#             print(f" Failed: {os.path.basename(sol_file)}")
#             print("---- ERROR ----")
#             print(result.stderr)
#             print("----------------")

#     except Exception as e:
#         print(f" Crash on {sol_file}: {e}")


# def main():
#     files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".sol")]

#     print(f" Found {len(files)} contracts\n")

#     success = 0
#     failed = 0

#     for file in files:
#         sol_path = os.path.join(INPUT_DIR, file)
#         json_path = os.path.join(OUTPUT_DIR, file.replace(".sol", ".json"))

#         run_pipeline(sol_path, json_path)

#         if os.path.exists(json_path):
#             success += 1
#         else:
#             failed += 1

#     print("\n SUMMARY")
#     print(f" Success: {success}")
#     print(f" Failed: {failed}")


# if __name__ == "__main__":
#     main()

import os
import subprocess

INPUT_DIR = "dataset"
OUTPUT_DIR = "dataset_output"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_pipeline(sol_file, json_file, label):
    result = subprocess.run(
        ["python", "pipeline.py", sol_file, json_file, label],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"[DONE] {os.path.basename(sol_file)}")
    else:
        print(f"[FAILED] {os.path.basename(sol_file)}")
        print(result.stderr)


def main():
    for root, dirs, files in os.walk(INPUT_DIR):
        label = os.path.basename(root)

        for file in files:
            if file.endswith(".sol"):
                sol_path = os.path.join(root, file)

                json_name = file.replace(".sol", ".json")
                json_path = os.path.join(OUTPUT_DIR, json_name)

                run_pipeline(sol_path, json_path, label)


if __name__ == "__main__":
    main()