import sitf
import extra

filename = "input.sitf"

header_sitf, all_sitf, sel_sitf = sitf.read_sitf_file(filename)

sitf.write_sitf_file(header_sitf, all_sitf, sel_sitf, "output.sitf")

test_dict = extra.make_dict(header_sitf, all_sitf, sel_sitf)
extra.save_yaml(test_dict, "output.yaml")
