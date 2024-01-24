import os
from concurrent.futures import ProcessPoolExecutor

def process_file(i):
    header_lim = 10   # header + cell info
    root = os.getcwd()
    header_file = "/work/e05/e05/wkjee/Masters/Zirui2023/MnO/coreOnly/new_header"
    footer_file = "/work/e05/e05/wkjee/Masters/Zirui2023/MnO/coreOnly/new_footer"
    size = 24

    Natoms = size + 72
    headN = Natoms + header_lim

    with open(f"{root}/summary_li{size}/A{i}.gin", "r") as target_input:
        lines = target_input.readlines()
        geometry_lines = lines[:headN]
        geometry_lines = geometry_lines[header_lim:]

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
    max_value = 18954
    os.makedirs("newrun", exist_ok=True)

    with ProcessPoolExecutor(max_workers=64) as executor:
        executor.map(process_file, range(sta, max_value + 1))

    os.rename("newrun.log", f"{os.getcwd()}/newrun/newrun.log")

    # Cleaning
    os.remove("geometry")

