from os.path import exists
import sys

uv_x_size = 256
uv_y_size = 1


def get_corrected_uv(index, uv: tuple, verts: int) -> tuple:
    signtest = int(round((verts - 1) / 2))
    uv_x = uv[0] + (1 if index < signtest else -1) * 1 / uv_x_size * 0.25 * (index % 2)
    uv_y = uv[1] + (-1 if index < signtest else 1) * (1 / uv_y_size * 0.25 * (1 if index % 2 == 0 else 0))

    return uv_x, uv_y


def assign_index(element: str, name: str, index: list, i: int):
    if element == name and index[0] == -1:
        index[0] = i
    elif not element == name and index[0] != -1 and index[1] == -1:
        index[1] = i - 1


class OBJ():
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.lines = None
        self.vt_index = [-1, -1]
        self.v_index = [-1, -1]
        self.f_index = [-1, -1]
        self.read(file_name)

    def read(self, new_file_name: str):
        with open(new_file_name, 'r') as file:
            self.lines = file.readlines()

            for i in range(len(self.lines)):
                line = self.lines[i]
                line_elements = line.split(" ")

                assign_index(line_elements[0], "v", self.v_index, i)
                assign_index(line_elements[0], "vt", self.vt_index, i)
                assign_index(line_elements[0], "f", self.f_index, i)

                if self.v_index[0] != -1 and self.v_index[1] != -1 and self.vt_index[0] != -1 \
                        and self.vt_index[1] != -1 and self.f_index[0] != -1 and self.f_index[1] != -1:
                    break

            assign_index("", "v", self.v_index, len(self.lines))
            assign_index("", "vt", self.vt_index, len(self.lines))
            assign_index("", "f", self.f_index, len(self.lines))

    def write(self):
        self.write(self.file_name)

    def write(self, new_name: str):
        with open(new_name, 'w') as file:
            file.write("".join(self.lines))

    # return the vt index of the appended uv
    def append_vt(self, uv_x, uv_y) -> int:
        vt_index = self.vt_index[1] - self.vt_index[0] + 2
        self.lines.insert(self.vt_index[1] + 1, "")
        self.change_uv(vt_index, uv_x, uv_y)
        self.vt_index[1] += 1

        if self.f_index[0] >= self.vt_index[1]:
            self.f_index = [self.f_index[0] + 1, self.f_index[1] + 1]

        if self.v_index[0] >= self.vt_index[1]:
            self.v_index = [self.v_index[0] + 1, self.v_index[1] + 1]

        return vt_index

    def change_uv(self, vt_index: int, new_uv_x, new_uv_y):
        self.lines[self.vt_index[0] + vt_index - 1] = "vt " + str(new_uv_x) + " " + str(new_uv_y) + "\n"

    def get_uv(self, vt_index: int) -> list[float]:
        vt_line = self.lines[self.vt_index[0] + vt_index - 1]
        uv = vt_line.split(" ")
        uv.remove("vt")
        uv[0] = float(uv[0])
        uv[1] = float(uv[1].strip())

        return uv

    def get_faces(self) -> list:
        return self.lines[self.f_index[0]:self.f_index[1] + 1]

    def change_face(self, f_index: int, face_element: list[str]):
        self.lines[self.f_index[0] + f_index - 1] = "f " + " ".join(face_element) + "\n"

    def get_face(self, f_index) -> str:
        if self.f_index[0] + f_index - 1 > self.f_index[1]:
            return None

        return self.lines[self.f_index[0] + f_index - 1]

    def are_uvs_equal(self, vt_indeces: list) -> bool:
        equal = True

        for vt_i in range(len(vt_indeces)):
            if vt_i == len(vt_indeces) - 1:
                break

            if self.get_uv(vt_indeces[vt_i]) != self.get_uv(vt_indeces[vt_i + 1]):
                equal = False
                break

        return equal

    def remove_lines(self, from_index: int, to_index):
        del self.lines[from_index:to_index + 1]

        new_v_index = (self.v_index[0], self.v_index[1])
        new_vt_index = (self.vt_index[0], self.vt_index[1])
        new_f_index = (self.f_index[0], self.f_index[1])

        # TODO adapt indeces


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("You need to provide the path to the obj to convert.")
        quit(0)

    file_name = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) == 3 else file_name

    if exists(file_name):
        obj = OBJ(file_name)

        if obj.lines is None:
            print("No lines were read in the file!")
            quit(1)

        # contains original vt index mapped to a tuple of new vt indeces
        vt_new_map = {}
        old_vt_index = (obj.vt_index[0], obj.vt_index[1])

        for f_index, face in enumerate(obj.get_faces()):
            # the mappings of the v index/vt index/vn index
            face_elements = face.split(" ")

            face_elements.remove("f")
            face_elements[len(face_elements) - 1] = face_elements[len(face_elements) - 1].replace("\n", "")

            # the vt indeces of the face element
            vt_indeces = []

            for v in face_elements:
                vt_indeces.append(int(str(v).split("/")[1]))

            if vt_new_map.get(vt_indeces[0]):
                # the vt indeces have already been changed and mapped
                vt_indeces = vt_new_map.get(vt_indeces[0])
            elif obj.are_uvs_equal(vt_indeces):
                uv = obj.get_uv(vt_indeces[0])

                #uv0 = get_corrected_uv(0, uv, len(vt_indeces))
                #obj.change_uv(vt_indeces[0], uv0[0], uv0[1])

                # add a new vt and correct the vt index
                for i in range(0, len(vt_indeces)):
                    new_uv = get_corrected_uv(i, obj.get_uv(vt_indeces[i]), len(vt_indeces))
                    vt_indeces[i] = obj.append_vt(new_uv[0], new_uv[1]) - (old_vt_index[1] - old_vt_index[0] + 1)

                vt_new_map[vt_indeces[0]] = tuple(vt_indeces)

            for fv in range(len(face_elements)):
                elements = face_elements[fv].split("/")
                elements[1] = str(vt_indeces[fv])

                face_elements[fv] = "/".join(elements)

            obj.change_face(f_index + 1, face_elements)

        obj.remove_lines(old_vt_index[0], old_vt_index[1])
        obj.write(output_name)
