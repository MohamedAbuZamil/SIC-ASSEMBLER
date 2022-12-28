import tkinter as tk

# Create the main window
window = tk.Tk()

# Set the size of the window
window.geometry("800x600")
window.config(bg="#00ffff")

# Create a function to save the text and run the script
def save_and_run():
    # Get the text from the text field
    text = text_field.get("1.0", "end")

    # Open the file for writing
    with open("CODE.txt", "w") as f:
        # Write the text to the file
        f.write(text)

    # Run the script
    import main

    # Open the files for reading
    with open("ans.txt") as f1, open("ObjectProgram.txt") as f2:
        # Read the contents of the files
        ans = f1.read()
        obj = f2.read()

    # Insert the contents of the files into the text field
    text_field.insert("end", "\n")
    text_field.insert("end", ans)
    text_field.insert("end", "\n")
    text_field.insert("end", obj)

# Create a text field to enter the text
text_field = tk.Text(window, width=70, height=35)
text_field.pack()

# Create a button to save the text and run the script
button = tk.Button(text="Save and Run", command=save_and_run,bg="#0000ff", fg="#ffffff", font=("Arial", 14), relief="groove", bd=5, padx=10, pady=5 )

button.pack()
un the main loop
window.mainloop()
