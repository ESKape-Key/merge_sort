import tempfile
import os
import csv
import tkinter as tk
from tkinter import filedialog



def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("CSV files", "*.csv")],
        initialdir="./"  # Optional: Set the initial directory
    )

    if file_path:
        print(f"Selected file: {file_path}")
    else:
        print("File selection canceled.")
        
    return file_path

def csv_to_list(file_path):
    data_list = []

    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data_list.append(dict(row))

    return data_list

def create_temp_csv_from_dict(data_dict):
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='', suffix='.csv')

    try:
        # Use csv.DictWriter to write data to the temporary CSV file
        csv_writer = csv.DictWriter(temp_file, fieldnames=data_dict[0].keys())
        
        # Write the header
        csv_writer.writeheader()

        # Write the data rows
        csv_writer.writerows(data_dict)
        return temp_file.name
    finally:
        temp_file.close()

def write_csv(file_path, data, header):
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(data)

def split_csv(file_path):
    #print("running split_csv")
    try:
        with open(file_path, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            #print(csv_reader)
            # Check if the file is empty
            try:
                header = next(csv_reader) # Read and store the header
            except StopIteration:
                return None, None

            # Split the rows into two parts
            row_count = sum(1 for row in csv_reader)
            split_point = row_count // 2

            # Reset the file pointer
            csv_file.seek(0)
            next(csv_reader)  # Skip the header
            
            # Create temporary files
            temp_file1 = tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='', suffix='.csv')
            temp_file2 = tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='', suffix='.csv')

            # Write the header to both temporary files
            csv_writer1 = csv.writer(temp_file1)
            csv_writer1.writerow(header)

            csv_writer2 = csv.writer(temp_file2)
            csv_writer2.writerow(header)
            
            # Write rows to temporary files based on the split point
            for index, row in enumerate(csv_reader):
                if index < split_point:
                    csv_writer1.writerow(row)
                else:
                    csv_writer2.writerow(row)
                    
        # Return the paths of the temporary files
        return temp_file1.name, temp_file2.name
    
    finally:
        temp_file1.close()
        temp_file2.close()
               
def merge(left, right, key):
    #print("running 'merge'")
    merged = []
    left_index = right_index = 0

    # Compare elements from both halves and merge them in sorted order
    while left_index < len(left) and right_index < len(right):
        #print("index = "+str(left_index))
        #print(left_index,left,right_index,right)
        try:
            if int(left[left_index][key]) <= int(right[right_index][key]):
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1
        except:
            if left[left_index][key] <= right[right_index][key]:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1
                
    # Append any remaining elements from both halves
    merged += left[left_index:]
    merged += right[right_index:]
    #print("merged")
    #print(merged)
    return merged

def merge_sorted_files(file1, file2, key):
    #print("running 'merged_sorted_files'")
    # Merge two sorted temporary files into a new sorted temporary file
    merged_data = merge(file1, file2, key)
    merged_file = create_temp_csv_from_dict(merged_data)

    return merged_file

def merge_sort_with_csv(file_path,key):
    #print("running merge_sort_with_csv")
    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        row_count = sum(1 for row in csv_reader)
        # Test CSV length
        if row_count <= 2:
            #print(row_count)
            #Create list of dictionaries from short CSV
            merged=csv_to_list(file_path)
            #print(merged)
            return merged
        else:
            #print(row_count)    
            #Split CSV
        
            csv_left_split, csv_right_split=split_csv(file_path)
            
            #print("left_half_sorted INICIO")
            csv_left_half=merge_sort_with_csv(csv_left_split,key)
            #print("left_half_sorted FIM")
            #print(csv_left_half)
            #print("right_half_sorted INICIO")
            csv_right_half=merge_sort_with_csv(csv_right_split,key)
            #print("right_half_sorted FIM")
            #print(csv_right_half)
            
            #print("try")
            if len(csv_left_half)>1:
                #print("left_half_list INICIO")
                csv_left_list=csv_to_list(csv_left_half)
                #print(csv_left_half)
                os.remove(csv_left_half)
            else:
                csv_left_list=csv_left_half
            if len(csv_right_half)>1:
                #print("right_half_list INICIO")
                csv_right_list=csv_to_list(csv_right_half)
                #print(csv_right_half)
                os.remove(csv_right_half)
            else:
                csv_right_list=csv_right_half
                
            result = merge_sorted_files(csv_left_list, csv_right_list, key)
            
            #print("finishing merge_sort_with_csv")
            
            return result

def merge_sort_main():
    # Specify the path to your input and output CSV files
    print("Choose input file:")
    input_csv_path = open_file_dialog()
    print("Choose output file:")
    output_csv_path = open_file_dialog()
    csv_data_list=csv_to_list(input_csv_path)
    print(csv_data_list[0])
    key=input("Sort based on what? ")
    sorted=merge_sort_with_csv(input_csv_path,key)
    #print(sorted)
    
    # Convert temp file to list
    sorted_list=csv_to_list(sorted)
    os.remove(sorted)
    
    # Write the sorted data to a new CSV file
    header = sorted_list[0].keys() if sorted else []
    write_csv(output_csv_path, sorted_list, header)
    
    print(f"CSV file has been sorted and saved to {output_csv_path}.")
    


merge_sort_main()