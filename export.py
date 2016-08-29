# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import zipfile
import sys
import os
import shutil

#just type in console:
#blender --background --python export.py 'YOUR_FILE_PATH' 'YOUR_FILE_NAME'

unit = 'millimeter'
name = 'test'

filepath = sys.argv[4]
filename = sys.argv[5]

print (filename)
print (filepath)	
bpy.ops.wm.open_mainfile(filepath=filepath+filename)

def create_types():
	t = open("[Content_Types].xml", 'w')
	t.write('''<?xml version="1.0" encoding="UTF-8"?>''')
	t.write('''<Types>''')
	t.write('''<Default ContentType="application/vnd.openxmlformats-package.relationships+xml" Extension="rels"/>''')
	t.write('''<Default ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" Extension="model"/>''')
	t.write('''</Types>''')
	t.close()	
	
def find_transformation(ob):	
	if ob.type == 'MESH':
			
			old_matrix = list(ob.matrix_world)
			print (ob.name)
			new_matrix = ''
			for line in old_matrix:
				new_matrix = new_matrix + str(line[0]) + ' ' +  str(line[1]) + ' ' +  str(line[2]) + ' '
			print (new_matrix)
			



			return new_matrix
def create_object(ob, i, t):			

	t.write('''<object id="''' + str(i) +  '''" name="''' + str(ob.name) + '''" type="model">''' + '\n')
	t.write('''<mesh>''' + '\n')
	t.write('''<vertices>''' + '\n')
	vert_coords = [(ob.matrix_world * v.co) for v in ob.data.vertices]
	for c in vert_coords:
		t.write('''<vertex x="''' + str(c[0]) + '''" y="''' + str(c[1]) + '''" z="''' + str(c[2]) + '''"/>''' + '\n')
	t.write('''</vertices>''' + '\n')
	t.write('''<triangles>''' + '\n')
	poly_coords = [(p.vertices[:]) for p in ob.data.polygons]
	for c in poly_coords:
		t.write('''<triangle v1="''' + str(c[0]) + '''" v2="''' + str(c[1]) + '''" v3="''' + str(c[2]) + '''"/>''' + '\n')
	t.write('''</triangles>''' + '\n')
	t.write('''</mesh>''' + '\n')
	t.write('''</object>''' + '\n')
	
	
def create_model():
	scene = bpy.context.scene
	t = open(filepath + "3D" "/3dmodel.model", 'w')
	t.write('''<?xml version="1.0" encoding="UTF-8"?>''' + '\n')
	t.write('''<model unit="''' + str(unit) + '''" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">''' + '\n')
	t.write('''<metadata name="Title">''' + name + '''</metadata>''' + '\n')
	t.write('''<metadata name="Designer">''' + name + '''</metadata>''' + '\n')
	t.write('''<metadata name="LicenseTerms">''' + name + '''</metadata>''' + '\n')
	t.write('''<metadata name="CreationDate">''' + name + '''</metadata>''' + '\n')
	t.write('''<metadata name="Description">''' + name + '''</metadata>''' + '\n')
	t.write('''<resources>''' + '\n')
	i = 1
	for ob in scene.objects:
		if ob.type == 'MESH':
			create_object(ob, i, t)
			i = i + 1
	#
	t.write('''</resources>''' + '\n')
		
	t.write('''<build>''' + '\n')
	i = 1
	for ob in scene.objects:
		if ob.type == 'MESH':
			new_matrix = find_transformation(ob)
			line = '''<item objectid="''' + str(i) + '''" transform="''' + str(new_matrix) + '''"/>''' + '\n'
			t.write(line)
			i = i + 1
	t.write('''</build>''' + '\n')

	t.write('''</model>''' + '\n')
	
	t.close

	
	
for param in sys.argv:
	print (param)
create_types()

os.mkdir(filepath+'/_rels')
os.mkdir(filepath+'/3D')
os.chdir(filepath+'/3D') 

create_model()

#creating .3dm archive
os.chdir(filepath) 
zip_name = filename + '.3mf'
zip_exp = zipfile.ZipFile(filepath + zip_name, mode='w')
zip_exp.write('[Content_Types].xml')
zip_exp.write('_rels')
zip_exp.write('3D/3dmodel.model')

zip_exp.close()

#deleting leftovers
os.remove(filepath+'[Content_Types].xml')
os.remove(filepath+'3D/3dmodel.model')
os.rmdir(filepath+'3D')
os.rmdir(filepath+'_rels')
