import os

def join_text_files(folder_path, master_file_path):
    """
    Joins all text files from a folder into a single master file,
    with each file's name written at the top of its content.
    
    Args:
        folder_path (str): Path to the folder containing text files.
        master_file_path (str): Path to save the combined master file.
    """
    # Open the master file in write mode
    with open(master_file_path, 'w', encoding='utf-8') as master_file:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            
            # Check if the file is a text file
            if os.path.isfile(file_path) and file_name.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as text_file:
                    content = text_file.read()
                    
                    # Write file name and content to the master file
                    master_file.write(f"=== {file_name} ===\n")
                    master_file.write(content + '\n\n')  # Add a newline after each file's content
                
                print(f"Added: {file_name}")

    print(f"Master file created: {master_file_path}")

# Example usage
folder_path = r'C:\Users\USER\Desktop\paid_ocr\gpt_mindee_v_0\shuvro\out_put_path'  # Replace with your folder path
master_file_path = 'master_file.txt'  # Replace with desired master file path
join_text_files(folder_path, master_file_path)
