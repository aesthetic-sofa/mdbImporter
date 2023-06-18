import struct

class COLOR_565:
    def __init__(self, color_bytes: bytearray):
        self.color_bytes = color_bytes
        im = int.from_bytes(color_bytes, 'little')

        self.B = (im & 0b011111) 
        self.G = ((im >> 5) & 0b111111)
        self.R = ((im >> (5 + 6)) & 0b011111)
    
    def __repr__(self):
        return str(["{:+10.3f}".format(i) for i in [self.R, self.G, self.B]])

class MBD_STRINGS:
    def __init__(self, data: bytearray):
        self.strings = data.decode("utf-8")
    
    def __repr__(self):
        string = self.strings + '\n'
        return string 
    
class MDB_CENTROID:
    def __init__(self, data: bytearray):
        self.x = struct.unpack('f', data[:4])[0]
        self.y = struct.unpack('f', data[4:8])[0]
        self.z = struct.unpack('f', data[8:12])[0]
        self.radius = struct.unpack('f', data[12:16])[0]
    
    def __repr__(self):
        string = 'Coordinates (XYZ):\t' + str(["{:+10.3f}".format(i) for i in [self.x, self.y, self.z]]) + '\n'
        string += 'Radius:\t' + "{:+10.3f}".format(self.radius) + '\n'
        return string 

class MDB_BOUNDING_BOX:
    def __init__(self, data: bytearray):
        self.x = struct.unpack('f', data[:4])[0]
        self.y = struct.unpack('f', data[4:8])[0]
        self.z = struct.unpack('f', data[8:12])[0]
        self.max_x = struct.unpack('f', data[12:16])[0]
        self.max_y = struct.unpack('f', data[16:20])[0]
        self.max_z = struct.unpack('f', data[20:24])[0]
    
    def __repr__(self):
        string = 'Coordinates (XYZ):\t' + str(["{:+10.3f}".format(i) for i in [self.x, self.y, self.z]]) + '\n'
        string += 'Coordinates (MAX-XYZ):\t' + str(["{:+10.3f}".format(i) for i in [self.max_x, self.max_y, self.max_z]]) + '\n'
        return string 

class MDB_ANIMATION_SECTION:
    def __init__(self, data: bytearray):
        self.sizeof_animation_section_data = int.from_bytes(data[:4], 'little')
        self.string_length = int.from_bytes(data[4:8], 'little')
        self.section_name = data[8:self.string_length+8].decode("utf-8", errors="replace")
        self.section_data = data[self.string_length+8:self.sizeof_material_data+4]
    
    def __repr__(self):
        string = 'Section name:\t' + self.section_name + '\n'
        return string 

class MDB_MATERIAL:
    def __init__(self, data: bytearray):
        self.sizeof_material_data = int.from_bytes(data[:4], 'little')
        self.string_length = int.from_bytes(data[4:8], 'little')
        self.texture_name = data[8:self.string_length+8].decode("utf-8", errors="replace")
        self.material_data = data[self.string_length+8:self.sizeof_material_data+4]
    
    def __repr__(self):
        string = 'Texture name:\t' + self.texture_name + '\n'
        return string 
    
class MDB_ANIMATION_FRAME:
    def __init__(self, data: bytearray):
        self.sizeof_frame = int.from_bytes(data[:4], 'little')
        self.frame_data = int.from_bytes(data[4:self.sizeof_frame], 'little')
    
    def __repr__(self):
        string = 'Size of animation frame:\t' + "{:05d}".format(self.sizeof_frame) + '\n'
        return string 

class MDB_FACE:
    def __init__(self, data: bytearray):
        self.sizeof_face_data = int.from_bytes(data[:4], 'little')
        self.vertex1 = struct.unpack('H', data[4:6])[0]
        self.vertex2 = struct.unpack('H', data[6:8])[0]
        self.vertex3 = struct.unpack('H', data[8:10])[0]
        self.material_id = struct.unpack('H', data[10:12])[0]
    
    def __repr__(self):
        string = 'Vertex indices:\t' + str(["{:05d}".format(i) for i in [self.vertex1, self.vertex2, self.vertex3]]) + '\n'
        string += 'Material ID:\t' + "{:05d}".format(self.material_id) + '\n'
        return string

class MDB_VERTEX:
    def __init__(self, data: bytearray):
        self.sizeof_vertex_data = int.from_bytes(data[:4], 'little')
        self.x = struct.unpack('f', data[4:8])[0]
        self.y = struct.unpack('f', data[8:12])[0]
        self.z = struct.unpack('f', data[12:16])[0]
        self.vt_u = struct.unpack('f', data[16:20])[0]
        self.vt_v = struct.unpack('f', data[20:24])[0]
        self.unknown = data[24:self.sizeof_vertex_data]
        self.transparence = COLOR_565(data[-4:])
    
    def __repr__(self):
        string = 'Coordinates (XYZ):\t' + str(["{:+10.3f}".format(i) for i in [self.x, self.y, self.z]]) + '\n'
        string += 'Coordinates (UV):\t' + str(["{:+10.3f}".format(i) for i in [self.vt_u, self.vt_v]]) + '\n'
        string += 'Transparence (RGB):\t' + str(self.transparence) + '\n'
        return string

class MDB_MODEL:
    def __init__(self, data: bytearray):
        self.data = data
        self.size_of_data = int.from_bytes(data[:4], 'little')
        self.model_ID = int.from_bytes(data[4:8], 'little')
        self.number_of_vertices = int.from_bytes(data[8:12], 'little')
        self.__load_vertices()
        self.__get_vertex_data_length()
        self.number_of_faces = int.from_bytes(data[12+self.vertex_data_length:12+self.vertex_data_length+4], 'little')
        self.__load_faces()
        self.__get_face_data_length()
        self.number_of_animation_frames = int.from_bytes(data[16 + self.vertex_data_length + self.face_data_length:16 + self.vertex_data_length + self.face_data_length+4], 'little')
        self.__load_animation_frames()
        self.__get_frame_data_length()
        self.real_data_size = 20 + self.vertex_data_length + self.face_data_length + self.frame_data_length
        assert self.size_of_data + 4 == self.real_data_size, f"Incomplete model! Bytes should be {self.size_of_data + 4}, but are {16 + self.vertex_data_length + self.face_data_length}"

    def __get_vertex_data_length(self):
        n = 4 * self.number_of_vertices
        for i in range(self.number_of_vertices):
            n += self.vertices[i].sizeof_vertex_data
        self.vertex_data_length = n

    def __get_face_data_length(self):
        n = 4 * self.number_of_faces
        for i in range(self.number_of_faces):
            n += self.faces[i].sizeof_face_data
        self.face_data_length = n

    def __get_frame_data_length(self):
        n = 4 * self.number_of_animation_frames
        for i in range(self.number_of_animation_frames):
            n += self.vertices[i].sizeof_frame
        self.frame_data_length = n

    def __load_vertices(self):
        self.vertices = []
        starting_byte = 12 # End of header
        for i in range(self.number_of_vertices):
            vertex = MDB_VERTEX(self.data[starting_byte:])
            self.vertices.append(vertex)
            starting_byte += self.vertices[-1].sizeof_vertex_data + 4

    def __load_faces(self):
        self.faces = []
        starting_byte = 16 + self.vertex_data_length # End of header + vertex data length
        for i in range(self.number_of_faces):
            face = MDB_FACE(self.data[starting_byte:])
            self.faces.append(face)
            starting_byte += self.faces[-1].sizeof_face_data + 4
    
    def __load_animation_frames(self):
        self.animation_frames = []
        starting_byte = 20 + self.vertex_data_length + self.face_data_length # End of header + vertex, face data length
        for i in range(self.number_of_animation_frames):
            frame = MDB_ANIMATION_FRAME(self.data[starting_byte:])
            self.animation_frames.append(frame)
            starting_byte += self.animation_frames[-1].sizeof_frame + 4

    def __repr__(self):
        string = 'Size of model data (bytes): ' + str(self.size_of_data) + '\n'
        string += 'Model ID: ' + str(self.model_ID) + '\n'
        string += 'Number of vertices: ' + str(self.number_of_vertices) + '\n'
        string += 'Number of faces: ' + str(self.number_of_faces) + '\n'
        # for i in range(self.number_of_vertices):
        #     string += str(self.vertices[i])
        # for i in range(self.number_of_faces):
        #     string += str(self.faces[i])
        return string

class MDB_HEADER:
    def __init__(self, data: bytearray):
        self.file_structure_offset = int.from_bytes(data[:4], 'little')
        self.unknown = int.from_bytes(data[4:8], 'little')
        self.last_four_bytes_before_strings_offset = int.from_bytes(data[4:12], 'little')
        self.number_of_models = int.from_bytes(data[12:16], 'little')

class MDB:
    def __init__(self, path: str):

        with open (path, 'rb') as file:
            self.data = file.read()
        
        self.name = path.rpartition('\\')[2]
        cursor = 0
        self.header = MDB_HEADER(self.data[:16])
        cursor = 16
        self.__load_models()
        self.__get_model_data_length()
        cursor += self.model_data_length
        self.number_of_materials = int.from_bytes(self.data[cursor:4 + cursor], 'little')
        self.__load_materials()
        self.__get_material_data_length()
        cursor += self.material_data_length
        self.number_of_animation_sections = int.from_bytes(self.data[cursor:4 + cursor], 'little')
        self.__load_animation_sections()
        self.__get_animation_section_data_length()
        cursor += self.animation_section_data_length
        self.bounding_box = MDB_BOUNDING_BOX(self.data[cursor:])
        cursor += 24
        self.centroid = MDB_CENTROID(self.data[cursor:])
        cursor += 16
        self.strings = MBD_STRINGS(self.data[self.header.file_structure_offset:])

    def __get_model_data_length(self):
        n = 4 * self.header.number_of_models
        for i in range(self.header.number_of_models):
            n += self.models[i].size_of_data
        self.model_data_length = n
    
    def __get_material_data_length(self):
        n = 4 * self.number_of_materials
        for i in range(self.number_of_materials):
            n += self.materials[i].sizeof_material_data
        self.material_data_length = n

    def __get_animation_section_data_length(self):
        n = 4 * self.number_of_animation_sections
        for i in range(self.number_of_animation_sections):
            n += self.animation_sections[i].sizeof_animation_section_data
        self.animation_section_data_length = n
        
    def __load_models(self):
        self.models = []
        starting_byte = 16 # End of header
        for i in range(self.header.number_of_models):
            model = MDB_MODEL(self.data[starting_byte:])
            self.models.append(model)
            starting_byte += self.models[-1].size_of_data + 4
    
    def __load_materials(self):
        self.materials = []
        starting_byte = 20 + self.model_data_length # End of header
        for i in range(self.number_of_materials):
            material = MDB_MATERIAL(self.data[starting_byte:])
            self.materials.append(material)
            starting_byte += self.materials[-1].sizeof_material_data + 4
    
    def __load_animation_sections(self):
        self.animation_sections = []
        starting_byte = 24 + self.model_data_length + self.material_data_length # End of header
        for i in range(self.number_of_animation_sections):
            material = MDB_MATERIAL(self.data[starting_byte:])
            self.animation_sections.append(material)
            starting_byte += self.animation_sections[-1].sizeof_animation_section_data + 4

    def __repr__(self):
        string = self.name + '\n'
        string += 'Number of models:\t' + str(self.header.number_of_models) + '\n'
        for i in range(self.header.number_of_models):
            string += "MODEL #" + str(i) +"\n"
            string += str(self.models[i])
            string += "*************************************\n"
        string += 'Number of materials:\t' + str(self.number_of_materials) + '\n'
        for i in range(self.number_of_materials):
            string += "MATERIAL #" + str(i) +"\n"
            string += str(self.materials[i])
            string += "*************************************\n"
        string += 'Number of animation sections:\t' + str(self.number_of_animation_sections) + '\n'
        string += "*************************************\nBOUNDING BOX\n" + str(self.bounding_box)
        string += "*************************************\nCENTROID\n" + str(self.centroid)
        string += "*************************************\nSTRINGS\n" + str(self.strings)
        return string