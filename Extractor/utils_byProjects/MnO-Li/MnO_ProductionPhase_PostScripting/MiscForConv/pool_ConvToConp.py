import os,sys
from concurrent.futures import ProcessPoolExecutor

def process_file(i):
    root = os.getcwd()
    header_file = "/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/new_header"
    footer_file = "/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/new_footer"

    size = 24

    with open(f"{root}/summary_li{size}/A{i}.gin", "r") as target_input:
        lines = target_input.readlines()

        end_line   = None
        for l,line in enumerate(lines):
            if 'total' in line:
                end_line = l
                break

        geometry_lines = lines[:l]
        geometry_lines = geometry_lines[5:]

    with open("geometry", "w") as geometry_file:
        geometry_file.writelines(geometry_lines)

    with open(f"{header_file}", "r") as header_content, \
         open(f"{root}/newrun/A{i}.gin", "w") as output_file, \
         open(f"{footer_file}", "r") as footer_content:

        output_file.write(header_content.read())
        output_file.writelines(geometry_lines)
        output_file.write(footer_content.read())

    print(f"progressing ... {i}")

if __name__ == "__main__":
    sta = 0
    max_value = 18914
    os.makedirs("newrun", exist_ok=True)

    with ProcessPoolExecutor(max_workers=64) as executor:
        executor.map(process_file, range(sta, max_value + 1))

    os.rename("newrun.log", f"{os.getcwd()}/newrun/newrun.log")

    # Cleaning
    os.remove("geometry")

