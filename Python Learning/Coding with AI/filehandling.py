# Simple file handling example in Python

file_name = "sample.txt"

# ✅ Write to a file (creates if not exists)
with open(file_name, "w") as file:
    file.write("Hello! This is my first file in Python.\n")
    file.write("I am learning file handling in VS Code.\n")

print("✅ File created and written successfully.")

# ✅ Append text to the same file
with open(file_name, "a") as file:
    file.write("This is an appended line.\n")

print("➕ Appended a new line to the file.")

# ✅ Read the file content
with open(file_name, "r") as file:
    content = file.read()

print("\n📖 File Content:")
print(content)