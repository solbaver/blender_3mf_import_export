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
from mathutils import Matrix
from bs4 import BeautifulSoup
import sys
import re
import os
import shutil

#just type in console:
#blender --background --python import.py 'YOUR_FILE_PATH' 'YOUR_FILE_NAME'



for i in sys.argv:
	print (i)


filepath = sys.argv[4]
filename = sys.argv[5]
modelpath = '/model'
zip_ref = zipfile.ZipFile(filepath + filename, 'r')
zip_ref.extractall(filepath + modelpath)
zip_ref.close()

model_file = open(filepath + modelpath + '/3D/' + '3dmodel.model', 'r')

soup = BeautifulSoup(model_file, features="xml")

#number of objects in scene
objects_number = len(soup.resources.findAll("object"))    


num = 1

unit = soup.model['unit']
print (unit)
if unit == 'micron':
	bpy.context.scene.unit_settings.system = 'METRIC'
	bpy.context.scene.scale_length = 0.001
if unit == 'millimeter':
	bpy.context.scene.unit_settings.system = 'METRIC'
	bpy.context.scene.unit_settings.scale_length = 0.01
if unit == 'centimeter':
	bpy.context.scene.unit_settings.system= 'METRIC'
	bpy.context.scene.scale_length = 0.1
if unit == 'meter':
	bpy.context.scene.unit_settings.system= 'METRIC'
	bpy.context.scene.scale_length = 1
if unit == 'foot':
	bpy.context.scene.unit_settings.system = 'IMPERIAL'
	bpy.context.scene.scale_length = 1	
if unit == 'inch':
	bpy.context.scene.unit_settings.system = 'IMPERIAL'
	bpy.context.scene.scale_length = 0.1	



while num < objects_number:
#id - number of current object
	ob = soup.resources.findAll(id=num)
	for n in ob:
		name = n.get('name')
		print (name)

	vetexes = []
	triangles = []


	ob = BeautifulSoup(str(ob)[1:-1], features="xml")
	vertex = ob.findAll('vertex')
	triangle = ob.findAll('triangle')
	ob = soup.resources.findAll(id=num)
#part for matrix calculations
	ob_transform = soup.build.findAll(objectid=num)
	ob_transform = BeautifulSoup(str(ob_transform)[1:-1])
	transform = ob_transform.item['transform']

	N = map(float,transform.split())
	N = list(N)

	matrix = [(N[0], N[1], N[2], 0), (N[3], N[4], N[5], 0), (N[6], N[7], N[8], 0), (N[9], N[10], N[11], 1.0)]
	matrix = Matrix(matrix)

	vertexes_x = []
	vertexes_y = []
	vertexes_z = []

	triangles_1 = []
	triangles_2 = []
	triangles_3 = []
 
	verts = []
	faces = []
 
	for v in vertex:
		v = BeautifulSoup(str(v), features="xml")
		vertexes_x.append(v.vertex['x'])
		vertexes_y.append(v.vertex['y'])
		vertexes_z.append(v.vertex['z'])

	for t in triangle:
		t = BeautifulSoup(str(t), features="xml")
		triangles_1.append(t.triangle['v1'])
		triangles_2.append(t.triangle['v2'])
		triangles_3.append(t.triangle['v3'])
	
	i = 0	

	while i < len(vertexes_x):
		vertex_tuple = (float(vertexes_x[i]), float(vertexes_y[i]), float(vertexes_z[i]))	
		verts.insert(i, vertex_tuple)
		i = i + 1
	verts = tuple(verts)


	i = 0	
	while i < len(triangles_1):
		triangle_tuple = (int(triangles_1[i]), int(triangles_2[i]), int(triangles_3[i]))	
		faces.insert(i, triangle_tuple )
		i = i + 1

	faces = tuple(faces)


	mesh_name = str(num)
	#creating object in blender
	blender_me = bpy.data.meshes.new(name)
	blender_ob = bpy.data.objects.new(name, blender_me)
	scn = bpy.context.scene
	scn.objects.link(blender_ob)	
	scn.objects.active = blender_ob
	blender_ob.select = True



	blender_me.from_pydata(verts, [], faces)

	blender_me.update(calc_edges=True)
	num = num + 1

	blender_ob.matrix_world = matrix * blender_ob.matrix_world 


    
model_file.close()
bpy.ops.wm.save_as_mainfile(filepath=filepath+filename+'.blend')


rempath = os.path.join(os.path.abspath(os.path.dirname(filepath)), 'model')

shutil.rmtree(rempath)

