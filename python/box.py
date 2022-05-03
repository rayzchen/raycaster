from pyunity import *
import pyunity.config
pyunity.config.size = (500, 500)

scene = SceneManager.AddScene("Scene")
scene.mainCamera.transform.position = Vector3(0, 0, -10)

light = scene.gameObjects[1].GetComponent(Light)
light.transform.position = Vector3(0, 7.5, 0)
light.transform.LookAtPoint(Vector3(0, -10, 0))
light.intensity = 200
light.type = LightType.Point

back = GameObject("Back")
back.transform.position = Vector3(0, 0, 10)
back.transform.scale = Vector3(10, 10, 1)
renderer = back.AddComponent(MeshRenderer)
renderer.mesh = Loader.Primitives.doubleQuad
renderer.mat = Material(RGB(255, 0, 0))
scene.Add(back)

ceiling = GameObject("Ceiling")
ceiling.transform.position = Vector3(0, 10, 0)
ceiling.transform.eulerAngles = Vector3(90, 0, 0)
ceiling.transform.scale = Vector3(10, 10, 1)
renderer = ceiling.AddComponent(MeshRenderer)
renderer.mesh = Loader.Primitives.doubleQuad
renderer.mat = Material(RGB(0, 255, 0))
scene.Add(ceiling)

floor = GameObject("Floor")
floor.transform.position = Vector3(0, -10, 0)
floor.transform.eulerAngles = Vector3(-90, 0, 0)
floor.transform.scale = Vector3(10, 10, 1)
renderer = floor.AddComponent(MeshRenderer)
renderer.mesh = Loader.Primitives.doubleQuad
renderer.mat = Material(RGB(0, 0, 255))
scene.Add(floor)

left = GameObject("Left")
left.transform.position = Vector3(-10, 0, 0)
left.transform.eulerAngles = Vector3(0, 90, 0)
left.transform.scale = Vector3(10, 10, 1)
renderer = left.AddComponent(MeshRenderer)
renderer.mesh = Loader.Primitives.doubleQuad
renderer.mat = Material(RGB(255, 255, 0))
scene.Add(left)

right = GameObject("Right")
right.transform.position = Vector3(10, 0, 0)
right.transform.eulerAngles = Vector3(0, -90, 0)
right.transform.scale = Vector3(10, 10, 1)
renderer = right.AddComponent(MeshRenderer)
renderer.mesh = Loader.Primitives.doubleQuad
renderer.mat = Material(RGB(0, 255, 255))
scene.Add(right)

sphere1 = GameObject("Sphere")
sphere1.transform.position = Vector3(4, -5, 8)
sphere1.transform.scale = Vector3(5, 5, 5)
renderer = sphere1.AddComponent(MeshRenderer)
renderer.mesh = Loader.Primitives.sphere
renderer.mat = Material(RGB(200, 200, 200))
scene.Add(sphere1)

sphere2 = GameObject("Sphere")
sphere2.transform.position = Vector3(-4, -5, 5)
sphere2.transform.scale = Vector3(5, 5, 5)
renderer = sphere2.AddComponent(MeshRenderer)
renderer.mesh = Loader.Primitives.sphere
renderer.mat = Material(RGB(127, 127, 127))
scene.Add(sphere2)

SceneManager.LoadScene(scene)
