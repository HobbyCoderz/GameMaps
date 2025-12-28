import re

# Configuration
input_file_path = 'izurvive.har'
output_file_path = 'map_tiles.txt'

# The pattern: \d+ matches any sequence of numbers
# We escape the dots and forward slashes where necessary
pattern = r'"url": "https://maps\.izurvive\.com/maps/ChernarusPlus-Top/1\.26\.0/tiles/6/\d+/\d+\.webp",'

def extract_map_urls():
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
             open(output_file_path, 'a', encoding='utf-8') as outfile:
            
            count = 0
            for line in infile:
                # search() finds the pattern anywhere in the line
                if re.search(pattern, line):
                    outfile.write(line)
                    count += 1
            
            print(f"Success! {count} lines were appended to {output_file_path}.")
            
    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    extract_map_urls()